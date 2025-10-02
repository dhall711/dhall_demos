"""
Comcast Revenue Reconciliation Operations Dashboard - ENHANCED
==================================================

A comprehensive operations center for AI-powered revenue reconciliation,
featuring real-time monitoring, Cortex AI recommendations, automated
remediation workflows, business intelligence, and enhanced data elements.

Enhanced with:
- Business Issue Classification
- Customer Risk Clustering  
- Promotion Stacking Detection
- Anticipatory Billing Intelligence
- Enhanced Mobile Line Management
- Revenue Protection Metrics
- Cycle Timing Analysis

Based on the End-to-End Workflow for Comcast Revenue Protection.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
from datetime import datetime, timedelta
import time
import os

# Configure page
st.set_page_config(
    page_title="🎯 Comcast Revenue Operations Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for operations dashboard theme
st.markdown("""
<style>
    /* Operations Dashboard Theme */
    .main > div {
        padding: 1rem 2rem;
    }
    
    /* Status Cards */
    .status-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .critical-card {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(220,38,38,0.2);
    }
    
    .success-card {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(5,150,105,0.2);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(217,119,6,0.2);
    }
    
    /* Alert Indicators */
    .alert-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .alert-critical { background-color: #ef4444; }
    .alert-high { background-color: #f59e0b; }
    .alert-medium { background-color: #3b82f6; }
    .alert-low { background-color: #10b981; }
    
    /* Operations Metrics */
    .metric-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        color: #6b7280;
    }
    
    /* Investigation Panel */
    .investigation-panel {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    /* Cortex Recommendations */
    .cortex-recommendation {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
        border-left: 4px solid #a855f7;
    }
    
    /* Timeline */
    .timeline-item {
        border-left: 3px solid #e5e7eb;
        padding-left: 1rem;
        margin: 0.5rem 0;
        position: relative;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 0.5rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #3b82f6;
    }
    
    /* Custom Tab Styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }
    
    .stButton > button[kind="secondary"] {
        background: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 8px 8px 0 0;
        font-weight: normal;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #e2e8f0;
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# === UTILITY FUNCTIONS ===

def find_column(df, *keywords):
    """Dynamically find column name based on keywords (case-insensitive)"""
    if df.empty:
        return None
    
    for col in df.columns:
        col_lower = col.lower()
        if all(keyword.lower() in col_lower for keyword in keywords):
            return col
    return None

def safe_filter(df, column, value, operator='=='):
    """Safely filter DataFrame with column existence check"""
    if column and column in df.columns:
        if operator == '==':
            return df[df[column] == value]
        elif operator == '!=':
            return df[df[column] != value]
        elif operator == 'isin':
            return df[df[column].isin(value)]
    return df.iloc[0:0]  # Return empty DataFrame

# === DATA LOADING FUNCTIONS ===

def get_snowflake_session():
    """Initialize and return a Snowflake Snowpark session if available."""
    session = None
    error = None
    try:
        # 1) If running in Snowflake/Streamlit native env
        try:
            from snowflake.snowpark.context import get_active_session
            session = get_active_session()
        except Exception:
            session = None
        
        # 2) If secrets contains connection config
        if session is None:
            try:
                import snowflake.snowpark as snowpark  # type: ignore
                if 'snowflake' in st.secrets:
                    conn_params = dict(st.secrets['snowflake'])
                    session = snowpark.Session.builder.configs(conn_params).create()
            except Exception:
                session = None
        
        # 3) Streamlit connections API
        if session is None:
            try:
                session = st.connection("snowflake").session()
            except Exception:
                session = None
    except Exception as e:
        error = str(e)
        session = None
    return session, error

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_snowflake_data(prefer_live: bool = True):
    """Load data from Snowflake tables (COMCAST_REVENUE only) or sample data.

    Returns: (df, anomaly_df, is_live, error_msg, meta)
    meta: { 'source': 'COMCAST_REVENUE' | 'SAMPLE' }
    """
    if not prefer_live:
        return load_sample_data(), pd.DataFrame(), False, None, { 'source': 'SAMPLE' }

    session, init_error = get_snowflake_session()
    if session is None:
        return load_sample_data(), pd.DataFrame(), False, init_error or "No Snowflake session available", { 'source': 'SAMPLE' }

    def try_load_from(session, db: str, schema: str, view: str, anomaly_table: str | None):
        rec_sql = f"SELECT * FROM {db}.{schema}.{view}"
        df = session.sql(rec_sql).to_pandas()
        anom_df = pd.DataFrame()
        if anomaly_table:
            try:
                anom_sql = f"SELECT * FROM {db}.{schema}.{anomaly_table}"
                anom_df = session.sql(anom_sql).to_pandas()
            except Exception:
                anom_df = pd.DataFrame()
        return df, anom_df

    # Only use COMCAST_REVENUE
    sources = [("COMCAST_REVENUE", "ANALYTICS", "PROMOTION_RECONCILIATION", "COMCAST_ANOMALIES_DETECTED")]

    last_error = None
    for db, schema, view, anom in sources:
        try:
            df, anom_df = try_load_from(session, db, schema, view, anom)
            if not df.empty:
                return df, anom_df, True, None, { 'source': db }
        except Exception as e:
            last_error = str(e)

    # Fallback to sample
    return load_sample_data(), pd.DataFrame(), False, last_error, { 'source': 'SAMPLE' }

def load_sample_data():
    """Generate comprehensive sample data with enhanced business intelligence elements"""
    np.random.seed(42)
    
    # Create sample reconciliation data
    n_records = 2500
    
    # Product categories and specific products
    products = {
        'Internet': ['Xfinity Internet Gigabit', 'Xfinity Internet Superfast', 'Xfinity Internet Performance'],
        'TV': ['Xfinity X1 TV Premier', 'Xfinity Flex 4K', 'Xfinity X1 Starter'],
        'Mobile': ['Xfinity Mobile Unlimited', 'Xfinity Mobile Shared Data', 'Xfinity Mobile By The Gig'],
        'Bundle': ['Triple Play Ultimate', 'Double Play Internet+TV', 'Quad Play Complete']
    }
    
    # Enhanced business elements
    customer_segments = ['High_Value', 'Standard', 'Price_Sensitive', 'New_Customer', 'Loyalty_Member']
    business_priorities = ['CRITICAL_FIRST_BILL', 'HIGH_CHURN_RISK', 'REVENUE_PROTECTION', 'STANDARD', 'LOW_IMPACT']
    stacking_violations = ['MOBILE_INTERNET_CONFLICT', 'BUNDLE_PROMO_OVERLAP', 'STUDENT_SENIOR_CONFLICT', 'NONE']
    
    # Generate base data
    data = []
    for i in range(n_records):
        category = np.random.choice(list(products.keys()))
        product = np.random.choice(products[category])
        
        # Customer and account info
        customer_id = f"CUST-{100000 + i}"
        account_id = f"ACCT-{customer_id.split('-')[1]}"
        
        # Enhanced customer intelligence
        customer_segment = np.random.choice(customer_segments)
        tenure_months = np.random.randint(1, 120)  # 1-10 years
        churn_risk_score = np.random.uniform(0, 1)
        
        # Adjust churn risk based on segment - more realistic ranges
        if customer_segment == 'High_Value':
            churn_risk_score = np.random.uniform(0.02, 0.15)  # Very low churn risk
        elif customer_segment == 'Price_Sensitive':
            churn_risk_score = np.random.uniform(0.15, 0.45)  # Moderate churn risk
        elif customer_segment == 'New_Customer':
            churn_risk_score = np.random.uniform(0.08, 0.35)  # Variable risk
        elif customer_segment == 'Loyalty_Member':
            churn_risk_score = np.random.uniform(0.01, 0.12)  # Very low churn risk
        else:  # Standard
            churn_risk_score = np.random.uniform(0.05, 0.25)  # Low to moderate churn risk
        
        promotion_usage_frequency = np.random.choice(['LOW', 'MEDIUM', 'HIGH'], p=[0.4, 0.4, 0.2])
        
        # Geographic distribution
        regions = ['Northeast', 'Southeast', 'Midwest', 'West', 'Southwest']
        region = np.random.choice(regions)
        
        cities = {
            'Northeast': ['Boston', 'New York', 'Philadelphia'],
            'Southeast': ['Atlanta', 'Miami', 'Charlotte'],
            'Midwest': ['Chicago', 'Detroit', 'Milwaukee'],
            'West': ['Los Angeles', 'San Francisco', 'Seattle'],
            'Southwest': ['Phoenix', 'Denver', 'Las Vegas']
        }
        city = np.random.choice(cities[region])
        
        # Determine first bill status first - more realistic rate
        first_bill_flag = np.random.choice([True, False], p=[0.08, 0.92])  # 8% are first bills
        
        # Financial data
        base_amount = np.random.uniform(50, 200)
        discount_amount = np.random.uniform(0, base_amount * 0.3)
        final_amount = base_amount - discount_amount
        
        # Billing variance scenarios - much more realistic match rates
        if first_bill_flag:
            # First bills have some issues but still mostly match
            variance_type = np.random.choice([
                'perfect_match', 'minor_diff', 'promo_not_applied', 
                'incorrect_promo', 'double_billing', 'proration', 'bundle_error'
            ], p=[0.75, 0.12, 0.06, 0.03, 0.01, 0.02, 0.01])  # Sum = 1.0
        else:
            # Regular bills have excellent match rates
            variance_type = np.random.choice([
                'perfect_match', 'minor_diff', 'promo_not_applied', 
                'incorrect_promo', 'double_billing', 'proration', 'bundle_error'
            ], p=[0.930, 0.03, 0.01, 0.01, 0.005, 0.01, 0.005])  # Sum = 1.0
        
        if variance_type == 'perfect_match':
            billing_discount = discount_amount
            variance = 0
            status = 'MATCHED'
        elif variance_type == 'minor_diff':
            billing_discount = discount_amount + np.random.uniform(-5, 5)
            variance = discount_amount - billing_discount
            status = 'MATCHED' if abs(variance) < 1 else 'MINOR_VARIANCE'
        elif variance_type == 'promo_not_applied':
            billing_discount = 0
            variance = discount_amount
            status = 'PROMO_NOT_APPLIED'
        elif variance_type == 'incorrect_promo':
            billing_discount = discount_amount * np.random.uniform(0.2, 0.8)
            variance = discount_amount - billing_discount
            status = 'INCORRECT_PROMO_AMOUNT'
        elif variance_type == 'double_billing':
            billing_discount = -discount_amount  # Negative means charged twice
            variance = discount_amount * 2
            status = 'DOUBLE_BILLING'
        elif variance_type == 'proration':
            billing_discount = discount_amount * np.random.uniform(0.3, 0.8)
            variance = discount_amount - billing_discount
            status = 'PRORATION_ADJUSTMENT'
        else:  # bundle_error
            billing_discount = discount_amount + np.random.uniform(15, 45)
            variance = discount_amount - billing_discount
            status = 'BUNDLE_DISCOUNT_ERROR'
        
        # Special cases for Comcast priority use cases
        line_number = f"({np.random.randint(200, 999)}) {np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}"
        
        # Mobile line duplicates (much lower rate - 2% chance for mobile products to show issues)
        if category == 'Mobile' and np.random.random() < 0.02:
            # Use a fixed set of duplicate line numbers
            duplicate_lines = ["(555) 123-4567", "(555) 234-5678", "(555) 345-6789", "(555) 456-7890", "(555) 567-8901"]
            line_number = np.random.choice(duplicate_lines)
            if status == 'MATCHED':
                status = 'DUPLICATE_LINE_NUMBER'
        
        # Additional mobile line conflicts for non-mobile products (very rare edge case)
        elif np.random.random() < 0.003:  # 0.3% chance for cross-product line conflicts
            conflict_lines = ["(555) 123-4567", "(555) 234-5678"]
            line_number = np.random.choice(conflict_lines)
            if status == 'MATCHED':
                status = 'DUPLICATE_LINE_NUMBER'
        
        # Mobile-specific service issues (much lower rates)
        if category == 'Mobile':
            mobile_issue_chance = np.random.random()
            if mobile_issue_chance < 0.005:  # 0.5% chance of ported number mismatch
                if status == 'MATCHED':
                    status = 'PORTED_NUMBER_MISMATCH'
            elif mobile_issue_chance < 0.008:  # 0.3% chance of account line assignment error
                if status == 'MATCHED':
                    status = 'ACCOUNT_LINE_ASSIGNMENT_ERROR'
        
        # Promo timing mismatches (much lower rate - 2% chance)
        promo_start_cycle = 1
        promo_applied_cycle = promo_start_cycle
        cycle_timing_variance = 0
        
        if np.random.random() < 0.02:
            promo_applied_cycle = np.random.choice([2, 3])
            cycle_timing_variance = promo_applied_cycle - promo_start_cycle
            if status == 'MATCHED':
                status = 'PROMO_TIMING_MISMATCH'
        
        # Enhanced business classification (much lower stacking violation rates)
        business_issue_classification = 'NONE'
        business_priority = 'STANDARD'
        stacking_violation = np.random.choice(stacking_violations, p=[0.01, 0.008, 0.005, 0.977])
        
        # Determine business classifications
        if first_bill_flag and status != 'MATCHED':
            business_issue_classification = 'FIRST_BILL_ISSUE'
            business_priority = 'CRITICAL_FIRST_BILL'
        elif status == 'DUPLICATE_LINE_NUMBER':
            business_issue_classification = 'DUPLICATE_LINE_CONFLICT'
            business_priority = 'HIGH_CHURN_RISK' if churn_risk_score > 0.25 else 'STANDARD'
        elif status == 'PROMO_TIMING_MISMATCH':
            business_issue_classification = 'PROMO_TIMING_MISMATCH'
            business_priority = 'REVENUE_PROTECTION'
        elif stacking_violation != 'NONE':
            business_issue_classification = 'STACKING_VIOLATION'
            business_priority = 'REVENUE_PROTECTION'
            # Override status for stacking violations
            status = 'STACKING_VIOLATION'
        elif status == 'DOUBLE_BILLING':
            business_issue_classification = 'BILLING_ERROR'
            business_priority = 'HIGH_CHURN_RISK'
        elif abs(variance) > 50:
            business_issue_classification = 'HIGH_VALUE_VARIANCE'
            business_priority = 'REVENUE_PROTECTION'
        
        # Revenue protection calculation
        if business_priority in ['REVENUE_PROTECTION', 'CRITICAL_FIRST_BILL']:
            revenue_protection_value = abs(variance) * (1.5 if stacking_violation != 'NONE' else 1.0)
        else:
            revenue_protection_value = 0
        
        # Risk level calculation
        if first_bill_flag and status != 'MATCHED':
            risk_level = 'CRITICAL'
        elif status in ['DUPLICATE_LINE_NUMBER', 'PROMO_TIMING_MISMATCH', 'DOUBLE_BILLING']:
            risk_level = 'HIGH'
        elif abs(variance) > 50:  # Raised threshold for high risk
            risk_level = 'HIGH'
        elif abs(variance) > 15:  # Raised threshold for medium risk
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # Transaction timing
        days_ago = np.random.randint(0, 30)
        transaction_date = datetime.now() - timedelta(days=days_ago)
        
        data.append({
            # Basic identifiers
            'RECORD_ID': f"REC-{1000000 + i}",
            'ORDER_ID': f"ORD-{500000 + i}",
            'BILLING_ID': f"BILL-{600000 + i}",
            'CUSTOMER_ID': customer_id,
            'ACCOUNT_ID': account_id,
            
            # Product and service details
            'PRODUCT_CATEGORY': category,
            'PRODUCT_NAME': product,
            'LINE_NUMBER': line_number,
            
            # Financial data
            'ORDER_BASE_AMOUNT': round(base_amount, 2),
            'ORDER_DISCOUNT_AMOUNT': round(discount_amount, 2),
            'ORDER_FINAL_AMOUNT': round(final_amount, 2),
            'BILLING_BASE_AMOUNT': round(base_amount, 2),
            'BILLING_DISCOUNT_AMOUNT': round(billing_discount, 2),
            'BILLING_FINAL_AMOUNT': round(base_amount - billing_discount, 2),
            'DISCOUNT_VARIANCE': round(variance, 2),
            'AMOUNT_VARIANCE': round(final_amount - (base_amount - billing_discount), 2),
            
            # Core reconciliation status
            'RECONCILIATION_STATUS': status,
            'RISK_LEVEL': risk_level,
            'FIRST_BILL_FLAG': first_bill_flag,
            
            # Enhanced business intelligence
            'BUSINESS_ISSUE_CLASSIFICATION': business_issue_classification,
            'BUSINESS_PRIORITY': business_priority,
            'STACKING_VIOLATION_TYPE': stacking_violation,
            'REVENUE_PROTECTION_VALUE': round(revenue_protection_value, 2),
            
            # Customer intelligence
            'CUSTOMER_SEGMENT': customer_segment,
            'TENURE_MONTHS': tenure_months,
            'CHURN_RISK_SCORE': round(churn_risk_score, 3),
            'PROMOTION_USAGE_FREQUENCY': promotion_usage_frequency,
            
            # Timing analysis
            'PROMO_START_CYCLE': promo_start_cycle,
            'PROMO_APPLIED_CYCLE': promo_applied_cycle,
            'CYCLE_TIMING_VARIANCE': cycle_timing_variance,
            
            # Geographic and temporal data
            'SERVICE_REGION': region,
            'SERVICE_CITY': city,
            'TRANSACTION_DATE': transaction_date,
            'CREATED_TIMESTAMP': datetime.now() - timedelta(hours=np.random.randint(1, 48))
        })
    
    return pd.DataFrame(data)

@st.cache_data(ttl=60)  # Cache for 1 minute for real-time feel
def generate_ml_insights(df):
    """Generate ML-powered insights and anomaly scores"""
    if df.empty:
        return pd.DataFrame()
    
    # Simulate ML anomaly detection results
    np.random.seed(42)
    
    # Calculate features for anomaly detection - more realistic
    df_ml = df.copy()
    df_ml['ML_ANOMALY_SCORE'] = np.random.uniform(0, 1, len(df))
    df_ml['ML_IS_ANOMALY'] = df_ml['ML_ANOMALY_SCORE'] > 0.95  # Much higher threshold
    
    # Adjust scores based on business rules - only truly high risk items
    high_risk_mask = df_ml['RISK_LEVEL'].isin(['HIGH', 'CRITICAL'])
    critical_mask = df_ml['RISK_LEVEL'] == 'CRITICAL'
    
    # Only critical items get flagged as ML anomalies
    df_ml.loc[critical_mask, 'ML_ANOMALY_SCORE'] = np.random.uniform(0.95, 1.0, critical_mask.sum())
    df_ml.loc[critical_mask, 'ML_IS_ANOMALY'] = True
    
    # High risk items get elevated scores but not necessarily flagged
    df_ml.loc[high_risk_mask & ~critical_mask, 'ML_ANOMALY_SCORE'] = np.random.uniform(0.7, 0.95, (high_risk_mask & ~critical_mask).sum())
    
    return df_ml

@st.cache_data(ttl=300)
def generate_cortex_recommendations(df, priority_issues):
    """Generate Cortex AI-powered recommendations"""
    recommendations = []
    
    # Analyze patterns in the data
    for issue_type, count in priority_issues.items():
        if count > 0:
            if issue_type == 'FIRST_BILL_ISSUES':
                recommendations.append({
                    'type': 'PROCESS_IMPROVEMENT',
                    'priority': 'CRITICAL',
                    'title': 'First Bill Accuracy Enhancement',
                    'description': f'Detected {count} first bill issues. Implement pre-billing validation checks.',
                    'impact': 'Prevents customer churn and improves onboarding experience',
                    'action': 'Deploy automated first-bill validation workflow',
                    'estimated_savings': '$125,000 annually',
                    'implementation_time': '2-3 weeks'
                })
            
            elif issue_type == 'DUPLICATE_LINES':
                recommendations.append({
                    'type': 'AUTOMATED_FIX',
                    'priority': 'HIGH',
                    'title': 'Mobile Line Deduplication',
                    'description': f'Found {count} duplicate mobile lines requiring immediate attention.',
                    'impact': 'Eliminates billing conflicts and service disruptions',
                    'action': 'Run automated line reassignment process',
                    'estimated_savings': '$45,000 in prevented disputes',
                    'implementation_time': 'Immediate'
                })
            
            elif issue_type == 'PROMO_TIMING':
                recommendations.append({
                    'type': 'SYSTEM_INTEGRATION',
                    'priority': 'HIGH',
                    'title': 'Promo Timing Synchronization',
                    'description': f'{count} promo timing mismatches detected across billing cycles.',
                    'impact': 'Ensures customer expectations are met for discount timing',
                    'action': 'Implement real-time order-to-billing sync',
                    'estimated_savings': '$78,000 in customer retention',
                    'implementation_time': '4-6 weeks'
                })
    
    # Add general AI insights (dynamic columns)
    if len(df) > 0:
        region_col = find_column(df, 'service', 'region') or find_column(df, 'region')
        variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
        try:
            if region_col and variance_col and region_col in df.columns and variance_col in df.columns:
                variance_pattern = df.groupby(region_col)[variance_col].agg(['mean', 'count']).reset_index()
                high_variance_region = variance_pattern.loc[variance_pattern['mean'].idxmax(), region_col]
                recommendations.append({
                    'type': 'REGIONAL_OPTIMIZATION',
                    'priority': 'MEDIUM',
                    'title': f'{high_variance_region} Region Performance',
                    'description': f'Region shows higher variance patterns. Consider regional billing process review.',
                    'impact': 'Standardizes reconciliation accuracy across all regions',
                    'action': f'Audit {high_variance_region} billing processes',
                    'estimated_savings': '$32,000 in efficiency gains',
                    'implementation_time': '3-4 weeks'
                })
        except Exception:
            # If grouping fails, skip regional recommendation silently
            pass
    
    return recommendations

# === DASHBOARD COMPONENTS ===

def render_header():
    """Render the operations dashboard header"""
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.markdown("""
        # 🎯 **Comcast Revenue Operations Center**
        ### *AI-Powered Reconciliation & Exception Management*
        """)
    
    with col2:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        **System Status:** <span style='color: #10b981'>🟢 Operational</span>  
        **Last Updated:** {current_time}  
        **Data Source:** {"Snowflake Live" if st.session_state.get('live_data', False) else "Demo Mode"}
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Show data source info
        if st.session_state.get('live_data', False):
            st.success("📡 Live Snowflake Data")
        else:
            st.info("🎲 Enhanced Sample Data")
            if st.button("🎯 Generate New Sample", use_container_width=True):
                # Clear cache to force regeneration with different seed
                st.cache_data.clear()
                # Change the random seed to get different sample data
                import time
                np.random.seed(int(time.time()))
                st.rerun()

def render_executive_kpis(df, ml_df):
    """Render executive-level KPIs"""
    if df.empty:
        st.warning("No data available for KPI calculation")
        return
    
    st.markdown("## 📊 **Executive Command Center**")
    
    # Find columns dynamically - Enhanced
    status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
    risk_col = find_column(df, 'risk', 'level') or find_column(df, 'risk')
    variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
    first_bill_col = find_column(df, 'first', 'bill', 'flag') or find_column(df, 'first', 'bill')
    product_col = find_column(df, 'product', 'category') or find_column(df, 'product')
    ml_anomaly_col = find_column(ml_df, 'ml', 'is', 'anomaly') or find_column(ml_df, 'is', 'anomaly') if not ml_df.empty else None
    
    # Enhanced business intelligence columns
    business_issue_col = find_column(df, 'business', 'issue', 'classification')
    business_priority_col = find_column(df, 'business', 'priority')
    stacking_violation_col = find_column(df, 'stacking', 'violation', 'type')
    revenue_protection_col = find_column(df, 'revenue', 'protection', 'value')
    customer_segment_col = find_column(df, 'customer', 'segment')
    churn_risk_col = find_column(df, 'churn', 'risk', 'score')
    cycle_timing_col = find_column(df, 'cycle', 'timing', 'variance')
    
    # Calculate KPIs with safe column access
    total_records = len(df)
    matched_records = len(safe_filter(df, status_col, 'MATCHED')) if status_col else 0
    match_rate = (matched_records / total_records * 100) if total_records > 0 else 0
    
    total_variance = df[variance_col].abs().sum() if variance_col and variance_col in df.columns else 0
    high_risk_df = safe_filter(df, risk_col, ['HIGH', 'CRITICAL'], 'isin') if risk_col else df.iloc[0:0]
    revenue_at_risk = high_risk_df[variance_col].abs().sum() if variance_col and not high_risk_df.empty else 0
    
    # First bill accuracy calculation
    if first_bill_col and status_col:
        first_bill_total = len(safe_filter(df, first_bill_col, True))
        first_bill_matched = len(df[(df[first_bill_col] == True) & (df[status_col] == 'MATCHED')])
        first_bill_accuracy = (first_bill_matched / first_bill_total * 100) if first_bill_total > 0 else 100
    else:
        first_bill_accuracy = 100
    
    # Mobile duplicates
    if product_col and status_col:
        mobile_duplicates = len(df[(df[product_col] == 'Mobile') & (df[status_col] == 'DUPLICATE_LINE_NUMBER')])
    else:
        mobile_duplicates = 0
    
    # ML anomalies
    ml_anomalies = len(safe_filter(ml_df, ml_anomaly_col, True)) if ml_anomaly_col and not ml_df.empty else 0
    
    # Enhanced business intelligence KPIs
    stacking_violations = 0
    revenue_protected = 0
    high_churn_customers = 0
    timing_mismatches = 0
    
    if stacking_violation_col and stacking_violation_col in df.columns:
        stacking_violations = len(df[df[stacking_violation_col] != 'NONE'])
    
    if revenue_protection_col and revenue_protection_col in df.columns:
        revenue_protected = df[revenue_protection_col].sum()
    
    if churn_risk_col and churn_risk_col in df.columns:
        high_churn_customers = len(df[df[churn_risk_col] > 0.25])
    
    if cycle_timing_col and cycle_timing_col in df.columns:
        timing_mismatches = len(df[df[cycle_timing_col].abs() > 1])
    
    # Customer segment insights
    critical_segments = 0
    if customer_segment_col and customer_segment_col in df.columns:
        critical_segments = len(df[df[customer_segment_col].isin(['High_Value', 'New_Customer'])])
    
    # Render Enhanced KPI cards - now 6 columns
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {'#10b981' if match_rate > 95 else '#f59e0b' if match_rate > 90 else '#ef4444'}">{match_rate:.1f}%</div>
            <div style="font-weight: bold;">Match Rate</div>
            <div class="metric-delta">Target: >95% | {matched_records:,} of {total_records:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {'#ef4444' if revenue_at_risk > 50000 else '#f59e0b' if revenue_at_risk > 25000 else '#10b981'}">${revenue_at_risk:,.0f}</div>
            <div style="font-weight: bold;">Revenue at Risk</div>
            <div class="metric-delta">High/Critical Issues | ${total_variance:,.0f} total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {'#10b981' if first_bill_accuracy > 98 else '#f59e0b' if first_bill_accuracy > 95 else '#ef4444'}">{first_bill_accuracy:.1f}%</div>
            <div style="font-weight: bold;">First Bill Health</div>
            <div class="metric-delta">New Customer Experience | Target: >99%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {'#10b981' if mobile_duplicates == 0 else '#f59e0b' if mobile_duplicates < 5 else '#ef4444'}">{mobile_duplicates}</div>
            <div style="font-weight: bold;">Mobile Line Issues</div>
            <div class="metric-delta">Duplicate Lines | Target: 0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col5:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {'#7c3aed'}">{ml_anomalies}</div>
            <div style="font-weight: bold;">AI Anomalies</div>
            <div class="metric-delta">ML Detected | Requires Investigation</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col6:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {'#10b981' if revenue_protected > 0 else '#6b7280'}">${revenue_protected:,.0f}</div>
            <div style="font-weight: bold;">Revenue Protected</div>
            <div class="metric-delta">Stacking Prevention | {stacking_violations} violations blocked</div>
        </div>
        """, unsafe_allow_html=True)

def render_critical_alerts(df):
    """Render critical alerts section"""
    st.markdown("## 🚨 **Critical Alert Center**")
    
    # Find columns dynamically
    risk_col = find_column(df, 'risk', 'level') or find_column(df, 'risk')
    first_bill_col = find_column(df, 'first', 'bill', 'flag') or find_column(df, 'first', 'bill')
    
    # Filter critical and high priority items
    if risk_col:
        critical_mask = df[risk_col] == 'CRITICAL'
        if first_bill_col:
            high_first_bill_mask = (df[risk_col] == 'HIGH') & (df[first_bill_col] == True)
            critical_issues = df[critical_mask | high_first_bill_mask]
        else:
            critical_issues = df[critical_mask]
    else:
        critical_issues = df.iloc[0:0]  # Empty DataFrame
    
    if critical_issues.empty:
        st.markdown("""
        <div class="success-card">
            <h3>✅ All Clear - No Critical Issues</h3>
            <p>No critical alerts requiring immediate attention. System operating within normal parameters.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Initialize session state for alert tabs
    if 'alert_tab_index' not in st.session_state:
        st.session_state.alert_tab_index = 0
    
    # Create tabs with session state management - Enhanced
    alert_tab_names = ["🔴 All Critical", "👶 First Bill", "📱 Mobile Lines", "💰 High Value", "🛡️ Stacking Violations"]
    
    # Create tab buttons that maintain state
    alert_tab_cols = st.columns(len(alert_tab_names))
    for i, (col, tab_name) in enumerate(zip(alert_tab_cols, alert_tab_names)):
        with col:
            button_style = "primary" if st.session_state.alert_tab_index == i else "secondary"
            if st.button(tab_name, key=f"alert_tab_{i}", use_container_width=True, type=button_style):
                st.session_state.alert_tab_index = i
                st.rerun()
    
    st.markdown("---")
    
    # Render content based on active tab
    if st.session_state.alert_tab_index == 0:
        st.markdown(f"**{len(critical_issues)} Critical Issues Requiring Immediate Action**")
        
        # Find column names dynamically
        customer_col = find_column(critical_issues, 'customer', 'id') or 'CUSTOMER_ID'
        variance_col = find_column(critical_issues, 'discount', 'variance') or find_column(critical_issues, 'variance') or 'DISCOUNT_VARIANCE'
        status_col = find_column(critical_issues, 'reconciliation', 'status') or find_column(critical_issues, 'status') or 'RECONCILIATION_STATUS'
        product_col = find_column(critical_issues, 'product', 'name') or 'PRODUCT_NAME'
        account_col = find_column(critical_issues, 'account', 'id') or 'ACCOUNT_ID'
        date_col = find_column(critical_issues, 'transaction', 'date') or find_column(critical_issues, 'date') or 'TRANSACTION_DATE'
        city_col = find_column(critical_issues, 'service', 'city') or find_column(critical_issues, 'city') or 'SERVICE_CITY'
        region_col = find_column(critical_issues, 'service', 'region') or find_column(critical_issues, 'region') or 'SERVICE_REGION'
        order_final_col = find_column(critical_issues, 'order', 'final') or 'ORDER_FINAL_AMOUNT'
        billing_final_col = find_column(critical_issues, 'billing', 'final') or 'BILLING_FINAL_AMOUNT'
        
        for idx, (_, row) in enumerate(critical_issues.head(10).iterrows()):
            customer_val = row.get(customer_col, 'N/A')
            variance_val = row.get(variance_col, 0)
            status_val = row.get(status_col, 'Unknown')
            
            with st.expander(f"🔴 **CRITICAL-{idx+1}** | {customer_val} | ${variance_val:.2f} | {status_val}", expanded=idx < 3):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    transaction_date = row.get(date_col, None)
                    date_str = transaction_date.strftime('%Y-%m-%d %H:%M') if transaction_date and hasattr(transaction_date, 'strftime') else 'N/A'
                    
                    st.markdown(f"""
                    **Issue Details:**
                    - Product: {row.get(product_col, 'N/A')}
                    - Account: {row.get(account_col, 'N/A')}
                    - Transaction: {date_str}
                    - Region: {row.get(city_col, 'N/A')}, {row.get(region_col, 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Financial Impact:**
                    - Order Amount: ${row.get(order_final_col, 0):.2f}
                    - Billing Amount: ${row.get(billing_final_col, 0):.2f}
                    - Variance: ${variance_val:.2f}
                    - Risk Level: **{row.get(risk_col, 'Unknown')}**
                    """)
                
                with col3:
                    if st.button(f"🔍 Investigate", key=f"investigate_{idx}"):
                        st.info("Investigation workflow initiated...")
                    if st.button(f"🚀 Auto-Resolve", key=f"resolve_{idx}"):
                        st.success("Queued for automated resolution")
    
    elif st.session_state.alert_tab_index == 1:
        first_bill_col_tab = find_column(critical_issues, 'first', 'bill', 'flag') or find_column(critical_issues, 'first', 'bill')
        first_bill_issues = safe_filter(critical_issues, first_bill_col_tab, True) if first_bill_col_tab else critical_issues.iloc[0:0]
        render_first_bill_alerts(first_bill_issues)
    
    elif st.session_state.alert_tab_index == 2:
        product_col_tab = find_column(critical_issues, 'product', 'category') or find_column(critical_issues, 'product')
        mobile_issues = safe_filter(critical_issues, product_col_tab, 'Mobile') if product_col_tab else critical_issues.iloc[0:0]
        render_mobile_line_alerts(mobile_issues)
    
    elif st.session_state.alert_tab_index == 3:
        variance_col_hv = find_column(critical_issues, 'discount', 'variance') or find_column(critical_issues, 'variance')
        if variance_col_hv and variance_col_hv in critical_issues.columns:
            high_value_issues = critical_issues[critical_issues[variance_col_hv].abs() > 50]
        else:
            high_value_issues = critical_issues.iloc[0:0]
        render_high_value_alerts(high_value_issues)
    
    elif st.session_state.alert_tab_index == 4:
        stacking_col = find_column(critical_issues, 'stacking', 'violation', 'type')
        if stacking_col and stacking_col in critical_issues.columns:
            stacking_issues = critical_issues[critical_issues[stacking_col] != 'NONE']
        else:
            stacking_issues = critical_issues.iloc[0:0]
        render_stacking_violations(stacking_issues)

def render_first_bill_alerts(first_bill_df):
    """Render first bill specific alerts"""
    if first_bill_df.empty:
        st.success("✅ All first bills processed successfully")
        return
    
    st.error(f"⚠️ {len(first_bill_df)} first bill issues detected - Customer experience impact")
    
    # Find columns dynamically
    customer_col = find_column(first_bill_df, 'customer', 'id') or 'CUSTOMER_ID'
    product_col = find_column(first_bill_df, 'product', 'name') or 'PRODUCT_NAME'
    status_col = find_column(first_bill_df, 'reconciliation', 'status') or find_column(first_bill_df, 'status') or 'RECONCILIATION_STATUS'
    variance_col = find_column(first_bill_df, 'discount', 'variance') or find_column(first_bill_df, 'variance') or 'DISCOUNT_VARIANCE'
    
    for idx, (_, row) in enumerate(first_bill_df.head(5).iterrows()):
        st.markdown(f"""
        <div class="critical-card">
            <h4>🆕 New Customer Issue #{idx+1}</h4>
            <p><strong>Customer:</strong> {row.get(customer_col, 'N/A')} | <strong>Product:</strong> {row.get(product_col, 'N/A')}</p>
            <p><strong>Issue:</strong> {row.get(status_col, 'Unknown')} | <strong>Impact:</strong> ${row.get(variance_col, 0):.2f}</p>
            <p><strong>⏰ Resolution SLA:</strong> 4 hours remaining</p>
        </div>
        """, unsafe_allow_html=True)

def render_mobile_line_alerts(mobile_df):
    """Render mobile line specific alerts"""
    # Find columns dynamically
    status_col = find_column(mobile_df, 'reconciliation', 'status') or find_column(mobile_df, 'status')
    line_col = find_column(mobile_df, 'line', 'number') or 'LINE_NUMBER'
    account_col = find_column(mobile_df, 'account', 'id') or 'ACCOUNT_ID'
    
    duplicate_lines = safe_filter(mobile_df, status_col, 'DUPLICATE_LINE_NUMBER') if status_col else mobile_df.iloc[0:0]
    
    if duplicate_lines.empty:
        st.success("✅ No mobile line conflicts detected")
        return
    
    st.error(f"📱 {len(duplicate_lines)} mobile line conflicts require immediate resolution")
    
    # Group by line number to show conflicts
    if line_col and line_col in duplicate_lines.columns:
        line_conflicts = duplicate_lines.groupby(line_col).size().reset_index(name='count')
        
        for _, conflict in line_conflicts.iterrows():
            conflict_records = duplicate_lines[duplicate_lines[line_col] == conflict[line_col]]
            accounts = conflict_records[account_col].tolist() if account_col in conflict_records.columns else ['N/A']
            
            st.markdown(f"""
            <div class="warning-card">
                <h4>📱 Line Conflict: {conflict[line_col]}</h4>
                <p><strong>Affected Accounts:</strong> {conflict['count']} accounts using same line number</p>
                <p><strong>Accounts:</strong> {', '.join(accounts)}</p>
            </div>
            """, unsafe_allow_html=True)

def render_high_value_alerts(high_value_df):
    """Render high value variance alerts"""
    if high_value_df.empty:
        st.success("✅ No high-value variances detected")
        return
    
    # Find columns dynamically
    variance_col = find_column(high_value_df, 'discount', 'variance') or find_column(high_value_df, 'variance') or 'DISCOUNT_VARIANCE'
    customer_col = find_column(high_value_df, 'customer', 'id') or 'CUSTOMER_ID'
    product_col = find_column(high_value_df, 'product', 'name') or 'PRODUCT_NAME'
    status_col = find_column(high_value_df, 'reconciliation', 'status') or find_column(high_value_df, 'status') or 'RECONCILIATION_STATUS'
    
    total_risk = high_value_df[variance_col].abs().sum() if variance_col in high_value_df.columns else 0
    st.error(f"💰 ${total_risk:,.2f} in high-value variances requiring review")
    
    for idx, (_, row) in enumerate(high_value_df.head(5).iterrows()):
        variance_val = row.get(variance_col, 0)
        st.markdown(f"""
        <div class="critical-card">
            <h4>💰 High-Value Issue #{idx+1}</h4>
            <p><strong>Customer:</strong> {row.get(customer_col, 'N/A')} | <strong>Variance:</strong> ${variance_val:,.2f}</p>
            <p><strong>Product:</strong> {row.get(product_col, 'N/A')} | <strong>Status:</strong> {row.get(status_col, 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)

def render_stacking_violations(stacking_df):
    """Render promotion stacking violation alerts"""
    if stacking_df.empty:
        st.success("✅ No promotion stacking violations detected")
        return
    
    # Find columns dynamically
    stacking_col = find_column(stacking_df, 'stacking', 'violation', 'type')
    customer_col = find_column(stacking_df, 'customer', 'id') or 'CUSTOMER_ID'
    product_col = find_column(stacking_df, 'product', 'name') or 'PRODUCT_NAME'
    revenue_protection_col = find_column(stacking_df, 'revenue', 'protection', 'value')
    
    total_protected = stacking_df[revenue_protection_col].sum() if revenue_protection_col and revenue_protection_col in stacking_df.columns else 0
    st.error(f"🛡️ {len(stacking_df)} revenue protection violations - ${total_protected:,.2f} protected")
    
    # Group by violation type
    if stacking_col and stacking_col in stacking_df.columns:
        violation_types = stacking_df[stacking_col].value_counts()
        
        for violation_type, count in violation_types.items():
            if violation_type != 'NONE':
                violation_subset = stacking_df[stacking_df[stacking_col] == violation_type]
                protected_value = violation_subset[revenue_protection_col].sum() if revenue_protection_col and revenue_protection_col in violation_subset.columns else 0
                
                st.markdown(f"""
                <div class="warning-card">
                    <h4>🛡️ {violation_type.replace('_', ' ').title()}</h4>
                    <p><strong>Cases:</strong> {count} violations detected</p>
                    <p><strong>Revenue Protected:</strong> ${protected_value:,.2f}</p>
                    <p><strong>Action:</strong> Automatic stacking prevention applied</p>
                </div>
                """, unsafe_allow_html=True)

def render_cortex_ai_center(df, recommendations):
    """Render Cortex AI recommendations and insights"""
    st.markdown("## 🤖 **Cortex AI Intelligence Center**")
    
    # Initialize session state for AI tabs
    if 'ai_tab_index' not in st.session_state:
        st.session_state.ai_tab_index = 0
    
    # Create tabs with session state management
    tab_names = ["💡 Recommendations", "🔮 Predictive Insights", "💬 Natural Language Query", "🎯 Pattern Analysis"]
    
    # Create tab buttons that maintain state
    tab_cols = st.columns(len(tab_names))
    for i, (col, tab_name) in enumerate(zip(tab_cols, tab_names)):
        with col:
            button_style = "primary" if st.session_state.ai_tab_index == i else "secondary"
            if st.button(tab_name, key=f"ai_tab_{i}", use_container_width=True, type=button_style):
                st.session_state.ai_tab_index = i
                st.rerun()
    
    st.markdown("---")
    
    # Render content based on active tab
    if st.session_state.ai_tab_index == 0:
        st.markdown("### AI-Powered Remediation Recommendations")
        
        if not recommendations:
            st.info("✨ No critical recommendations at this time. System operating optimally.")
        else:
            for idx, rec in enumerate(recommendations):
                priority_color = {
                    'CRITICAL': '#ef4444',
                    'HIGH': '#f59e0b', 
                    'MEDIUM': '#3b82f6',
                    'LOW': '#10b981'
                }.get(rec['priority'], '#6b7280')
                
                st.markdown(f"""
                <div class="cortex-recommendation">
                    <h4>🎯 {rec['title']} <span style="background: {priority_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{rec['priority']}</span></h4>
                    <p><strong>Insight:</strong> {rec['description']}</p>
                    <p><strong>Impact:</strong> {rec['impact']}</p>
                    <p><strong>Recommended Action:</strong> {rec['action']}</p>
                    <p><strong>💰 Estimated Savings:</strong> {rec['estimated_savings']} | <strong>⏱️ Timeline:</strong> {rec['implementation_time']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ Implement", key=f"implement_{idx}"):
                        st.success(f"Implementation initiated for: {rec['title']}")
                with col2:
                    if st.button(f"📋 Create Ticket", key=f"ticket_{idx}"):
                        st.info(f"Support ticket created for: {rec['title']}")
                with col3:
                    if st.button(f"📊 Deep Dive", key=f"analyze_{idx}"):
                        st.info(f"Detailed analysis queued for: {rec['title']}")
    
    elif st.session_state.ai_tab_index == 1:
        render_predictive_insights(df)
    
    elif st.session_state.ai_tab_index == 2:
        render_natural_language_interface(df)
    
    elif st.session_state.ai_tab_index == 3:
        render_pattern_analysis(df)

def render_predictive_insights(df):
    """Render predictive analytics insights"""
    st.markdown("### 🔮 Predictive Analytics & Forecasting")
    
    # Trend analysis
    if not df.empty:
        # Find date and variance columns dynamically
        date_col = find_column(df, 'transaction', 'date') or find_column(df, 'date')
        variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
        
        if date_col and variance_col and date_col in df.columns and variance_col in df.columns:
            # Ensure date column is datetime
            df_trend = df.copy()
            if not pd.api.types.is_datetime64_any_dtype(df_trend[date_col]):
                try:
                    df_trend[date_col] = pd.to_datetime(df_trend[date_col])
                except:
                    # If conversion fails, create simulated data
                    df_trend = None
            
            if df_trend is not None:
                # Group by date
                daily_stats = df_trend.groupby(df_trend[date_col].dt.date).agg({
                    variance_col: ['mean', 'sum', 'count']
                }).reset_index()
                
                # Create trend chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_stats[date_col],
                    y=daily_stats[(variance_col, 'mean')],
                    mode='lines+markers',
                    name='Average Daily Variance',
                    line=dict(color='#3b82f6', width=3)
                ))
                
                fig.update_layout(
                    title="📈 Variance Trend Prediction (Next 7 Days)",
                    xaxis_title="Date",
                    yaxis_title="Average Variance ($)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback: create simulated trend data
                dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
                trend_values = np.random.uniform(5, 25, len(dates))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=trend_values,
                    mode='lines+markers',
                    name='Average Daily Variance (Simulated)',
                    line=dict(color='#3b82f6', width=3)
                ))
                
                fig.update_layout(
                    title="📈 Variance Trend Prediction (Simulated Data)",
                    xaxis_title="Date",
                    yaxis_title="Average Variance ($)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            # No valid date/variance columns found - show simulated data
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            trend_values = np.random.uniform(5, 25, len(dates))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend_values,
                mode='lines+markers',
                name='Average Daily Variance (Demo)',
                line=dict(color='#3b82f6', width=3)
            ))
            
            fig.update_layout(
                title="📈 Variance Trend Prediction (Demo Data)",
                xaxis_title="Date", 
                yaxis_title="Average Variance ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Predictive alerts
        st.markdown("""
        <div class="investigation-panel">
            <h4>🚨 Predictive Alerts</h4>
            <ul>
                <li><strong>Revenue Risk Forecast:</strong> 15% increase in high-risk variances expected next week</li>
                <li><strong>Seasonal Pattern:</strong> Mobile line issues typically spike on Mondays (deployment recommendation)</li>
                <li><strong>Regional Trend:</strong> Northeast region showing improving reconciliation rates (+8% this month)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_natural_language_interface(df):
    """Render natural language query interface"""
    st.markdown("### 💬 Ask Cortex Analyst")
    
    # Enhanced sample queries with new use cases
    sample_queries = [
        "Which customers are at risk for billing issues before next invoice generation?",
        "What promotion stacking violations are we preventing to protect revenue?", 
        "How is our first bill accuracy performing against the 95% target?",
        "Which customer segments are most prone to billing issues?",
        "What mobile line conflicts need immediate attention?",
        "Which promotion timing mismatches require immediate intervention?",
        "Show me the executive summary of revenue protection metrics",
        "Find high-value customers with churn risk above 30%",
        "What cycle timing variances are causing billing delays?",
        "Which business priority classifications need executive attention?"
    ]
    
    selected_query = st.selectbox("Choose a sample query or type your own:", [""] + sample_queries)
    
    user_query = st.text_input("Ask a question about the reconciliation data:", 
                               value=selected_query if selected_query else "",
                               placeholder="e.g., Show me high-risk items from last week...")
    
    if st.button("🔍 Query Cortex Analyst", use_container_width=True) and user_query:
        # Simulate Cortex response
        with st.spinner("🤖 Cortex Analyst processing your query..."):
            time.sleep(1.5)  # Simulate processing
            
            # Generate enhanced mock response based on query keywords
            if "first bill" in user_query.lower():
                response = analyze_first_bill_query(df)
            elif "mobile" in user_query.lower():
                response = analyze_mobile_query(df)
            elif "revenue" in user_query.lower() or "protection" in user_query.lower():
                response = analyze_revenue_query(df)
            elif "stacking" in user_query.lower() or "violation" in user_query.lower():
                response = analyze_stacking_query(df)
            elif "churn" in user_query.lower() or "customer segment" in user_query.lower():
                response = analyze_customer_intelligence_query(df)
            elif "timing" in user_query.lower() or "cycle" in user_query.lower():
                response = analyze_timing_query(df)
            elif "business priority" in user_query.lower() or "classification" in user_query.lower():
                response = analyze_business_priority_query(df)
            else:
                response = generate_general_response(df)
            
            st.markdown(f"""
            <div class="cortex-recommendation">
                <h4>🤖 Cortex Analyst Response</h4>
                <p>{response}</p>
            </div>
            """, unsafe_allow_html=True)

def analyze_first_bill_query(df):
    """Generate response for first bill related queries"""
    first_bill_col = find_column(df, 'first', 'bill', 'flag') or find_column(df, 'first', 'bill')
    status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
    variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
    
    if first_bill_col and status_col and first_bill_col in df.columns and status_col in df.columns:
        first_bill_issues = df[(df[first_bill_col] == True) & (df[status_col] != 'MATCHED')]
        if first_bill_issues.empty:
            return "✅ Excellent news! All first bills processed successfully with no issues detected."
        
        total_issues = len(first_bill_issues)
        if variance_col and variance_col in first_bill_issues.columns:
            avg_variance = first_bill_issues[variance_col].abs().mean()
        else:
            avg_variance = 15.50  # Demo value
    else:
        # Demo response when columns not found
        total_issues = 12
        avg_variance = 18.75
    
    return f"Found {total_issues} first bill issues with an average variance of ${avg_variance:.2f}. The Northeast region accounts for 35% of these issues, primarily related to promo timing mismatches. Recommendation: Implement pre-billing validation checks to catch these before customer impact."

def analyze_mobile_query(df):
    """Generate response for mobile related queries"""
    product_col = find_column(df, 'product', 'category') or find_column(df, 'product')
    status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
    account_col = find_column(df, 'account', 'id')
    
    if product_col and status_col and product_col in df.columns and status_col in df.columns:
        mobile_issues = df[(df[product_col] == 'Mobile') & (df[status_col] == 'DUPLICATE_LINE_NUMBER')]
        
        if mobile_issues.empty:
            return "✅ No mobile line conflicts detected. All mobile line numbers are properly assigned."
        
        duplicate_count = len(mobile_issues)
        affected_accounts = mobile_issues[account_col].nunique() if account_col and account_col in mobile_issues.columns else duplicate_count
    else:
        # Demo response when columns not found
        duplicate_count = 8
        affected_accounts = 6
    
    return f"Detected {duplicate_count} mobile line conflicts affecting {affected_accounts} accounts. The 'Xfinity Mobile Unlimited' plan shows highest duplicate rate at 12%. Immediate action required to prevent billing disputes."

def analyze_revenue_query(df):
    """Generate response for revenue impact queries"""
    variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
    risk_col = find_column(df, 'risk', 'level') or find_column(df, 'risk')
    
    if variance_col and variance_col in df.columns:
        total_variance = df[variance_col].abs().sum()
        if risk_col and risk_col in df.columns:
            high_risk_variance = df[df[risk_col].isin(['HIGH', 'CRITICAL'])][variance_col].abs().sum()
        else:
            high_risk_variance = total_variance * 0.3  # Estimate
    else:
        total_variance = 125000  # Demo value
        high_risk_variance = 76250  # Demo value
    
    return f"Total revenue variance: ${total_variance:,.2f} with ${high_risk_variance:,.2f} (61%) in high-risk categories. Seattle shows highest variance concentration at ${high_risk_variance * 0.18:,.2f}. Promo timing mismatches contribute 43% of total variance."

def analyze_stacking_query(df):
    """Generate response for stacking violation queries"""
    stacking_col = find_column(df, 'stacking', 'violation', 'type')
    revenue_protection_col = find_column(df, 'revenue', 'protection', 'value')
    
    if stacking_col and stacking_col in df.columns:
        violations = df[df[stacking_col] != 'NONE']
        total_protected = violations[revenue_protection_col].sum() if revenue_protection_col and revenue_protection_col in violations.columns else 0
        violation_types = violations[stacking_col].value_counts()
    else:
        violations = pd.DataFrame()
        total_protected = 45250  # Demo value
        violation_types = pd.Series({'MOBILE_INTERNET_CONFLICT': 8, 'BUNDLE_PROMO_OVERLAP': 5})
    
    return f"Detected {len(violations)} promotion stacking violations with ${total_protected:,.2f} in revenue protection. Top violation: {violation_types.index[0] if not violation_types.empty else 'Mobile-Internet conflicts'} ({violation_types.iloc[0] if not violation_types.empty else 8} cases). Automatic prevention rules successfully blocked potential revenue cannibalization."

def analyze_customer_intelligence_query(df):
    """Generate response for customer intelligence queries"""
    churn_col = find_column(df, 'churn', 'risk', 'score')
    segment_col = find_column(df, 'customer', 'segment')
    
    if churn_col and churn_col in df.columns:
        high_churn = df[df[churn_col] > 0.25]
        if segment_col and segment_col in df.columns:
            segment_analysis = high_churn[segment_col].value_counts()
            top_segment = segment_analysis.index[0] if not segment_analysis.empty else 'Price_Sensitive'
        else:
            top_segment = 'Price_Sensitive'
    else:
        high_churn = pd.DataFrame()
        top_segment = 'Price_Sensitive'
    
    return f"Identified {len(high_churn)} customers with churn risk >25%. The '{top_segment}' segment shows highest risk concentration (38% of high-risk customers). Proactive retention campaigns recommended for high-value customers with billing issues."

def analyze_timing_query(df):
    """Generate response for timing analysis queries"""
    timing_col = find_column(df, 'cycle', 'timing', 'variance')
    
    if timing_col and timing_col in df.columns:
        timing_issues = df[df[timing_col].abs() > 1]
        avg_delay = timing_issues[timing_col].abs().mean() if not timing_issues.empty else 2.3
    else:
        timing_issues = pd.DataFrame()
        avg_delay = 2.3
    
    return f"Found {len(timing_issues)} cycle timing variances causing billing delays. Average delay: {avg_delay:.1f} cycles. West region accounts for 35% of timing issues. Recommendation: Implement real-time order-to-billing synchronization to reduce cycle drift."

def analyze_business_priority_query(df):
    """Generate response for business priority classification queries"""
    priority_col = find_column(df, 'business', 'priority')
    classification_col = find_column(df, 'business', 'issue', 'classification')
    
    if priority_col and priority_col in df.columns:
        priority_dist = df[priority_col].value_counts()
        critical_count = priority_dist.get('CRITICAL_FIRST_BILL', 0) + priority_dist.get('HIGH_CHURN_RISK', 0)
    else:
        priority_dist = pd.Series({'REVENUE_PROTECTION': 45, 'CRITICAL_FIRST_BILL': 23, 'HIGH_CHURN_RISK': 18})
        critical_count = 41
    
    return f"Business priority distribution shows {critical_count} cases requiring executive attention. 'Revenue Protection' leads with {priority_dist.get('REVENUE_PROTECTION', 45)} cases. Critical first bill issues: {priority_dist.get('CRITICAL_FIRST_BILL', 23)} cases. Immediate action recommended for high-churn risk customers."

def generate_general_response(df):
    """Generate general response for other queries"""
    status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
    if status_col and status_col in df.columns:
        match_rate = len(df[df[status_col] == 'MATCHED']) / len(df) * 100
    else:
        match_rate = 95.0  # Default for demo
    return f"Current reconciliation performance: {match_rate:.1f}% match rate across {len(df):,} transactions. Enhanced with business intelligence: customer segmentation, stacking prevention, and predictive analytics. System is operating {'within' if match_rate > 95 else 'below'} target parameters with comprehensive revenue protection."

def render_pattern_analysis(df):
    """Render pattern analysis and insights"""
    st.markdown("### 🎯 Intelligent Pattern Recognition")
    
    if df.empty:
        st.info("No data available for pattern analysis")
        return
    
    # Find columns dynamically
    region_col = find_column(df, 'service', 'region') or find_column(df, 'region')
    status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
    date_col = find_column(df, 'transaction', 'date') or find_column(df, 'date')
    
    # Geographic pattern analysis
    if region_col and status_col and region_col in df.columns and status_col in df.columns:
        try:
            geo_analysis = df.groupby([region_col, status_col]).size().unstack(fill_value=0)
            
            fig = px.bar(
                geo_analysis.reset_index(),
                x=region_col,
                y=geo_analysis.columns,
                title="🗺️ Geographic Issue Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Geographic pattern analysis unavailable with current data structure")
    else:
        st.info("Geographic columns not found - showing simulated pattern")
        # Create simulated geographic data
        regions = ['Northeast', 'Southeast', 'Midwest', 'West', 'Southwest']
        statuses = ['MATCHED', 'PROMO_NOT_APPLIED', 'DUPLICATE_LINE_NUMBER', 'PROMO_TIMING_MISMATCH']
        sim_data = []
        for region in regions:
            for status in statuses:
                sim_data.append({'Region': region, 'Status': status, 'Count': np.random.randint(10, 100)})
        
        sim_df = pd.DataFrame(sim_data)
        fig = px.bar(sim_df, x='Region', y='Count', color='Status', 
                    title="🗺️ Geographic Issue Distribution (Simulated)",
                    color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time-based patterns
    if date_col and status_col and date_col in df.columns and status_col in df.columns:
        try:
            # Ensure date column is datetime
            df_time = df.copy()
            if not pd.api.types.is_datetime64_any_dtype(df_time[date_col]):
                df_time[date_col] = pd.to_datetime(df_time[date_col])
            
            df_time['HOUR'] = df_time[date_col].dt.hour
            hourly_pattern = df_time.groupby('HOUR')[status_col].apply(lambda x: (x != 'MATCHED').sum()).reset_index()
            
            fig2 = px.line(
                hourly_pattern,
                x='HOUR',
                y=status_col,
                title="⏰ Hourly Issue Pattern Detection",
                labels={status_col: 'Number of Issues', 'HOUR': 'Hour of Day'}
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.info("Time pattern analysis unavailable - showing simulated pattern")
            # Create simulated hourly data
            hours = list(range(24))
            issues = [np.random.randint(5, 50) for _ in hours]
            sim_time_df = pd.DataFrame({'Hour': hours, 'Issues': issues})
            
            fig2 = px.line(sim_time_df, x='Hour', y='Issues',
                          title="⏰ Hourly Issue Pattern Detection (Simulated)",
                          labels={'Issues': 'Number of Issues', 'Hour': 'Hour of Day'})
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Date/time columns not found - showing simulated pattern")
        # Create simulated hourly data
        hours = list(range(24))
        issues = [np.random.randint(5, 50) for _ in hours]
        sim_time_df = pd.DataFrame({'Hour': hours, 'Issues': issues})
        
        fig2 = px.line(sim_time_df, x='Hour', y='Issues',
                      title="⏰ Hourly Issue Pattern Detection (Demo)",
                      labels={'Issues': 'Number of Issues', 'Hour': 'Hour of Day'})
        st.plotly_chart(fig2, use_container_width=True)
    
    # Pattern insights
    st.markdown("""
    <div class="investigation-panel">
        <h4>🔍 Key Pattern Insights</h4>
        <ul>
            <li><strong>Peak Issue Time:</strong> 2-4 PM (lunch break system load)</li>
            <li><strong>Regional Hotspot:</strong> West region shows 23% higher variance rates</li>
            <li><strong>Product Correlation:</strong> Bundle products have 3x higher promo timing issues</li>
            <li><strong>Seasonal Impact:</strong> Month-end shows 45% increase in reconciliation volume</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_operations_workflow(df, ml_df):
    """Render the operations workflow section"""
    st.markdown("## ⚙️ **Automated Operations Workflow**")
    
    # Initialize session state for workflow tabs
    if 'workflow_tab_index' not in st.session_state:
        st.session_state.workflow_tab_index = 0
    
    # Create tabs with session state management
    workflow_tab_names = ["🔄 Live Processing", "🤖 Auto-Resolution", "📋 Case Management", "📈 Performance Metrics"]
    
    # Create tab buttons that maintain state
    workflow_tab_cols = st.columns(len(workflow_tab_names))
    for i, (col, tab_name) in enumerate(zip(workflow_tab_cols, workflow_tab_names)):
        with col:
            button_style = "primary" if st.session_state.workflow_tab_index == i else "secondary"
            if st.button(tab_name, key=f"workflow_tab_{i}", use_container_width=True, type=button_style):
                st.session_state.workflow_tab_index = i
                st.rerun()
    
    st.markdown("---")
    
    # Render content based on active tab
    if st.session_state.workflow_tab_index == 0:
        render_live_processing(df)
    
    elif st.session_state.workflow_tab_index == 1:
        render_auto_resolution(df)
    
    elif st.session_state.workflow_tab_index == 2:
        render_case_management(df)
    
    elif st.session_state.workflow_tab_index == 3:
        render_performance_metrics(df, ml_df)

def render_live_processing(df):
    """Render live processing status"""
    st.markdown("### 🔄 Real-Time Processing Status")
    
    # Simulate live processing metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Processing Queue", "47", delta="-12")
    
    with col2:
        st.metric("Throughput/Min", "156", delta="8")
    
    with col3:
        st.metric("Auto-Resolved", "89%", delta="2%")
    
    with col4:
        st.metric("SLA Compliance", "96.8%", delta="1.2%")
    
    # Processing timeline
    st.markdown("#### ⏱️ Recent Processing Activity")
    
    timeline_data = [
        {"time": "14:32:15", "action": "Processed batch 2847", "status": "success", "count": 234},
        {"time": "14:31:45", "action": "Auto-resolved mobile line conflict", "status": "warning", "count": 3},
        {"time": "14:31:20", "action": "Escalated first bill issues", "status": "error", "count": 7},
        {"time": "14:30:58", "action": "Applied ML anomaly scoring", "status": "info", "count": 234},
        {"time": "14:30:12", "action": "Cortex recommendations generated", "status": "success", "count": 5}
    ]
    
    for item in timeline_data:
        status_colors = {
            "success": "#10b981",
            "warning": "#f59e0b", 
            "error": "#ef4444",
            "info": "#3b82f6"
        }
        
        st.markdown(f"""
        <div class="timeline-item" style="border-left-color: {status_colors[item['status']]}">
            <strong>{item['time']}</strong> - {item['action']} ({item['count']} items)
        </div>
        """, unsafe_allow_html=True)

def render_auto_resolution(df):
    """Render auto-resolution capabilities"""
    st.markdown("### 🤖 Automated Resolution Engine")
    
    # Find columns dynamically
    risk_col = find_column(df, 'risk', 'level') or find_column(df, 'risk')
    variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
    status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
    
    # Auto-resolvable issues
    auto_resolvable_mask = pd.Series([True] * len(df), index=df.index)
    
    if risk_col and risk_col in df.columns:
        auto_resolvable_mask &= (df[risk_col] == 'LOW')
    
    if variance_col and variance_col in df.columns:
        auto_resolvable_mask &= (df[variance_col].abs() <= 10)
    
    if status_col and status_col in df.columns:
        auto_resolvable_mask &= df[status_col].isin(['MINOR_VARIANCE', 'PRORATION_ADJUSTMENT'])
    
    auto_resolvable = df[auto_resolvable_mask]
    
    col1, col2 = st.columns(2)
    
    with col1:
        estimated_savings = auto_resolvable[variance_col].abs().sum() if variance_col and variance_col in auto_resolvable.columns and not auto_resolvable.empty else 0
        
        st.markdown(f"""
        <div class="success-card">
            <h4>✅ Auto-Resolution Eligible</h4>
            <p><strong>{len(auto_resolvable)}</strong> items can be automatically resolved</p>
            <p><strong>Estimated Savings:</strong> ${estimated_savings:,.2f}</p>
            <p><strong>Processing Time:</strong> ~15 minutes</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Execute Auto-Resolution", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(101):
                progress_bar.progress(i)
                status_text.text(f'Processing auto-resolution... {i}%')
                time.sleep(0.02)
            
            st.success(f"✅ Successfully auto-resolved {len(auto_resolvable)} items!")
    
    with col2:
        st.markdown("#### 🎯 Resolution Rules Engine")
        
        # Calculate resolution rule counts safely
        small_variance_count = len(auto_resolvable[auto_resolvable[variance_col].abs() < 5]) if variance_col and variance_col in auto_resolvable.columns and not auto_resolvable.empty else 0
        proration_count = len(safe_filter(auto_resolvable, status_col, 'PRORATION_ADJUSTMENT')) if status_col and not auto_resolvable.empty else 0
        
        resolution_rules = [
            {"condition": "Variance < $5 AND Risk = LOW", "action": "Auto-credit adjustment", "count": small_variance_count},
            {"condition": "Proration + First Month", "action": "Apply pro-rata logic", "count": proration_count},
            {"condition": "Duplicate Promotion Code", "action": "Remove duplicate, retain best", "count": 12},
            {"condition": "Bundle Discount Overlap", "action": "Apply hierarchy rules", "count": 8}
        ]
        
        for rule in resolution_rules:
            st.markdown(f"""
            <div style="background: #f8fafc; padding: 0.5rem; margin: 0.25rem 0; border-radius: 4px; border-left: 3px solid #10b981;">
                <strong>Rule:</strong> {rule['condition']}<br>
                <strong>Action:</strong> {rule['action']}<br>
                <strong>Applicable:</strong> {rule['count']} items
            </div>
            """, unsafe_allow_html=True)

def render_case_management(df):
    """Render case management interface"""
    st.markdown("### 📋 Case Management & Investigation")
    
    # Find columns dynamically
    risk_col = find_column(df, 'risk', 'level') or find_column(df, 'risk')
    first_bill_col = find_column(df, 'first', 'bill', 'flag') or find_column(df, 'first', 'bill')
    variance_col = find_column(df, 'discount', 'variance') or find_column(df, 'variance')
    
    # Critical cases requiring manual review
    manual_review_mask = pd.Series([False] * len(df), index=df.index)
    
    # Add high/critical risk cases
    if risk_col and risk_col in df.columns:
        manual_review_mask |= df[risk_col].isin(['HIGH', 'CRITICAL'])
    
    # Add first bill cases
    if first_bill_col and first_bill_col in df.columns:
        manual_review_mask |= (df[first_bill_col] == True)
    
    # Add high variance cases
    if variance_col and variance_col in df.columns:
        manual_review_mask |= (df[variance_col].abs() > 20)
    
    manual_review = df[manual_review_mask]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"#### 🔍 Active Investigations ({len(manual_review)} cases)")
        
        # Case priority queue - find additional columns
        record_col = find_column(manual_review, 'record', 'id') or find_column(manual_review, 'order', 'id')
        customer_col = find_column(manual_review, 'customer', 'id')
        status_col = find_column(manual_review, 'reconciliation', 'status') or find_column(manual_review, 'status')
        product_col = find_column(manual_review, 'product', 'name')
        
        # Sort by available columns
        sort_cols = []
        sort_ascending = []
        if risk_col and risk_col in manual_review.columns:
            sort_cols.append(risk_col)
            sort_ascending.append(False)
        if variance_col and variance_col in manual_review.columns:
            sort_cols.append(variance_col)
            sort_ascending.append(False)
        
        if sort_cols:
            priority_queue = manual_review.sort_values(sort_cols, ascending=sort_ascending).head(10)
        else:
            priority_queue = manual_review.head(10)
        
        for idx, (_, case) in enumerate(priority_queue.iterrows()):
            # Safe value extraction
            record_val = case.get(record_col, f"REC-{idx+1000}") if record_col else f"REC-{idx+1000}"
            case_id = f"CASE-{record_val.split('-')[1] if isinstance(record_val, str) and '-' in record_val else idx+1000}"
            customer_val = case.get(customer_col, 'N/A') if customer_col else 'N/A'
            variance_val = case.get(variance_col, 0) if variance_col else 0
            risk_val = case.get(risk_col, 'Unknown') if risk_col else 'Unknown'
            
            with st.expander(f"🎯 **{case_id}** | {customer_val} | ${variance_val:.2f} | {risk_val}", expanded=idx < 2):
                
                investigation_col1, investigation_col2 = st.columns(2)
                
                with investigation_col1:
                    status_val = case.get(status_col, 'Unknown') if status_col else 'Unknown'
                    product_val = case.get(product_col, 'N/A') if product_col else 'N/A'
                    first_bill_val = case.get(first_bill_col, False) if first_bill_col else False
                    
                    st.markdown(f"""
                    **Case Details:**
                    - Issue Type: {status_val}
                    - Product: {product_val}
                    - Customer Impact: {'HIGH - First Bill' if first_bill_val else 'Standard'}
                    - Financial Impact: ${variance_val:.2f}
                    """)
                
                with investigation_col2:
                    st.markdown(f"""
                    **Investigation Status:**
                    - Assigned: Revenue Team Alpha
                    - SLA: {'⚠️ 2hrs remaining' if risk_val == 'CRITICAL' else '✅ 18hrs remaining'}
                    - Next Action: {'Customer notification' if first_bill_val else 'System adjustment'}
                    """)
                
                # Action buttons
                action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                
                with action_col1:
                    if st.button("📞 Contact Customer", key=f"contact_{idx}"):
                        st.info("Customer contact initiated")
                
                with action_col2:
                    if st.button("💳 Issue Credit", key=f"credit_{idx}"):
                        st.success("Credit adjustment processed")
                
                with action_col3:
                    if st.button("🔄 Escalate", key=f"escalate_{idx}"):
                        st.warning("Case escalated to L2 support")
                
                with action_col4:
                    if st.button("✅ Resolve", key=f"resolve_{idx}"):
                        st.success("Case marked as resolved")
    
    with col2:
        st.markdown("#### 📊 Case Metrics")
        
        # Case statistics
        total_cases = len(manual_review)
        critical_cases = len(safe_filter(manual_review, risk_col, 'CRITICAL')) if risk_col else 0
        first_bill_cases = len(safe_filter(manual_review, first_bill_col, True)) if first_bill_col else 0
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_cases}</div>
            <div style="font-weight: bold;">Open Cases</div>
            <div class="metric-delta">{critical_cases} Critical | {first_bill_cases} First Bill</div>
        </div>
        """, unsafe_allow_html=True)
        
        # SLA tracking
        st.markdown("#### ⏱️ SLA Performance")
        sla_data = {
            'Critical (4hr)': {'target': 95, 'actual': 96.8, 'color': '#10b981'},
            'High (24hr)': {'target': 98, 'actual': 94.2, 'color': '#f59e0b'},
            'Medium (48hr)': {'target': 99, 'actual': 99.1, 'color': '#10b981'}
        }
        
        for sla_type, data in sla_data.items():
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <strong>{sla_type}:</strong> {data['actual']}% 
                <span style="color: {data['color']}">{'✅' if data['actual'] >= data['target'] else '⚠️'}</span>
            </div>
            """, unsafe_allow_html=True)

def render_performance_metrics(df, ml_df):
    """Render performance metrics and analytics"""
    st.markdown("### 📈 Performance Analytics & Trends")
    
    if df.empty:
        st.info("No performance data available")
        return
    
    # Create performance dashboard
    metric_col1, metric_col2 = st.columns(2)
    
    with metric_col1:
        # Resolution time trends
        fig1 = go.Figure()
        
        # Simulate resolution time data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        resolution_times = np.random.uniform(2, 8, len(dates))  # hours
        
        fig1.add_trace(go.Scatter(
            x=dates,
            y=resolution_times,
            mode='lines+markers',
            name='Avg Resolution Time',
            line=dict(color='#3b82f6', width=3)
        ))
        
        fig1.add_hline(y=4, line_dash="dash", line_color="red", annotation_text="SLA Target: 4hrs")
        
        fig1.update_layout(
            title="⏱️ Average Resolution Time Trend",
            xaxis_title="Date",
            yaxis_title="Hours",
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with metric_col2:
        # Issue type distribution
        status_counts = df['RECONCILIATION_STATUS'].value_counts()
        
        fig2 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="🎯 Issue Type Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Performance summary
    st.markdown("#### 📊 Monthly Performance Summary")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.metric("Cases Resolved", "2,847", delta="156 (+5.8%)")
    
    with perf_col2:
        st.metric("Revenue Protected", "$1.2M", delta="$187K (+18%)")
    
    with perf_col3:
        st.metric("Customer Satisfaction", "94.2%", delta="2.1%")
    
    with perf_col4:
        st.metric("Process Efficiency", "87%", delta="4%")

# === MAIN APPLICATION ===

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'live_data' not in st.session_state:
        st.session_state.live_data = False
    if 'nav' not in st.session_state:
        st.session_state.nav = 'Command Center'
    
    # Sidebar: data source control
    with st.sidebar:
        st.markdown("## 🔌 Data Source")
        prefer_live = st.toggle("Use Snowflake (live)", value=True, help="Disable to use enhanced sample data")
        test_conn = st.button("🔍 Test Snowflake Connection")
    
    # Load data
    with st.spinner("🔄 Loading reconciliation data..."):
        df, ml_df, is_live, live_error, meta = load_snowflake_data(prefer_live=prefer_live)
        st.session_state.live_data = is_live
        
        # Generate ML insights (if no external anomaly table)
        if not df.empty:
            ml_df = generate_ml_insights(df)
        
        # Sidebar: report connection status
        with st.sidebar:
            if is_live:
                st.success(f"✅ Live Snowflake data loaded from {meta.get('source', 'UNKNOWN')} (rows: {len(df):,})")
            else:
                st.info("🎲 Using enhanced sample data")
                if live_error:
                    st.caption(f"Live error: {live_error}")
            
            if test_conn:
                sess, err = get_snowflake_session()
                if sess is not None:
                    st.success("✅ Snowflake session OK")
                else:
                    st.error("❌ Unable to establish Snowflake session")
                    if err:
                        st.caption(err)
        
        # Calculate priority issues for recommendations with dynamic column detection
        if not df.empty:
            status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
            first_bill_col = find_column(df, 'first', 'bill', 'flag') or find_column(df, 'first', 'bill')
            
            # Calculate priority issues safely
            first_bill_issues = 0
            if first_bill_col and status_col:
                first_bill_issues = len(df[(df[first_bill_col] == True) & (df[status_col] != 'MATCHED')])
            
            duplicate_lines = 0
            if status_col:
                duplicate_lines = len(df[df[status_col] == 'DUPLICATE_LINE_NUMBER'])
            
            promo_timing = 0
            if status_col:
                promo_timing = len(df[df[status_col] == 'PROMO_TIMING_MISMATCH'])
            
            priority_issues = {
                'FIRST_BILL_ISSUES': first_bill_issues,
                'DUPLICATE_LINES': duplicate_lines,
                'PROMO_TIMING': promo_timing
            }
        else:
            priority_issues = {
                'FIRST_BILL_ISSUES': 0,
                'DUPLICATE_LINES': 0,
                'PROMO_TIMING': 0
            }
        
        # Generate Cortex recommendations
        recommendations = generate_cortex_recommendations(df, priority_issues)
    
    # Sidebar navigation and filters
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        nav = st.radio(
            "Go to",
            ["Command Center", "Critical Alerts", "AI Intelligence", "Operations", "Insights"],
            index=["Command Center", "Critical Alerts", "AI Intelligence", "Operations", "Insights"].index(st.session_state.nav),
            key="nav_radio",
        )
        st.session_state.nav = nav

        st.markdown("---")
        st.markdown("## 🔎 Enhanced Filters")
        # Dynamic columns for filters - Enhanced
        status_col = find_column(df, 'reconciliation', 'status') or find_column(df, 'status')
        risk_col = find_column(df, 'risk', 'level') or find_column(df, 'risk')
        product_col = find_column(df, 'product', 'category') or find_column(df, 'product')
        region_col = find_column(df, 'service', 'region') or find_column(df, 'region')
        date_col = find_column(df, 'transaction', 'date') or find_column(df, 'date')
        
        # Enhanced business intelligence filters
        business_priority_col = find_column(df, 'business', 'priority')
        customer_segment_col = find_column(df, 'customer', 'segment')
        stacking_violation_col = find_column(df, 'stacking', 'violation', 'type')

        # Build filtered view
        df_view = df.copy()
        if status_col:
            selected_statuses = st.multiselect("Status", sorted(df_view[status_col].dropna().unique().tolist()))
            if selected_statuses:
                df_view = df_view[df_view[status_col].isin(selected_statuses)]
        if risk_col:
            selected_risks = st.multiselect("Risk", sorted(df_view[risk_col].dropna().unique().tolist()))
            if selected_risks:
                df_view = df_view[df_view[risk_col].isin(selected_risks)]
        if product_col:
            selected_products = st.multiselect("Product", sorted(df_view[product_col].dropna().unique().tolist()))
            if selected_products:
                df_view = df_view[df_view[product_col].isin(selected_products)]
        if region_col:
            selected_regions = st.multiselect("Region", sorted(df_view[region_col].dropna().unique().tolist()))
            if selected_regions:
                df_view = df_view[df_view[region_col].isin(selected_regions)]
        
        # Enhanced business intelligence filters
        if business_priority_col:
            selected_priorities = st.multiselect("Business Priority", sorted(df_view[business_priority_col].dropna().unique().tolist()))
            if selected_priorities:
                df_view = df_view[df_view[business_priority_col].isin(selected_priorities)]
        
        if customer_segment_col:
            selected_segments = st.multiselect("Customer Segment", sorted(df_view[customer_segment_col].dropna().unique().tolist()))
            if selected_segments:
                df_view = df_view[df_view[customer_segment_col].isin(selected_segments)]
        
        if stacking_violation_col:
            selected_violations = st.multiselect("Stacking Violations", sorted(df_view[stacking_violation_col].dropna().unique().tolist()))
            if selected_violations:
                df_view = df_view[df_view[stacking_violation_col].isin(selected_violations)]
        
        if date_col and date_col in df_view.columns:
            try:
                if not pd.api.types.is_datetime64_any_dtype(df_view[date_col]):
                    df_view[date_col] = pd.to_datetime(df_view[date_col])
                min_d = df_view[date_col].min().date()
                max_d = df_view[date_col].max().date()
                d_range = st.date_input("Date range", value=(min_d, max_d))
                if isinstance(d_range, tuple) and len(d_range) == 2:
                    start_d, end_d = d_range
                    df_view = df_view[(df_view[date_col] >= pd.to_datetime(start_d)) & (df_view[date_col] <= pd.to_datetime(end_d) + pd.Timedelta(days=1))]
            except Exception:
                pass

    # Render header
    render_header()

    # Empty check after filters
    if df_view.empty:
        st.error("⚠️ No data after filters. Adjust filters or refresh data.")
        return

    # Route to selected section
    if st.session_state.nav == "Command Center":
        render_executive_kpis(df_view, ml_df)
    elif st.session_state.nav == "Critical Alerts":
        render_critical_alerts(df_view)
    elif st.session_state.nav == "AI Intelligence":
        render_cortex_ai_center(df_view, recommendations)
    elif st.session_state.nav == "Operations":
        render_operations_workflow(df_view, ml_df)
    elif st.session_state.nav == "Insights":
        render_performance_metrics(df_view, ml_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <p><strong>Comcast Revenue Operations Center</strong> | Powered by Snowflake Intelligence & Cortex AI</p>
        <p>🎯 Protecting Revenue | 🚀 Enhancing Experience | 🤖 Driving Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
