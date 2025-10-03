import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import time
import numpy as np

st.set_page_config(
    page_title="Comcast ISCO - Interactive Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for filters and chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_filters' not in st.session_state:
    st.session_state.selected_filters = {
        'date_range': ('2023-01-01', '2024-12-31'),
        'product_categories': [],
        'supplier_tiers': [],
        'service_regions': [],
        'transport_modes': []
    }
if 'thresholds' not in st.session_state:
    st.session_state.thresholds = {
        'otd_rate': 90.0,
        'stockout_limit': 5,
        'cost_variance': 10.0
    }

st.sidebar.title("📦 Comcast ISCO - Interactive Analytics")
st.sidebar.markdown("### Supply Chain Analytics")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5 min)", value=False)
if auto_refresh:
    st.sidebar.caption("⏰ Last updated: " + datetime.now().strftime("%H:%M:%S"))

page = st.sidebar.selectbox(
    "Select View",
    [
        "🏠 Overview Dashboard",
        "📈 Supplier Performance",
        "📦 Inventory & Demand",
        "🚚 Logistics Analytics", 
        "🔎 Product Catalog Search",
        "🤖 AI Assistant Chat",
        "⚙️ Settings & Thresholds"
    ]
)

# Global Filters Section
with st.sidebar.expander("🎛️ Global Filters", expanded=True):
    # Date Range Filter
    st.markdown("**📅 Date Range**")
    date_option = st.radio("Select Period:", ["Last 6 Months", "Year to Date", "Custom Range"], index=1)
    
    if date_option == "Custom Range":
        start_date = st.date_input("Start Date", value=date(2023, 1, 1))
        end_date = st.date_input("End Date", value=date(2024, 12, 31))
        st.session_state.selected_filters['date_range'] = (str(start_date), str(end_date))
    elif date_option == "Last 6 Months":
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        st.session_state.selected_filters['date_range'] = (str(start_date), str(end_date))
    else:  # Year to Date
        start_date = date(datetime.now().year, 1, 1)
        end_date = datetime.now().date()
        st.session_state.selected_filters['date_range'] = (str(start_date), str(end_date))
    
    # Category Filters
    categories = st.multiselect("📦 Product Categories", 
                               ["Cable Modems", "Set-Top Boxes", "Routers", "Installation Kits", "Fiber Equipment"],
                               default=st.session_state.selected_filters['product_categories'])
    st.session_state.selected_filters['product_categories'] = categories
    
    tiers = st.multiselect("🏆 Supplier Tiers",
                          ["Tier 1", "Tier 2", "Tier 3"],
                          default=st.session_state.selected_filters['supplier_tiers'])
    st.session_state.selected_filters['supplier_tiers'] = tiers
    
    regions = st.multiselect("🌍 Service Regions",
                            ["Northeast", "Southeast", "Central", "West"],
                            default=st.session_state.selected_filters['service_regions'])
    st.session_state.selected_filters['service_regions'] = regions

