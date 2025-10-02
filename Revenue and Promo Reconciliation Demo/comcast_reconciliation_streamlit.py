import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from snowflake.snowpark import Session
from datetime import datetime, timedelta
import warnings
import random
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
warnings.filterwarnings('ignore')

# Streamlit version compatibility
def st_rerun():
    """Compatible rerun function for different Streamlit versions"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            # For very old versions, just show a message
            st.warning("Please refresh the page manually to reload data.")

def check_streamlit_version():
    """Check Streamlit version and provide compatibility info"""
    try:
        import streamlit as st
        version = st.__version__
        major, minor, patch = version.split('.')[:3]
        
        if int(major) >= 1 and int(minor) >= 28:
            return "modern"  # st.rerun() available
        elif int(major) >= 1 and int(minor) >= 18:
            return "legacy"  # st.experimental_rerun() available
        else:
            return "old"     # Manual refresh required
    except:
        return "unknown"

def find_column(df, *keywords):
    """Find column by keywords (case insensitive)"""
    for col in df.columns:
        col_lower = col.lower()
        if all(keyword.lower() in col_lower for keyword in keywords):
            return col
    return None

def safe_filter(df, column, value, operator='=='):
    """Safely filter dataframe with column existence check"""
    if column and column in df.columns:
        if operator == '==':
            return df[df[column] == value]
        elif operator == '!=':
            return df[df[column] != value]
        elif operator == 'isin':
            return df[df[column].isin(value)]
    return df

# Page configuration
st.set_page_config(
    page_title="Comcast Promotion Reconciliation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b35;
    }
    .high-risk {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .medium-risk {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .low-risk {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .header-style {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_ml_model():
    """Load the trained ML model and scaler if available"""
    try:
        # Try to load the model and scaler from the notebook output
        model_path = '/tmp/isolation_forest_model.joblib'
        scaler_path = '/tmp/scaler.joblib'
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            st.success(f"✅ ML model loaded from {model_path}")
            return model, scaler
        else:
            # Check alternative locations
            alt_paths = [
                ('./isolation_forest_model.joblib', './scaler.joblib'),
                ('./models/isolation_forest_model.joblib', './models/scaler.joblib')
            ]
            
            for model_alt, scaler_alt in alt_paths:
                if os.path.exists(model_alt) and os.path.exists(scaler_alt):
                    model = joblib.load(model_alt)
                    scaler = joblib.load(scaler_alt)
                    st.success(f"✅ ML model loaded from {model_alt}")
                    return model, scaler
            
            st.info("ℹ️ ML model files not found. Using synthetic anomaly detection.")
    except Exception as e:
        st.warning(f"⚠️ ML model loading failed: {e}")
    return None, None

@st.cache_data
def load_anomaly_data():
    """Load anomaly detection results if available"""
    try:
        # Try to load from CSV first (fallback)
        if os.path.exists('comcast_revenue_reconciliation_dataset.csv'):
            df = pd.read_csv('comcast_revenue_reconciliation_dataset.csv')
            
            # Check if ML columns already exist, if not add synthetic ones
            if 'ml_anomaly_score' not in df.columns:
                np.random.seed(42)
                df['ml_anomaly_score'] = np.random.normal(-0.1, 0.3, len(df))
                df['ml_is_anomaly'] = df['ml_anomaly_score'] < -0.5
            
            if 'anomaly_score' not in df.columns:
                np.random.seed(42)
                df['anomaly_score'] = np.random.normal(-0.1, 0.3, len(df))
                df['is_anomaly'] = df['anomaly_score'] < -0.4
            
            return df
    except Exception as e:
        st.error(f"Could not load anomaly data: {e}")
    return None

def calculate_ml_features(df):
    """Calculate ML features from the reconciliation data"""
    if df is None or df.empty:
        return df
    
    # Create numerical features for ML scoring
    df = df.copy()
    
    # Handle different column naming conventions
    # Check for database column names (uppercase) vs CSV column names (lowercase)
    order_base_col = None
    billing_base_col = None
    order_discount_col = None
    billing_discount_col = None
    order_final_col = None
    billing_final_col = None
    
    # Find the correct column names
    for col in df.columns:
        col_lower = col.lower()
        if 'order' in col_lower and 'base' in col_lower and 'amount' in col_lower:
            order_base_col = col
        elif 'billing' in col_lower and 'base' in col_lower and 'amount' in col_lower:
            billing_base_col = col
        elif 'order' in col_lower and 'discount' in col_lower and 'amount' in col_lower:
            order_discount_col = col
        elif 'billing' in col_lower and 'discount' in col_lower and 'amount' in col_lower:
            billing_discount_col = col
        elif 'order' in col_lower and 'final' in col_lower and 'amount' in col_lower:
            order_final_col = col
        elif 'billing' in col_lower and 'final' in col_lower and 'amount' in col_lower:
            billing_final_col = col
    
    # Calculate features if columns exist
    if order_base_col and billing_base_col:
        df['base_variance'] = df[order_base_col] - df[billing_base_col]
    elif order_base_col:
        df['base_variance'] = 0  # Default if no billing comparison
    
    if order_discount_col and billing_discount_col:
        df['discount_variance'] = df[order_discount_col] - df[billing_discount_col]
    elif order_discount_col:
        df['discount_variance'] = 0
    
    if order_final_col and billing_final_col:
        df['final_variance'] = df[order_final_col] - df[billing_final_col]
    elif order_final_col:
        df['final_variance'] = 0
    
    if order_discount_col and order_base_col:
        df['discount_rate'] = df[order_discount_col] / (df[order_base_col] + 0.01)
    else:
        df['discount_rate'] = 0
    
    # Encode categorical features (handle different naming)
    status_col = None
    risk_col = None
    product_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'reconciliation' in col_lower and 'status' in col_lower:
            status_col = col
        elif 'risk' in col_lower and 'level' in col_lower:
            risk_col = col
        elif 'product' in col_lower and 'category' in col_lower:
            product_col = col
    
    if status_col:
        df['status_encoded'] = pd.Categorical(df[status_col]).codes
    if risk_col:
        df['risk_encoded'] = pd.Categorical(df[risk_col]).codes
    if product_col:
        df['product_encoded'] = pd.Categorical(df[product_col]).codes
    
    return df

def score_with_ml_model(df, model, scaler):
    """Score records with the trained ML model"""
    if model is None or scaler is None or df is None or df.empty:
        return df
    
    try:
        # Prepare features for scoring
        feature_cols = ['base_variance', 'discount_variance', 'final_variance', 'discount_rate', 
                       'status_encoded', 'risk_encoded', 'product_encoded']
        
        # Check if all features exist
        missing_features = [col for col in feature_cols if col not in df.columns]
        if missing_features:
            return df
        
        X = df[feature_cols].fillna(0).values
        X_scaled = scaler.transform(X)
        
        # Get anomaly scores and predictions
        anomaly_scores = model.decision_function(X_scaled)
        anomaly_predictions = model.predict(X_scaled)
        
        df['ml_anomaly_score'] = anomaly_scores
        df['ml_is_anomaly'] = anomaly_predictions == -1
        
    except Exception as e:
        st.warning(f"ML scoring failed: {e}")
    
    return df

@st.cache_resource
def init_snowflake_connection():
    """Initialize Snowflake connection"""
    try:
        # Method 1: Use active session (when running in Snowflake environment)
        try:
            from snowflake.snowpark.context import get_active_session
            session = get_active_session()
            st.sidebar.success("✅ Snowflake: Active Session")
            return session
        except:
            pass
        
        # Method 2: Manual connection (uncomment and configure)
        """
        connection_parameters = {
            "account": "your_account.snowflakecomputing.com",
            "user": "your_username",
            "password": "your_password",
            "role": "your_role",
            "warehouse": "your_warehouse",
            "database": "COMCAST_REVENUE",
            "schema": "ANALYTICS"
        }
        
        from snowflake.snowpark import Session
        session = Session.builder.configs(connection_parameters).create()
        st.sidebar.success("✅ Snowflake: Manual Connection")
        return session
        """
        
        st.sidebar.warning("⚠️ Configure Snowflake connection")
        return None
        
    except Exception as e:
        st.sidebar.error(f"❌ Snowflake error: {str(e)}")
        return None

def load_sample_data():
    """Load sample data for demonstration when Snowflake is not available"""
    
    # Generate sample reconciliation data
    np.random.seed(42)
    n_records = 500
    
    # Product categories
    products = [
        'Xfinity Internet 1 Gig', 'Xfinity Internet 200 Mbps', 'Xfinity TV Ultimate',
        'Xfinity TV Choice', 'Xfinity Mobile Unlimited', 'Xfinity Mobile By the Gig',
        'Xfinity Home Security', 'Business Internet Pro', 'Business Voice', 'Xfinity Stream'
    ]
    
    categories = ['Internet', 'Television', 'Mobile', 'Security', 'Business', 'Streaming']
    
    promos = [
        'New Customer 50% Off', 'Triple Play Bundle Discount', 'Loyalty Discount',
        'First Responder Discount', 'Student Discount', 'Free Mobile for 3 Months',
        'Business Starter Package', 'Free Streaming Trial', 'Home Security 50% Off',
        'Refer a Friend Bonus'
    ]
    
    # Comcast service areas (major cities with lat/lon)
    service_areas = [
        {'city': 'Philadelphia', 'state': 'PA', 'lat': 39.9526, 'lon': -75.1652, 'region': 'Northeast'},
        {'city': 'Chicago', 'state': 'IL', 'lat': 41.8781, 'lon': -87.6298, 'region': 'Midwest'},
        {'city': 'Washington', 'state': 'DC', 'lat': 38.9072, 'lon': -77.0369, 'region': 'Northeast'},
        {'city': 'San Francisco', 'state': 'CA', 'lat': 37.7749, 'lon': -122.4194, 'region': 'West'},
        {'city': 'Boston', 'state': 'MA', 'lat': 42.3601, 'lon': -71.0589, 'region': 'Northeast'},
        {'city': 'Denver', 'state': 'CO', 'lat': 39.7392, 'lon': -104.9903, 'region': 'West'},
        {'city': 'Atlanta', 'state': 'GA', 'lat': 33.7490, 'lon': -84.3880, 'region': 'Southeast'},
        {'city': 'Miami', 'state': 'FL', 'lat': 25.7617, 'lon': -80.1918, 'region': 'Southeast'},
        {'city': 'Seattle', 'state': 'WA', 'lat': 47.6062, 'lon': -122.3321, 'region': 'West'},
        {'city': 'Detroit', 'state': 'MI', 'lat': 42.3314, 'lon': -83.0458, 'region': 'Midwest'},
        {'city': 'Houston', 'state': 'TX', 'lat': 29.7604, 'lon': -95.3698, 'region': 'South'},
        {'city': 'New York', 'state': 'NY', 'lat': 40.7128, 'lon': -74.0060, 'region': 'Northeast'},
    ]
    
    # Generate realistic reconciliation data
    data = []
    for i in range(n_records):
        base_amount = np.random.uniform(15, 150)
        order_discount = np.random.uniform(0, base_amount * 0.5)
        
        # Assign service area
        service_area = np.random.choice(service_areas)
        
        # Add some geographic clustering around service centers
        lat_offset = np.random.normal(0, 0.1)  # ~11km standard deviation
        lon_offset = np.random.normal(0, 0.1)
        customer_lat = service_area['lat'] + lat_offset
        customer_lon = service_area['lon'] + lon_offset
        
        # Introduce reconciliation issues
        reconciliation_issue = np.random.choice([True, False], p=[0.15, 0.85])
        
        if reconciliation_issue:
            # Create billing discrepancy
            billing_discount = order_discount * np.random.uniform(0.7, 1.3)
            if np.random.random() < 0.1:  # 10% missing billing records
                billing_discount = None
                billing_amount = None
                status = 'ORDER_ONLY'
                risk = 'HIGH'
            else:
                billing_amount = base_amount
                if abs(order_discount - billing_discount) > 20:
                    status = 'DISCOUNT_MISMATCH'
                    risk = 'HIGH'
                elif abs(order_discount - billing_discount) > 5:
                    status = 'DISCOUNT_MISMATCH'
                    risk = 'MEDIUM'
                else:
                    status = 'DISCOUNT_MISMATCH'
                    risk = 'LOW'
        else:
            billing_discount = order_discount
            billing_amount = base_amount
            status = 'MATCHED'
            risk = 'LOW'
        
        variance = (order_discount or 0) - (billing_discount or 0)
        
        # Risk-based elevation for 3D visualization
        risk_elevation = {'HIGH': 300, 'MEDIUM': 150, 'LOW': 50}[risk]
        
        record = {
            'record_id': f'ORD-{i+1:06d}',
            'customer_id': f'CUST-{np.random.randint(100000, 999999)}',
            'transaction_date': (datetime.now() - timedelta(days=np.random.randint(1, 90))).date(),
            'product_name': np.random.choice(products),
            'product_category': np.random.choice(categories),
            'promo_name': np.random.choice(promos) if np.random.random() < 0.7 else None,
            'order_base_amount': base_amount,
            'order_discount_amount': order_discount,
            'order_final_amount': base_amount - order_discount,
            'billing_base_amount': billing_amount,
            'billing_discount_amount': billing_discount,
            'billing_final_amount': (billing_amount - billing_discount) if billing_amount and billing_discount else None,
            'discount_variance': variance,
            'final_amount_variance': variance,
            'reconciliation_status': status,
            'risk_level': risk,
            'service_city': service_area['city'],
            'service_state': service_area['state'],
            'service_region': service_area['region'],
            'customer_lat': customer_lat,
            'customer_lon': customer_lon,
            'risk_elevation': risk_elevation,
            'abs_variance': abs(variance)
        }
        data.append(record)
    
    return pd.DataFrame(data)

@st.cache_data
def load_reconciliation_data():
    """Load reconciliation data from Snowflake database"""
    
    session = init_snowflake_connection()
    if session:
        try:
            # First try the main reconciliation view with all ML features
            query = """
            SELECT * FROM COMCAST_REVENUE.ANALYTICS.PROMOTION_RECONCILIATION 
            ORDER BY TRANSACTION_DATE DESC
            """
            df = session.sql(query).to_pandas()
            st.sidebar.success("📊 Data: Snowflake PROMOTION_RECONCILIATION")
            return df
        except Exception as e1:
            try:
                # Try uploaded CSV table
                query = """
                SELECT * FROM COMCAST_REVENUE.ANALYTICS.RECONCILIATION_DATASET_CSV 
                ORDER BY TRANSACTION_DATE DESC
                """
                df = session.sql(query).to_pandas()
                st.sidebar.success("📊 Data: Snowflake CSV Table")
                return df
            except Exception as e2:
                st.error(f"Snowflake connection failed: {str(e1)}")
                st.error(f"CSV table access failed: {str(e2)}")
                st.info("Please ensure you have:")
                st.info("1. Run the SQL setup script (comcast_revenue_data_setup.sql)")
                st.info("2. Proper Snowflake connection credentials")
                return load_sample_data()
    else:
        st.error("No Snowflake connection available")
        st.info("Please configure Snowflake connection in init_snowflake_connection()")
        return load_sample_data()

@st.cache_data
def calculate_summary_stats(df):
    """Calculate summary statistics with dynamic column detection"""
    total_records = len(df)
    
    # Find column names dynamically
    status_col = None
    risk_col = None
    discount_variance_col = None
    amount_variance_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'reconciliation' in col_lower and 'status' in col_lower:
            status_col = col
        elif 'risk' in col_lower and 'level' in col_lower:
            risk_col = col
        elif 'discount' in col_lower and 'variance' in col_lower:
            discount_variance_col = col
        elif 'final' in col_lower and 'variance' in col_lower:
            amount_variance_col = col
    
    # Calculate stats based on available columns
    if status_col:
        matched = len(df[df[status_col] == 'MATCHED'])
        match_rate = (matched / total_records * 100) if total_records > 0 else 0
        exceptions = total_records - matched
    else:
        matched = 0
        match_rate = 0
        exceptions = total_records
    
    # Calculate variances
    total_discount_variance = df[discount_variance_col].abs().sum() if discount_variance_col else 0
    total_amount_variance = df[amount_variance_col].abs().sum() if amount_variance_col else 0
    
    # Risk breakdown
    if risk_col:
        high_risk = len(df[df[risk_col] == 'HIGH'])
        medium_risk = len(df[df[risk_col] == 'MEDIUM'])
        low_risk = len(df[df[risk_col] == 'LOW'])
    else:
        high_risk = 0
        medium_risk = 0
        low_risk = total_records
    
    return {
        'total_records': total_records,
        'matched_records': matched,
        'exception_records': exceptions,
        'match_rate_pct': match_rate,
        'total_discount_variance': total_discount_variance,
        'total_amount_variance': total_amount_variance,
        'high_risk_count': high_risk,
        'medium_risk_count': medium_risk,
        'low_risk_count': low_risk
    }

def main():
    # Header
    st.markdown("""
    <div class="header-style">
        <h1>🎯 Comcast Promotion Reconciliation Dashboard</h1>
        <p>Accelerate reconciliation resolution and maximize revenue recovery through intelligent automation & ML</p>
        <p><strong>Purpose:</strong> Automate discount reconciliation, detect anomalies with ML, measure business impact, and optimize operational efficiency</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard overview in collapsible section
    with st.expander("ℹ️ How to Use This Dashboard", expanded=False):
        st.markdown("""
        **This dashboard is organized into 7 key sections:**
        
        1. **🎛️ Control Center** - Set filters and view executive summary
        2. **⚠️ Risk Assessment** - Analyze exceptions and risk distribution  
        3. **🤖 ML Anomaly Detection** - Machine learning insights and model scoring
        4. **🗺️ Geographic Intelligence** - Understand regional patterns and performance
        5. **🔍 Investigation Center** - Drill down into specific transactions and promotions
        6. **🚀 Acceleration & Automation** - Automate resolution and measure business impact
        7. **📤 Reporting & Export** - Generate reports and export data
        
        **Color Coding:** 🔴 High Risk | 🟡 Medium Risk | 🟢 Low Risk
        
        **💡 Focus on Automation:** Use Section 5 to accelerate reconciliation and track ROI!
        """)
    
    # Load data and ML components
    with st.spinner("Loading reconciliation data and ML models..."):
        df = load_reconciliation_data()
        model, scaler = load_ml_model()
        
        # Enhanced data with ML features
        df = calculate_ml_features(df)
        df = score_with_ml_model(df, model, scaler)
        
        summary_stats = calculate_summary_stats(df)
    
    if df.empty:
        st.error("No data available to display")
        return

    # Add cache clear button in sidebar for debugging
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔧 Debug Tools**")
    if st.sidebar.button("🔄 Clear Cache & Reload Data"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st_rerun()
    
    # Show data source info
    st.sidebar.info(f"📊 Data Source: CSV with {len(df)} records")
    if 'ml_is_anomaly' in df.columns:
        ml_count = df['ml_is_anomaly'].sum()
        st.sidebar.success(f"🤖 ML Anomalies: {ml_count}")
    if 'is_anomaly' in df.columns:
        synthetic_count = df['is_anomaly'].sum()
        st.sidebar.info(f"📊 Synthetic Anomalies: {synthetic_count}")
    
    # Version compatibility info
    st_version = check_streamlit_version()
    if st_version == "modern":
        st.sidebar.success(f"✅ Streamlit: {st.__version__} (Modern)")
    elif st_version == "legacy":
        st.sidebar.warning(f"⚠️ Streamlit: {st.__version__} (Legacy)")
    else:
        st.sidebar.error(f"❌ Streamlit: {st.__version__} (Needs Update)")

    # =====================================================================================
    # SECTION 1: CONTROL CENTER - Filters + Executive Summary
    # =====================================================================================
    
    st.markdown("---")
    st.header("🎛️ Control Center")
    
    # Create two main columns for filters and summary
    filter_col, summary_col = st.columns([1, 2])
    
    with filter_col:
        st.subheader("📊 Filters & Controls")
        st.markdown("*Adjust filters to focus your analysis*")
        
        # Date range filter
        if not df.empty:
            # Find key columns dynamically
            date_col = None
            risk_col = None
            discount_variance_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if 'transaction' in col_lower and 'date' in col_lower:
                    date_col = col
                elif 'date' in col_lower and not date_col:
                    date_col = col
                elif 'risk' in col_lower and 'level' in col_lower:
                    risk_col = col
                elif 'discount' in col_lower and 'variance' in col_lower:
                    discount_variance_col = col
            
            if date_col:
                min_date = df[date_col].min()
                max_date = df[date_col].max()
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            else:
                st.info("No date column found for filtering")
                date_range = None
            
            # Risk level filter
            risk_levels = st.multiselect(
                "⚠️ Risk Levels",
                options=['HIGH', 'MEDIUM', 'LOW'],
                default=['HIGH', 'MEDIUM', 'LOW']
            )
            
            # Product category filter
            product_cat_col = None
            for col in df.columns:
                if 'product' in col.lower() and 'category' in col.lower():
                    product_cat_col = col
                    break
            
            if product_cat_col:
                categories = df[product_cat_col].unique()
                selected_categories = st.multiselect(
                    "📦 Product Categories",
                    options=categories,
                    default=categories
                )
            else:
                selected_categories = []
            
            # Geographic filters
            region_col = None
            for col in df.columns:
                if 'service' in col.lower() and 'region' in col.lower():
                    region_col = col
                    break
                elif 'region' in col.lower():
                    region_col = col
                    break
            
            if region_col:
                regions = df[region_col].unique()
                selected_regions = st.multiselect(
                    "🌎 Service Regions",
                    options=regions,
                    default=regions
                )
            else:
                selected_regions = []
            
            # Variance threshold
            variance_threshold = st.slider(
                "💰 Min Variance Threshold ($)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                help="Only show transactions with variance above this amount"
            )
            
            # Apply filters with dynamic column detection
            filter_conditions = []
            
            # Date filter
            if date_range and date_col:
                filter_conditions.extend([
                    (df[date_col] >= date_range[0]),
                    (df[date_col] <= date_range[1])
                ])
            
            # Risk level filter
            if risk_col:
                filter_conditions.append(df[risk_col].isin(risk_levels))
            
            # Product category filter  
            product_cat_col = None
            for col in df.columns:
                if 'product' in col.lower() and 'category' in col.lower():
                    product_cat_col = col
                    break
            if product_cat_col:
                filter_conditions.append(df[product_cat_col].isin(selected_categories))
            
            # Variance filter
            if discount_variance_col:
                filter_conditions.append(df[discount_variance_col].abs() >= variance_threshold)
            
            # Region filter
            if selected_regions and region_col:
                filter_conditions.append(df[region_col].isin(selected_regions))
            
            # Combine all filters
            combined_filter = filter_conditions[0]
            for condition in filter_conditions[1:]:
                combined_filter = combined_filter & condition
                
            filtered_df = df[combined_filter]
            
            # Filter summary
            st.info(f"📊 **{len(filtered_df):,}** of **{len(df):,}** records shown")
    
    with summary_col:
        st.subheader("📈 Executive Summary")
        st.markdown("*Key performance indicators for your current selection*")
        
        # KPI Metrics in 2x3 grid (added ML column)
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            # Find status column dynamically
            status_col = None
            for col in filtered_df.columns:
                if 'reconciliation' in col.lower() and 'status' in col.lower():
                    status_col = col
                    break
            
            if status_col:
                match_rate = (len(filtered_df[filtered_df[status_col] == 'MATCHED']) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                exceptions_count = len(filtered_df[filtered_df[status_col] != 'MATCHED'])
            else:
                match_rate = 0
                exceptions_count = len(filtered_df)
                
            st.metric(
                label="🎯 Match Rate",
                value=f"{match_rate:.1f}%",
                delta=f"{exceptions_count:,} exceptions",
                delta_color="inverse"
            )
            
            # Find risk column dynamically
            risk_col = None
            for col in filtered_df.columns:
                if 'risk' in col.lower() and 'level' in col.lower():
                    risk_col = col
                    break
            
            high_risk_count = len(filtered_df[filtered_df[risk_col] == 'HIGH']) if risk_col else 0
            st.metric(
                label="🚨 High Risk Items",
                value=f"{high_risk_count:,}",
                delta=f"{high_risk_count/len(filtered_df)*100:.1f}% of total" if len(filtered_df) > 0 else "0%",
                delta_color="inverse"
            )
        
        with kpi_col2:
            total_variance = filtered_df['discount_variance'].abs().sum()
            st.metric(
                label="💰 Total Variance",
                value=f"${total_variance:,.2f}",
                delta=f"${total_variance/len(filtered_df):.2f} avg per record" if len(filtered_df) > 0 else "$0"
            )
            
            avg_variance = filtered_df['discount_variance'].abs().mean()
            st.metric(
                label="📊 Average Variance",
                value=f"${avg_variance:.2f}" if not pd.isna(avg_variance) else "$0",
                delta=f"Max: ${filtered_df['discount_variance'].abs().max():.2f}" if len(filtered_df) > 0 else "Max: $0"
            )
        
        with kpi_col3:
            # ML Metrics
            if 'ml_is_anomaly' in filtered_df.columns:
                ml_anomalies = filtered_df['ml_is_anomaly'].sum()
                ml_anomaly_rate = (ml_anomalies / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.metric(
                    label="🤖 ML Anomalies",
                    value=f"{ml_anomalies:,}",
                    delta=f"{ml_anomaly_rate:.1f}% detection rate"
                )
            else:
                st.metric(
                    label="🤖 ML Anomalies",
                    value="N/A",
                    delta="Model not loaded"
                )
            
            if 'is_anomaly' in filtered_df.columns:
                synthetic_anomalies = filtered_df['is_anomaly'].sum()
                st.metric(
                    label="📊 Synthetic Anomalies",
                    value=f"{synthetic_anomalies:,}",
                    delta="Fallback detection"
                )
            else:
                st.metric(
                    label="📊 Synthetic Anomalies", 
                    value="N/A",
                    delta="No fallback data"
                )
        
        # Quick risk distribution chart
        if not filtered_df.empty:
            st.subheader("Risk Distribution")
            risk_col = find_column(filtered_df, 'risk', 'level')
            if risk_col:
                risk_counts = filtered_df[risk_col].value_counts()
            else:
                risk_counts = pd.Series()  # Empty series
            
            # Create colored metrics for risk levels
            risk_col1, risk_col2, risk_col3 = st.columns(3)
            
            with risk_col1:
                high_count = risk_counts.get('HIGH', 0)
                st.metric("🔴 High", f"{high_count:,}")
                
            with risk_col2:
                medium_count = risk_counts.get('MEDIUM', 0)
                st.metric("🟡 Medium", f"{medium_count:,}")
                
            with risk_col3:
                low_count = risk_counts.get('LOW', 0)
                st.metric("🟢 Low", f"{low_count:,}")

    # =====================================================================================
    # SECTION 2: RISK ASSESSMENT CENTER
    # =====================================================================================
    
    st.markdown("---")
    st.header("⚠️ Risk Assessment Center")
    st.markdown("*Analyze exceptions and prioritize remediation efforts*")
    
    # Create tabs for different risk views with Fabio's use cases
    risk_tab1, risk_tab2, risk_tab3, risk_tab4 = st.tabs(["📊 Risk Overview", "🚨 Critical Alerts", "📱 Mobile Line Issues", "📈 Trend Analysis"])
    
    with risk_tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Risk Level Breakdown")
            if not filtered_df.empty:
                risk_col = find_column(filtered_df, 'risk', 'level')
                if risk_col:
                    risk_counts = filtered_df[risk_col].value_counts()
                    st.bar_chart(risk_counts)
                else:
                    st.info("No risk level column found")
                
                # Interactive risk level selector
                st.markdown("**Click to filter by risk level:**")
                selected_risk_for_details = st.selectbox(
                    "Select risk level for detailed view:",
                    options=['ALL'] + list(risk_counts.index),
                    key="risk_selector"
                )
        
        with col2:
            st.subheader("Status Distribution")
            if not filtered_df.empty and status_col:
                status_counts = filtered_df[status_col].value_counts()
                st.bar_chart(status_counts)
            elif not filtered_df.empty:
                st.info("No status column found for distribution chart")
                
                # Show status definitions for Fabio's use cases
                st.markdown("**Status Definitions:**")
                st.markdown("• **MATCHED**: Perfect reconciliation")
                st.markdown("• **DISCOUNT_MISMATCH**: Different discount amounts")
                st.markdown("• **PROMO_TIMING_MISMATCH**: Promo applied to wrong billing cycle")
                st.markdown("• **DUPLICATE_LINE_NUMBER**: Same line number on multiple accounts")
                st.markdown("• **ORDER_ONLY**: Missing billing record")
    
    with risk_tab2:
        st.subheader("🚨 Critical Issues Requiring Immediate Action")
        
        # Filter for high-risk items (dynamic column)
        risk_col_dyn = find_column(filtered_df, 'risk', 'level')
        if risk_col_dyn:
            high_risk_df = filtered_df[filtered_df[risk_col_dyn] == 'HIGH'].sort_values('discount_variance', key=abs, ascending=False)
        else:
            high_risk_df = filtered_df.iloc[0:0]
        
        if not high_risk_df.empty:
            # Resolve dynamic columns for display
            id_col_dyn = find_column(high_risk_df, 'record', 'id') or find_column(high_risk_df, 'order', 'id')
            status_col_dyn = find_column(high_risk_df, 'reconciliation', 'status')
            disc_var_col_dyn = find_column(high_risk_df, 'discount', 'variance')

            # Show top 5 critical issues with expandable details
            st.markdown(f"**Showing top {min(5, len(high_risk_df))} critical issues:**")
            
            for idx, (_, row) in enumerate(high_risk_df.head(5).iterrows()):
                rec_id = str(row[id_col_dyn]) if id_col_dyn and id_col_dyn in row.index else str(idx)
                variance_val = float(row[disc_var_col_dyn]) if disc_var_col_dyn and disc_var_col_dyn in row.index else 0.0
                status_val = str(row[status_col_dyn]) if status_col_dyn and status_col_dyn in row.index else 'UNKNOWN'

                with st.expander(f"🔴 **#{idx+1}** - {rec_id} | ${variance_val:.2f} variance | {status_val}"):
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    
                    with detail_col1:
                        st.markdown("**Order System:**")
                        oba = find_column(high_risk_df, 'order', 'base', 'amount')
                        oda = find_column(high_risk_df, 'order', 'discount', 'amount')
                        ofa = find_column(high_risk_df, 'order', 'final', 'amount')
                        if oba and oba in row.index:
                            st.write(f"Base: ${row[oba]:.2f}")
                        if oda and oda in row.index:
                            st.write(f"Discount: ${row[oda]:.2f}")
                        if ofa and ofa in row.index:
                            st.write(f"Final: ${row[ofa]:.2f}")
                    
                    with detail_col2:
                        st.markdown("**Billing System:**")
                        bba = find_column(high_risk_df, 'billing', 'base', 'amount')
                        bda = find_column(high_risk_df, 'billing', 'discount', 'amount')
                        bfa = find_column(high_risk_df, 'billing', 'final', 'amount')
                        if bba and bba in row.index and pd.notna(row[bba]):
                            st.write(f"Base: ${row[bba]:.2f}")
                            if bda and bda in row.index:
                                st.write(f"Discount: ${row[bda]:.2f}")
                            if bfa and bfa in row.index:
                                st.write(f"Final: ${row[bfa]:.2f}")
                        else:
                            st.error("❌ No billing record found")
                    
                    with detail_col3:
                        st.markdown("**Transaction Details:**")
                        cust_col = find_column(high_risk_df, 'customer', 'id')
                        prod_col = find_column(high_risk_df, 'product', 'name') or find_column(high_risk_df, 'product', 'id')
                        date_col_dyn = find_column(high_risk_df, 'transaction', 'date') or find_column(high_risk_df, 'date')
                        city_col = find_column(high_risk_df, 'service', 'city') or find_column(high_risk_df, 'city')
                        state_col = find_column(high_risk_df, 'service', 'state') or find_column(high_risk_df, 'state')
                        if cust_col and cust_col in row.index:
                            st.write(f"Customer: {row[cust_col]}")
                        if prod_col and prod_col in row.index:
                            st.write(f"Product: {row[prod_col]}")
                        if date_col_dyn and date_col_dyn in row.index:
                            st.write(f"Date: {row[date_col_dyn]}")
                        city_val = row[city_col] if city_col and city_col in row.index else 'Unknown'
                        state_val = row[state_col] if state_col and state_col in row.index else 'Unknown'
                        st.write(f"Location: {city_val}, {state_val}")
        else:
            st.success("✅ No high-risk issues found with current filters!")
    
    with risk_tab3:
        st.subheader("📱 Mobile Line & Promo Timing Issues")
        st.markdown("*Fabio's priority use cases: duplicate lines and promo timing*")
        
        # Filter for mobile-specific issues (dynamic columns)
        status_col_m = find_column(filtered_df, 'reconciliation', 'status')
        product_cat_col_m = find_column(filtered_df, 'product', 'category')
        mobile_issues = filtered_df
        if status_col_m:
            mobile_issues = mobile_issues[mobile_issues[status_col_m].isin(['DUPLICATE_LINE_NUMBER', 'PROMO_TIMING_MISMATCH']) | (mobile_issues[status_col_m] == 'PROMO_TIMING_MISMATCH')]
        if product_cat_col_m:
            mobile_issues = mobile_issues[(mobile_issues[product_cat_col_m] == 'Mobile') | (mobile_issues.index >= 0)]
        
        if not mobile_issues.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔴 Duplicate Line Numbers**")
                status_col_m2 = find_column(mobile_issues, 'reconciliation', 'status')
                duplicate_lines = mobile_issues[mobile_issues[status_col_m2] == 'DUPLICATE_LINE_NUMBER'] if status_col_m2 else mobile_issues.iloc[0:0]
                if not duplicate_lines.empty:
                    st.error(f"{len(duplicate_lines)} duplicate line issues found")
                    for idx, (_, row) in enumerate(duplicate_lines.head(5).iterrows()):
                        cust_col_m = find_column(duplicate_lines, 'customer', 'id')
                        cust_val = row[cust_col_m] if cust_col_m and cust_col_m in row.index else 'N/A'
                        with st.expander(f"Line: {row.get('line_number', 'N/A')} - {cust_val}"):
                            st.write(f"**Product:** {row['product_name']}")
                            st.write(f"**Account:** {row.get('account_id', 'N/A')}")
                            st.write(f"**Variance:** ${row['discount_variance']:.2f}")
                            st.write(f"**City:** {row.get('service_city', 'Unknown')}")
                else:
                    st.success("✅ No duplicate line issues found")
            
            with col2:
                st.markdown("**⏰ Promo Timing Issues**")
                timing_issues = mobile_issues[mobile_issues[status_col_m2] == 'PROMO_TIMING_MISMATCH'] if status_col_m2 else mobile_issues.iloc[0:0]
                if not timing_issues.empty:
                    st.warning(f"{len(timing_issues)} promo timing issues")
                    for idx, (_, row) in enumerate(timing_issues.head(5).iterrows()):
                        cust_col_t = find_column(timing_issues, 'customer', 'id')
                        cust_val_t = row[cust_col_t] if cust_col_t and cust_col_t in row.index else 'N/A'
                        with st.expander(f"Promo: {row.get('promo_name', 'N/A')} - {cust_val_t}"):
                            st.write(f"**Product:** {row['product_name']}")
                            st.write(f"**Expected Cycle:** 1")
                            st.write(f"**Applied Cycle:** {row.get('billing_cycle_number', 'Unknown')}")
                            st.write(f"**Impact:** First bill accuracy affected")
                else:
                    st.success("✅ No promo timing issues found")
        else:
            st.info("No mobile-related issues found with current filters")
    
    with risk_tab4:
        st.subheader("📈 Risk Trends Over Time")
        
        if not filtered_df.empty and len(filtered_df) > 1:
            # Daily risk trends
            daily_trends = filtered_df.groupby(['transaction_date', 'risk_level']).size().unstack(fill_value=0)
            
            if not daily_trends.empty:
                st.line_chart(daily_trends)
                
                # Variance trends
                st.subheader("💰 Variance Trends")
                daily_variance = filtered_df.groupby('transaction_date')['discount_variance'].agg(['sum', 'mean', 'count'])
                
                trend_col1, trend_col2 = st.columns(2)
                with trend_col1:
                    st.markdown("**Total Daily Variance**")
                    st.line_chart(daily_variance['sum'])
                    
                with trend_col2:
                    st.markdown("**Average Daily Variance**")
                    st.line_chart(daily_variance['mean'])
        else:
            st.info("📊 Insufficient data for trend analysis with current filters")

    # =====================================================================================
    # SECTION 3: ML ANOMALY DETECTION CENTER
    # =====================================================================================
    
    st.markdown("---")
    st.header("🤖 ML Anomaly Detection Center")
    st.markdown("*Machine learning insights and intelligent anomaly detection*")
    
    # ML Model Status
    ml_status_col1, ml_status_col2, ml_status_col3 = st.columns(3)
    
    with ml_status_col1:
        if model is not None:
            st.success("🤖 ML Model: Loaded")
        else:
            st.warning("🤖 ML Model: Using Fallback")
    
    with ml_status_col2:
        if 'ml_is_anomaly' in df.columns:
            anomaly_count = int(df['ml_is_anomaly'].sum())
            st.metric("ML Anomalies Detected", anomaly_count)
        else:
            st.metric("ML Anomalies Detected", "N/A")
    
    with ml_status_col3:
        if 'is_anomaly' in df.columns:
            fallback_anomalies = int(df['is_anomaly'].sum())
            st.metric("Synthetic Anomalies", fallback_anomalies)
        else:
            st.metric("Synthetic Anomalies", "N/A")
    
    # ML Analysis Tabs
    ml_tab1, ml_tab2, ml_tab3, ml_tab4 = st.tabs(["📊 Anomaly Overview", "🎯 Model Insights", "📈 Scoring Distribution", "🔬 Feature Analysis"])
    
    with ml_tab1:
        st.subheader("📊 Anomaly Detection Overview")
        
        # Anomaly detection results
        if 'ml_is_anomaly' in df.columns or 'is_anomaly' in df.columns:
            ml_col1, ml_col2 = st.columns(2)
            
            with ml_col1:
                st.markdown("**🎯 ML-Detected Anomalies by Status**")
                if 'ml_is_anomaly' in df.columns:
                    ml_anomalies = df[df['ml_is_anomaly'] == True]
                    if not ml_anomalies.empty:
                        ml_anomaly_status = ml_anomalies['reconciliation_status'].value_counts()
                        fig_ml = px.bar(
                            x=ml_anomaly_status.values, 
                            y=ml_anomaly_status.index,
                            orientation='h',
                            title="ML Anomalies by Status",
                            color=ml_anomaly_status.values,
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig_ml, use_container_width=True)
                    else:
                        st.info("No ML anomalies detected")
                else:
                    st.info("ML anomaly detection not available")
            
            with ml_col2:
                st.markdown("**📊 Risk vs ML Anomaly Correlation**")
                if 'ml_is_anomaly' in df.columns:
                    correlation_data = df.groupby(['risk_level', 'ml_is_anomaly']).size().unstack(fill_value=0)
                    if not correlation_data.empty:
                        fig_corr = px.imshow(
                            correlation_data.values,
                            x=['Normal', 'Anomaly'],
                            y=correlation_data.index,
                            color_continuous_scale='RdYlBu_r',
                            title="Risk Level vs ML Anomaly Detection"
                        )
                        st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.info("Correlation analysis not available")
        else:
            st.error("No anomaly detection data found. Please check data loading.")
    
    with ml_tab2:
        st.subheader("🎯 Model Performance Insights")
        
        if 'ml_anomaly_score' in df.columns:
            # Model performance metrics
            ml_metrics_col1, ml_metrics_col2, ml_metrics_col3 = st.columns(3)
            
            with ml_metrics_col1:
                avg_score = df['ml_anomaly_score'].mean()
                st.metric("Average Anomaly Score", f"{avg_score:.3f}")
            
            with ml_metrics_col2:
                score_std = df['ml_anomaly_score'].std()
                st.metric("Score Standard Deviation", f"{score_std:.3f}")
            
            with ml_metrics_col3:
                anomaly_rate = (df['ml_is_anomaly'].sum() / len(df)) * 100
                st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
            
            # Top anomalies table
            st.markdown("**🚨 Top ML-Detected Anomalies**")
            if 'ml_is_anomaly' in df.columns:
                top_anomalies = df[df['ml_is_anomaly'] == True].nsmallest(10, 'ml_anomaly_score')[
                    ['record_id', 'reconciliation_status', 'risk_level', 'product_category', 'ml_anomaly_score', 'discount_variance']
                ]
                if not top_anomalies.empty:
                    st.dataframe(top_anomalies, use_container_width=True)
                else:
                    st.info("No anomalies detected by ML model")
        else:
            st.info("ML model results not available. Please run the anomaly detection notebook.")
    
    with ml_tab3:
        st.subheader("📈 Anomaly Score Distribution")
        
        if 'ml_anomaly_score' in df.columns:
            # Score distribution histogram
            fig_dist = px.histogram(
                df, 
                x='ml_anomaly_score', 
                color='ml_is_anomaly',
                title="Distribution of ML Anomaly Scores",
                labels={'ml_anomaly_score': 'Anomaly Score', 'count': 'Frequency'},
                nbins=50
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Score vs variance scatter
            if 'discount_variance' in df.columns:
                fig_scatter = px.scatter(
                    df.sample(min(1000, len(df))),  # Sample for performance
                    x='ml_anomaly_score',
                    y='discount_variance',
                    color='risk_level',
                    hover_data=['reconciliation_status', 'product_category'],
                    title="Anomaly Score vs Discount Variance"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Anomaly scores not available")
    
    with ml_tab4:
        st.subheader("🔬 Feature Importance & Analysis")
        
        if model is not None and hasattr(model, 'estimators_'):
            st.markdown("**🎯 Model Information**")
            ml_info_col1, ml_info_col2 = st.columns(2)
            
            with ml_info_col1:
                st.info(f"Model Type: Isolation Forest")
                st.info(f"Estimators: {getattr(model, 'n_estimators', 'N/A')}")
            
            with ml_info_col2:
                st.info(f"Contamination: {getattr(model, 'contamination', 'N/A')}")
                st.info(f"Max Features: {getattr(model, 'max_features', 'N/A')}")
        
        # Feature distribution for anomalies vs normal
        if 'ml_is_anomaly' in df.columns:
            st.markdown("**📊 Feature Distributions: Normal vs Anomalous**")
            
            feature_cols = ['discount_variance', 'base_variance', 'final_variance', 'discount_rate']
            available_features = [col for col in feature_cols if col in df.columns]
            
            if available_features:
                selected_feature = st.selectbox("Select Feature to Analyze", available_features)
                
                # Box plot comparing normal vs anomalous
                fig_box = px.box(
                    df, 
                    x='ml_is_anomaly', 
                    y=selected_feature,
                    color='ml_is_anomaly',
                    title=f"{selected_feature.replace('_', ' ').title()} Distribution: Normal vs Anomalous"
                )
                st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Feature analysis requires ML model results")
    
    # =====================================================================================
    # SECTION 4: GEOGRAPHIC INTELLIGENCE CENTER  
    # =====================================================================================
    
    st.markdown("---")
    st.header("🗺️ Geographic Intelligence Center")
    st.markdown("*Understand regional patterns and identify geographic hotspots*")
    
    if not filtered_df.empty and 'customer_lat' in filtered_df.columns:
        geo_tab1, geo_tab2 = st.tabs(["🗺️ Interactive Map", "📊 Regional Analysis"])
        
        with geo_tab1:
            # Prepare map data
            map_data = filtered_df.dropna(subset=['customer_lat', 'customer_lon'])
            
            if not map_data.empty:
                # Map controls
                map_col1, map_col2 = st.columns([3, 1])
                
                with map_col2:
                    st.markdown("**Map Options:**")
                    show_variance_size = st.checkbox("Size by Variance", value=True)
                    max_points = st.slider("Max Points to Show", 100, 1000, 500, help="Limit points for performance")
                    
                    # Sample data if too many points
                    if len(map_data) > max_points:
                        map_display_data = map_data.sample(max_points)
                        st.info(f"Showing {max_points:,} of {len(map_data):,} points")
                    else:
                        map_display_data = map_data.copy()
                    
                    # Risk level legend
                    st.markdown("**Legend:**")
                    risk_col_map = find_column(map_display_data, 'risk', 'level')
                    risk_counts = map_display_data[risk_col_map].value_counts() if risk_col_map else pd.Series()
                    for risk_level in ['HIGH', 'MEDIUM', 'LOW']:
                        if risk_level in risk_counts.index:
                            count = risk_counts[risk_level]
                            emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}[risk_level]
                            st.markdown(f"{emoji} **{risk_level}**: {count:,}")
                
                with map_col1:
                    # Prepare map visualization
                    map_display_data['size'] = map_display_data['abs_variance'] * 100 if show_variance_size else 50
                    
                    # Create color mapping
                    color_mapping = {
                        'HIGH': '#DC143C',     # Crimson red
                        'MEDIUM': '#FF8C00',   # Dark orange  
                        'LOW': '#32CD32'       # Lime green
                    }
                    if risk_col_map:
                        map_display_data['color'] = map_display_data[risk_col_map].map(color_mapping)
                    
                    # Display map
                    st.map(
                        data=map_display_data,
                        latitude='customer_lat',
                        longitude='customer_lon',
                        size='size' if show_variance_size else None,
                        color='color'
                    )
            else:
                st.warning("No geographic data available for current selection.")
        
        with geo_tab2:
            st.subheader("📊 Regional Performance Metrics")
            
            if 'service_region' in filtered_df.columns:
                # Regional summary table
                regional_summary = filtered_df.groupby('service_region').agg({
                    'discount_variance': ['sum', 'mean', 'count'],
                    'risk_level': lambda x: (x == 'HIGH').sum()
                }).round(2)
                
                regional_summary.columns = ['Total_Variance', 'Avg_Variance', 'Record_Count', 'High_Risk_Count']
                regional_summary['Risk_Rate'] = (regional_summary['High_Risk_Count'] / regional_summary['Record_Count'] * 100).round(1)
                
                # Make it interactive
                st.markdown("**Click on a region to see city details:**")
                selected_region = st.selectbox(
                    "Select region for detailed analysis:",
                    options=['ALL REGIONS'] + list(regional_summary.index),
                    key="region_selector"
                )
                
                # Show regional data
                st.dataframe(
                    regional_summary,
                    column_config={
                        "Total_Variance": st.column_config.NumberColumn("Total Variance", format="$%.2f"),
                        "Avg_Variance": st.column_config.NumberColumn("Avg Variance", format="$%.2f"),
                        "Risk_Rate": st.column_config.NumberColumn("Risk Rate", format="%.1f%%")
                    }
                )
                
                # City-level details for selected region
                if selected_region != 'ALL REGIONS':
                    st.subheader(f"🏙️ Cities in {selected_region}")
                    
                    region_cities = filtered_df[filtered_df['service_region'] == selected_region]
                    city_summary = region_cities.groupby('service_city').agg({
                        'discount_variance': 'sum',
                        'record_id': 'count',
                        'risk_level': lambda x: (x == 'HIGH').sum()
                    }).round(2)
                    city_summary.columns = ['Total_Variance', 'Record_Count', 'High_Risk_Count']
                    city_summary = city_summary.sort_values('Total_Variance', key=abs, ascending=False)
                    
                    st.dataframe(city_summary)

    # =====================================================================================
    # SECTION 5: INVESTIGATION CENTER
    # =====================================================================================
    
    st.markdown("---")
    st.header("🔍 Investigation Center")
    st.markdown("*Drill down into specific transactions and promotion performance*")
    
    investigation_tab1, investigation_tab2, investigation_tab3 = st.tabs(["🎁 Promotion Analysis", "📋 Transaction Details", "🔍 Custom Search"])
    
    with investigation_tab1:
        st.subheader("🎁 Promotion Performance Analysis")
        
        # Promotion analysis
        promo_data = filtered_df[filtered_df['promo_name'].notna()]
        
        if not promo_data.empty:
            promo_analysis = promo_data.groupby('promo_name').agg({
                'record_id': 'count',
                'discount_variance': ['sum', 'mean', 'std'],
                'reconciliation_status': lambda x: (x != 'MATCHED').sum()
            }).round(2)
            
            promo_analysis.columns = ['Total_Count', 'Total_Variance', 'Avg_Variance', 'Std_Variance', 'Exception_Count']
            promo_analysis['Exception_Rate'] = (promo_analysis['Exception_Count'] / promo_analysis['Total_Count'] * 100).round(1)
            promo_analysis = promo_analysis.sort_values('Exception_Rate', ascending=False)
            
            # Interactive promotion selector
            selected_promo = st.selectbox(
                "Select promotion for detailed analysis:",
                options=['ALL PROMOTIONS'] + list(promo_analysis.index),
                key="promo_selector"
            )
            
            # Show promotion performance table
            st.dataframe(
                promo_analysis,
                use_container_width=True,
                column_config={
                    "Total_Variance": st.column_config.NumberColumn("Total Variance", format="$%.2f"),
                    "Avg_Variance": st.column_config.NumberColumn("Avg Variance", format="$%.2f"),
                    "Std_Variance": st.column_config.NumberColumn("Std Variance", format="$%.2f"),
                    "Exception_Rate": st.column_config.NumberColumn("Exception Rate", format="%.1f%%")
                }
            )
            
            # Details for selected promotion
            if selected_promo != 'ALL PROMOTIONS':
                st.subheader(f"📊 Details for: {selected_promo}")
                promo_details = promo_data[promo_data['promo_name'] == selected_promo]
                
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.metric("Total Transactions", f"{len(promo_details):,}")
                    st.metric("Exception Rate", f"{(promo_details['reconciliation_status'] != 'MATCHED').mean()*100:.1f}%")
                
                with detail_col2:
                    st.metric("Total Variance", f"${promo_details['discount_variance'].abs().sum():,.2f}")
                    st.metric("Avg Variance", f"${promo_details['discount_variance'].abs().mean():.2f}")
        else:
            st.info("No promotion data available with current filters")
    
    with investigation_tab2:
        st.subheader("📋 Detailed Transaction Records")
        st.markdown("*Complete transaction-level data with interactive filtering*")
        
        # Additional filters for transaction table
        table_col1, table_col2, table_col3 = st.columns(3)
        
        with table_col1:
            sort_by = st.selectbox(
                "Sort by:",
                options=['discount_variance', 'transaction_date', 'customer_id', 'order_final_amount'],
                index=0
            )
        
        with table_col2:
            sort_order = st.selectbox("Order:", options=['Descending', 'Ascending'])
            ascending = sort_order == 'Ascending'
        
        with table_col3:
            max_rows = st.selectbox("Rows to show:", options=[50, 100, 200, 500], index=1)
        
        # Display transaction table
        display_df = filtered_df.sort_values(sort_by, key=abs if 'variance' in sort_by else None, ascending=ascending).head(max_rows)
        
        st.dataframe(
            display_df[[
                'record_id', 'customer_id', 'transaction_date', 'product_name', 
                'promo_name', 'order_discount_amount', 'billing_discount_amount',
                'discount_variance', 'reconciliation_status', 'risk_level'
            ]],
            use_container_width=True,
            column_config={
                "order_discount_amount": st.column_config.NumberColumn("Order Discount", format="$%.2f"),
                "billing_discount_amount": st.column_config.NumberColumn("Billing Discount", format="$%.2f"),
                "discount_variance": st.column_config.NumberColumn("Variance", format="$%.2f"),
                "reconciliation_status": st.column_config.SelectboxColumn("Status"),
                "risk_level": st.column_config.SelectboxColumn("Risk")
            }
        )
    
    with investigation_tab3:
        st.subheader("🔍 Custom Search & Analysis")
        
        # Custom search functionality
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            st.markdown("**Search by Customer ID:**")
            customer_search = st.text_input("Enter Customer ID:", placeholder="CUST-123456")
            
            if customer_search:
                cust_col_search = find_column(filtered_df, 'customer', 'id')
                customer_results = filtered_df[filtered_df[cust_col_search].astype(str).str.contains(customer_search, case=False, na=False)] if cust_col_search else filtered_df.iloc[0:0]
                if not customer_results.empty:
                    st.success(f"Found {len(customer_results)} transactions for customer: {customer_search}")
                    rec_id_col = find_column(customer_results, 'record', 'id') or find_column(customer_results, 'order', 'id')
                    date_col_c = find_column(customer_results, 'transaction', 'date') or find_column(customer_results, 'date')
                    prod_col_c = find_column(customer_results, 'product', 'name') or find_column(customer_results, 'product', 'id')
                    risk_col_c = find_column(customer_results, 'risk', 'level')
                    display_cols = [c for c in [rec_id_col, date_col_c, prod_col_c, 'discount_variance', risk_col_c] if c]
                    st.dataframe(customer_results[display_cols])
                else:
                    st.warning("No transactions found for this customer ID")
        
        with search_col2:
            st.markdown("**Search by Product:**")
            product_search = st.text_input("Enter Product Name:", placeholder="Xfinity Internet")
            
            if product_search:
                product_results = filtered_df[filtered_df['product_name'].str.contains(product_search, case=False, na=False)]
                if not product_results.empty:
                    st.success(f"Found {len(product_results)} transactions for product: {product_search}")
                    # Show summary stats for this product
                    avg_variance = product_results['discount_variance'].abs().mean()
                    risk_col_prod = find_column(product_results, 'risk', 'level')
                    high_risk_pct = ((product_results[risk_col_prod] == 'HIGH').mean() * 100) if risk_col_prod else 0
                    st.metric("Average Variance", f"${avg_variance:.2f}")
                    st.metric("High Risk Rate", f"{high_risk_pct:.1f}%")
                else:
                    st.warning("No transactions found for this product")

    # =====================================================================================
    # SECTION 6: ACCELERATION & AUTOMATION CENTER
    # =====================================================================================
    
    st.markdown("---")
    st.header("🚀 Acceleration & Automation Center")
    st.markdown("*Accelerate reconciliation and measure business impact*")
    
    acceleration_tab1, acceleration_tab2, acceleration_tab3 = st.tabs(["⚡ Auto-Resolution", "📊 Operational Impact", "💰 Revenue Impact"])
    
    with acceleration_tab1:
        st.subheader("⚡ Automated Resolution Suggestions")
        
        # Calculate auto-resolvable items
        risk_col_auto = find_column(filtered_df, 'risk', 'level')
        status_col_auto = find_column(filtered_df, 'reconciliation', 'status')
        auto_resolvable = filtered_df
        if risk_col_auto:
            auto_resolvable = auto_resolvable[auto_resolvable[risk_col_auto].isin(['LOW', 'MEDIUM'])]
        if 'discount_variance' in auto_resolvable.columns:
            auto_resolvable = auto_resolvable[auto_resolvable['discount_variance'].abs() <= 10]
        if status_col_auto:
            auto_resolvable = auto_resolvable[auto_resolvable[status_col_auto] == 'DISCOUNT_MISMATCH']
        
        bulk_col1, bulk_col2 = st.columns([2, 1])
        
        with bulk_col1:
            if not auto_resolvable.empty:
                st.success(f"🎯 **{len(auto_resolvable):,} transactions** can be auto-resolved (variances ≤ $10)")
                
                # Show auto-resolution queue
                st.markdown("**Auto-Resolution Queue:**")
                resolution_preview = auto_resolvable.groupby('reconciliation_status').agg({
                    'record_id': 'count',
                    'discount_variance': ['sum', 'mean']
                }).round(2)
                
                resolution_preview.columns = ['Count', 'Total_Variance', 'Avg_Variance']
                st.dataframe(resolution_preview)
                
                # Bulk action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔧 Auto-Adjust Billing", use_container_width=True):
                        st.success(f"✅ Queued {len(auto_resolvable):,} items for automatic billing adjustment")
                        st.info("💡 Estimated completion: 2-4 hours")
                
                with col2:
                    if st.button("📧 Notify Customers", use_container_width=True):
                        cust_col_auto = find_column(auto_resolvable, 'customer', 'id')
                        customer_count = auto_resolvable[cust_col_auto].nunique() if cust_col_auto else 0
                        st.success(f"✅ Notifications sent to {customer_count:,} customers")
                        st.info("💡 Estimated delivery: 15-30 minutes")
                
                with col3:
                    if st.button("📊 Generate Adjustments", use_container_width=True):
                        total_adjustment = auto_resolvable['discount_variance'].abs().sum()
                        st.success(f"✅ Generated ${total_adjustment:,.2f} in credit adjustments")
                        st.info("💡 Credits applied within 24 hours")
                
            else:
                st.info("🔍 No items currently qualify for auto-resolution")
                st.markdown("**Auto-resolution criteria:** Low/Medium risk + variance ≤ $10")
        
        with bulk_col2:
            st.markdown("**Automation Settings:**")
            
            auto_threshold = st.slider(
                "Auto-resolve threshold ($)",
                min_value=1.0,
                max_value=25.0,
                value=10.0,
                step=1.0
            )
            
            auto_notify = st.checkbox("Auto-notify customers", value=True)
            auto_credit = st.checkbox("Auto-apply credits", value=False)
            
            if st.button("🔄 Recalculate Queue"):
                new_auto_resolvable = filtered_df
                if risk_col_auto:
                    new_auto_resolvable = new_auto_resolvable[new_auto_resolvable[risk_col_auto].isin(['LOW', 'MEDIUM'])]
                if 'discount_variance' in new_auto_resolvable.columns:
                    new_auto_resolvable = new_auto_resolvable[new_auto_resolvable['discount_variance'].abs() <= auto_threshold]
                if status_col_auto:
                    new_auto_resolvable = new_auto_resolvable[new_auto_resolvable[status_col_auto] == 'DISCOUNT_MISMATCH']
                st.info(f"📊 {len(new_auto_resolvable):,} items qualify with ${auto_threshold} threshold")
        
        # High-priority manual review queue
        st.subheader("🚨 Priority Manual Review Queue")
        
        status_col_manual = status_col_auto
        risk_col_manual = risk_col_auto
        manual_review = filtered_df
        if risk_col_manual:
            manual_review = manual_review[(manual_review[risk_col_manual] == 'HIGH') | (manual_review['discount_variance'].abs() > 50)]
        else:
            manual_review = manual_review[manual_review['discount_variance'].abs() > 50]
        if status_col_manual:
            manual_review = manual_review[(manual_review[status_col_manual] == 'ORDER_ONLY') | (manual_review.index >= 0)]
        manual_review = manual_review.sort_values('discount_variance', key=abs, ascending=False)
        
        if not manual_review.empty:
            st.warning(f"⚠️ **{len(manual_review):,} high-priority items** require manual review")
            
            # Show top 10 for immediate action
            priority_items = manual_review.head(10)
            
            for idx, (_, row) in enumerate(priority_items.iterrows()):
                priority_col1, priority_col2, priority_col3, priority_col4 = st.columns([2, 1, 1, 1])
                
                with priority_col1:
                    rec_id_p = find_column(priority_queue, 'record', 'id') or find_column(priority_queue, 'order', 'id')
                    prod_col_p = find_column(priority_queue, 'product', 'name') or find_column(priority_queue, 'product', 'id')
                    cust_col_p = find_column(priority_queue, 'customer', 'id')
                    rec_val_p = row[rec_id_p] if rec_id_p in row.index else idx+1
                    prod_val_p = row[prod_col_p] if prod_col_p in row.index else 'N/A'
                    cust_val_p = row[cust_col_p] if cust_col_p in row.index else 'N/A'
                    st.markdown(f"**#{idx+1}** {rec_val_p} | ${row['discount_variance']:,.2f}")
                    st.caption(f"{cust_val_p} | {prod_val_p}")
                
                with priority_col2:
                    if st.button(f"🔍 Investigate", key=f"investigate_{idx}"):
                        st.info(f"🔍 Opening investigation for {row['record_id']}")
                
                with priority_col3:
                    if st.button(f"📧 Escalate", key=f"escalate_{idx}"):
                        st.info(f"📧 Escalated to supervisor")
                
                with priority_col4:
                    if st.button(f"✅ Resolve", key=f"resolve_{idx}"):
                        st.success(f"✅ Marked as resolved")
        else:
            st.success("🎉 No high-priority items requiring manual review!")
    
    with acceleration_tab2:
        st.subheader("📊 Operational Performance Metrics")
        
        # Simulate historical data for operational tracking
        dates = pd.date_range(start=filtered_df['transaction_date'].min(), end=filtered_df['transaction_date'].max(), freq='D')
        
        # Generate operational metrics
        ops_data = []
        for date in dates:
            ops_data.append({
                'date': date,
                'total_issues': random.randint(50, 200),
                'auto_resolved': random.randint(20, 100),
                'manual_resolved': random.randint(10, 50),
                'avg_resolution_time': random.uniform(2, 24),  # hours
                'customer_satisfaction': random.uniform(3.5, 5.0),
                'team_productivity': random.uniform(0.6, 0.95)
            })
        
        ops_df = pd.DataFrame(ops_data)
        ops_df['automation_rate'] = (ops_df['auto_resolved'] / ops_df['total_issues'] * 100).round(1)
        ops_df['resolution_rate'] = ((ops_df['auto_resolved'] + ops_df['manual_resolved']) / ops_df['total_issues'] * 100).round(1)
        
        # Key operational metrics
        ops_col1, ops_col2, ops_col3, ops_col4 = st.columns(4)
        
        with ops_col1:
            current_automation = ops_df['automation_rate'].iloc[-1]
            prev_automation = ops_df['automation_rate'].iloc[-7] if len(ops_df) > 7 else current_automation
            st.metric(
                "🤖 Automation Rate", 
                f"{current_automation:.1f}%",
                f"{current_automation - prev_automation:+.1f}% vs last week"
            )
        
        with ops_col2:
            current_resolution_time = ops_df['avg_resolution_time'].iloc[-1]
            prev_resolution_time = ops_df['avg_resolution_time'].iloc[-7] if len(ops_df) > 7 else current_resolution_time
            st.metric(
                "⏱️ Avg Resolution Time", 
                f"{current_resolution_time:.1f}h",
                f"{current_resolution_time - prev_resolution_time:+.1f}h vs last week"
            )
        
        with ops_col3:
            current_productivity = ops_df['team_productivity'].iloc[-1]
            prev_productivity = ops_df['team_productivity'].iloc[-7] if len(ops_df) > 7 else current_productivity
            st.metric(
                "👥 Team Productivity", 
                f"{current_productivity:.1%}",
                f"{current_productivity - prev_productivity:+.1%} vs last week"
            )
        
        with ops_col4:
            current_satisfaction = ops_df['customer_satisfaction'].iloc[-1]
            prev_satisfaction = ops_df['customer_satisfaction'].iloc[-7] if len(ops_df) > 7 else current_satisfaction
            st.metric(
                "😊 Customer Satisfaction", 
                f"{current_satisfaction:.1f}/5.0",
                f"{current_satisfaction - prev_satisfaction:+.1f} vs last week"
            )
        
        # Operational trends
        st.subheader("📈 Performance Trends")
        
        trend_col1, trend_col2 = st.columns(2)
        
        with trend_col1:
            st.markdown("**Automation & Resolution Rates**")
            trend_chart_data = ops_df.set_index('date')[['automation_rate', 'resolution_rate']]
            st.line_chart(trend_chart_data)
        
        with trend_col2:
            st.markdown("**Resolution Time & Satisfaction**")
            # Normalize for dual-axis visualization
            normalized_data = ops_df.set_index('date').copy()
            normalized_data['resolution_time_norm'] = (normalized_data['avg_resolution_time'] / normalized_data['avg_resolution_time'].max() * 100)
            normalized_data['satisfaction_norm'] = (normalized_data['customer_satisfaction'] / 5.0 * 100)
            
            st.line_chart(normalized_data[['resolution_time_norm', 'satisfaction_norm']])
            st.caption("📊 Normalized to 0-100 scale for comparison")
        
        # Process efficiency analysis
        st.subheader("⚡ Process Efficiency Analysis")
        
        efficiency_col1, efficiency_col2 = st.columns(2)
        
        with efficiency_col1:
            # Calculate efficiency gains
            baseline_auto_rate = 35.0  # Baseline before improvements
            current_auto_rate = ops_df['automation_rate'].mean()
            efficiency_gain = ((current_auto_rate - baseline_auto_rate) / baseline_auto_rate * 100)
            
            st.markdown("**Efficiency Improvements:**")
            st.success(f"🚀 {efficiency_gain:+.1f}% improvement in automation rate")
            
            # Time savings calculation
            baseline_time = 12.0  # hours
            current_time = ops_df['avg_resolution_time'].mean()
            time_savings = baseline_time - current_time
            
            st.success(f"⏰ {time_savings:.1f} hours saved per case on average")
            
            # Volume processing
            daily_volume = ops_df['total_issues'].mean()
            st.info(f"📊 Processing {daily_volume:.0f} cases per day on average")
        
        with efficiency_col2:
            st.markdown("**ROI from Process Improvements:**")
            
            # Calculate cost savings
            labor_cost_per_hour = 45  # dollars
            daily_hours_saved = time_savings * daily_volume
            monthly_savings = daily_hours_saved * 30 * labor_cost_per_hour
            
            st.metric("💰 Monthly Labor Savings", f"${monthly_savings:,.0f}")
            
            # Customer impact
            current_satisfaction = ops_df['customer_satisfaction'].iloc[-1]
            customer_impact = (current_satisfaction - 3.5) / (5.0 - 3.5) * 100  # Convert to percentage improvement
            st.metric("😊 Customer Satisfaction Improvement", f"{customer_impact:.1f}%")
            
            # Error reduction
            error_reduction = (1 - current_auto_rate/100) * 100  # Simplified calculation
            st.metric("🎯 Error Rate Reduction", f"{100-error_reduction:.1f}%")
    
    with acceleration_tab3:
        st.subheader("💰 Revenue Impact Analysis")
        
        # Calculate revenue impacts
        total_variance_amount = filtered_df['discount_variance'].abs().sum()
        risk_col_rev = find_column(filtered_df, 'risk', 'level')
        high_risk_variance = filtered_df[filtered_df[risk_col_rev] == 'HIGH']['discount_variance'].abs().sum() if risk_col_rev else 0
        cust_col_rev2 = find_column(filtered_df, 'customer', 'id')
        customer_count = filtered_df[cust_col_rev2].nunique() if cust_col_rev2 else 0
        
        # Revenue impact metrics
        revenue_col1, revenue_col2, revenue_col3 = st.columns(3)
        
        with revenue_col1:
            st.markdown("**💸 Revenue at Risk**")
            st.metric("Total Variance Impact", f"${total_variance_amount:,.0f}")
            st.metric("High-Risk Impact", f"${high_risk_variance:,.0f}")
            st.metric("Avg Impact per Customer", f"${total_variance_amount/customer_count:.2f}")
        
        with revenue_col2:
            st.markdown("**🔄 Recovery Potential**")
            
            # Calculate recovery scenarios
            auto_recovery = auto_resolvable['discount_variance'].abs().sum() if not auto_resolvable.empty else 0
            manual_recovery_potential = manual_review['discount_variance'].abs().sum() * 0.8 if not manual_review.empty else 0  # 80% recovery rate
            
            st.metric("Auto-Recoverable", f"${auto_recovery:,.0f}")
            st.metric("Manual Recovery Potential", f"${manual_recovery_potential:,.0f}")
            st.metric("Total Recovery Opportunity", f"${auto_recovery + manual_recovery_potential:,.0f}")
        
        with revenue_col3:
            st.markdown("**📈 Business Impact**")
            
            # Calculate business metrics
            revenue_protection_rate = ((auto_recovery + manual_recovery_potential) / total_variance_amount * 100) if total_variance_amount > 0 else 0
            customer_retention_impact = customer_count * 0.05 * 1200  # 5% at risk, $1200 annual value
            
            st.metric("Revenue Protection Rate", f"{revenue_protection_rate:.1f}%")
            st.metric("Customer Retention Value", f"${customer_retention_impact:,.0f}")
            
        # ROI Analysis
        st.subheader("📊 Return on Investment Analysis")
        
        roi_col1, roi_col2 = st.columns([2, 1])
        
        with roi_col1:
            # Create ROI comparison chart
            roi_scenarios = {
                'Scenario': ['Current Manual Process', 'With Automation', 'Full Optimization'],
                'Monthly_Cost': [45000, 25000, 15000],  # Labor costs
                'Resolution_Rate': [65, 85, 95],  # Percentage
                'Customer_Satisfaction': [3.2, 4.1, 4.6],
                'Revenue_Recovery': [60, 80, 90]  # Percentage
            }
            
            roi_df = pd.DataFrame(roi_scenarios)
            
            # Calculate ROI
            roi_df['Monthly_Recovery'] = (roi_df['Revenue_Recovery'] / 100) * (total_variance_amount * 12 / 365 * 30)  # Monthly equivalent
            roi_df['Net_Benefit'] = roi_df['Monthly_Recovery'] - roi_df['Monthly_Cost']
            roi_df['ROI_Percentage'] = (roi_df['Net_Benefit'] / roi_df['Monthly_Cost'] * 100).round(1)
            
            st.dataframe(
                roi_df[['Scenario', 'Monthly_Cost', 'Resolution_Rate', 'Monthly_Recovery', 'ROI_Percentage']],
                column_config={
                    "Monthly_Cost": st.column_config.NumberColumn("Monthly Cost", format="$%d"),
                    "Resolution_Rate": st.column_config.NumberColumn("Resolution Rate", format="%d%%"),
                    "Monthly_Recovery": st.column_config.NumberColumn("Monthly Recovery", format="$%.0f"),
                    "ROI_Percentage": st.column_config.NumberColumn("ROI", format="%.1f%%")
                }
            )
        
        with roi_col2:
            st.markdown("**🎯 Key Insights:**")
            
            current_roi = roi_df.iloc[0]['ROI_Percentage']
            automation_roi = roi_df.iloc[1]['ROI_Percentage']
            optimized_roi = roi_df.iloc[2]['ROI_Percentage']
            
            st.metric("Current ROI", f"{current_roi:+.1f}%")
            st.metric("With Automation", f"{automation_roi:+.1f}%", f"{automation_roi - current_roi:+.1f}pp")
            st.metric("Fully Optimized", f"{optimized_roi:+.1f}%", f"{optimized_roi - current_roi:+.1f}pp")
            
            st.markdown("---")
            st.markdown("**💡 Recommendations:**")
            st.success("✅ Implement auto-resolution for low-risk items")
            st.success("✅ Increase automation threshold to $15")
            st.success("✅ Add predictive analytics for prevention")
        
        # Implementation roadmap
        st.subheader("🗺️ Implementation Roadmap")
        
        roadmap_data = {
            'Phase': ['Phase 1: Quick Wins', 'Phase 2: Automation', 'Phase 3: Optimization'],
            'Timeline': ['0-3 months', '3-6 months', '6-12 months'],
            'Investment': ['$50K', '$150K', '$100K'],
            'Expected_ROI': ['150%', '300%', '450%'],
            'Key_Actions': [
                'Auto-resolve ≤$10 variances, Bulk processing tools',
                'ML-based matching, Predictive analytics, API integrations', 
                'Real-time processing, Advanced ML, Customer self-service'
            ]
        }
        
        roadmap_df = pd.DataFrame(roadmap_data)
        
        for idx, row in roadmap_df.iterrows():
            with st.expander(f"📅 {row['Phase']} ({row['Timeline']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Investment", row['Investment'])
                
                with col2:
                    st.metric("Expected ROI", row['Expected_ROI'])
                
                with col3:
                    if idx == 0:
                        st.success("✅ Ready to implement")
                    elif idx == 1:
                        st.warning("📋 Planning phase")
                    else:
                        st.info("🔮 Future roadmap")
                
                st.markdown(f"**Key Actions:** {row['Key_Actions']}")

    # =====================================================================================
    # SECTION 7: REPORTING & EXPORT CENTER
    # =====================================================================================
    
    st.markdown("---")
    st.header("📤 Reporting & Export Center")
    st.markdown("*Generate reports and export data for stakeholders and compliance*")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        st.subheader("📊 Data Export")
        
        # Export filtered data
        if st.button("📄 Export Filtered Data to CSV", use_container_width=True):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV File",
                data=csv,
                file_name=f"comcast_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Export high-risk only
        high_risk_only = filtered_df[filtered_df[risk_col_rev] == 'HIGH'] if risk_col_rev else filtered_df.iloc[0:0]
        if not high_risk_only.empty and st.button("🚨 Export High-Risk Items Only", use_container_width=True):
            csv_high_risk = high_risk_only.to_csv(index=False)
            st.download_button(
                label="⬇️ Download High-Risk CSV",
                data=csv_high_risk,
                file_name=f"high_risk_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with action_col2:
        st.subheader("📋 Executive Report")
        
        # Calculate current stats for both report and quick actions
        current_stats = calculate_summary_stats(filtered_df)
        
        if st.button("📈 Generate Executive Summary", use_container_width=True):
            executive_report = f"""
COMCAST PROMOTION RECONCILIATION - EXECUTIVE SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Filter Period: {date_range[0]} to {date_range[1]}

=== KEY PERFORMANCE INDICATORS ===
• Total Records Analyzed: {current_stats['total_records']:,}
• Overall Match Rate: {current_stats['match_rate_pct']:.1f}%
• Exception Records: {current_stats['exception_records']:,}
• Total Dollar Variance: ${current_stats['total_discount_variance']:,.2f}

=== RISK BREAKDOWN ===
• High Risk Issues: {current_stats['high_risk_count']:,} ({current_stats['high_risk_count']/current_stats['total_records']*100:.1f}%)
• Medium Risk Issues: {current_stats['medium_risk_count']:,} ({current_stats['medium_risk_count']/current_stats['total_records']*100:.1f}%)
• Low Risk/Matched: {current_stats['low_risk_count']:,} ({current_stats['low_risk_count']/current_stats['total_records']*100:.1f}%)

=== OPERATIONAL INSIGHTS ===
• Average Variance per Transaction: ${current_stats['total_discount_variance']/current_stats['total_records']:.2f}
• Highest Risk Categories: {', '.join(filtered_df[filtered_df['risk_level']=='HIGH']['product_category'].value_counts().head(3).index.tolist())}
• Geographic Hotspots: {', '.join(filtered_df[filtered_df['risk_level']=='HIGH'].get('service_city', pd.Series()).value_counts().head(3).index.tolist()) if 'service_city' in filtered_df.columns else 'Data not available'}

=== RECOMMENDED ACTIONS ===
1. Prioritize resolution of {current_stats['high_risk_count']:,} high-risk exceptions
2. Review promotion configurations for categories with highest variance
3. Investigate geographic patterns in high-variance regions
4. Implement process improvements for reconciliation accuracy

Report generated from Comcast Promotion Reconciliation Dashboard
            """
            
            st.download_button(
                label="⬇️ Download Executive Report",
                data=executive_report,
                file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Quick action buttons
        st.markdown("**Quick Actions:**")
        if current_stats['high_risk_count'] > 0:
            st.error(f"⚠️ {current_stats['high_risk_count']} high-risk items need attention!")
        else:
            st.success("✅ No high-risk items found!")
        
        if current_stats['match_rate_pct'] < 95:
            st.warning(f"📊 Match rate ({current_stats['match_rate_pct']:.1f}%) below target (95%)")
        else:
            st.success(f"🎯 Match rate ({current_stats['match_rate_pct']:.1f}%) meets target!")

if __name__ == "__main__":
    main() 