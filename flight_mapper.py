# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

# Get the current credentials
session = get_active_session()

# Page configuration
st.set_page_config(
    page_title="Advanced Flight Mapper",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✈️ Advanced Flight Tracker & Mapper")
st.markdown("---")

# Sidebar for controls
st.sidebar.header("🎛️ Flight Filters & Controls")

def get_flights_on_day_and_hour(dt_obj, hour_int, opts={}):
    """
    Retrieves comprehensive flight data aggregated by minute for operational analysis.
    """
    date_part = dt_obj.strftime("%Y-%m-%d")
    
    # Build WHERE clause with optional filters
    where_conditions = [
        f"DATE(record_ts_utz) = '{date_part}'",
        f"HOUR(record_ts_utz) = {hour_int}"
    ]
    
    if opts.get('air_ground_filter'):
        where_conditions.append(f"air_ground = '{opts['air_ground_filter']}'")
    
    if opts.get('source_filter'):
        where_conditions.append(f"source_table = '{opts['source_filter']}'")
    
    where_clause = " AND ".join(where_conditions)

    sql_query = f"""
        SELECT
            DATE_TRUNC('minute', record_ts_utz) as MINUTE_TS,
            COUNT(*) as TOTAL_AIRCRAFT,
            COUNT(CASE WHEN air_ground = 'A' THEN 1 END) as AIRBORNE_COUNT,
            COUNT(CASE WHEN air_ground = 'G' THEN 1 END) as GROUND_COUNT,
            COUNT(DISTINCT hex) as UNIQUE_AIRCRAFT,
            AVG(CASE WHEN air_ground = 'A' THEN gs END) as AVG_AIRBORNE_SPEED,
            AVG(CASE WHEN air_ground = 'G' THEN gs END) as AVG_GROUND_SPEED,
            AVG(CASE WHEN air_ground = 'A' THEN alt_baro END) as AVG_ALTITUDE,
            MAX(CASE WHEN air_ground = 'A' THEN alt_baro END) as MAX_ALTITUDE,
            MIN(CASE WHEN air_ground = 'A' THEN alt_baro END) as MIN_ALTITUDE,
            COUNT(CASE WHEN source_table = 'KBFI' THEN 1 END) as KBFI_COUNT,
            COUNT(CASE WHEN source_table = 'KAPA' THEN 1 END) as KAPA_COUNT,
            COUNT(CASE WHEN squawk IN ('7500', '7600', '7700') THEN 1 END) as EMERGENCY_COUNT,
            AVG(gs) as OVERALL_AVG_SPEED,
            STDDEV(alt_baro) as ALTITUDE_SPREAD
        FROM capstone_dhall.ads_b.flight_data_dt
        WHERE {where_clause}
        GROUP BY MINUTE_TS
        ORDER BY MINUTE_TS
    """
    
    return session.sql(sql_query).to_pandas()

def get_detailed_flights(dt_obj, hour_int, opts={}):
    """Enhanced detailed flight data retrieval with filtering options."""
    date_part = dt_obj.strftime("%Y-%m-%d")
    
    # Build WHERE clause with optional filters
    where_conditions = [
        f"DATE(record_ts_utz) = '{date_part}'",
        f"HOUR(record_ts_utz) = {hour_int}"
    ]
    
    if opts.get('flight_filter'):
        where_conditions.append(f"UPPER(flight) LIKE UPPER('%{opts['flight_filter']}%')")
    
    if opts.get('hex_filter'):
        where_conditions.append(f"UPPER(hex) = UPPER('{opts['hex_filter']}')")
    
    if opts.get('air_ground_filter'):
        where_conditions.append(f"air_ground = '{opts['air_ground_filter']}'")
    
    if opts.get('source_filter'):
        where_conditions.append(f"source_table = '{opts['source_filter']}'")
    
    if opts.get('min_altitude'):
        where_conditions.append(f"alt_baro >= {opts['min_altitude']}")
    
    if opts.get('max_altitude'):
        where_conditions.append(f"alt_baro <= {opts['max_altitude']}")
    
    if opts.get('min_speed'):
        where_conditions.append(f"gs >= {opts['min_speed']}")
    
    if opts.get('max_speed'):
        where_conditions.append(f"gs <= {opts['max_speed']}")
    
    where_clause = " AND ".join(where_conditions)
    
    return session.sql(f"""
        SELECT 
            record_ts_utz, 
            record_ts, 
            lat, 
            lon, 
            alt_baro,
            gps_alt,
            gs,
            heading,
            flight,
            hex,
            squawk,
            air_ground,
            source_table
        FROM capstone_dhall.ads_b.flight_data_dt
        WHERE {where_clause}
        AND lat IS NOT NULL 
        AND lon IS NOT NULL
        ORDER BY record_ts_utz
    """).to_pandas()

def get_flight_path(hex_code, dt_obj):
    """Get complete flight path for a specific aircraft on a given date."""
    date_part = dt_obj.strftime("%Y-%m-%d")
    
    return session.sql(f"""
        SELECT 
            record_ts_utz,
            lat,
            lon,
            alt_baro,
            gs,
            heading,
            flight
        FROM capstone_dhall.ads_b.flight_data_dt
        WHERE hex = '{hex_code}'
        AND DATE(record_ts_utz) = '{date_part}'
        AND lat IS NOT NULL 
        AND lon IS NOT NULL
        ORDER BY record_ts_utz
    """).to_pandas()

def get_airport_stats(dt_obj):
    """Get statistics by airport for the selected date."""
    date_part = dt_obj.strftime("%Y-%m-%d")
    
    return session.sql(f"""
        SELECT 
            source_table,
            COUNT(*) as total_records,
            COUNT(DISTINCT hex) as unique_aircraft,
            AVG(alt_baro) as avg_altitude,
            AVG(gs) as avg_speed,
            COUNT(CASE WHEN air_ground = 'G' THEN 1 END) as ground_records,
            COUNT(CASE WHEN air_ground = 'A' THEN 1 END) as air_records
        FROM capstone_dhall.ads_b.flight_data_dt
        WHERE DATE(record_ts_utz) = '{date_part}'
        GROUP BY source_table
    """).to_pandas()

# Sidebar Controls
date_slider_val = st.sidebar.date_input(
    "📅 Select Date:",
    min_value=datetime(2021, 3, 1).date(),
    max_value=datetime.today().date(),
    value=datetime(2024, 3, 9).date()  # Fixed future date issue
)

hour_slider_val = st.sidebar.slider(
    "🕐 Hour (UTC):",
    min_value=0,
    max_value=23,
    value=datetime.now().hour,
)

# Advanced Filters
st.sidebar.subheader("🔍 Advanced Filters")

flight_filter = st.sidebar.text_input("✈️ Flight Number (partial match):", "")
hex_filter = st.sidebar.text_input("🔢 Aircraft HEX ID:", "")

air_ground_options = st.sidebar.selectbox(
    "🛬 Aircraft Status:",
    options=["All", "Airborne (A)", "Ground (G)"],
    index=0
)
air_ground_filter = None if air_ground_options == "All" else air_ground_options[-2]

source_options = st.sidebar.selectbox(
    "📍 Data Source:",
    options=["All", "KBFI", "KAPA"],
    index=0
)
source_filter = None if source_options == "All" else source_options

# Altitude and Speed Filters
st.sidebar.subheader("📊 Range Filters")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_altitude = st.number_input("Min Altitude (ft):", value=0, step=1000)
    min_speed = st.number_input("Min Speed (knots):", value=0, step=50)
with col2:
    max_altitude = st.number_input("Max Altitude (ft):", value=50000, step=1000)
    max_speed = st.number_input("Max Speed (knots):", value=1000, step=50)

# Build options dictionary
filter_opts = {
    'flight_filter': flight_filter if flight_filter else None,
    'hex_filter': hex_filter if hex_filter else None,
    'air_ground_filter': air_ground_filter,
    'source_filter': source_filter,
    'min_altitude': min_altitude if min_altitude > 0 else None,
    'max_altitude': max_altitude if max_altitude < 50000 else None,
    'min_speed': min_speed if min_speed > 0 else None,
    'max_speed': max_speed if max_speed < 1000 else None,
}

date_as_string = date_slider_val.strftime("%Y-%m-%d")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.header(f"📊 Flight Data for {date_as_string} at {hour_slider_val}:00 UTC")

with col2:
    # Airport Statistics
    airport_stats = get_airport_stats(date_slider_val)
    if not airport_stats.empty:
        st.metric("Total Aircraft", airport_stats['UNIQUE_AIRCRAFT'].sum())
        st.metric("Total Records", airport_stats['TOTAL_RECORDS'].sum())

# Get data with filters
flights_by_minute_df = get_flights_on_day_and_hour(date_slider_val, hour_slider_val, filter_opts)
detailed_flights_df = get_detailed_flights(date_slider_val, hour_slider_val, filter_opts)

# Enhanced Operational Timeline Dashboard
if not flights_by_minute_df.empty:
    
    st.subheader("🎯 Operational Flight Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        peak_traffic = flights_by_minute_df['TOTAL_AIRCRAFT'].max()
        st.metric("Peak Traffic", f"{peak_traffic} aircraft/min")
    with col2:
        avg_airborne = flights_by_minute_df['AIRBORNE_COUNT'].mean()
        st.metric("Avg Airborne", f"{avg_airborne:.1f}")
    with col3:
        total_unique = flights_by_minute_df['UNIQUE_AIRCRAFT'].sum()
        st.metric("Unique Aircraft", f"{total_unique}")
    with col4:
        emergency_total = flights_by_minute_df['EMERGENCY_COUNT'].sum() if 'EMERGENCY_COUNT' in flights_by_minute_df.columns else 0
        st.metric("Emergency Codes", f"{emergency_total}", delta_color="inverse")
    
    # Enhanced timeline tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛫 Traffic Control", "🏢 Ground Operations", "📊 Altitude Management", 
        "🏁 Airport Comparison", "⚠️ Safety Monitoring"
    ])
    
    with tab1:
        # Air Traffic Control View
        st.markdown("##### Air Traffic Control Dashboard")
        
        # Airborne vs Ground Traffic
        fig_atc = go.Figure()
        
        # Add airborne aircraft
        fig_atc.add_trace(go.Scatter(
            x=flights_by_minute_df['MINUTE_TS'],
            y=flights_by_minute_df['AIRBORNE_COUNT'],
            mode='lines+markers',
            name='Airborne Aircraft',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        # Add ground aircraft
        fig_atc.add_trace(go.Scatter(
            x=flights_by_minute_df['MINUTE_TS'],
            y=flights_by_minute_df['GROUND_COUNT'],
            mode='lines+markers',
            name='Ground Aircraft',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255, 127, 14, 0.2)'
        ))
        
        # Highlight peak traffic periods
        peak_threshold = flights_by_minute_df['TOTAL_AIRCRAFT'].quantile(0.8)
        peak_periods = flights_by_minute_df[flights_by_minute_df['TOTAL_AIRCRAFT'] >= peak_threshold]
        
        if not peak_periods.empty:
            for _, period in peak_periods.iterrows():
                try:
                    # Convert timestamp to string to avoid pandas arithmetic issues
                    timestamp_str = pd.to_datetime(period['MINUTE_TS']).strftime('%H:%M:%S')
                    fig_atc.add_vline(
                        x=period['MINUTE_TS'].isoformat() if hasattr(period['MINUTE_TS'], 'isoformat') else str(period['MINUTE_TS']),
                        line_color="red",
                        line_width=2,
                        opacity=0.6,
                        annotation_text=f"Peak: {period['TOTAL_AIRCRAFT']}"
                    )
                except Exception as e:
                    # If vline fails, add a shape instead
                    fig_atc.add_shape(
                        type="line",
                        x0=period['MINUTE_TS'], x1=period['MINUTE_TS'],
                        y0=0, y1=1,
                        yref="paper",
                        line=dict(color="red", width=2),
                        opacity=0.6
                    )
        
        fig_atc.update_layout(
            title="Air Traffic Control: Real-time Aircraft Status",
            xaxis_title="Time (UTC)",
            yaxis_title="Number of Aircraft",
            hovermode='x unified',
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig_atc, use_container_width=True)
        
        # Speed monitoring for ATC
        col1, col2 = st.columns(2)
        with col1:
            if 'AVG_AIRBORNE_SPEED' in flights_by_minute_df.columns:
                fig_speed = px.line(
                    flights_by_minute_df, 
                    x='MINUTE_TS', 
                    y='AVG_AIRBORNE_SPEED',
                    title='Average Airborne Speed',
                    color_discrete_sequence=['#2ca02c']
                )
                fig_speed.update_layout(yaxis_title="Speed (knots)", height=300)
                st.plotly_chart(fig_speed, use_container_width=True)
        
        with col2:
            # Unique aircraft tracking
            fig_unique = px.bar(
                flights_by_minute_df, 
                x='MINUTE_TS', 
                y='UNIQUE_AIRCRAFT',
                title='Unique Aircraft per Minute',
                color='UNIQUE_AIRCRAFT',
                color_continuous_scale='viridis'
            )
            fig_unique.update_layout(yaxis_title="Unique Aircraft", height=300)
            st.plotly_chart(fig_unique, use_container_width=True)
    
    with tab2:
        # Ground Operations View
        st.markdown("##### Ground Operations Dashboard")
        
        # Ground movement analysis
        if 'AVG_GROUND_SPEED' in flights_by_minute_df.columns:
            fig_ground = go.Figure()
            
            # Ground aircraft count
            fig_ground.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['GROUND_COUNT'],
                mode='lines+markers',
                name='Aircraft on Ground',
                line=dict(color='#d62728', width=3),
                yaxis='y1'
            ))
            
            # Ground speed (secondary axis)
            fig_ground.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['AVG_GROUND_SPEED'],
                mode='lines+markers',
                name='Avg Ground Speed',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                yaxis='y2'
            ))
            
            fig_ground.update_layout(
                title="Ground Operations: Aircraft Movement & Speed",
                xaxis_title="Time (UTC)",
                yaxis=dict(title="Aircraft on Ground", side="left", color="#d62728"),
                yaxis2=dict(title="Ground Speed (knots)", side="right", overlaying="y", color="#ff7f0e"),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_ground, use_container_width=True)
        
        # Ground traffic density heatmap
        col1, col2 = st.columns(2)
        with col1:
            if 'GROUND_COUNT' in flights_by_minute_df.columns:
                # Create ground traffic intensity chart
                fig_intensity = px.bar(
                    flights_by_minute_df,
                    x='MINUTE_TS',
                    y='GROUND_COUNT',
                    title='Ground Traffic Intensity',
                    color='GROUND_COUNT',
                    color_continuous_scale='Reds'
                )
                fig_intensity.update_layout(height=300)
                st.plotly_chart(fig_intensity, use_container_width=True)
        
        with col2:
            # Turnaround efficiency (airborne to ground ratio)
            if 'AIRBORNE_COUNT' in flights_by_minute_df.columns and 'GROUND_COUNT' in flights_by_minute_df.columns:
                flights_by_minute_df['EFFICIENCY_RATIO'] = (
                    flights_by_minute_df['AIRBORNE_COUNT'] / 
                    (flights_by_minute_df['GROUND_COUNT'] + 1)  # +1 to avoid division by zero
                )
                
                fig_efficiency = px.line(
                    flights_by_minute_df,
                    x='MINUTE_TS',
                    y='EFFICIENCY_RATIO',
                    title='Operations Efficiency Ratio',
                    color_discrete_sequence=['#9467bd']
                )
                fig_efficiency.update_layout(yaxis_title="Airborne/Ground Ratio", height=300)
                st.plotly_chart(fig_efficiency, use_container_width=True)
    
    with tab3:
        # Altitude Management View
        st.markdown("##### Altitude Management Dashboard")
        
        # Altitude envelope visualization
        fig_altitude = go.Figure()
        
        # Average altitude
        if 'AVG_ALTITUDE' in flights_by_minute_df.columns:
            fig_altitude.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['AVG_ALTITUDE'],
                mode='lines+markers',
                name='Average Altitude',
                line=dict(color='#1f77b4', width=3)
            ))
        
        # Altitude envelope (min/max)
        if all(col in flights_by_minute_df.columns for col in ['MIN_ALTITUDE', 'MAX_ALTITUDE']):
            fig_altitude.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['MAX_ALTITUDE'],
                mode='lines',
                name='Max Altitude',
                line=dict(color='rgba(255,0,0,0.3)'),
                fill='tonexty'
            ))
            
            fig_altitude.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['MIN_ALTITUDE'],
                mode='lines',
                name='Min Altitude',
                line=dict(color='rgba(255,0,0,0.3)'),
                fill='tozeroy'
            ))
        
        # Add standard altitude levels
        for alt_level in [10000, 20000, 30000, 40000]:
            fig_altitude.add_hline(
                y=alt_level,
                line_dash="dot",
                line_color="gray",
                annotation_text=f"FL{alt_level//100}"
            )
        
        fig_altitude.update_layout(
            title="Altitude Management: Flight Level Distribution",
            xaxis_title="Time (UTC)",
            yaxis_title="Altitude (feet)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_altitude, use_container_width=True)
        
        # Altitude spread analysis
        if 'ALTITUDE_SPREAD' in flights_by_minute_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_spread = px.line(
                    flights_by_minute_df,
                    x='MINUTE_TS',
                    y='ALTITUDE_SPREAD',
                    title='Altitude Separation Quality',
                    color_discrete_sequence=['#e377c2']
                )
                fig_spread.update_layout(yaxis_title="Altitude Std Dev (ft)", height=300)
                st.plotly_chart(fig_spread, use_container_width=True)
            
            with col2:
                # Create altitude distribution summary
                avg_spread = flights_by_minute_df['ALTITUDE_SPREAD'].mean()
                st.metric("Avg Altitude Separation", f"{avg_spread:.0f} ft")
                
                if avg_spread > 5000:
                    st.success("✅ Good altitude separation")
                elif avg_spread > 2000:
                    st.warning("⚠️ Moderate altitude separation")
                else:
                    st.error("❌ Poor altitude separation")
    
    with tab4:
        # Airport Comparison View
        st.markdown("##### Airport Operations Comparison")
        
        if all(col in flights_by_minute_df.columns for col in ['KBFI_COUNT', 'KAPA_COUNT']):
            # Side-by-side airport comparison
            fig_airports = go.Figure()
            
            fig_airports.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['KBFI_COUNT'],
                mode='lines+markers',
                name='KBFI (Seattle)',
                line=dict(color='#1f77b4', width=3),
                fill='tonexty'
            ))
            
            fig_airports.add_trace(go.Scatter(
                x=flights_by_minute_df['MINUTE_TS'],
                y=flights_by_minute_df['KAPA_COUNT'],
                mode='lines+markers',
                name='KAPA (Denver)',
                line=dict(color='#ff7f0e', width=3),
                fill='tozeroy'
            ))
            
            fig_airports.update_layout(
                title="Airport Traffic Comparison",
                xaxis_title="Time (UTC)",
                yaxis_title="Aircraft Count",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_airports, use_container_width=True)
            
            # Airport statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                kbfi_total = flights_by_minute_df['KBFI_COUNT'].sum()
                kapa_total = flights_by_minute_df['KAPA_COUNT'].sum()
                
                fig_pie = px.pie(
                    values=[kbfi_total, kapa_total],
                    names=['KBFI', 'KAPA'],
                    title='Total Traffic Distribution'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.metric("KBFI Peak Traffic", f"{flights_by_minute_df['KBFI_COUNT'].max()}")
                st.metric("KAPA Peak Traffic", f"{flights_by_minute_df['KAPA_COUNT'].max()}")
            
            with col3:
                kbfi_avg = flights_by_minute_df['KBFI_COUNT'].mean()
                kapa_avg = flights_by_minute_df['KAPA_COUNT'].mean()
                st.metric("KBFI Avg Traffic", f"{kbfi_avg:.1f}")
                st.metric("KAPA Avg Traffic", f"{kapa_avg:.1f}")
    
    with tab5:
        # Safety Monitoring View
        st.markdown("##### Safety & Emergency Monitoring")
        
        # Emergency codes tracking
        if 'EMERGENCY_COUNT' in flights_by_minute_df.columns:
            fig_emergency = px.bar(
                flights_by_minute_df,
                x='MINUTE_TS',
                y='EMERGENCY_COUNT',
                title='Emergency Squawk Codes (7500, 7600, 7700)',
                color='EMERGENCY_COUNT',
                color_continuous_scale='Reds'
            )
            fig_emergency.update_layout(height=300)
            st.plotly_chart(fig_emergency, use_container_width=True)
            
            if flights_by_minute_df['EMERGENCY_COUNT'].sum() > 0:
                st.error("⚠️ Emergency codes detected during this period!")
            else:
                st.success("✅ No emergency codes detected")
        
        # Traffic density safety analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # High traffic periods (safety concern)
            high_traffic_threshold = flights_by_minute_df['TOTAL_AIRCRAFT'].quantile(0.9)
            high_traffic_periods = len(flights_by_minute_df[flights_by_minute_df['TOTAL_AIRCRAFT'] >= high_traffic_threshold])
            
            fig_safety = px.histogram(
                flights_by_minute_df,
                x='TOTAL_AIRCRAFT',
                title='Traffic Density Distribution',
                nbins=20,
                color_discrete_sequence=['#d62728']
            )
            fig_safety.add_vline(x=high_traffic_threshold, line_dash="dash", line_color="red", 
                               annotation_text="High Traffic Threshold")
            st.plotly_chart(fig_safety, use_container_width=True)
        
        with col2:
            # Safety metrics
            st.metric("High Traffic Minutes", f"{high_traffic_periods}")
            
            avg_separation = flights_by_minute_df.get('ALTITUDE_SPREAD', pd.Series([0])).mean()
            if avg_separation > 3000:
                st.success(f"✅ Good Separation: {avg_separation:.0f} ft")
            else:
                st.warning(f"⚠️ Monitor Separation: {avg_separation:.0f} ft")
            
            # Traffic complexity index
            try:
                total_aircraft = flights_by_minute_df['TOTAL_AIRCRAFT'].fillna(0)
                altitude_spread = flights_by_minute_df.get('ALTITUDE_SPREAD', pd.Series([0] * len(flights_by_minute_df))).fillna(0)
                complexity = (total_aircraft * (1 + altitude_spread / 10000)).mean()
                st.metric("Traffic Complexity Index", f"{complexity:.1f}")
            except:
                st.metric("Traffic Complexity Index", "N/A")

else:
    st.warning(f"⚠️ No flight data available for the selected filters.")

# Enhanced map visualization with pydeck
if not detailed_flights_df.empty:
    st.subheader("🗺️ Interactive Flight Map")
    
    # Performance warning and controls
    total_points = len(detailed_flights_df)
    unique_aircraft_count = detailed_flights_df['HEX'].nunique()
    
    if total_points > 1000:
        st.warning(f"⚠️ Large dataset detected: {total_points:,} data points from {unique_aircraft_count} aircraft. Performance controls enabled.")
    
    # Map visualization options with performance controls
    map_col1, map_col2, map_col3, map_col4, map_col5 = st.columns(5)
    
    with map_col1:
        visualization_type = st.selectbox("Visualization:", ["Flight Paths", "Individual Points", "Both"])
    with map_col2:
        color_by = st.selectbox("Color by:", ["Aircraft", "Altitude", "Speed", "Source", "Air/Ground"])
    with map_col3:
        performance_mode = st.checkbox("Performance Mode", value=total_points > 500, help="Reduces data for better map responsiveness")
    with map_col4:
        max_aircraft = st.slider("Max Aircraft", min_value=10, max_value=min(200, unique_aircraft_count), 
                                value=min(50, unique_aircraft_count), help="Limit number of aircraft shown")
    with map_col5:
        show_aircraft_labels = st.checkbox("Show labels", value=False and total_points < 100)
    
    # Additional map controls row
    map_style_col1, map_style_col2, map_style_col3 = st.columns([2, 2, 3])
    
    with map_style_col1:
        map_style = st.selectbox(
            "Map Style:",
            options=[
                "mapbox://styles/mapbox/light-v9",
                "mapbox://styles/mapbox/dark-v9", 
                "mapbox://styles/mapbox/satellite-v9",
                "mapbox://styles/mapbox/streets-v11",
                "mapbox://styles/mapbox/outdoors-v11"
            ],
            format_func=lambda x: {
                "mapbox://styles/mapbox/light-v9": "Light",
                "mapbox://styles/mapbox/dark-v9": "Dark", 
                "mapbox://styles/mapbox/satellite-v9": "Satellite",
                "mapbox://styles/mapbox/streets-v11": "Streets",
                "mapbox://styles/mapbox/outdoors-v11": "Outdoors"
            }.get(x, x),
            index=0,
            help="Choose map background style"
        )
    
    with map_style_col2:
        map_zoom = st.slider("Zoom Level", min_value=1, max_value=15, value=8, help="Adjust map zoom")
    
    with map_style_col3:
        if st.button("🎯 Auto-Center Map", help="Center map on flight data"):
            st.rerun()
        
        # Add debugging toggle
        debug_mode = st.checkbox("Debug Map", help="Show map configuration details")
    
    # Map display guidance
    with st.expander("🗺️ Map Display Help", expanded=False):
        st.markdown("""
        **Map Style Guide:**
        - **Light**: Clean, light background - excellent for professional presentations
        - **Dark**: Dark theme - good for night operations or presentations
        - **Satellite**: Satellite imagery view - shows real terrain and buildings
        - **Streets**: Detailed street-level view with good geographic detail
        - **Outdoors**: Topographic view - shows elevation and terrain features
        
        **Performance Tips:**
        - Use Performance Mode for large datasets (>500 aircraft points)
        - Lower zoom level (1-5) for wider area view, higher (10-15) for detailed view
        - Reduce "Max Aircraft" slider for better map responsiveness
        """)
    
    st.markdown("---")
    
    # Prepare map data with performance optimization
    map_df = detailed_flights_df.copy()
    map_df = map_df.sort_values(['HEX', 'RECORD_TS_UTZ'])
    
    # Apply performance optimizations
    if performance_mode or total_points > 1000:
        st.info(f"🚀 Performance optimization applied: Sampling data for better map responsiveness")
        
        # Step 1: Limit number of aircraft
        if len(map_df['HEX'].unique()) > max_aircraft:
            # Select aircraft with the most data points (most interesting flights)
            aircraft_counts = map_df['HEX'].value_counts()
            top_aircraft = aircraft_counts.head(max_aircraft).index.tolist()
            map_df = map_df[map_df['HEX'].isin(top_aircraft)]
            st.info(f"📊 Showing top {max_aircraft} most active aircraft out of {unique_aircraft_count} total")
        
        # Step 2: Intelligent point sampling for remaining aircraft
        optimized_data = []
        for hex_id in map_df['HEX'].unique():
            aircraft_data = map_df[map_df['HEX'] == hex_id].copy()
            
            if len(aircraft_data) > 20:  # Only sample if aircraft has many points
                # Keep start and end points
                start_point = aircraft_data.iloc[0:1]
                end_point = aircraft_data.iloc[-1:]
                
                # Sample middle points based on performance mode
                middle_data = aircraft_data.iloc[1:-1]
                if performance_mode:
                    # More aggressive sampling in performance mode
                    sample_size = min(10, len(middle_data))
                else:
                    # Moderate sampling
                    sample_size = min(20, len(middle_data))
                
                if len(middle_data) > sample_size:
                    # Use time-based sampling to preserve flight progression
                    step = len(middle_data) // sample_size
                    sampled_middle = middle_data.iloc[::step][:sample_size]
                else:
                    sampled_middle = middle_data
                
                # Combine start, sampled middle, and end points
                aircraft_optimized = pd.concat([start_point, sampled_middle, end_point])
            else:
                # Keep all points for aircraft with few data points
                aircraft_optimized = aircraft_data
            
            optimized_data.append(aircraft_optimized)
        
        if optimized_data:
            map_df = pd.concat(optimized_data, ignore_index=True)
            map_df = map_df.sort_values(['HEX', 'RECORD_TS_UTZ'])
            
            # Performance summary
            final_points = len(map_df)
            reduction_pct = ((total_points - final_points) / total_points * 100)
            st.success(f"✅ Optimized: {total_points:,} → {final_points:,} points ({reduction_pct:.1f}% reduction)")
    
    # Calculate map center
    try:
        center_lat = map_df['LAT'].mean()
        center_lon = map_df['LON'].mean()
        
        if pd.isna(center_lat) or pd.isna(center_lon):
            center_lat, center_lon = 39.8283, -98.5795  # Geographic center of US
    except:
        center_lat, center_lon = 39.8283, -98.5795  # Geographic center of US
    
    # Create pydeck layers
    layers = []
    
    # Get unique aircraft for consistent coloring
    unique_aircraft = map_df['HEX'].unique()
    
    # Color mapping function
    def get_color_for_aircraft(i, aircraft_data, color_by):
        color_palette = [
            [31, 119, 180, 160],    # Blue
            [255, 127, 14, 160],    # Orange  
            [44, 160, 44, 160],     # Green
            [214, 39, 40, 160],     # Red
            [148, 103, 189, 160],   # Purple
            [140, 86, 75, 160],     # Brown
            [227, 119, 194, 160],   # Pink
            [127, 127, 127, 160],   # Gray
            [188, 189, 34, 160],    # Olive
            [23, 190, 207, 160]     # Cyan
        ]
        
        if color_by == "Aircraft":
            return color_palette[i % len(color_palette)]
        elif color_by == "Source":
            return [31, 119, 180, 160] if aircraft_data['SOURCE_TABLE'].iloc[0] == 'KBFI' else [214, 39, 40, 160]
        elif color_by == "Air/Ground":
            return [44, 160, 44, 160] if aircraft_data['AIR_GROUND'].iloc[0] == 'A' else [255, 127, 14, 160]
        elif color_by == "Altitude":
            avg_alt = aircraft_data['ALT_BARO'].mean()
            if pd.isna(avg_alt):
                return [127, 127, 127, 160]
            # Color scale from blue (low) to red (high)
            if avg_alt < 10000:
                return [31, 119, 180, 160]  # Blue
            elif avg_alt < 25000:
                return [44, 160, 44, 160]   # Green
            else:
                return [214, 39, 40, 160]   # Red
        elif color_by == "Speed":
            avg_speed = aircraft_data['GS'].mean()
            if pd.isna(avg_speed):
                return [127, 127, 127, 160]
            # Color scale from blue (slow) to red (fast)
            if avg_speed < 200:
                return [31, 119, 180, 160]  # Blue
            elif avg_speed < 400:
                return [44, 160, 44, 160]   # Green
            else:
                return [214, 39, 40, 160]   # Red
        else:
            return color_palette[i % len(color_palette)]
    
    if visualization_type in ["Flight Paths", "Both"]:
        # Create flight path data for LineLayer
        path_data = []
        for i, hex_id in enumerate(unique_aircraft):
            aircraft_data = map_df[map_df['HEX'] == hex_id].copy()
            
            if len(aircraft_data) > 1:  # Only draw paths for aircraft with multiple points
                flight_name = aircraft_data['FLIGHT'].iloc[0] if aircraft_data['FLIGHT'].iloc[0] not in [None, ''] else f"Aircraft {hex_id}"
                color = get_color_for_aircraft(i, aircraft_data, color_by)
                
                # Create path coordinates
                path_coordinates = []
                for _, row in aircraft_data.iterrows():
                    path_coordinates.append([row['LON'], row['LAT']])
                
                path_data.append({
                    'path': path_coordinates,
                    'name': flight_name,
                    'hex': hex_id,
                    'color': color,
                    'width': 3
                })
        
        if path_data:
            path_df = pd.DataFrame(path_data)
            
            layers.append(pdk.Layer(
                'PathLayer',
                data=path_df,
                get_path='path',
                get_color='color',
                get_width='width',
                width_scale=1,
                width_min_pixels=2,
                pickable=True,
                auto_highlight=True
            ))
    
    if visualization_type in ["Individual Points", "Both"]:
        # Create aircraft points data
        points_data = []
        displayed_aircraft = 0
        max_display_aircraft = max_aircraft if performance_mode else len(unique_aircraft)
        
        for i, hex_id in enumerate(unique_aircraft):
            if displayed_aircraft >= max_display_aircraft:
                break
                
            aircraft_data = map_df[map_df['HEX'] == hex_id].copy()
            
            # Skip aircraft with very few points in performance mode
            if performance_mode and len(aircraft_data) < 3:
                continue
                
            flight_name = aircraft_data['FLIGHT'].iloc[0] if aircraft_data['FLIGHT'].iloc[0] not in [None, ''] else f"Aircraft {hex_id}"
            color = get_color_for_aircraft(i, aircraft_data, color_by)
            
            # Create airplane icons for each point (with performance sampling)
            if performance_mode and len(aircraft_data) > 10:
                # In performance mode, sample points for individual aircraft too
                sample_step = max(1, len(aircraft_data) // 5)  # Show max 5 icons per aircraft
                aircraft_data = aircraft_data.iloc[::sample_step]
            
            for _, row in aircraft_data.iterrows():
                # Determine size based on altitude or status
                if color_by == "Altitude":
                    size = max(20, min(60, row['ALT_BARO'] / 1000 + 20)) if pd.notna(row['ALT_BARO']) else 30
                elif color_by == "Speed":
                    size = max(20, min(60, row['GS'] / 20 + 20)) if pd.notna(row['GS']) else 30
                else:
                    size = 40 if row['AIR_GROUND'] == 'A' else 25
                
                points_data.append({
                    'lat': row['LAT'],
                    'lon': row['LON'],
                    'altitude': row['ALT_BARO'] if pd.notna(row['ALT_BARO']) else 0,
                    'speed': row['GS'] if pd.notna(row['GS']) else 0,
                    'heading': row['HEADING'] if pd.notna(row['HEADING']) else 0,
                    'flight': flight_name,
                    'hex': hex_id,
                    'status': 'Airborne' if row['AIR_GROUND'] == 'A' else 'Ground',
                    'time': pd.to_datetime(row['RECORD_TS_UTZ']).strftime('%H:%M:%S'),
                    'color': color,
                    'size': size
                })
            
            displayed_aircraft += 1
        
        if points_data:
            points_df = pd.DataFrame(points_data)
            
            layers.append(pdk.Layer(
                'ScatterplotLayer',
                data=points_df,
                get_position=['lon', 'lat'],
                get_color='color',
                get_radius='size',
                radius_scale=1,
                radius_min_pixels=8,
                pickable=True,
                auto_highlight=True,
                get_fill_color='color'
            ))
    
    # Add start/end markers if showing paths
    if visualization_type in ["Flight Paths", "Both"]:
        start_end_data = []
        for i, hex_id in enumerate(unique_aircraft):
            aircraft_data = map_df[map_df['HEX'] == hex_id].copy()
            
            if len(aircraft_data) > 1:
                flight_name = aircraft_data['FLIGHT'].iloc[0] if aircraft_data['FLIGHT'].iloc[0] not in [None, ''] else f"Aircraft {hex_id}"
                
                # Start point (takeoff)
                start_point = aircraft_data.iloc[0]
                start_end_data.append({
                    'lat': start_point['LAT'],
                    'lon': start_point['LON'],
                    'type': 'Takeoff',
                    'flight': flight_name,
                    'time': pd.to_datetime(start_point['RECORD_TS_UTZ']).strftime('%H:%M:%S'),
                    'color': [44, 160, 44, 200],  # Green
                    'size': 50
                })
                
                # End point (landing)
                end_point = aircraft_data.iloc[-1]
                start_end_data.append({
                    'lat': end_point['LAT'],
                    'lon': end_point['LON'],
                    'type': 'Landing',
                    'flight': flight_name,
                    'time': pd.to_datetime(end_point['RECORD_TS_UTZ']).strftime('%H:%M:%S'),
                    'color': [214, 39, 40, 200],  # Red
                    'size': 50
                })
        
        if start_end_data:
            start_end_df = pd.DataFrame(start_end_data)
            
            layers.append(pdk.Layer(
                'ScatterplotLayer',
                data=start_end_df,
                get_position=['lon', 'lat'],
                get_color='color',
                get_radius='size',
                radius_scale=1,
                radius_min_pixels=15,
                pickable=True,
                auto_highlight=True,
                get_fill_color='color'
            ))
    
    # Create and display the pydeck map
    if layers:
        # Create the deck
        deck = pdk.Deck(
            map_style=map_style,
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=map_zoom,
                pitch=0,
                bearing=0
            ),
            layers=layers,
            tooltip={
                'html': '<b>Flight:</b> {flight}<br/>'
                       '<b>HEX:</b> {hex}<br/>'
                       '<b>Time:</b> {time}<br/>'
                       '<b>Altitude:</b> {altitude} ft<br/>'
                       '<b>Speed:</b> {speed} kts<br/>'
                       '<b>Status:</b> {status}<br/>'
                       '<b>Type:</b> {type}',
                'style': {
                    'backgroundColor': 'steelblue',
                    'color': 'white'
                }
            }
        )
        
        # Display the map
        st.pydeck_chart(deck, use_container_width=True)
        
        # Map information
        st.success("✅ **Pydeck Map**: Interactive flight visualization with improved performance and reliability.")
    else:
        st.warning("⚠️ No flight data to display on map with current filters.")
    
    # Flight path statistics and performance summary
    actual_aircraft_shown = len(unique_aircraft)
    
    if visualization_type in ["Flight Paths", "Both"]:
        st.info(f"✈️ **Enhanced Flight Path Visualization**: Showing {actual_aircraft_shown} aircraft trajectories with airplane icons along flight paths. 🛫 indicates takeoff positions, 🛬 indicates landing positions, and ✈️ shows aircraft positions during flight.")
    elif visualization_type == "Individual Points":
        st.info(f"🛩️ **Aircraft Position Display**: Showing individual aircraft positions with airplane icons. ✈️ represents airborne aircraft, 🛩️ represents aircraft on ground.")
    
    # Performance summary
    if performance_mode or total_points > 1000:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Aircraft Displayed", f"{actual_aircraft_shown}/{unique_aircraft_count}")
        with col2:
            current_points = len(map_df)
            st.metric("Data Points", f"{current_points:,}")
        with col3:
            if total_points != current_points:
                reduction = (total_points - current_points) / total_points * 100
                st.metric("Performance Gain", f"{reduction:.1f}% fewer points")
    
    # Enhanced Flight tracking section
    st.subheader("🎯 Enhanced Individual Flight Tracking")
    
    if len(detailed_flights_df['HEX'].unique()) > 0:
        # Enhanced flight selection with more details
        flight_options = []
        flight_details = {}
        
        for hex_id in detailed_flights_df['HEX'].unique():
            aircraft_data = detailed_flights_df[detailed_flights_df['HEX'] == hex_id]
            flight_name = aircraft_data['FLIGHT'].iloc[0] if aircraft_data['FLIGHT'].iloc[0] not in [None, ''] else 'Unknown Flight'
            
            # Calculate flight statistics
            total_points = len(aircraft_data)
            duration_minutes = 0
            max_alt = aircraft_data['ALT_BARO'].max() if not aircraft_data['ALT_BARO'].isna().all() else 0
            avg_speed = aircraft_data['GS'].mean() if not aircraft_data['GS'].isna().all() else 0
            
            try:
                start_time = pd.to_datetime(aircraft_data['RECORD_TS_UTZ'].iloc[0])
                end_time = pd.to_datetime(aircraft_data['RECORD_TS_UTZ'].iloc[-1])
                duration_minutes = (end_time - start_time).total_seconds() / 60
            except:
                duration_minutes = 0
            
            display_text = f"✈️ {flight_name} ({hex_id}) - {duration_minutes:.0f}min, {max_alt:.0f}ft max, {avg_speed:.0f}kts avg"
            flight_options.append(display_text)
            flight_details[display_text] = {
                'hex': hex_id,
                'flight': flight_name,
                'points': total_points,
                'duration': duration_minutes,
                'max_alt': max_alt,
                'avg_speed': avg_speed
            }
        
        # Enhanced selection interface
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            selected_display = st.selectbox(
                "🛩️ Select aircraft to track:",
                options=flight_options,
                help="Select an aircraft to view detailed flight path and analytics"
            )
        
        with col2:
            show_3d = st.checkbox("🏔️ 3D View", help="Show altitude as 3D elevation")
        
        with col3:
            animate_path = st.checkbox("🎬 Animate", help="Animate flight progression")
        
        # Get selected aircraft details
        selected_details = flight_details[selected_display]
        selected_hex = selected_details['hex']
        
        # Display quick stats
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        with stats_col1:
            st.metric("Flight Duration", f"{selected_details['duration']:.0f} min")
        with stats_col2:
            st.metric("Data Points", f"{selected_details['points']}")
        with stats_col3:
            st.metric("Max Altitude", f"{selected_details['max_alt']:.0f} ft")
        with stats_col4:
            st.metric("Avg Speed", f"{selected_details['avg_speed']:.0f} kts")
        
        if selected_hex:
            flight_path_df = get_flight_path(selected_hex, date_slider_val)
            
            if not flight_path_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🗺️ Interactive Flight Path")
                    
                    # Enhanced map controls
                    map_controls_col1, map_controls_col2, map_controls_col3 = st.columns(3)
                    
                    with map_controls_col1:
                        map_zoom_level = st.slider("🔍 Zoom Level", min_value=8, max_value=16, value=11, help="Adjust map zoom for better detail")
                    
                    with map_controls_col2:
                        point_density = st.selectbox("📍 Point Density", 
                                                   options=["Low (5 points)", "Medium (10 points)", "High (15 points)", "All points"],
                                                   index=1,
                                                   help="Control number of aircraft icons shown")
                    
                    with map_controls_col3:
                        color_scheme = st.selectbox("🎨 Color Scheme",
                                                  options=["Altitude", "Speed", "Time", "Single Color"],
                                                  index=0,
                                                  help="Color aircraft points by different metrics")
                    
                    # Enhanced flight path map with pydeck
                    flight_name = flight_path_df['FLIGHT'].iloc[0] if flight_path_df['FLIGHT'].iloc[0] not in [None, ''] else f"Aircraft {selected_hex}"
                    
                    # Calculate center for individual flight
                    try:
                        flight_center_lat = flight_path_df['LAT'].mean()
                        flight_center_lon = flight_path_df['LON'].mean()
                        
                        if pd.isna(flight_center_lat) or pd.isna(flight_center_lon):
                            flight_center_lat, flight_center_lon = center_lat, center_lon
                    except:
                        flight_center_lat, flight_center_lon = center_lat, center_lon
                    
                    # Enhanced path data with elevation if 3D view is enabled
                    if show_3d:
                        path_coordinates = []
                        for _, row in flight_path_df.iterrows():
                            alt = row['ALT_BARO'] if pd.notna(row['ALT_BARO']) else 0
                            path_coordinates.append([row['LON'], row['LAT'], alt * 0.3048])  # Convert feet to meters
                    else:
                        path_coordinates = []
                        for _, row in flight_path_df.iterrows():
                            path_coordinates.append([row['LON'], row['LAT']])
                    
                    flight_path_data = pd.DataFrame([{
                        'path': path_coordinates,
                        'name': flight_name,
                        'color': [31, 119, 180, 200],  # Blue
                        'width': 8 if show_3d else 6
                    }])
                    
                    # Enhanced aircraft points with smart sampling
                    if point_density == "Low (5 points)":
                        num_points = min(5, len(flight_path_df))
                    elif point_density == "Medium (10 points)":
                        num_points = min(10, len(flight_path_df))
                    elif point_density == "High (15 points)":
                        num_points = min(15, len(flight_path_df))
                    else:  # All points
                        num_points = len(flight_path_df)
                    
                    if num_points < len(flight_path_df):
                        step_size = max(1, len(flight_path_df) // num_points)
                        icon_indices = list(range(0, len(flight_path_df), step_size))
                        if icon_indices[-1] != len(flight_path_df) - 1:
                            icon_indices.append(len(flight_path_df) - 1)
                    else:
                        icon_indices = list(range(len(flight_path_df)))
                    
                    icon_data = flight_path_df.iloc[icon_indices].copy()
                    
                    # Enhanced aircraft points with dynamic coloring
                    aircraft_points_data = []
                    for i, (_, row) in enumerate(icon_data.iterrows()):
                        # Dynamic sizing based on altitude
                        size = max(40, min(80, row['ALT_BARO'] / 1000 + 40)) if pd.notna(row['ALT_BARO']) else 50
                        
                        # Dynamic coloring based on selected scheme
                        if color_scheme == "Altitude":
                            alt = row['ALT_BARO'] if pd.notna(row['ALT_BARO']) else 0
                            if alt < 10000:
                                color = [31, 119, 180, 180]  # Blue (low)
                            elif alt < 25000:
                                color = [44, 160, 44, 180]   # Green (medium)
                            else:
                                color = [214, 39, 40, 180]   # Red (high)
                        elif color_scheme == "Speed":
                            speed = row['GS'] if pd.notna(row['GS']) else 0
                            if speed < 200:
                                color = [31, 119, 180, 180]  # Blue (slow)
                            elif speed < 400:
                                color = [255, 127, 14, 180]  # Orange (medium)
                            else:
                                color = [214, 39, 40, 180]   # Red (fast)
                        elif color_scheme == "Time":
                            # Color progression from start (green) to end (red)
                            progress = i / (len(icon_data) - 1) if len(icon_data) > 1 else 0
                            color = [
                                int(44 + (214 - 44) * progress),   # Red component
                                int(160 - 160 * progress),         # Green component  
                                int(44 - 44 * progress),           # Blue component
                                180
                            ]
                        else:  # Single Color
                            color = [31, 119, 180, 180]
                        
                        # Enhanced data with more flight details
                        aircraft_points_data.append({
                            'lat': row['LAT'],
                            'lon': row['LON'],
                            'elevation': row['ALT_BARO'] * 0.3048 if pd.notna(row['ALT_BARO']) and show_3d else 0,
                            'altitude': row['ALT_BARO'] if pd.notna(row['ALT_BARO']) else 0,
                            'speed': row['GS'] if pd.notna(row['GS']) else 0,
                            'heading': row['HEADING'] if pd.notna(row['HEADING']) else 0,
                            'flight': flight_name,
                            'hex': selected_hex,
                            'time': pd.to_datetime(row['RECORD_TS_UTZ']).strftime('%H:%M:%S'),
                            'timestamp': pd.to_datetime(row['RECORD_TS_UTZ']).strftime('%Y-%m-%d %H:%M:%S'),
                            'sequence': i + 1,
                            'total_points': len(icon_data),
                            'color': color,
                            'size': size
                        })
                    
                    aircraft_points_df = pd.DataFrame(aircraft_points_data)
                    
                    # Enhanced start/end markers with better visibility
                    start_point = flight_path_df.iloc[0]
                    end_point = flight_path_df.iloc[-1]
                    
                    start_end_data = [
                        {
                            'lat': start_point['LAT'],
                            'lon': start_point['LON'],
                            'elevation': start_point['ALT_BARO'] * 0.3048 if pd.notna(start_point['ALT_BARO']) and show_3d else 0,
                            'type': '🛫 TAKEOFF',
                            'phase': 'Departure',
                            'flight': flight_name,
                            'time': pd.to_datetime(start_point['RECORD_TS_UTZ']).strftime('%H:%M:%S'),
                            'altitude': start_point['ALT_BARO'] if pd.notna(start_point['ALT_BARO']) else 0,
                            'speed': start_point['GS'] if pd.notna(start_point['GS']) else 0,
                            'color': [44, 160, 44, 255],  # Bright Green
                            'size': 100
                        },
                        {
                            'lat': end_point['LAT'],
                            'lon': end_point['LON'],
                            'elevation': end_point['ALT_BARO'] * 0.3048 if pd.notna(end_point['ALT_BARO']) and show_3d else 0,
                            'type': '🛬 LANDING',
                            'phase': 'Arrival',
                            'flight': flight_name,
                            'time': pd.to_datetime(end_point['RECORD_TS_UTZ']).strftime('%H:%M:%S'),
                            'altitude': end_point['ALT_BARO'] if pd.notna(end_point['ALT_BARO']) else 0,
                            'speed': end_point['GS'] if pd.notna(end_point['GS']) else 0,
                            'color': [214, 39, 40, 255],  # Bright Red
                            'size': 100
                        }
                    ]
                    
                    start_end_df = pd.DataFrame(start_end_data)
                    
                    # Create enhanced pydeck layers
                    flight_layers = []
                    
                    # Enhanced flight path layer
                    if show_3d:
                        flight_layers.append(pdk.Layer(
                            'PathLayer',
                            data=flight_path_data,
                            get_path='path',
                            get_color='color',
                            get_width='width',
                            width_scale=1,
                            width_min_pixels=4,
                            pickable=True,
                            auto_highlight=True,
                            extruded=True
                        ))
                    else:
                        flight_layers.append(pdk.Layer(
                            'PathLayer',
                            data=flight_path_data,
                            get_path='path',
                            get_color='color',
                            get_width='width',
                            width_scale=1,
                            width_min_pixels=4,
                            pickable=True,
                            auto_highlight=True
                        ))
                    
                    # Enhanced aircraft positions layer
                    if show_3d:
                        flight_layers.append(pdk.Layer(
                            'ColumnLayer',
                            data=aircraft_points_df,
                            get_position=['lon', 'lat'],
                            get_elevation='elevation',
                            get_fill_color='color',
                            get_radius='size',
                            radius_scale=1,
                            elevation_scale=1,
                            pickable=True,
                            auto_highlight=True,
                            extruded=True,
                            coverage=0.8
                        ))
                    else:
                        flight_layers.append(pdk.Layer(
                            'ScatterplotLayer',
                            data=aircraft_points_df,
                            get_position=['lon', 'lat'],
                            get_color='color',
                            get_radius='size',
                            radius_scale=1,
                            radius_min_pixels=15,
                            pickable=True,
                            auto_highlight=True,
                            get_fill_color='color'
                        ))
                    
                    # Enhanced start and end points layer
                    if show_3d:
                        flight_layers.append(pdk.Layer(
                            'ColumnLayer',
                            data=start_end_df,
                            get_position=['lon', 'lat'],
                            get_elevation='elevation',
                            get_fill_color='color',
                            get_radius='size',
                            radius_scale=1,
                            elevation_scale=1,
                            pickable=True,
                            auto_highlight=True,
                            extruded=True,
                            coverage=1.0
                        ))
                    else:
                        flight_layers.append(pdk.Layer(
                            'ScatterplotLayer',
                            data=start_end_df,
                            get_position=['lon', 'lat'],
                            get_color='color',
                            get_radius='size',
                            radius_scale=1,
                            radius_min_pixels=25,
                            pickable=True,
                            auto_highlight=True,
                            get_fill_color='color'
                        ))
                    
                    # Create the enhanced flight deck
                    flight_deck = pdk.Deck(
                        map_style=map_style,
                        initial_view_state=pdk.ViewState(
                            latitude=flight_center_lat,
                            longitude=flight_center_lon,
                            zoom=map_zoom_level,
                            pitch=45 if show_3d else 0,
                            bearing=0
                        ),
                        layers=flight_layers,
                        tooltip={
                            'html': '<div style="font-family: Arial, sans-serif; padding: 10px; max-width: 300px;">'
                                   '<b style="color: #1f77b4; font-size: 16px;">✈️ {flight}</b><br/>'
                                   '<hr style="margin: 8px 0; border: 1px solid #ddd;">'
                                   '<b>Flight Details:</b><br/>'
                                   '• Aircraft ID: <b>{hex}</b><br/>'
                                   '• Phase: <b>{phase}</b><br/>'
                                   '• Time: <b>{time}</b><br/>'
                                   '<b>Flight Data:</b><br/>'
                                   '• Altitude: <b>{altitude:,} ft</b><br/>'
                                   '• Speed: <b>{speed:.0f} knots</b><br/>'
                                   '• Heading: <b>{heading:.0f}°</b><br/>'
                                   '<b>Progress:</b><br/>'
                                   '• Point {sequence} of {total_points}<br/>'
                                   '• Type: <b>{type}</b>'
                                   '</div>',
                            'style': {
                                'backgroundColor': 'rgba(255, 255, 255, 0.95)',
                                'color': '#333',
                                'border': '2px solid #1f77b4',
                                'borderRadius': '8px',
                                'fontSize': '12px'
                            }
                        },
                        parameters={
                            'blend': True,
                            'blendFunc': ['SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA']
                        }
                    )
                    
                    st.pydeck_chart(flight_deck, use_container_width=True)
                    
                    # Enhanced information display
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.info(f"🎯 **Tracking**: {flight_name} ({selected_hex})")
                        st.info(f"📍 **Showing**: {len(aircraft_points_df)} of {len(flight_path_df)} data points")
                    
                    with info_col2:
                        if show_3d:
                            st.success("🏔️ **3D Mode**: Altitude shown as elevation")
                        else:
                            st.info("🗺️ **2D Mode**: Standard map view")
                        
                        st.info(f"🎨 **Coloring**: {color_scheme}")
                    
                    # Legend for color schemes
                    if color_scheme == "Altitude":
                        st.markdown("""
                        **🎨 Altitude Color Legend:**
                        - 🔵 **Blue**: Below 10,000 ft (Low altitude)
                        - 🟢 **Green**: 10,000 - 25,000 ft (Medium altitude)  
                        - 🔴 **Red**: Above 25,000 ft (High altitude)
                        """)
                    elif color_scheme == "Speed":
                        st.markdown("""
                        **🎨 Speed Color Legend:**
                        - 🔵 **Blue**: Below 200 knots (Slow)
                        - 🟠 **Orange**: 200 - 400 knots (Medium)
                        - 🔴 **Red**: Above 400 knots (Fast)
                        """)
                    elif color_scheme == "Time":
                        st.markdown("""
                        **🎨 Time Color Legend:**
                        - 🟢 **Green**: Flight start
                        - 🟠 **Orange**: Flight middle  
                        - 🔴 **Red**: Flight end
                        """)
                    
                    # Map interaction tips
                    st.markdown("""
                    **💡 Map Interaction Tips:**
                    - 🖱️ **Click and drag** to pan the map
                    - 🔍 **Scroll** to zoom in/out
                    - 👆 **Click aircraft points** for detailed information
                    - 🎛️ **Adjust controls above** to customize the view
                    """, help="Use these controls to explore the flight path interactively")
                
                with col2:
                    st.markdown("### 📊 Interactive Flight Analytics")
                    
                    # Enhanced chart controls
                    chart_tabs = st.tabs(["📈 Profiles", "⏱️ Timeline", "📋 Details"])
                    
                    with chart_tabs[0]:
                        # Chart customization controls
                        chart_col1, chart_col2 = st.columns(2)
                        
                        with chart_col1:
                            show_markers = st.checkbox("Show Data Points", value=True, help="Show individual data markers on charts")
                        
                        with chart_col2:
                            smooth_lines = st.checkbox("Smooth Lines", value=False, help="Apply smoothing to flight data")
                        
                        # Enhanced altitude and speed profile
                        fig_profiles = go.Figure()
                        
                        # Prepare data
                        timestamps = pd.to_datetime(flight_path_df['RECORD_TS_UTZ'])
                        altitudes = flight_path_df['ALT_BARO']
                        speeds = flight_path_df['GS']
                        headings = flight_path_df['HEADING']
                        
                        # Apply smoothing if requested
                        if smooth_lines and len(flight_path_df) > 3:
                            try:
                                from scipy.signal import savgol_filter
                                window_length = min(11, len(flight_path_df) // 2 * 2 + 1)  # Ensure odd number
                                if window_length >= 3:
                                    altitudes = savgol_filter(altitudes.ffill().bfill(), window_length, 3)
                                    speeds = savgol_filter(speeds.ffill().bfill(), window_length, 3)
                            except ImportError:
                                st.warning("⚠️ Scipy not available. Smoothing disabled. Install scipy for advanced smoothing features.")
                            except Exception:
                                pass  # Fall back to original data
                        
                        # Enhanced altitude profile with fill
                        mode = 'lines+markers' if show_markers else 'lines'
                        marker_size = 6 if show_markers else 0
                        
                        fig_profiles.add_trace(go.Scatter(
                            x=timestamps,
                            y=altitudes,
                            mode=mode,
                            name='🛫 Altitude',
                            line=dict(color='#1f77b4', width=3),
                            marker=dict(size=marker_size, color='#1f77b4'),
                            fill='tonexty',
                            fillcolor='rgba(31, 119, 180, 0.1)',
                            yaxis='y1',
                            hovertemplate="<b>Altitude Profile</b><br>" +
                                         "Time: %{x}<br>" +
                                         "Altitude: <b>%{y:,.0f} ft</b><br>" +
                                         "<extra></extra>"
                        ))
                        
                        # Enhanced speed profile
                        fig_profiles.add_trace(go.Scatter(
                            x=timestamps,
                            y=speeds,
                            mode=mode,
                            name='🚀 Ground Speed',
                            line=dict(color='#ff7f0e', width=2),
                            marker=dict(size=marker_size, color='#ff7f0e'),
                            yaxis='y2',
                            hovertemplate="<b>Speed Profile</b><br>" +
                                         "Time: %{x}<br>" +
                                         "Speed: <b>%{y:.0f} knots</b><br>" +
                                         "<extra></extra>"
                        ))
                        
                        # Add heading profile if data is available
                        if not headings.isna().all():
                            fig_profiles.add_trace(go.Scatter(
                                x=timestamps,
                                y=headings,
                                mode='lines',
                                name='🧭 Heading',
                                line=dict(color='#2ca02c', width=1.5, dash='dot'),
                                yaxis='y3',
                                visible='legendonly',  # Hidden by default
                                hovertemplate="<b>Heading Profile</b><br>" +
                                             "Time: %{x}<br>" +
                                             "Heading: <b>%{y:.0f}°</b><br>" +
                                             "<extra></extra>"
                            ))
                        
                        # Add flight phase annotations
                        max_alt = altitudes.max()
                        cruise_threshold = max_alt * 0.9  # 90% of max altitude considered cruise
                        
                        # Find takeoff, cruise, and landing phases
                        takeoff_end = None
                        cruise_start = None
                        cruise_end = None
                        
                        for i, alt in enumerate(altitudes):
                            if pd.notna(alt):
                                if takeoff_end is None and alt > cruise_threshold:
                                    takeoff_end = i
                                    cruise_start = i
                                elif cruise_end is None and alt < cruise_threshold and takeoff_end is not None:
                                    cruise_end = i
                        
                        # Add phase annotations
                        if takeoff_end is not None:
                            fig_profiles.add_annotation(
                                x=timestamps.iloc[min(takeoff_end + 5, len(timestamps) - 1)],
                                y=altitudes[takeoff_end],
                                text="🛫 Takeoff Complete",
                                showarrow=True,
                                arrowhead=2,
                                arrowcolor="green",
                                arrowwidth=2,
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="green",
                                borderwidth=1
                            )
                        
                        if cruise_end is not None:
                            fig_profiles.add_annotation(
                                x=timestamps.iloc[max(cruise_end - 5, 0)],
                                y=altitudes[cruise_end],
                                text="🛬 Descent Start",
                                showarrow=True,
                                arrowhead=2,
                                arrowcolor="red",
                                arrowwidth=2,
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="red",
                                borderwidth=1
                            )
                        
                        # Enhanced layout with multiple y-axes
                        fig_profiles.update_layout(
                            title=dict(
                                text=f"📊 Flight Profile Analysis: {flight_name}",
                                font=dict(size=16)
                            ),
                            xaxis=dict(
                                title="Time (UTC)",
                                showgrid=True,
                                gridwidth=1,
                                gridcolor='lightgray'
                            ),
                            yaxis=dict(
                                title="Altitude (ft)",
                                side="left",
                                color="#1f77b4",
                                showgrid=True,
                                gridwidth=1,
                                gridcolor='lightblue'
                            ),
                            yaxis2=dict(
                                title="Ground Speed (knots)",
                                side="right",
                                overlaying="y",
                                color="#ff7f0e",
                                showgrid=False
                            ),
                            yaxis3=dict(
                                title="Heading (degrees)",
                                side="right",
                                overlaying="y",
                                position=0.95,
                                color="#2ca02c",
                                showgrid=False
                            ),
                            height=450,
                            legend=dict(
                                x=0.02, 
                                y=0.98,
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="gray",
                                borderwidth=1
                            ),
                            hovermode='x unified',
                            template="plotly_white"
                        )
                        
                        st.plotly_chart(fig_profiles, use_container_width=True)
                        
                        # Quick stats below the chart
                        quick_stats_col1, quick_stats_col2, quick_stats_col3 = st.columns(3)
                        
                        with quick_stats_col1:
                            climb_rate = 0
                            if len(flight_path_df) > 1:
                                alt_diff = flight_path_df['ALT_BARO'].iloc[-1] - flight_path_df['ALT_BARO'].iloc[0]
                                time_diff = (timestamps.iloc[-1] - timestamps.iloc[0]).total_seconds() / 60
                                if time_diff > 0:
                                    climb_rate = alt_diff / time_diff
                            
                            st.metric("Avg Climb Rate", f"{climb_rate:.0f} ft/min")
                        
                        with quick_stats_col2:
                            speed_range = speeds.max() - speeds.min() if not speeds.isna().all() else 0
                            st.metric("Speed Range", f"{speed_range:.0f} kts")
                        
                        with quick_stats_col3:
                            altitude_range = altitudes.max() - altitudes.min() if not pd.isna(altitudes).all() else 0
                            st.metric("Altitude Range", f"{altitude_range:.0f} ft")
                    
                    with chart_tabs[1]:
                        st.markdown("#### ⏱️ Flight Timeline Scrubber")
                        
                        # Time-based filtering
                        if len(flight_path_df) > 1:
                            time_range = st.slider(
                                "Select time range to analyze:",
                                min_value=0,
                                max_value=len(flight_path_df) - 1,
                                value=(0, len(flight_path_df) - 1),
                                format="%d",
                                help="Drag to select a portion of the flight to analyze"
                            )
                            
                            # Show selected time range details
                            start_idx, end_idx = time_range
                            selected_data = flight_path_df.iloc[start_idx:end_idx+1]
                            
                            if len(selected_data) > 0:
                                start_time = pd.to_datetime(selected_data['RECORD_TS_UTZ'].iloc[0])
                                end_time = pd.to_datetime(selected_data['RECORD_TS_UTZ'].iloc[-1])
                                
                                st.info(f"**Selected Range**: {start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')}")
                                
                                # Mini charts for selected range
                                timeline_col1, timeline_col2 = st.columns(2)
                                
                                with timeline_col1:
                                    # Selected altitude chart
                                    fig_alt_mini = px.line(
                                        x=pd.to_datetime(selected_data['RECORD_TS_UTZ']),
                                        y=selected_data['ALT_BARO'],
                                        title="Altitude in Selected Range",
                                        labels={'x': 'Time', 'y': 'Altitude (ft)'}
                                    )
                                    fig_alt_mini.update_layout(height=250, showlegend=False)
                                    st.plotly_chart(fig_alt_mini, use_container_width=True)
                                
                                with timeline_col2:
                                    # Selected speed chart
                                    fig_speed_mini = px.line(
                                        x=pd.to_datetime(selected_data['RECORD_TS_UTZ']),
                                        y=selected_data['GS'],
                                        title="Speed in Selected Range",
                                        labels={'x': 'Time', 'y': 'Speed (knots)'},
                                        color_discrete_sequence=['orange']
                                    )
                                    fig_speed_mini.update_layout(height=250, showlegend=False)
                                    st.plotly_chart(fig_speed_mini, use_container_width=True)
                                
                                # Statistics for selected range
                                range_col1, range_col2, range_col3, range_col4 = st.columns(4)
                                
                                with range_col1:
                                    avg_alt = selected_data['ALT_BARO'].mean()
                                    st.metric("Avg Altitude", f"{avg_alt:.0f} ft" if pd.notna(avg_alt) else "N/A")
                                
                                with range_col2:
                                    avg_speed = selected_data['GS'].mean()
                                    st.metric("Avg Speed", f"{avg_speed:.0f} kts" if pd.notna(avg_speed) else "N/A")
                                
                                with range_col3:
                                    duration = (end_time - start_time).total_seconds() / 60
                                    st.metric("Duration", f"{duration:.1f} min")
                                
                                with range_col4:
                                    distance = len(selected_data)
                                    st.metric("Data Points", f"{distance}")
                    
                    with chart_tabs[2]:
                        st.markdown("#### 📋 Detailed Flight Information")
                        
                        # Comprehensive flight details
                        details_col1, details_col2 = st.columns(2)
                        
                        with details_col1:
                            st.markdown("**🛩️ Aircraft Information:**")
                            st.write(f"• Flight ID: `{flight_name}`")
                            st.write(f"• Aircraft HEX: `{selected_hex}`")
                            st.write(f"• Source: `{flight_path_df['SOURCE_TABLE'].iloc[0] if 'SOURCE_TABLE' in flight_path_df.columns else 'Unknown'}`")
                            
                            st.markdown("**📊 Flight Statistics:**")
                            total_distance = 0
                            if len(flight_path_df) > 1:
                                for i in range(1, len(flight_path_df)):
                                    if pd.notna(flight_path_df['LAT'].iloc[i]) and pd.notna(flight_path_df['LON'].iloc[i]):
                                        # Simple distance calculation (not great circle, but approximate)
                                        lat_diff = flight_path_df['LAT'].iloc[i] - flight_path_df['LAT'].iloc[i-1]
                                        lon_diff = flight_path_df['LON'].iloc[i] - flight_path_df['LON'].iloc[i-1]
                                        total_distance += (lat_diff**2 + lon_diff**2)**0.5 * 69  # Rough miles conversion
                            
                            st.write(f"• Approximate Distance: `{total_distance:.1f} miles`")
                            st.write(f"• Total Data Points: `{len(flight_path_df)}`")
                            st.write(f"• Data Quality: `{(flight_path_df[['LAT', 'LON', 'ALT_BARO']].notna().all(axis=1).sum() / len(flight_path_df) * 100):.1f}% complete`")
                        
                        with details_col2:
                            st.markdown("**⏰ Timing Information:**")
                            start_time = pd.to_datetime(flight_path_df['RECORD_TS_UTZ'].iloc[0])
                            end_time = pd.to_datetime(flight_path_df['RECORD_TS_UTZ'].iloc[-1])
                            
                            st.write(f"• Start Time: `{start_time.strftime('%H:%M:%S UTC')}`")
                            st.write(f"• End Time: `{end_time.strftime('%H:%M:%S UTC')}`")
                            st.write(f"• Duration: `{((end_time - start_time).total_seconds() / 60):.1f} minutes`")
                            
                            st.markdown("**🎯 Performance Metrics:**")
                            max_alt = flight_path_df['ALT_BARO'].max()
                            min_alt = flight_path_df['ALT_BARO'].min()
                            max_speed = flight_path_df['GS'].max()
                            min_speed = flight_path_df['GS'].min()
                            
                            st.write(f"• Max Altitude: `{max_alt:.0f} ft`" if pd.notna(max_alt) else "• Max Altitude: `N/A`")
                            st.write(f"• Min Altitude: `{min_alt:.0f} ft`" if pd.notna(min_alt) else "• Min Altitude: `N/A`")
                            st.write(f"• Max Speed: `{max_speed:.0f} kts`" if pd.notna(max_speed) else "• Max Speed: `N/A`")
                            st.write(f"• Min Speed: `{min_speed:.0f} kts`" if pd.notna(min_speed) else "• Min Speed: `N/A`")
                        
                        # Data quality visualization
                        st.markdown("**📈 Data Quality Analysis:**")
                        
                        # Check for data gaps
                        data_quality = flight_path_df[['LAT', 'LON', 'ALT_BARO', 'GS', 'HEADING']].notna()
                        quality_stats = data_quality.mean() * 100
                        
                        quality_fig = px.bar(
                            x=quality_stats.index,
                            y=quality_stats.values,
                            title="Data Completeness by Field (%)",
                            labels={'x': 'Data Field', 'y': 'Completeness (%)'},
                            color=quality_stats.values,
                            color_continuous_scale='RdYlGn'
                        )
                        quality_fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(quality_fig, use_container_width=True)
                        
                        # Export options
                        st.markdown("**💾 Export Options:**")
                        export_col1, export_col2 = st.columns(2)
                        
                        with export_col1:
                            if st.button("📄 Export Flight Data"):
                                csv_data = flight_path_df.to_csv(index=False)
                                st.download_button(
                                    label="💾 Download CSV",
                                    data=csv_data,
                                    file_name=f"flight_{selected_hex}_{date_as_string}.csv",
                                    mime="text/csv"
                                )
                        
                        with export_col2:
                            if st.button("📊 Export Summary Report"):
                                summary = f"""
Flight Analysis Summary
======================
Flight ID: {flight_name}
Aircraft HEX: {selected_hex}
Date: {date_as_string}
Duration: {((end_time - start_time).total_seconds() / 60):.1f} minutes
Max Altitude: {max_alt:.0f} ft
Max Speed: {max_speed:.0f} kts
Total Distance: {total_distance:.1f} miles
Data Points: {len(flight_path_df)}
                                """
                                st.download_button(
                                    label="💾 Download Report",
                                    data=summary,
                                    file_name=f"flight_report_{selected_hex}_{date_as_string}.txt",
                                    mime="text/plain"
                                )
                
                # Flight statistics summary
                st.subheader("📈 Flight Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    try:
                        start_time = pd.to_datetime(flight_path_df['RECORD_TS_UTZ'].iloc[0])
                        end_time = pd.to_datetime(flight_path_df['RECORD_TS_UTZ'].iloc[-1])
                        duration = end_time - start_time
                        st.metric("Flight Duration", f"{duration.total_seconds()/60:.0f} min")
                    except:
                        st.metric("Flight Duration", "N/A")
                
                with col2:
                    max_alt = flight_path_df['ALT_BARO'].max()
                    st.metric("Max Altitude", f"{max_alt:.0f} ft" if pd.notna(max_alt) else "N/A")
                
                with col3:
                    max_speed = flight_path_df['GS'].max()
                    st.metric("Max Speed", f"{max_speed:.0f} kts" if pd.notna(max_speed) else "N/A")
                
                with col4:
                    total_points = len(flight_path_df)
                    st.metric("Data Points", total_points)

# Analytics Dashboard
st.subheader("📊 Flight Analytics")

if not detailed_flights_df.empty:
    
    analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4 = st.tabs(
        ["Speed vs Altitude", "Heading Distribution", "Airport Comparison", "Summary Stats"]
    )
    
    with analytics_tab1:
        # Speed vs Altitude scatter plot
        fig_scatter = px.scatter(
            detailed_flights_df,
            x="GS",
            y="ALT_BARO",
            color="SOURCE_TABLE",
            hover_data=["FLIGHT", "HEX"],
            title="Ground Speed vs Altitude",
            labels={"GS": "Ground Speed (knots)", "ALT_BARO": "Altitude (ft)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with analytics_tab2:
        # Heading distribution
        if 'HEADING' in detailed_flights_df.columns:
            detailed_flights_df['heading_sector'] = pd.cut(
                detailed_flights_df['HEADING'], 
                bins=8, 
                labels=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            )
            heading_counts = detailed_flights_df['heading_sector'].value_counts()
            
            fig_heading = px.bar(
                x=heading_counts.index,
                y=heading_counts.values,
                title="Aircraft Heading Distribution"
            )
            fig_heading.update_layout(xaxis_title="Direction", yaxis_title="Count")
            st.plotly_chart(fig_heading, use_container_width=True)
    
    with analytics_tab3:
        # Airport comparison
        if not airport_stats.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_airport = px.bar(
                    airport_stats,
                    x="SOURCE_TABLE",
                    y="UNIQUE_AIRCRAFT",
                    title="Unique Aircraft by Airport"
                )
                st.plotly_chart(fig_airport, use_container_width=True)
            
            with col2:
                fig_records = px.pie(
                    airport_stats,
                    values="TOTAL_RECORDS",
                    names="SOURCE_TABLE",
                    title="Total Records by Airport"
                )
                st.plotly_chart(fig_records, use_container_width=True)
    
    with analytics_tab4:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Flights", len(detailed_flights_df))
            st.metric("Unique Aircraft", detailed_flights_df['HEX'].nunique())
        
        with col2:
            avg_speed = detailed_flights_df['GS'].mean()
            st.metric("Avg Speed", f"{avg_speed:.0f} kts" if pd.notna(avg_speed) else "N/A")
            max_speed = detailed_flights_df['GS'].max()
            st.metric("Max Speed", f"{max_speed:.0f} kts" if pd.notna(max_speed) else "N/A")
        
        with col3:
            avg_alt = detailed_flights_df['ALT_BARO'].mean()
            st.metric("Avg Altitude", f"{avg_alt:.0f} ft" if pd.notna(avg_alt) else "N/A")
            max_alt = detailed_flights_df['ALT_BARO'].max()
            st.metric("Max Altitude", f"{max_alt:.0f} ft" if pd.notna(max_alt) else "N/A")
        
        with col4:
            airborne = len(detailed_flights_df[detailed_flights_df['AIR_GROUND'] == 'A'])
            ground = len(detailed_flights_df[detailed_flights_df['AIR_GROUND'] == 'G'])
            st.metric("Airborne", airborne)
            st.metric("On Ground", ground)

# Detailed data table
with st.expander("📋 Detailed Flight Data", expanded=False):
    if not detailed_flights_df.empty:
        # Format the dataframe for better display
        display_df = detailed_flights_df.copy()
        
        # Format timestamps
        if 'RECORD_TS_UTZ' in display_df.columns:
            display_df['RECORD_TS_UTZ'] = pd.to_datetime(display_df['RECORD_TS_UTZ']).dt.strftime('%H:%M:%S')
        
        # Round numeric columns
        numeric_cols = ['LAT', 'LON', 'ALT_BARO', 'GPS_ALT', 'GS', 'HEADING']
        for col in numeric_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(2)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"flight_data_{date_as_string}_{hour_slider_val}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available for the selected filters.")

# Footer
st.markdown("---")
st.markdown("🛠️ **Enhanced Flight Mapper** - Advanced ADS-B Data Analysis Tool")

    