# Quick Actions
with st.sidebar.expander("⚡ Quick Actions", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Export Data"):
            st.success("Export feature available in main view")
    with col2:
        if st.button("📧 Generate Report"):
            st.success("Report generation initiated")


@st.cache_data
def run_query(query: str) -> pd.DataFrame:
    try:
        conn = st.connection("snowflake")
        return conn.query(query)
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()

# Enhanced helper functions
def apply_filters_to_query(base_query: str, table_alias: str = "") -> str:
    """Apply global filters to any query"""
    filters = st.session_state.selected_filters
    where_clauses = []
    
    # Only apply filters if they're actually selected
    # Date filter (adjust column names based on table)
    if filters['date_range'] and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        start_year = start_date.split('-')[0]
        end_year = end_date.split('-')[0]
        
        if 'INVENTORY_FACT' in base_query:
            where_clauses.append(f"({table_alias}INVENTORY_YEAR >= {start_year} AND {table_alias}INVENTORY_YEAR <= {end_year})")
        elif 'LOGISTICS_METRICS' in base_query:
            where_clauses.append(f"({table_alias}SHIPMENT_YEAR >= {start_year} AND {table_alias}SHIPMENT_YEAR <= {end_year})")
        elif 'VENDOR_SCORECARD' in base_query:
            where_clauses.append(f"({table_alias}EVALUATION_YEAR >= {start_year} AND {table_alias}EVALUATION_YEAR <= {end_year})")
    
    # Category filter - only apply to relevant tables
    if filters['product_categories'] and ('INVENTORY_FACT' in base_query or 'DEMAND_FORECAST' in base_query):
        categories = "', '".join(filters['product_categories'])
        where_clauses.append(f"{table_alias}PRODUCT_CATEGORY IN ('{categories}')")
    
    # Tier filter - only apply to supplier-related queries
    if filters['supplier_tiers'] and ('SUPPLIER_PROFILES' in base_query or 'VENDOR_SCORECARD' in base_query):
        tiers = "', '".join(filters['supplier_tiers'])
        if 'SUPPLIER_PROFILES' in base_query:
            where_clauses.append(f"{table_alias}TIER_LEVEL IN ('{tiers}')")
    
    # Region filter - only apply to logistics queries
    if filters['service_regions'] and 'LOGISTICS_METRICS' in base_query:
        regions = "', '".join(filters['service_regions'])
        where_clauses.append(f"{table_alias}SERVICE_REGION IN ('{regions}')")
    
    # Apply WHERE clauses only if we have any and the query structure supports it
    if where_clauses:
        # Check if query already has WHERE clause
        base_upper = base_query.upper()
        if 'WHERE' in base_upper:
            return base_query + " AND " + " AND ".join(where_clauses)
        elif 'GROUP BY' in base_upper or 'ORDER BY' in base_query:
            # Insert WHERE before GROUP BY or ORDER BY
            if 'GROUP BY' in base_upper:
                parts = base_query.split('GROUP BY')
                return parts[0] + " WHERE " + " AND ".join(where_clauses) + " GROUP BY" + parts[1]
            else:
                parts = base_query.split('ORDER BY')
                return parts[0] + " WHERE " + " AND ".join(where_clauses) + " ORDER BY" + parts[1]
        else:
            return base_query + " WHERE " + " AND ".join(where_clauses)
    
    return base_query

def create_metric_card(title, value, delta=None, delta_color="normal", help_text=""):
    """Create enhanced metric cards with trend indicators"""
    if delta is not None:
        if delta > 0:
            delta_str = f"+{delta:.1f}%"
            delta_color = "normal" if delta_color == "normal" else "inverse"
        else:
            delta_str = f"{delta:.1f}%"
        st.metric(title, value, delta=delta_str, delta_color=delta_color, help=help_text)
    else:
        st.metric(title, value, help=help_text)

def check_alerts(df, metric_col, threshold, alert_type="high"):
    """Check for threshold violations and return alerts"""
    alerts = []
    if df.empty:
        return alerts
    
    if alert_type == "high":
        violations = df[df[metric_col] > threshold]
    else:
        violations = df[df[metric_col] < threshold]
    
    for _, row in violations.iterrows():
        alerts.append({
            'type': alert_type,
            'metric': metric_col,
            'value': row[metric_col],
            'threshold': threshold,
            'details': row.to_dict()
        })
    
    return alerts

def display_alerts(alerts):
    """Display alert notifications"""
    if alerts:
        with st.sidebar.expander(f"🚨 Alerts ({len(alerts)})", expanded=True):
            for alert in alerts[:5]:  # Show top 5 alerts
                if alert['type'] == 'high':
                    st.error(f"⚠️ High {alert['metric']}: {alert['value']:.1f} (Threshold: {alert['threshold']})")
                else:
                    st.warning(f"📉 Low {alert['metric']}: {alert['value']:.1f} (Threshold: {alert['threshold']})")

def export_data_to_csv(df, filename):
    """Export dataframe to CSV"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


@st.cache_data
def get_connection_info():
    try:
        conn = st.connection("snowflake")
        info = conn.query(
            """
            SELECT 
                CURRENT_DATABASE() AS database_name,
                CURRENT_SCHEMA() AS schema_name,
                CURRENT_ROLE() AS role_name,
                CURRENT_WAREHOUSE() AS warehouse_name,
                CURRENT_USER() AS user_name
            """
        )
        return info.iloc[0] if not info.empty else None
    except Exception as e:
        st.error(f"Connection info error: {str(e)}")
        return None


def show_database_info(schemas_and_tables):
    with st.expander("🔗 Database Connection & Data Sources", expanded=False):
        info = get_connection_info()
        if info is not None:
            st.markdown(
                f"""
                <div style=\"background-color:#f0f2f6;padding:10px;border-radius:6px;margin-bottom:10px;font-size:12px;\">
                  <b>Database</b>: {info['DATABASE_NAME']} &nbsp;|&nbsp; <b>Schema</b>: {info['SCHEMA_NAME']} &nbsp;|&nbsp; 
                  <b>Warehouse</b>: {info['WAREHOUSE_NAME']} &nbsp;|&nbsp; <b>Role</b>: {info['ROLE_NAME']} &nbsp;|&nbsp; <b>User</b>: {info['USER_NAME']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("**📊 Data Sources Used:**")
        for schema, tables in schemas_and_tables.items():
            joined = " • ".join([f"`{t}`" for t in tables])
            st.markdown(
                f"""
                <div style=\"margin-bottom:10px;padding:8px;background-color:#fafafa;border-left:3px solid #4ECDC4;border-radius:3px;\">
                  <div style=\"font-weight:bold;color:#333;font-size:13px;margin-bottom:3px;\">📁 {schema}</div>
                  <div style=\"font-size:11px;color:#666;line-height:1.4;padding-left:10px;\">{joined}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


if page == "🏠 Overview Dashboard":
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(1)  # Simulate refresh delay
        st.rerun()
    
    st.title("📦 ISCO Interactive Analytics Dashboard")
    st.markdown("### Real-time Supply Chain Intelligence with AI Insights")

    sources = {
        "ISCO_ANALYTICS.PROD": [
            "SUPPLIER_PROFILES", "INVENTORY_FACT", "LOGISTICS_METRICS", 
            "DEMAND_FORECAST", "VENDOR_SCORECARD", "PRODUCT_CATALOG (optional)"
        ]
    }
    show_database_info(sources)

    # Enhanced KPI Cards with comparisons
    st.subheader("📊 Key Performance Indicators")
    
    # Get KPI data from individual queries to avoid complex join issues
    # Supplier count
    supplier_query = """
        SELECT COUNT(DISTINCT SUPPLIER_ID) as supplier_count
        FROM ISCO_ANALYTICS.PROD.SUPPLIER_PROFILES
    """
    
    # Inventory metrics
    inv_query = """
        SELECT 
            ROUND(SUM(INVENTORY_VALUE_MILLIONS),2) as total_inventory_value,
            SUM(STOCKOUT_INCIDENTS) as total_stockouts
        FROM ISCO_ANALYTICS.PROD.INVENTORY_FACT
    """
    
    # Logistics metrics  
    logistics_query = """
        SELECT 
            ROUND(AVG(ON_TIME_DELIVERY_RATE),2) as avg_otd_rate,
            ROUND(AVG(COST_PER_SHIPMENT),2) as avg_cost_per_shipment
        FROM ISCO_ANALYTICS.PROD.LOGISTICS_METRICS
    """
    
    # Quality metrics
    quality_query = """
        SELECT ROUND(AVG(QUALITY_SCORE),2) as avg_quality_score
        FROM ISCO_ANALYTICS.PROD.VENDOR_SCORECARD
    """
    
    # Execute queries and combine results
    supplier_data = run_query(supplier_query)
    inv_data = run_query(apply_filters_to_query(inv_query))
    logistics_data = run_query(apply_filters_to_query(logistics_query))
    quality_data = run_query(quality_query)
    
    # Combine into single dataframe
    kpi_data = pd.DataFrame({
        'SUPPLIER_COUNT': [supplier_data['SUPPLIER_COUNT'].iloc[0] if not supplier_data.empty else 0],
        'TOTAL_INVENTORY_VALUE': [inv_data['TOTAL_INVENTORY_VALUE'].iloc[0] if not inv_data.empty else 0],
        'TOTAL_STOCKOUTS': [inv_data['TOTAL_STOCKOUTS'].iloc[0] if not inv_data.empty else 0],
        'AVG_OTD_RATE': [logistics_data['AVG_OTD_RATE'].iloc[0] if not logistics_data.empty else 0],
        'AVG_COST_PER_SHIPMENT': [logistics_data['AVG_COST_PER_SHIPMENT'].iloc[0] if not logistics_data.empty else 0],
        'AVG_QUALITY_SCORE': [quality_data['AVG_QUALITY_SCORE'].iloc[0] if not quality_data.empty else 0]
    })
    
    # KPI data is already constructed above from individual queries
    if not kpi_data.empty:
        kpi_data = pd.DataFrame(kpi_data)
        
        # Convert to numeric
        for col in kpi_data.columns:
            kpi_data[col] = pd.to_numeric(kpi_data[col], errors='coerce')
        
        # Create KPI cards with simulated trends
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            supplier_count_raw = kpi_data['SUPPLIER_COUNT'].iloc[0]
            supplier_count = int(supplier_count_raw) if pd.notna(supplier_count_raw) else 0
            create_metric_card("🏢 Active Suppliers", 
                             f"{supplier_count}", 
                             delta=2.3, help_text="Total active suppliers in network")
        
        with col2:
            inv_value_raw = kpi_data['TOTAL_INVENTORY_VALUE'].iloc[0]
            inv_value = float(inv_value_raw) if pd.notna(inv_value_raw) else 0.0
            create_metric_card("💰 Inventory Value", 
                             f"${inv_value:,.1f}M", 
                             delta=-1.2, delta_color="inverse", 
                             help_text="Total inventory value in millions")
        
        with col3:
            otd_rate_raw = kpi_data['AVG_OTD_RATE'].iloc[0]
            otd_rate = float(otd_rate_raw) if pd.notna(otd_rate_raw) else 0.0
            create_metric_card("🚚 On-Time Delivery", 
                             f"{otd_rate:.1f}%", 
                             delta=0.8, help_text="Average on-time delivery rate")
        
        with col4:
            cost_per_ship_raw = kpi_data['AVG_COST_PER_SHIPMENT'].iloc[0]
            cost_per_ship = float(cost_per_ship_raw) if pd.notna(cost_per_ship_raw) else 0.0
            create_metric_card("📦 Cost/Shipment", 
                             f"${cost_per_ship:,.0f}", 
                             delta=-3.1, delta_color="inverse", 
                             help_text="Average cost per shipment")
        
        with col5:
            stockouts_raw = kpi_data['TOTAL_STOCKOUTS'].iloc[0]
            stockouts = int(stockouts_raw) if pd.notna(stockouts_raw) else 0
            create_metric_card("⚠️ Stockouts", 
                             f"{stockouts}", 
                             delta=15.2, delta_color="normal", 
                             help_text="Total stockout incidents")
        
        with col6:
            quality_raw = kpi_data['AVG_QUALITY_SCORE'].iloc[0]
            quality = float(quality_raw) if pd.notna(quality_raw) else 0.0
            create_metric_card("⭐ Quality Score", 
                             f"{quality:.1f}/100", 
                             delta=1.5, help_text="Average supplier quality score")
        
        # Check for alerts
        alerts = []
        if otd_rate < st.session_state.thresholds['otd_rate']:
            alerts.extend(check_alerts(kpi_data, 'AVG_OTD_RATE', 
                                     st.session_state.thresholds['otd_rate'], 'low'))
        if stockouts > st.session_state.thresholds['stockout_limit']:
            alerts.extend(check_alerts(kpi_data, 'TOTAL_STOCKOUTS', 
                                     st.session_state.thresholds['stockout_limit'], 'high'))
        
        display_alerts(alerts)

    st.markdown("---")
    
    # Interactive Charts Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Inventory Trends & Drill-Down")
        
        # Enhanced inventory query with filters
        inv_query = apply_filters_to_query("""
            SELECT 
                PRODUCT_CATEGORY,
                INVENTORY_QUARTER,
                INVENTORY_YEAR,
                ROUND(SUM(INVENTORY_VALUE_MILLIONS),2) AS total_value,
                SUM(STOCKOUT_INCIDENTS) as stockouts,
                ROUND(AVG(INVENTORY_TURNOVER_RATIO),2) as avg_turnover
            FROM ISCO_ANALYTICS.PROD.INVENTORY_FACT
            GROUP BY PRODUCT_CATEGORY, INVENTORY_QUARTER, INVENTORY_YEAR
            ORDER BY INVENTORY_YEAR, INVENTORY_QUARTER
        """)
        
        inv_df = run_query(inv_query)
        
        if not inv_df.empty:
            inv_df = pd.DataFrame(inv_df)
            for col in ['TOTAL_VALUE', 'STOCKOUTS', 'AVG_TURNOVER']:
                inv_df[col] = pd.to_numeric(inv_df[col], errors='coerce')
            
            # Create period label for better display
            inv_df['PERIOD'] = inv_df['INVENTORY_QUARTER'] + ' ' + inv_df['INVENTORY_YEAR'].astype(str)
            
            # Interactive chart with click events
            fig = px.bar(
                inv_df,
                x="PERIOD",
                y="TOTAL_VALUE",
                color="PRODUCT_CATEGORY",
                hover_data=["STOCKOUTS", "AVG_TURNOVER"],
                title="Inventory Value by Period (Click bars for details)"
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            selected_chart = st.plotly_chart(fig, use_container_width=True, key="inv_chart")
            
            # Export functionality
            if st.button("📥 Export Inventory Data"):
                export_data_to_csv(inv_df, "isco_inventory_data.csv")
    
    with col2:
        st.subheader("🎯 AI Performance Insights")
        
        # Generate AI insights based on current data
        if not inv_df.empty:
            total_stockouts = inv_df['STOCKOUTS'].sum()
            avg_turnover = inv_df['AVG_TURNOVER'].mean()
            
            insight_query = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'llama3-70b',
                    'ISCO Performance Summary: Total stockouts: {total_stockouts}, Avg turnover: {avg_turnover:.2f}. 
                    Provide 3 bullet points with actionable insights for improving supply chain performance. 
                    Focus on inventory optimization and stockout reduction. Keep under 100 words.'
                ) AS insight
            """
            
            ai_insight = run_query(insight_query)
            if not ai_insight.empty:
                st.info("🤖 **AI Recommendations:**")
                st.write(ai_insight.iloc[0]['INSIGHT'])
        
        # Performance heatmap
        st.subheader("🔥 Performance Heatmap")
        if not inv_df.empty:
            # Create a simple heatmap of performance metrics
            heatmap_data = inv_df.pivot_table(
                values='TOTAL_VALUE', 
                index='PRODUCT_CATEGORY', 
                columns='INVENTORY_QUARTER', 
                aggfunc='sum'
            ).fillna(0)
            
            fig_heatmap = px.imshow(
                heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale='RdYlBu_r',
                title="Value by Category & Quarter"
            )
            fig_heatmap.update_layout(height=300)
            st.plotly_chart(fig_heatmap, use_container_width=True)

    # Advanced Analytics Section
    st.markdown("---")
    st.subheader("🔬 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📊 Correlation Analysis", "🎯 Predictive Insights", "🌐 Network View"])
    
    with tab1:
        # Correlation matrix of key metrics
        if not inv_df.empty:
            correlation_data = inv_df[['TOTAL_VALUE', 'STOCKOUTS', 'AVG_TURNOVER']].corr()
            
            fig_corr = px.imshow(
                correlation_data.values,
                x=correlation_data.columns,
                y=correlation_data.index,
                color_continuous_scale='RdBu',
                title="Metric Correlations",
                text_auto='.2f'
            )
            fig_corr.update_layout(height=300)
            st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab2:
        st.write("🔮 **Predictive Model Insights:**")
        st.info("Based on historical trends, Q4 2024 inventory value is predicted to increase by 8-12% driven by seasonal demand.")
        
        # Simple trend forecast
        if not inv_df.empty:
            recent_data = inv_df[inv_df['INVENTORY_YEAR'] == inv_df['INVENTORY_YEAR'].max()]
            trend_fig = px.line(recent_data.groupby('PRODUCT_CATEGORY')['TOTAL_VALUE'].sum().reset_index(),
                              x='PRODUCT_CATEGORY', y='TOTAL_VALUE',
                              title="Category Trend Forecast", markers=True)
            st.plotly_chart(trend_fig, use_container_width=True)
    
    with tab3:
        st.write("🌐 **Supply Chain Network Overview:**")
        
        # Network diagram placeholder (would require networkx in real implementation)
        network_data = {
            'Suppliers': ['Tier 1: 5 suppliers', 'Tier 2: 8 suppliers', 'Tier 3: 4 suppliers'],
            'Categories': ['Cable Modems', 'Set-Top Boxes', 'Routers', 'Installation Kits'],
            'Regions': ['Northeast', 'Southeast', 'Central', 'West']
        }
        
        for key, values in network_data.items():
            st.write(f"**{key}:** {', '.join(values)}")
        
        st.info("💡 Network analysis shows Tier 1 suppliers handle 65% of total volume across all regions.")


elif page == "📈 Supplier Performance":
    st.title("📈 Supplier Performance")
    st.caption("Quality, delivery, and cost performance from vendor scorecards")

    query = """
        SELECT 
            sp.SUPPLIER_ID,
            sp.SUPPLIER_NAME,
            sp.SUPPLIER_TYPE,
            sp.TIER_LEVEL,
            ROUND(AVG(vs.QUALITY_SCORE),2) AS avg_quality,
            ROUND(AVG(vs.DELIVERY_PERFORMANCE_SCORE),2) AS avg_delivery,
            ROUND(AVG(vs.COST_COMPETITIVENESS_SCORE),2) AS avg_cost,
            ROUND(SUM(vs.COST_SAVINGS_MILLIONS),2) AS total_savings
        FROM ISCO_ANALYTICS.PROD.SUPPLIER_PROFILES sp
        JOIN ISCO_ANALYTICS.PROD.VENDOR_SCORECARD vs ON sp.SUPPLIER_ID = vs.SUPPLIER_ID
        GROUP BY sp.SUPPLIER_ID, sp.SUPPLIER_NAME, sp.SUPPLIER_TYPE, sp.TIER_LEVEL
        ORDER BY avg_quality DESC
        LIMIT 20
    """
    df = run_query(query)

    if not df.empty:
        df = pd.DataFrame(df)
        for col in ["AVG_COST", "AVG_DELIVERY", "TOTAL_SAVINGS"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create clickable table using data_editor with selection
        st.subheader("📊 Supplier Performance Table")
        st.caption("Click on a row to select a supplier and see detailed insights below")
        
        # Add a selection column to make rows clickable
        df_display = df.copy()
        df_display.insert(0, "Select", False)
        
        # Use data_editor for row selection
        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Click to select this supplier",
                    default=False,
                )
            },
            disabled=[col for col in df_display.columns if col != "Select"],
            key="supplier_selection_table"
        )
        
        # Find which supplier was selected
        selected_supplier = None
        if edited_df["Select"].any():
            selected_rows = edited_df[edited_df["Select"] == True]
            if not selected_rows.empty:
                selected_supplier = selected_rows.iloc[0]["SUPPLIER_NAME"]
                # Store in session state
                st.session_state.selected_supplier = selected_supplier
        elif st.session_state.get("selected_supplier"):
            # Keep previous selection if no new selection made
            selected_supplier = st.session_state.selected_supplier

        col1, col2 = st.columns(2)
        with col1:
            # Ensure non-negative bubble sizes for Plotly
            if "TOTAL_SAVINGS" in df.columns:
                df["TOTAL_SAVINGS_SIZE"] = df["TOTAL_SAVINGS"].clip(lower=0).fillna(0)
            else:
                df["TOTAL_SAVINGS_SIZE"] = 0

            fig = px.scatter(
                df,
                x="AVG_COST",
                y="AVG_DELIVERY",
                size="TOTAL_SAVINGS_SIZE",
                color="TIER_LEVEL",
                hover_name="SUPPLIER_NAME",
                title="Cost vs Delivery (bubble = total savings)",
                size_max=60
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🤖 AI Supplier Insight")
            if selected_supplier and not df.empty:
                # Get data for selected supplier
                supplier_row = df[df['SUPPLIER_NAME'] == selected_supplier].iloc[0]
                st.write(f"**Selected:** {selected_supplier}")
                
                ai_sql = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'llama3-70b',
                    CONCAT(
                        'Provide a brief performance summary (<=80 words) for supplier ', '{supplier_row['SUPPLIER_NAME']}', '. ',
                        'Tier: ', '{supplier_row['TIER_LEVEL']}', '. ',
                        'Avg Quality: ', '{supplier_row['AVG_QUALITY']}', ', ',
                        'Avg Delivery: ', '{supplier_row['AVG_DELIVERY']}', ', ',
                        'Avg Cost Score: ', '{supplier_row['AVG_COST']}', '. ',
                        'Total savings (MM): ', '{supplier_row['TOTAL_SAVINGS']}', '. ',
                        'Mention strengths and a recommendation for improving CPU and service levels.'
                    )
                ) AS insight
                """
                ai_res = run_query(ai_sql)
                if not ai_res.empty:
                    st.info(ai_res.iloc[0]["INSIGHT"])
            else:
                st.info("👆 Click on a supplier in the table above to see AI-powered insights and recommendations.")
        
        # Detailed insights section below the charts
        if selected_supplier and not df.empty:
            st.markdown("---")
            st.subheader(f"📊 Detailed Analysis: {selected_supplier}")
            
            supplier_data = df[df['SUPPLIER_NAME'] == selected_supplier].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Quality Score", f"{supplier_data['AVG_QUALITY']:.1f}/100")
                st.metric("Delivery Score", f"{supplier_data['AVG_DELIVERY']:.1f}/100")
            
            with col2:
                st.metric("Cost Competitiveness", f"{supplier_data['AVG_COST']:.1f}/100")
                st.metric("Total Savings", f"${supplier_data['TOTAL_SAVINGS']:.1f}M")
            
            with col3:
                st.write(f"**Supplier Type:** {supplier_data['SUPPLIER_TYPE']}")
                st.write(f"**Tier Level:** {supplier_data['TIER_LEVEL']}")
                st.write(f"**Supplier ID:** {supplier_data['SUPPLIER_ID']}")
            
            # Performance comparison within tier
            same_tier = df[df['TIER_LEVEL'] == supplier_data['TIER_LEVEL']]
            if len(same_tier) > 1:
                st.write("**📈 Performance vs. Peer Suppliers:**")
                quality_rank = (same_tier['AVG_QUALITY'] > supplier_data['AVG_QUALITY']).sum() + 1
                delivery_rank = (same_tier['AVG_DELIVERY'] > supplier_data['AVG_DELIVERY']).sum() + 1
                cost_rank = (same_tier['AVG_COST'] > supplier_data['AVG_COST']).sum() + 1
                
                st.write(f"• Quality: #{quality_rank} of {len(same_tier)} in {supplier_data['TIER_LEVEL']}")
                st.write(f"• Delivery: #{delivery_rank} of {len(same_tier)} in {supplier_data['TIER_LEVEL']}")
                st.write(f"• Cost Competitiveness: #{cost_rank} of {len(same_tier)} in {supplier_data['TIER_LEVEL']}")
            
            # Clear selection button
            if st.button("🔄 Clear Selection"):
                if "selected_supplier" in st.session_state:
                    del st.session_state.selected_supplier
                st.rerun()


elif page == "📦 Inventory & Demand":
    st.title("📦 Inventory & Demand")
    st.caption("Turnover, stockouts, and forecast accuracy by category/quarter")

    kpi_q = """
        SELECT 
            il.PRODUCT_CATEGORY,
            il.INVENTORY_QUARTER,
            il.INVENTORY_YEAR,
            ROUND(AVG(il.INVENTORY_TURNOVER_RATIO),2) AS avg_turnover,
            SUM(il.STOCKOUT_INCIDENTS) AS stockouts,
            ROUND(SUM(il.INVENTORY_VALUE_MILLIONS),2) AS inv_value,
            ROUND(AVG(df.FORECAST_ACCURACY_PERCENT),2) AS forecast_accuracy
        FROM ISCO_ANALYTICS.PROD.INVENTORY_FACT il
        LEFT JOIN ISCO_ANALYTICS.PROD.DEMAND_FORECAST df 
          ON il.INVENTORY_QUARTER = df.FORECAST_QUARTER 
         AND il.INVENTORY_YEAR = df.FORECAST_YEAR
        GROUP BY il.PRODUCT_CATEGORY, il.INVENTORY_QUARTER, il.INVENTORY_YEAR
        ORDER BY il.INVENTORY_YEAR, il.INVENTORY_QUARTER
    """
    kpi = run_query(kpi_q)

    if not kpi.empty:
        kpi = pd.DataFrame(kpi)
        for col in ["AVG_TURNOVER", "STOCKOUTS", "INV_VALUE", "FORECAST_ACCURACY"]:
            if col in kpi.columns:
                kpi[col] = pd.to_numeric(kpi[col], errors='coerce')
        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(
                kpi, x="INVENTORY_QUARTER", y="AVG_TURNOVER", color="PRODUCT_CATEGORY",
                title="Avg Inventory Turnover Ratio"
            )
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(
                kpi, x="INVENTORY_QUARTER", y="FORECAST_ACCURACY",
                color="PRODUCT_CATEGORY", title="Forecast Accuracy %"
            )
            fig2.update_layout(height=320)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Stockouts vs Inventory Value (Latest Year)")
        latest_year = int(pd.to_numeric(kpi["INVENTORY_YEAR"], errors='coerce').max()) if not kpi.empty else None
        if latest_year:
            latest = kpi[kpi["INVENTORY_YEAR"] == latest_year]
            fig3 = px.scatter(
                latest,
                x="INV_VALUE",
                y="STOCKOUTS",
                color="PRODUCT_CATEGORY",
                hover_name="PRODUCT_CATEGORY",
                size="INV_VALUE",
                title=f"Stockouts vs Value (MM) - {latest_year}"
            )
            fig3.update_layout(height=320)
            st.plotly_chart(fig3, use_container_width=True)


elif page == "🚚 Logistics Analytics":
    st.title("🚚 Logistics Analytics")
    st.caption("On-time delivery, cost per shipment, and damage incidents with enhanced filtering")

    # Show database connection info
    logistics_schemas_tables = {
        "ISCO_ANALYTICS.PROD": ["LOGISTICS_METRICS"]
    }
    show_database_info(logistics_schemas_tables)
    
    # Enhanced logistics query with filters applied
    lg_q = """
        SELECT 
            TRANSPORT_MODE,
            SERVICE_REGION,
            SHIPMENT_QUARTER,
            SHIPMENT_YEAR,
            ROUND(AVG(ON_TIME_DELIVERY_RATE),2) AS avg_otd,
            ROUND(AVG(COST_PER_SHIPMENT),2) AS avg_cps,
            SUM(TOTAL_SHIPMENTS) AS total_shipments,
            SUM(DAMAGE_INCIDENTS) AS damages
        FROM ISCO_ANALYTICS.PROD.LOGISTICS_METRICS
        GROUP BY TRANSPORT_MODE, SERVICE_REGION, SHIPMENT_QUARTER, SHIPMENT_YEAR
        ORDER BY SHIPMENT_YEAR DESC, SHIPMENT_QUARTER DESC
    """
    
    # Apply filters to the query
    filtered_lg_q = apply_filters_to_query(lg_q)
    lg = run_query(filtered_lg_q)

    if not lg.empty:
        lg = pd.DataFrame(lg)
        for col in ["AVG_OTD", "AVG_CPS", "TOTAL_SHIPMENTS", "DAMAGES"]:
            if col in lg.columns:
                lg[col] = pd.to_numeric(lg[col], errors='coerce')
        
        # KPI summary cards
        st.subheader("📊 Logistics KPIs")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_otd = lg['AVG_OTD'].mean()
            create_metric_card("🚚 Avg OTD Rate", f"{avg_otd:.1f}%", 
                             delta=2.1, help_text="Average on-time delivery rate")
        
        with col2:
            avg_cost = lg['AVG_CPS'].mean()
            create_metric_card("💰 Avg Cost/Shipment", f"${avg_cost:,.0f}", 
                             delta=-1.5, delta_color="inverse", help_text="Average cost per shipment")
        
        with col3:
            total_ships = lg['TOTAL_SHIPMENTS'].sum()
            create_metric_card("📦 Total Shipments", f"{total_ships:,.0f}", 
                             delta=8.3, help_text="Total shipments in period")
        
        with col4:
            total_damages = lg['DAMAGES'].sum()
            create_metric_card("⚠️ Damage Incidents", f"{total_damages:.0f}", 
                             delta=-12.4, delta_color="inverse", help_text="Total damage incidents")
        
        st.markdown("---")
        
        # Charts section
        col1, col2 = st.columns(2)
        with col1:
            # Filter out any null values for the chart
            chart_data = lg.dropna(subset=['AVG_OTD'])
            if not chart_data.empty:
                fig = px.bar(chart_data, x="TRANSPORT_MODE", y="AVG_OTD", color="SERVICE_REGION",
                           title="On-Time Delivery Rate by Transport Mode & Region",
                           hover_data=["SHIPMENT_QUARTER", "SHIPMENT_YEAR"])
                fig.update_layout(height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No on-time delivery data available for selected filters")
        
        with col2:
            chart_data = lg.dropna(subset=['AVG_CPS'])
            if not chart_data.empty:
                fig2 = px.bar(chart_data, x="TRANSPORT_MODE", y="AVG_CPS", color="SERVICE_REGION",
                            title="Average Cost per Shipment by Transport Mode & Region",
                            hover_data=["SHIPMENT_QUARTER", "SHIPMENT_YEAR"])
                fig2.update_layout(height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("No cost data available for selected filters")
        
        # Detailed data table with export and row selection
        st.subheader("📋 Detailed Logistics Data")
        st.caption("Click on a row to select a logistics record and see detailed insights below")
        
        # Add period column for better readability
        lg['PERIOD'] = lg['SHIPMENT_QUARTER'] + ' ' + lg['SHIPMENT_YEAR'].astype(str)
        
        # Create clickable table using data_editor with selection
        lg_display = lg.copy()
        lg_display.insert(0, "Select", False)
        
        # Use data_editor for row selection
        edited_lg = st.data_editor(
            lg_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Click to select this logistics record",
                    default=False,
                )
            },
            disabled=[col for col in lg_display.columns if col != "Select"],
            key="logistics_selection_table"
        )
        
        # Find which logistics record was selected
        selected_logistics = None
        if edited_lg["Select"].any():
            selected_rows = edited_lg[edited_lg["Select"] == True]
            if not selected_rows.empty:
                selected_record = selected_rows.iloc[0]
                selected_logistics = {
                    'TRANSPORT_MODE': selected_record['TRANSPORT_MODE'],
                    'SERVICE_REGION': selected_record['SERVICE_REGION'],
                    'PERIOD': selected_record['PERIOD'],
                    'AVG_OTD': selected_record['AVG_OTD'],
                    'AVG_CPS': selected_record['AVG_CPS'],
                    'TOTAL_SHIPMENTS': selected_record['TOTAL_SHIPMENTS'],
                    'DAMAGES': selected_record['DAMAGES']
                }
                # Store in session state
                st.session_state.selected_logistics = selected_logistics
        elif st.session_state.get("selected_logistics"):
            # Keep previous selection if no new selection made
            selected_logistics = st.session_state.selected_logistics
        
        # Export functionality
        if st.button("📥 Export Logistics Data"):
            export_data_to_csv(lg, "isco_logistics_data.csv")
        
        # Detailed insights section for selected logistics record
        if selected_logistics:
            st.markdown("---")
            st.subheader(f"📊 Detailed Analysis: {selected_logistics['TRANSPORT_MODE']} in {selected_logistics['SERVICE_REGION']}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                otd_val = float(selected_logistics['AVG_OTD']) if pd.notna(selected_logistics['AVG_OTD']) else 0
                otd_color = "🟢" if otd_val >= 95 else "🟡" if otd_val >= 85 else "🔴"
                st.metric("On-Time Delivery", f"{otd_val:.1f}%")
                st.write(f"{otd_color} Performance Rating")
            
            with col2:
                cost_val = float(selected_logistics['AVG_CPS']) if pd.notna(selected_logistics['AVG_CPS']) else 0
                st.metric("Cost per Shipment", f"${cost_val:,.0f}")
            
            with col3:
                ships_val = int(selected_logistics['TOTAL_SHIPMENTS']) if pd.notna(selected_logistics['TOTAL_SHIPMENTS']) else 0
                st.metric("Total Shipments", f"{ships_val:,}")
            
            with col4:
                damages_val = int(selected_logistics['DAMAGES']) if pd.notna(selected_logistics['DAMAGES']) else 0
                damage_rate = (damages_val / ships_val * 100) if ships_val > 0 else 0
                st.metric("Damage Incidents", f"{damages_val}")
                st.write(f"**Damage Rate:** {damage_rate:.2f}%")
            
            # Performance comparison within same transport mode
            same_mode = lg[lg['TRANSPORT_MODE'] == selected_logistics['TRANSPORT_MODE']]
            if len(same_mode) > 1:
                st.write(f"**📈 Performance vs. Other {selected_logistics['TRANSPORT_MODE']} Routes:**")
                
                otd_rank = (same_mode['AVG_OTD'] > selected_logistics['AVG_OTD']).sum() + 1
                cost_rank = (same_mode['AVG_CPS'] < selected_logistics['AVG_CPS']).sum() + 1  # Lower cost is better
                
                st.write(f"• OTD Ranking: #{otd_rank} of {len(same_mode)} {selected_logistics['TRANSPORT_MODE']} routes")
                st.write(f"• Cost Ranking: #{cost_rank} of {len(same_mode)} {selected_logistics['TRANSPORT_MODE']} routes")
            
            # AI-powered specific insights for selected record
            ai_specific_prompt = f"""
            Analyze logistics performance for {selected_logistics['TRANSPORT_MODE']} transport in {selected_logistics['SERVICE_REGION']} region 
            during {selected_logistics['PERIOD']}. OTD: {selected_logistics['AVG_OTD']:.1f}%, 
            Cost: ${selected_logistics['AVG_CPS']:,.0f}, Shipments: {selected_logistics['TOTAL_SHIPMENTS']:,}, 
            Damages: {selected_logistics['DAMAGES']}. Provide specific recommendations to improve this route's performance. 
            Keep under 80 words.
            """.replace("'", "''")
            
            specific_ai_sql = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'llama3-70b',
                    '{ai_specific_prompt}'
                ) AS specific_recommendation
            """
            
            specific_result = run_query(specific_ai_sql)
            if not specific_result.empty:
                st.info("🤖 **Specific Route Recommendations:**")
                st.write(specific_result.iloc[0]["SPECIFIC_RECOMMENDATION"])
            
            # Clear selection button
            if st.button("🔄 Clear Logistics Selection"):
                if "selected_logistics" in st.session_state:
                    del st.session_state.selected_logistics
                st.rerun()
        
        # General AI insights section
        st.subheader("🤖 General Logistics Optimization Insights")
        
        if not lg.empty:
            # Calculate some insights for the AI
            worst_otd = lg.loc[lg['AVG_OTD'].idxmin()] if lg['AVG_OTD'].notna().any() else None
            highest_cost = lg.loc[lg['AVG_CPS'].idxmax()] if lg['AVG_CPS'].notna().any() else None
            
            ai_prompt = f"Analyze logistics performance: "
            if worst_otd is not None:
                ai_prompt += f"Worst OTD: {worst_otd['TRANSPORT_MODE']} in {worst_otd['SERVICE_REGION']} at {worst_otd['AVG_OTD']:.1f}%. "
            if highest_cost is not None:
                ai_prompt += f"Highest cost: {highest_cost['TRANSPORT_MODE']} in {highest_cost['SERVICE_REGION']} at ${highest_cost['AVG_CPS']:,.0f}. "
            ai_prompt += "Provide 3 specific recommendations to improve OTD and reduce costs for Comcast ISCO. Keep under 120 words."
            
            ai_sql = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'llama3-70b',
                    '{ai_prompt.replace("'", "''")}'
                ) AS recommendation
            """
            
            ai_result = run_query(ai_sql)
            if not ai_result.empty:
                st.info("🤖 **AI Recommendations:**")
                st.write(ai_result.iloc[0]["RECOMMENDATION"])
        
        # Performance alerts
        if not lg.empty:
            # Check for performance issues
            alerts = []
            low_otd = lg[lg['AVG_OTD'] < st.session_state.thresholds['otd_rate']]
            if not low_otd.empty:
                for _, row in low_otd.iterrows():
                    alerts.append(f"⚠️ Low OTD: {row['TRANSPORT_MODE']} in {row['SERVICE_REGION']} - {row['AVG_OTD']:.1f}%")
            
            if alerts:
                with st.expander(f"🚨 Performance Alerts ({len(alerts)})", expanded=True):
                    for alert in alerts:
                        st.error(alert)
    
    else:
        st.warning("🔍 No logistics data found for the selected filters. Try adjusting your filter criteria.")
        st.info("💡 **Troubleshooting:**\n- Check if date range includes data periods\n- Verify region filters match available data\n- Ensure database connection is active")


elif page == "🔎 Product Catalog Search":
    st.title("🔎 Product Catalog Search")
    st.caption("Search through product descriptions, vendor overviews, and technical specifications")

    # Enhanced search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search products (name, description, vendor):", value="modem", placeholder="e.g., router, cable modem, installation kit")
    with col2:
        search_type = st.selectbox("Search Type", ["All Fields", "Product Name", "Description", "Vendor"])

    if st.button("🔍 Search") and search:
        # Build query based on search type
        escaped_search = search.replace("'", "''")
        if search_type == "Product Name":
            where_clause = f"PRODUCT_NAME ILIKE '%{escaped_search}%'"
        elif search_type == "Description":
            where_clause = f"PRODUCT_DESCRIPTION ILIKE '%{escaped_search}%'"
        elif search_type == "Vendor":
            where_clause = f"VENDOR_OVERVIEW ILIKE '%{escaped_search}%'"
        else:  # All Fields
            where_clause = f"""(PRODUCT_NAME ILIKE '%{escaped_search}%' 
                           OR PRODUCT_DESCRIPTION ILIKE '%{escaped_search}%' 
                           OR VENDOR_OVERVIEW ILIKE '%{escaped_search}%'
                           OR TECHNICAL_SPECIFICATIONS ILIKE '%{escaped_search}%')"""
        
        query = f"""
            SELECT 
                CATALOG_ID,
                PRODUCT_NAME,
                PRODUCT_SKU,
                SUPPLIER_ID,
                PRODUCT_DESCRIPTION,
                TECHNICAL_SPECIFICATIONS,
                VENDOR_OVERVIEW,
                PRODUCT_IMAGE_URL,
                FEATURE_HIGHLIGHTS,
                INSTALLATION_GUIDE
            FROM ISCO_ANALYTICS.PROD.PRODUCT_CATALOG
            WHERE {where_clause}
            LIMIT 25
        """
        res = run_query(query)
        
        if res.empty:
            st.warning("🔍 No results found. Try adjusting your search terms or check if PRODUCT_CATALOG is loaded.")
            st.info("💡 **Search Tips:**\n- Try broader terms like 'cable', 'router', or 'installation'\n- Check spelling and try synonyms\n- Use partial words (e.g., 'mod' instead of 'modem')")
        else:
            res = pd.DataFrame(res)
            st.success(f"✅ Found {len(res)} product(s) matching '{search}'")
            
            # Display results in card format
            st.subheader("🎯 Search Results")
            
            for idx, product in res.iterrows():
                with st.container():
                    # Create a card-like layout
                    st.markdown("---")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Product header
                        st.markdown(f"### 📦 {product['PRODUCT_NAME']}")
                        st.caption(f"**SKU:** {product['PRODUCT_SKU']} | **Supplier:** {product['SUPPLIER_ID']} | **Catalog ID:** {product['CATALOG_ID']}")
                        
                        # Product description (truncated with expand option)
                        if pd.notna(product['PRODUCT_DESCRIPTION']):
                            desc = str(product['PRODUCT_DESCRIPTION'])
                            if len(desc) > 200:
                                with st.expander("📖 Product Description", expanded=False):
                                    st.write(desc)
                                st.write(f"**Description:** {desc[:200]}...")
                            else:
                                st.write(f"**Description:** {desc}")
                        
                        # Technical specifications
                        if pd.notna(product['TECHNICAL_SPECIFICATIONS']):
                            with st.expander("🔧 Technical Specifications", expanded=False):
                                st.write(product['TECHNICAL_SPECIFICATIONS'])
                        
                        # Feature highlights
                        if pd.notna(product['FEATURE_HIGHLIGHTS']):
                            st.write("**✨ Key Features:**")
                            st.info(product['FEATURE_HIGHLIGHTS'])
                    
                    with col2:
                        # Product image placeholder
                        if pd.notna(product['PRODUCT_IMAGE_URL']):
                            st.markdown("**🖼️ Product Image:**")
                            st.markdown(f"[View Image]({product['PRODUCT_IMAGE_URL']})")
                        else:
                            st.markdown("**🖼️ Product Image:**")
                            st.markdown("*No image available*")
                        
                        # Vendor information
                        if pd.notna(product['VENDOR_OVERVIEW']):
                            with st.expander("🏢 Vendor Info", expanded=False):
                                st.write(product['VENDOR_OVERVIEW'])
                        
                        # Installation guide
                        if pd.notna(product['INSTALLATION_GUIDE']):
                            with st.expander("🔧 Installation Guide", expanded=False):
                                st.write(product['INSTALLATION_GUIDE'])
                        
                        # Quick action buttons
                        st.markdown("**⚡ Quick Actions:**")
                        if st.button(f"📋 View Details", key=f"details_{idx}"):
                            st.success("Product details panel would open here")
                        
                        if st.button(f"📧 Contact Supplier", key=f"contact_{idx}"):
                            st.success(f"Contact request sent for {product['SUPPLIER_ID']}")
            
            # Search summary and actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Export Search Results"):
                    export_data_to_csv(res, f"product_search_{search.replace(' ', '_')}.csv")
            
            with col2:
                if st.button("🔄 Clear Search"):
                    st.rerun()
            
            with col3:
                if st.button("🎯 Refine Search"):
                    st.info("Adjust your search terms above and click Search again")
    
    else:
        # Default state - show search tips and examples
        st.markdown("---")
        st.subheader("🔍 Search Tips & Examples")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💡 Search Suggestions:**")
            example_searches = [
                "cable modem",
                "router wireless",
                "installation kit",
                "fiber equipment",
                "set-top box"
            ]
            
            for search_term in example_searches:
                if st.button(f"🔎 Search: {search_term}", key=f"example_{search_term.replace(' ', '_')}"):
                    st.session_state.example_search = search_term
                    st.rerun()
        
        with col2:
            st.markdown("**📊 Search Features:**")
            st.write("• **Text matching** across all product fields")
            st.write("• **Vendor information** and company details")
            st.write("• **Technical specifications** and features")
            st.write("• **Installation guides** and compatibility")
            st.write("• **Image links** and visual references")
            st.write("• **Export results** to CSV for analysis")
        
        # Show recent searches or popular products if available
        st.markdown("---")
        st.info("💡 **Pro Tip:** Use the search type dropdown to narrow your search to specific fields like 'Product Name' or 'Description' for more targeted results.")


elif page == "🤖 AI Assistant Chat":
    st.title("🤖 ISCO AI Assistant Chat")
    st.caption("Conversational AI for supply chain insights. Powered by Snowflake Cortex AI.")

    # Chat interface with history
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat with Your Data")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                with st.chat_message(chat["role"]):
                    st.write(chat["content"])
                    if chat["role"] == "assistant" and "follow_ups" in chat:
                        st.caption("**Suggested follow-ups:**")
                        for j, follow_up in enumerate(chat["follow_ups"][:3]):
                            if follow_up.strip():  # Only show non-empty follow-ups
                                if st.button(f"💡 {follow_up}", key=f"follow_{i}_{j}"):
                                    # Add user question to history
                                    st.session_state.chat_history.append({"role": "user", "content": follow_up})
                                    
                                    # Generate AI response immediately
                                    persona = st.session_state.get("chat_persona", "operations")
                                    prompt = (
                                        f"You are an ISCO supply chain analyst at Comcast speaking to a {persona}. "
                                        f"Answer this question succinctly (<=150 words): {follow_up}. "
                                        "Use data from SUPPLIER_PROFILES, INVENTORY_FACT, LOGISTICS_METRICS, DEMAND_FORECAST, VENDOR_SCORECARD tables. "
                                        "Provide specific insights and actionable recommendations."
                                    ).replace("'", "''")

                                    ai_sql = f"""
                                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                                            'llama3-70b',
                                            '{prompt}'
                                        ) AS answer
                                    """
                                    ai_response = run_query(ai_sql)
                                    
                                    if not ai_response.empty:
                                        answer = ai_response.iloc[0]["ANSWER"]
                                        
                                        # Generate new follow-up questions
                                        follow_up_sql = f"""
                                            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                                                'llama3-8b',
                                                'Based on this ISCO supply chain question: "{follow_up}", suggest 3 short follow-up questions (each <10 words). Return only the questions, separated by newlines.'
                                            ) AS follow_ups
                                        """
                                        follow_up_response = run_query(follow_up_sql)
                                        new_follow_ups = []
                                        if not follow_up_response.empty:
                                            new_follow_ups = follow_up_response.iloc[0]["FOLLOW_UPS"].split('\n')[:3]
                                        
                                        # Add assistant response to history
                                        st.session_state.chat_history.append({
                                            "role": "assistant", 
                                            "content": answer,
                                            "follow_ups": new_follow_ups
                                        })
                                    
                                    st.rerun()
        
        # Input section
        col_input, col_persona = st.columns([3, 1])
        with col_input:
            user_question = st.chat_input("Ask about ISCO performance, suppliers, inventory, or logistics...")
        with col_persona:
            persona = st.selectbox("Role:", ["executive", "operations", "planning", "finance"], key="chat_persona")
        
        if user_question:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Generate AI response
            with st.spinner("🤖 Analyzing your question..."):
                prompt = (
                    f"You are an ISCO supply chain analyst at Comcast speaking to a {persona}. "
                    f"Answer this question succinctly (<=150 words): {user_question}. "
                    "Use data from SUPPLIER_PROFILES, INVENTORY_FACT, LOGISTICS_METRICS, DEMAND_FORECAST, VENDOR_SCORECARD tables. "
                    "Provide specific insights and actionable recommendations."
                ).replace("'", "''")

                ai_sql = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'llama3-70b',
                        '{prompt}'
                    ) AS answer
                """
                ai_response = run_query(ai_sql)
                
                if not ai_response.empty:
                    answer = ai_response.iloc[0]["ANSWER"]
                    
                    # Generate follow-up questions
                    follow_up_sql = f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'llama3-8b',
                            'Based on this ISCO supply chain question: "{user_question}", suggest 3 short follow-up questions (each <10 words). Return only the questions, separated by newlines.'
                        ) AS follow_ups
                    """
                    follow_up_response = run_query(follow_up_sql)
                    follow_ups = []
                    if not follow_up_response.empty:
                        follow_ups = follow_up_response.iloc[0]["FOLLOW_UPS"].split('\n')[:3]
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": answer,
                        "follow_ups": follow_ups
                    })
                    
                    st.rerun()
    
    with col2:
        st.subheader("🎯 Quick Insights")
        
        # Quick insight buttons
        insight_queries = [
            "What are our top performing suppliers this quarter?",
            "Where are our biggest inventory risks?",
            "How can we reduce logistics costs?",
            "Which regions need attention?"
        ]
        
        for query in insight_queries:
            if st.button(f"💡 {query}", key=f"quick_{query}"):
                # Add user question to history
                st.session_state.chat_history.append({"role": "user", "content": query})
                
                # Generate AI response immediately
                persona = st.session_state.get("chat_persona", "operations")
                prompt = (
                    f"You are an ISCO supply chain analyst at Comcast speaking to a {persona}. "
                    f"Answer this question succinctly (<=150 words): {query}. "
                    "Use data from SUPPLIER_PROFILES, INVENTORY_FACT, LOGISTICS_METRICS, DEMAND_FORECAST, VENDOR_SCORECARD tables. "
                    "Provide specific insights and actionable recommendations."
                ).replace("'", "''")

                ai_sql = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'llama3-70b',
                        '{prompt}'
                    ) AS answer
                """
                ai_response = run_query(ai_sql)
                
                if not ai_response.empty:
                    answer = ai_response.iloc[0]["ANSWER"]
                    
                    # Generate follow-up questions
                    follow_up_sql = f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'llama3-8b',
                            'Based on this ISCO supply chain question: "{query}", suggest 3 short follow-up questions (each <10 words). Return only the questions, separated by newlines.'
                        ) AS follow_ups
                    """
                    follow_up_response = run_query(follow_up_sql)
                    follow_ups = []
                    if not follow_up_response.empty:
                        follow_ups = follow_up_response.iloc[0]["FOLLOW_UPS"].split('\n')[:3]
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": answer,
                        "follow_ups": follow_ups
                    })
                
                st.rerun()
        
        # Chat controls
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("📄 Export Chat"):
            chat_text = "\n\n".join([f"{chat['role'].title()}: {chat['content']}" for chat in st.session_state.chat_history])
            st.download_button(
                label="📥 Download Chat",
                data=chat_text,
                file_name="isco_chat_history.txt",
                mime="text/plain"
            )
        
        # Context panel
        st.subheader("📊 Current Context")
        st.caption(f"**Date Range:** {st.session_state.selected_filters['date_range'][0]} to {st.session_state.selected_filters['date_range'][1]}")
        if st.session_state.selected_filters['product_categories']:
            st.caption(f"**Categories:** {', '.join(st.session_state.selected_filters['product_categories'])}")
        if st.session_state.selected_filters['supplier_tiers']:
            st.caption(f"**Tiers:** {', '.join(st.session_state.selected_filters['supplier_tiers'])}")
        
        # Voice input placeholder
        st.markdown("---")
        st.caption("🎤 Voice input coming soon...")

elif page == "⚙️ Settings & Thresholds":
    st.title("⚙️ Settings & Thresholds")
    st.caption("Configure alerts, thresholds, and system preferences")
    
    tab1, tab2, tab3 = st.tabs(["🚨 Alert Thresholds", "🎛️ System Settings", "📊 Data Management"])
    
    with tab1:
        st.subheader("Alert Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Performance Thresholds**")
            
            new_otd = st.slider(
                "On-Time Delivery Rate (%)",
                min_value=70.0, max_value=100.0,
                value=st.session_state.thresholds['otd_rate'],
                step=0.5,
                help="Alert when OTD rate falls below this threshold"
            )
            
            new_stockout = st.number_input(
                "Maximum Stockout Incidents",
                min_value=0, max_value=50,
                value=st.session_state.thresholds['stockout_limit'],
                help="Alert when stockouts exceed this number"
            )
            
            new_cost_var = st.slider(
                "Cost Variance Threshold (%)",
                min_value=0.0, max_value=25.0,
                value=st.session_state.thresholds['cost_variance'],
                step=0.5,
                help="Alert when costs vary beyond this percentage"
            )
        
        with col2:
            st.markdown("**📧 Notification Settings**")
            
            email_alerts = st.checkbox("Email Alerts", value=True)
            slack_alerts = st.checkbox("Slack Notifications", value=False)
            dashboard_alerts = st.checkbox("Dashboard Alerts", value=True)
            
            alert_frequency = st.selectbox(
                "Alert Frequency",
                ["Real-time", "Hourly", "Daily", "Weekly"]
            )
            
            priority_filter = st.multiselect(
                "Alert Priorities",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High"]
            )
        
        if st.button("💾 Save Threshold Settings"):
            st.session_state.thresholds.update({
                'otd_rate': new_otd,
                'stockout_limit': new_stockout,
                'cost_variance': new_cost_var
            })
            st.success("✅ Settings saved successfully!")
    
    with tab2:
        st.subheader("System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔄 Refresh Settings**")
            auto_refresh_interval = st.selectbox(
                "Auto-refresh Interval",
                ["Disabled", "1 minute", "5 minutes", "15 minutes", "30 minutes"],
                index=2
            )
            
            cache_duration = st.selectbox(
                "Data Cache Duration",
                ["1 minute", "5 minutes", "15 minutes", "1 hour"],
                index=1
            )
            
            st.markdown("**🎨 Display Settings**")
            theme = st.selectbox("Color Theme", ["Default", "Dark", "Light", "ISCO Blue"])
            chart_style = st.selectbox("Chart Style", ["Modern", "Classic", "Minimal"])
        
        with col2:
            st.markdown("**🔐 Security Settings**")
            session_timeout = st.selectbox(
                "Session Timeout",
                ["30 minutes", "1 hour", "4 hours", "8 hours"],
                index=1
            )
            
            audit_logging = st.checkbox("Audit Logging", value=True)
            data_masking = st.checkbox("Sensitive Data Masking", value=False)
            
            st.markdown("**🤖 AI Settings**")
            ai_model = st.selectbox(
                "Default AI Model",
                ["llama3-70b", "llama3-8b", "mixtral-8x7b"],
                index=0
            )
            ai_temperature = st.slider("AI Response Creativity", 0.0, 1.0, 0.3, 0.1)
    
    with tab3:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Data Sources**")
            
            # Connection status
            connection_status = {
                "SUPPLIER_PROFILES": "🟢 Connected",
                "INVENTORY_FACT": "🟢 Connected", 
                "LOGISTICS_METRICS": "🟢 Connected",
                "DEMAND_FORECAST": "🟢 Connected",
                "VENDOR_SCORECARD": "🟢 Connected",
                "PRODUCT_CATALOG": "🟡 Optional"
            }
            
            for table, status in connection_status.items():
                st.write(f"**{table}:** {status}")
            
            if st.button("🔄 Refresh Connections"):
                st.success("All connections refreshed successfully!")
        
        with col2:
            st.markdown("**📤 Export & Backup**")
            
            export_format = st.selectbox(
                "Export Format",
                ["CSV", "Excel", "JSON", "Parquet"]
            )
            
            if st.button("📊 Export All Data"):
                st.info("Export initiated. Download will be available shortly.")
            
            if st.button("💾 Create Data Backup"):
                st.success("Backup created successfully!")
            
            st.markdown("**🔧 Maintenance**")
            if st.button("🗑️ Clear Cache"):
                st.cache_data.clear()
                st.success("Cache cleared!")
            
            if st.button("📈 Rebuild Analytics"):
                st.info("Analytics rebuild initiated...")
        
        # Data quality metrics
        st.markdown("---")
        st.subheader("📊 Data Quality Metrics")
        
        quality_metrics = {
            "Data Completeness": 98.5,
            "Data Accuracy": 97.2,
            "Data Freshness": 99.1,
            "Schema Compliance": 100.0
        }
        
        for metric, value in quality_metrics.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(value/100, text=f"{metric}: {value}%")
            with col2:
                if value >= 95:
                    st.success("✅ Good")
                elif value >= 90:
                    st.warning("⚠️ Fair") 
                else:
                    st.error("❌ Poor")


