# Unified Polus Atlas Threat Intelligence Platform
# Ready for Snowflake Streamlit deployment
# Combines enhanced UI components and MITRE ATTACK visualization features
# Note: Import warnings in IDE are normal - packages are available in Snowflake Streamlit

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Polus Atlas - Threat Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SNOWFLAKE CORTEX AI VISIBILITY COMPONENTS
# ============================================================================

@st.cache_data
def simulate_cortex_query(query_type, complexity="medium"):
    """Simulate Snowflake Cortex AI query execution with realistic metrics"""
    
    # Simulate different query types and their characteristics
    query_templates = {
        "threat_classification": {
            "sql": """
SELECT 
    event_id,
    threat_domain,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Analyze this DNS threat event: Domain: ', threat_domain, 
            ', Category: ', threat_category, 
            ', Source IP: ', source_ip,
            '. Map to MITRE ATTACK framework with confidence score. Format: Tactic|Technique|Confidence'
        )
    ) AS mitre_classification
FROM THREAT_INTEL.SECURITY_EDGE_EVENTS 
WHERE threat_score > 7.0 
LIMIT 1000
            """,
            "tokens_per_row": 450,
            "avg_response_time_ms": 125,
            "model": "llama3-70b"
        },
        "customer_insights": {
            "sql": """
SELECT 
    customer_id,
    company_name,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Generate upselling recommendations for: ', company_name, 
            ' (', industry, '). Current services: ', current_services,
            '. Contract value: $', contract_value,
            '. Risk score: ', risk_score, '/10'
        )
    ) AS ai_recommendations
FROM ATLAS_INTERNAL.CUSTOMER_INSIGHTS
WHERE risk_score > 6.0 OR contract_value < 1000
            """,
            "tokens_per_row": 380,
            "avg_response_time_ms": 95,
            "model": "llama3-70b"
        },
        "compliance_analysis": {
            "sql": """
SELECT 
    customer_id,
    framework_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-8b',
        CONCAT(
            'Analyze compliance for customer: ', customer_id,
            '. Framework: ', framework_type,
            '. Current status: ', compliance_data,
            '. Generate score and recommendations.'
        )
    ) AS compliance_assessment
FROM COMPLIANCE.FRAMEWORK_CONTROLS
            """,
            "tokens_per_row": 280,
            "avg_response_time_ms": 65,
            "model": "llama3-8b"
        }
    }
    
    template = query_templates.get(query_type, query_templates["threat_classification"])
    
    # Simulate execution metrics based on complexity
    complexity_multipliers = {
        "low": {"rows": 100, "time_mult": 0.7, "token_mult": 0.8},
        "medium": {"rows": 1000, "time_mult": 1.0, "token_mult": 1.0},
        "high": {"rows": 10000, "time_mult": 1.8, "token_mult": 1.3}
    }
    
    mult = complexity_multipliers[complexity]
    
    return {
        "sql_query": template["sql"],
        "model_used": template["model"],
        "rows_processed": int(mult["rows"]),
        "tokens_consumed": int(template["tokens_per_row"] * mult["rows"] * mult["token_mult"]),
        "execution_time_ms": int(template["avg_response_time_ms"] * mult["time_mult"]),
        "tokens_per_row": template["tokens_per_row"],
        "cost_estimate_usd": round((template["tokens_per_row"] * mult["rows"] * mult["token_mult"]) * 0.000002, 4)
    }

def create_cortex_ai_dashboard():
    """Create comprehensive Snowflake Cortex AI operations dashboard"""
    
    st.header("🧠 Snowflake Cortex AI Operations Center")
    st.markdown("### Real-time AI Model Performance & Query Transparency")
    
    # Model Selection and Configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_model = st.selectbox(
            "Cortex AI Model",
            ["llama3-70b", "llama3-8b", "mistral-7b", "mixtral-8x7b"],
            help="Select the Snowflake Cortex AI model for analysis"
        )
    
    with col2:
        query_complexity = st.selectbox(
            "Query Complexity",
            ["low", "medium", "high"],
            index=1,
            help="Adjust query complexity to see impact on performance and costs"
        )
    
    with col3:
        auto_refresh = st.checkbox(
            "Auto-refresh metrics",
            value=True,
            help="Automatically refresh AI performance metrics"
        )
    
    # Real-time AI Metrics
    st.markdown("#### 📊 Live AI Performance Metrics")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    # Simulate current AI operations
    threat_metrics = simulate_cortex_query("threat_classification", query_complexity)
    customer_metrics = simulate_cortex_query("customer_insights", query_complexity)
    compliance_metrics = simulate_cortex_query("compliance_analysis", query_complexity)
    
    with metrics_col1:
        st.metric(
            "Active AI Queries",
            "3",
            delta="↑ 1 from last minute",
            help="Number of Cortex AI queries currently executing"
        )
    
    with metrics_col2:
        total_tokens = threat_metrics["tokens_consumed"] + customer_metrics["tokens_consumed"] + compliance_metrics["tokens_consumed"]
        st.metric(
            "Tokens Consumed (5min)",
            f"{total_tokens:,}",
            delta=f"↑ {int(total_tokens * 0.15):,}",
            help="Total tokens consumed by Cortex AI in last 5 minutes"
        )
    
    with metrics_col3:
        avg_response_time = (threat_metrics["execution_time_ms"] + customer_metrics["execution_time_ms"] + compliance_metrics["execution_time_ms"]) / 3
        st.metric(
            "Avg Response Time",
            f"{avg_response_time:.0f}ms",
            delta="↓ 12ms improvement",
            help="Average response time for AI queries"
        )
    
    with metrics_col4:
        total_cost = threat_metrics["cost_estimate_usd"] + customer_metrics["cost_estimate_usd"] + compliance_metrics["cost_estimate_usd"]
        st.metric(
            "Cost (5min)",
            f"${total_cost:.4f}",
            delta=f"↑ ${total_cost * 0.08:.4f}",
            help="Estimated cost for Cortex AI operations in last 5 minutes"
        )

def create_query_inspector():
    """Create detailed query inspector showing actual SQL with AI calls"""
    
    st.markdown("#### 🔍 Query Inspector & SQL Transparency")
    
    # Query type selector
    query_type = st.selectbox(
        "Select Query Type to Inspect",
        [
            "MITRE ATTACK Classification",
            "Customer Upselling Analysis", 
            "PCI Compliance Assessment",
            "Threat Pattern Recognition"
        ],
        help="Choose which type of AI-enhanced query to examine"
    )
    
    # Map display names to internal types
    query_type_map = {
        "MITRE ATTACK Classification": "threat_classification",
        "Customer Upselling Analysis": "customer_insights",
        "PCI Compliance Assessment": "compliance_analysis",
        "Threat Pattern Recognition": "threat_classification"
    }
    
    internal_type = query_type_map.get(query_type, "threat_classification")
    query_data = simulate_cortex_query(internal_type, "medium")
    
    # Create tabs for different views
    sql_tab, metrics_tab, optimization_tab = st.tabs(["📝 SQL Query", "📈 Execution Metrics", "⚡ Optimization"])
    
    with sql_tab:
        st.markdown("**Live SQL Query with Cortex AI Integration:**")
        st.code(query_data["sql_query"], language="sql")
        
        st.markdown("**Query Explanation:**")
        if internal_type == "threat_classification":
            st.info("""
            🎯 **MITRE ATTACK Classification Process:**
            1. **Data Selection**: Queries high-severity threats (score > 7.0) from SecurityEdge events
            2. **AI Enhancement**: Uses Cortex `llama3-70b` to analyze threat characteristics
            3. **Framework Mapping**: AI maps threats to MITRE ATTACK tactics and techniques
            4. **Confidence Scoring**: Provides confidence levels for each classification
            """)
        elif internal_type == "customer_insights":
            st.info("""
            💼 **Customer Upselling Analysis Process:**
            1. **Customer Profiling**: Analyzes risk scores and contract values
            2. **Service Assessment**: Reviews current service portfolio
            3. **AI Recommendations**: Cortex AI generates personalized upselling suggestions
            4. **ROI Calculation**: Estimates revenue opportunity for each recommendation
            """)
        else:
            st.info("""
            ✅ **Compliance Assessment Process:**
            1. **Framework Analysis**: Maps customer data to regulatory requirements
            2. **Gap Identification**: AI identifies compliance gaps and risks
            3. **Scoring**: Generates quantified compliance scores
            4. **Remediation**: Provides specific steps to improve compliance posture
            """)
    
    with metrics_tab:
        st.markdown("**Real-time Execution Metrics:**")
        
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.json({
                "Model Used": query_data["model_used"],
                "Rows Processed": f"{query_data['rows_processed']:,}",
                "Execution Time": f"{query_data['execution_time_ms']}ms",
                "Query Complexity": "Medium"
            })
        
        with metric_col2:
            st.json({
                "Tokens Consumed": f"{query_data['tokens_consumed']:,}",
                "Tokens per Row": query_data["tokens_per_row"],
                "Estimated Cost": f"${query_data['cost_estimate_usd']:.4f}",
                "Cost per 1K Tokens": "$0.002"
            })
        
        # Performance visualization
        st.markdown("**Token Consumption Breakdown:**")
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Input Tokens', 'Output Tokens', 'Processing Overhead'],
                y=[
                    query_data["tokens_consumed"] * 0.7,
                    query_data["tokens_consumed"] * 0.25,
                    query_data["tokens_consumed"] * 0.05
                ],
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
            )
        ])
        
        fig.update_layout(
            title="Token Usage Distribution",
            yaxis_title="Tokens",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with optimization_tab:
        st.markdown("**Query Optimization Recommendations:**")
        
        if query_data["tokens_consumed"] > 500000:
            st.warning("""
            ⚠️ **High Token Usage Detected**
            - Consider using `llama3-8b` for simpler classifications
            - Implement caching for repeated queries
            - Batch similar requests to reduce overhead
            """)
        else:
            st.success("""
            ✅ **Query Performance Optimal**
            - Token usage within efficient range
            - Model selection appropriate for complexity
            - Response time meets SLA requirements
            """)
        
        st.markdown("**Cost Optimization Tips:**")
        st.markdown("""
        1. **Model Selection**: Use `llama3-8b` for simple tasks, `llama3-70b` for complex analysis
        2. **Query Batching**: Process multiple records in single AI calls when possible
        3. **Result Caching**: Cache AI responses for frequently accessed data
        4. **Pattern Recognition**: Use AI to identify patterns, then apply rules for similar cases
        """)

def create_ai_decision_engine():
    """Create AI decision engine showing reasoning and thought process"""
    
    st.markdown("#### 🎯 AI Decision Engine - Live Reasoning Process")
    
    # Real-time AI decision simulation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Current AI Decision Stream:**")
        
        # Simulate live AI decisions
        decisions = [
            {
                "timestamp": "14:32:15",
                "event": "DNS Query Analysis",
                "input": "Query to crypto-mining-domain.net from 192.168.1.45",
                "reasoning": [
                    "🔍 Analyzing domain reputation...",
                    "⚠️ Domain matches cryptocurrency mining patterns",
                    "📊 Internal IP shows high bandwidth usage (2.1GB/hour)",
                    "🕒 Activity pattern: 85% outside business hours",
                    "🎯 Mapping to MITRE ATTACK framework..."
                ],
                "decision": "THREAT: TA0040 Impact - Resource Hijacking",
                "confidence": 91.7,
                "action": "Block and Alert SOC"
            },
            {
                "timestamp": "14:31:42",
                "event": "Email Content Analysis", 
                "input": "Attachment 'invoice.pdf.exe' received by user@company.com",
                "reasoning": [
                    "🔍 File extension analysis: Double extension detected",
                    "🧬 Behavioral analysis: Executable disguised as PDF",
                    "📧 Email reputation: Sender not in whitelist",
                    "🔗 Link analysis: Contains shortened URLs",
                    "🎯 Classification: Social Engineering attack vector"
                ],
                "decision": "THREAT: TA0001 Initial Access - Spearphishing",
                "confidence": 96.4,
                "action": "Quarantine and Notify User"
            },
            {
                "timestamp": "14:31:08",
                "event": "Network Traffic Analysis",
                "input": "Unusual outbound connections from server-01.internal",
                "reasoning": [
                    "🔍 Analyzing connection patterns...",
                    "📈 Bandwidth spike: 400% above baseline",
                    "🌐 Destination analysis: Multiple external IPs",
                    "⏰ Timing correlation: After-hours activity",
                    "🔒 Protocol analysis: Encrypted channels"
                ],
                "decision": "SUSPICIOUS: Possible TA0010 Exfiltration",
                "confidence": 78.2,
                "action": "Monitor and Investigate"
            }
        ]
        
        for decision in decisions:
            with st.container():
                # Decision header
                header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
                with header_col1:
                    st.write(f"**{decision['timestamp']}**")
                with header_col2:
                    st.write(f"**{decision['event']}**")
                with header_col3:
                    # Color code confidence
                    if decision['confidence'] > 90:
                        st.markdown(f"<span style='color: green'>**{decision['confidence']:.1f}%**</span>", unsafe_allow_html=True)
                    elif decision['confidence'] > 75:
                        st.markdown(f"<span style='color: orange'>**{decision['confidence']:.1f}%**</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: red'>**{decision['confidence']:.1f}%**</span>", unsafe_allow_html=True)
                
                # Input and reasoning
                st.code(decision['input'], language=None)
                
                # AI reasoning process
                st.markdown("**AI Reasoning Process:**")
                for step in decision['reasoning']:
                    st.write(f"  {step}")
                
                # Final decision and action
                decision_col1, decision_col2 = st.columns(2)
                with decision_col1:
                    if "THREAT" in decision['decision']:
                        st.error(f"**Decision:** {decision['decision']}")
                    elif "SUSPICIOUS" in decision['decision']:
                        st.warning(f"**Decision:** {decision['decision']}")
                    else:
                        st.info(f"**Decision:** {decision['decision']}")
                
                with decision_col2:
                    st.success(f"**Action:** {decision['action']}")
                
                st.markdown("---")
    
    with col2:
        st.markdown("**AI Decision Metrics:**")
        
        # Real-time decision statistics
        st.metric("Decisions/Minute", "127", delta="↑ 8 from avg")
        st.metric("Avg Confidence", "89.2%", delta="↑ 2.1% improvement")
        st.metric("Threat Detection Rate", "15.3%", delta="↓ 1.2% from yesterday")
        
        st.markdown("**Decision Categories:**")
        
        # Decision type distribution
        decision_types = {
            "Type": ["Threats Blocked", "Suspicious Flagged", "Benign Approved", "Require Review"],
            "Count": [245, 387, 1502, 89],
            "Percentage": [11.0, 17.4, 67.5, 4.1]
        }
        
        decision_df = pd.DataFrame(decision_types)
        
        # Mini pie chart
        fig = go.Figure(data=[go.Pie(
            labels=decision_df['Type'], 
            values=decision_df['Count'],
            hole=0.3,
            marker_colors=['#ff4444', '#ffaa44', '#44ff44', '#4444ff']
        )])
        
        fig.update_layout(
            height=300,
            showlegend=True,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**AI Learning Status:**")
        st.progress(0.87, text="Model Adaptation: 87%")
        st.progress(0.94, text="Pattern Recognition: 94%")
        st.progress(0.91, text="Confidence Calibration: 91%")

def create_ai_pipeline_visualizer():
    """Create real-time AI processing pipeline visualization"""
    
    st.markdown("#### 🔄 Real-time AI Processing Pipeline")
    
    # Pipeline stages
    pipeline_data = {
        "Stage": [
            "Data Ingestion",
            "Pre-processing", 
            "Cortex AI Analysis",
            "Post-processing",
            "Results Storage",
            "Dashboard Update"
        ],
        "Status": ["✅ Active", "✅ Active", "🔄 Processing", "⏳ Queued", "⏳ Queued", "⏳ Queued"],
        "Throughput": ["2.1M/min", "1.8M/min", "1.2K/min", "0/min", "0/min", "0/min"],
        "Queue_Depth": [0, 150000, 450000, 280000, 0, 0],
        "Avg_Time_ms": [12, 45, 125, 35, 28, 15]
    }
    
    pipeline_df = pd.DataFrame(pipeline_data)
    
    # Create pipeline flow chart
    fig = go.Figure()
    
    # Add bars for queue depth
    fig.add_trace(go.Bar(
        x=pipeline_df["Stage"],
        y=pipeline_df["Queue_Depth"],
        name="Queue Depth",
        marker_color=['#28a745' if 'Active' in status else '#ffc107' if 'Processing' in status else '#6c757d' 
                     for status in pipeline_df["Status"]]
    ))
    
    fig.update_layout(
        title="AI Processing Pipeline - Queue Depth by Stage",
        xaxis_title="Pipeline Stage",
        yaxis_title="Items in Queue",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed pipeline table
    st.markdown("**Pipeline Stage Details:**")
    
    # Style the dataframe
    def color_status(val):
        if "Active" in val:
            return 'background-color: #d4edda; color: #155724'
        elif "Processing" in val:
            return 'background-color: #fff3cd; color: #856404'
        else:
            return 'background-color: #f8d7da; color: #721c24'
    
    styled_df = pipeline_df.style.map(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)

# ============================================================================
# UI COMPONENTS LAYER
# ============================================================================

def create_polus_atlas_sidebar():
    """Enhanced sidebar matching Polus Atlas design with better organization"""
    
    # Custom CSS for better sidebar styling
    st.markdown("""
    <style>
    .sidebar-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
        text-align: center;
        font-weight: bold;
    }
    .filter-section {
        background-color: #f8fafc;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 3px solid #3b82f6;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 10px;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .section-divider {
        border-top: 2px solid #e5e7eb;
        margin: 30px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced header
    st.sidebar.markdown("""
    <div class="sidebar-header">
        🛡️ POLUS ATLAS<br>
        <small>Threat Intelligence Platform</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics Type Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("**📊 Analytics Type**")
    analytics_type = st.sidebar.selectbox(
        "Select Analysis",
        [
            "Threat Landscape by MITRE ATTACK",
            "Threat Events by Techniques Volume", 
            "Sub-Techniques Volume Analysis",
            "Threat Timeline Analysis",
            "Customer Impact Assessment",
            "IOC Correlation Analysis",
            "🧠 Cortex AI Operations Center"
        ],
        label_visibility="collapsed"
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Date Range Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("**📅 Date Range**")
    date_range = st.sidebar.selectbox(
        "Time Period",
        ["2024", "Last 90 Days", "Last 30 Days", "Last 7 Days", "Last 24 Hours", "Custom"],
        label_visibility="collapsed"
    )
    
    start_date = None
    end_date = None
    if date_range == "Custom":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.sidebar.date_input("From", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.sidebar.date_input("To", value=datetime.now())
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Source Type Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("**🔍 Source Type**")
    source_type = st.sidebar.selectbox(
        "Data Source",
        ["All Sources", "SecurityEdge DNS", "Akamai Threat Intel", "Custom Feeds", "OSINT"],
        label_visibility="collapsed"
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Customer Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("**🏢 Customer**")
    customer_filter = st.sidebar.selectbox(
        "Customer Segment",
        ["All", "Enterprise", "Mid-Market", "Small Business", "Government", "Healthcare"],
        label_visibility="collapsed"
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time Status
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📡 System Status**")
    
    # Status indicators
    status_col1, status_col2 = st.sidebar.columns(2)
    with status_col1:
        st.sidebar.markdown("🟢 **Live Feed**")
        st.sidebar.markdown("🟢 **AI Engine**") 
    with status_col2:
        st.sidebar.markdown("🟢 **Analytics**")
        st.sidebar.markdown("🟢 **APIs**")
    
    # Last updated timestamp
    current_time = datetime.now().strftime("%H:%M:%S")
    st.sidebar.markdown(f"*Last Updated: {current_time}*")
    
    return {
        'analytics_type': analytics_type,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'source_type': source_type,
        'customer_filter': customer_filter
    }

def create_threat_volume_cards():
    """Create threat volume metric cards similar to Polus Atlas"""
    
    st.markdown("### 📊 Threat Intelligence Overview")
    
    # Main metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #1e40af; margin: 0; font-size: 1.2em;">Total Threat Events</h3>
            <h2 style="color: #059669; margin: 5px 0; font-size: 2em;">29,077,785,376</h2>
            <p style="color: #6b7280; margin: 0; font-size: 0.9em;">↑ 2.3M from yesterday</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #1e40af; margin: 0; font-size: 1.2em;">MITRE Techniques</h3>
            <h2 style="color: #dc2626; margin: 5px 0; font-size: 2em;">145</h2>
            <p style="color: #6b7280; margin: 0; font-size: 0.9em;">Distinct techniques detected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #1e40af; margin: 0; font-size: 1.2em;">High Severity Events</h3>
            <h2 style="color: #ea580c; margin: 5px 0; font-size: 2em;">1,453,872</h2>
            <p style="color: #6b7280; margin: 0; font-size: 0.9em;">Threat score > 8.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #1e40af; margin: 0; font-size: 1.2em;">AI Classification Rate</h3>
            <h2 style="color: #7c3aed; margin: 5px 0; font-size: 2em;">94.2%</h2>
            <p style="color: #6b7280; margin: 0; font-size: 0.9em;">Automatic MITRE mapping</p>
        </div>
        """, unsafe_allow_html=True)

def create_ai_processing_metrics():
    """Create AI processing metrics panel"""
    
    st.markdown("### 🤖 AI Processing Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Processing rate gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 1250000,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Events/Hour"},
            delta = {'reference': 1000000},
            gauge = {'axis': {'range': [None, 2000000]},
                    'bar': {'color': "darkblue"},
                    'steps' : [{'range': [0, 500000], 'color': "lightgray"},
                              {'range': [500000, 1000000], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 1500000}}))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Classification accuracy
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 94.2,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Classification Accuracy %"},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "green"},
                    'steps' : [{'range': [0, 80], 'color': "lightgray"},
                              {'range': [80, 90], 'color': "yellow"}],
                    'threshold' : {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 95}}))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Response time
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 85,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Avg Response Time (ms)"},
            gauge = {'axis': {'range': [None, 200]},
                    'bar': {'color': "orange"},
                    'steps' : [{'range': [0, 100], 'color': "lightgreen"},
                              {'range': [100, 150], 'color': "yellow"}],
                    'threshold' : {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 150}}))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

def create_threat_heatmap():
    """Create threat activity heatmap"""
    
    st.markdown("### 🔥 Threat Activity Heatmap")
    
    # Generate sample heatmap data (24 hours x 7 days)
    hours = list(range(24))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Simulate threat activity patterns
    np.random.seed(42)
    threat_matrix = np.random.exponential(2, (7, 24)) * 1000000
    
    # Add business hours pattern
    for day_idx in range(5):  # Weekdays
        for hour in range(8, 18):  # Business hours
            threat_matrix[day_idx][hour] *= 1.5
    
    # Add weekend pattern (lower activity)
    threat_matrix[5:] *= 0.7  # Weekend multiplier
    
    fig = go.Figure(data=go.Heatmap(
        z=threat_matrix,
        x=hours,
        y=days,
        colorscale='Reds',
        hovertemplate='<b>%{y} %{x}:00</b><br>Threats: %{z:,.0f}<extra></extra>',
        colorbar=dict(title="Threat Events")
    ))
    
    fig.update_layout(
        title="Threat Activity by Day of Week and Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=300,
        font=dict(size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_top_threats_table():
    """Create top threats table with enhanced formatting"""
    
    st.markdown("### 🚨 Top Threat Events (Real-time)")
    
    # Sample threat data
    threat_data = {
        'Timestamp': [
            datetime.now() - timedelta(minutes=5),
            datetime.now() - timedelta(minutes=8),
            datetime.now() - timedelta(minutes=12),
            datetime.now() - timedelta(minutes=15),
            datetime.now() - timedelta(minutes=18)
        ],
        'Source_IP': ['192.168.1.100', '10.0.0.45', '172.16.1.200', '203.0.113.5', '198.51.100.75'],
        'Threat_Type': ['Malware C2', 'Phishing', 'Data Exfiltration', 'Botnet Activity', 'Credential Harvesting'],
        'MITRE_Tactic': ['TA0011 C2', 'TA0001 Initial Access', 'TA0010 Exfiltration', 'TA0011 C2', 'TA0006 Credential Access'],
        'Severity': [9.2, 8.7, 9.5, 7.8, 8.9],
        'Customer': ['CUST_001', 'CUST_003', 'CUST_002', 'CUST_001', 'CUST_004'],
        'Status': ['Blocked', 'Investigated', 'Blocked', 'Monitored', 'Blocked']
    }
    
    threats_df = pd.DataFrame(threat_data)
    threats_df['Timestamp'] = threats_df['Timestamp'].dt.strftime('%H:%M:%S')
    
    st.dataframe(threats_df, use_container_width=True, height=250)

# ============================================================================
# MITRE ATTACK ANALYSIS FEATURES LAYER  
# ============================================================================

def generate_mitre_attack_data():
    """Generate synthetic MITRE ATTACK data matching the Polus Atlas format"""
    
    # MITRE ATTACK Tactics 
    tactics_data = {
        'Tactic': [
            'TA0042 Resource Development',
            'TA0001 Initial Access', 
            'TA0002 Execution',
            'TA0003 Persistence',
            'TA0004 Privilege Escalation',
            'TA0005 Defense Evasion',
            'TA0006 Credential Access',
            'TA0007 Discovery',
            'TA0008 Lateral Movement',
            'TA0009 Collection',
            'TA0010 Command and Control',
            'TA0011 Exfiltration',
            'TA0040 Impact'
        ],
        'Event_Count': [
            29077785376,  # Highest volume
            3424707056,
            1890862247,
            1488439,
            1420765,
            457362,
            414726,
            369157,
            282266,
            268933,
            220000,
            2893189,
            75000
        ],
        'Techniques_Count': [12, 9, 8, 19, 13, 40, 15, 29, 9, 17, 16, 9, 13],
        'Confidence_Score': [95.2, 89.7, 92.1, 87.3, 91.5, 88.9, 94.1, 86.7, 90.3, 85.8, 93.4, 88.2, 89.9]
    }
    
    return pd.DataFrame(tactics_data)

def create_tactics_horizontal_chart(data):
    """Create horizontal bar chart for MITRE ATTACK tactics"""
    
    # Sort by event count (descending)
    data_sorted = data.sort_values('Event_Count', ascending=True)
    
    # Create horizontal bar chart with custom colors
    fig = go.Figure()
    
    # Add bars with gradient colors
    colors = ['#1f77b4', '#3399ff', '#66b3ff', '#99ccff'] * 4  # Blue gradient
    
    fig.add_trace(go.Bar(
        y=data_sorted['Tactic'],
        x=data_sorted['Event_Count'],
        orientation='h',
        marker=dict(
            color=colors[:len(data_sorted)],
            line=dict(color='rgba(50, 50, 50, 0.8)', width=1)
        ),
        text=[f"{val:,.0f}" for val in data_sorted['Event_Count']],
        textposition='outside',
        textfont=dict(size=10, color='black'),
        hovertemplate='<b>%{y}</b><br>' +
                     'Events: %{x:,.0f}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f"Threat Events Mapped to MITRE ATTACK in Tactics Order<br><sub>Total Threat Events: {data['Event_Count'].sum():,.0f}</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title="Number of Threat Events",
        yaxis_title="MITRE ATTACK Tactics",
        height=600,
        margin=dict(l=250, r=100, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=11),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            tickformat='.2s'  # Scientific notation for large numbers
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=10)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_techniques_volume_chart(data):
    """Create techniques volume chart"""
    
    # Generate techniques data
    techniques_data = {
        'Technique': [
            'T1059 Command and Scripting Interpreter',
            'T1083 File and Directory Discovery', 
            'T1059.003 Command and Scripting Interpreter',
            'T1047 Windows Management Instrumentation',
            'T1053 Scheduled Task/Job',
            'T1071 Application Layer Protocol'
        ],
        'Event_Count': [17689545245, 6778284764, 6843583070, 5039169558, 34887255, 3471447]
    }
    
    techniques_df = pd.DataFrame(techniques_data)
    techniques_df = techniques_df.sort_values('Event_Count', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=techniques_df['Technique'],
        x=techniques_df['Event_Count'],
        orientation='h',
        marker=dict(color='#2E86AB', line=dict(color='rgba(50, 50, 50, 0.8)', width=1)),
        text=[f"{val:,.0f}" for val in techniques_df['Event_Count']],
        textposition='outside',
        textfont=dict(size=10, color='black')
    ))
    
    fig.update_layout(
        title={
            'text': f"Threat Events Mapped to MITRE ATTACK by Techniques Volume<br><sub>Total Threat Events: {techniques_df['Event_Count'].sum():,.0f}</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Number of Events",
        yaxis_title="MITRE ATTACK Techniques",
        height=500,
        margin=dict(l=300, r=100, t=80, b=60),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgray', tickformat='.2s'),
        yaxis=dict(tickfont=dict(size=10))
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_subtechniques_chart(data):
    """Create sub-techniques analysis chart"""
    
    subtechniques_data = {
        'Sub_Technique': [
            'T1059.003 Windows Command Shell',
            'T1087.002 Domain Account',
            'T1087.001 Local Account', 
            'T1055.012 Process Hollowing',
            'T1087.003 Email Account',
            'T1059.001 PowerShell'
        ],
        'Event_Count': [2139805658, 201684576, 204958425, 229348025, 3788830, 233149589]
    }
    
    subtechniques_df = pd.DataFrame(subtechniques_data)
    subtechniques_df = subtechniques_df.sort_values('Event_Count', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=subtechniques_df['Sub_Technique'],
        x=subtechniques_df['Event_Count'],
        orientation='h',
        marker=dict(color='#A23B72', line=dict(color='rgba(50, 50, 50, 0.8)', width=1)),
        text=[f"{val:,.0f}" for val in subtechniques_df['Event_Count']],
        textposition='outside',
        textfont=dict(size=10, color='black')
    ))
    
    fig.update_layout(
        title={
            'text': f"Threat Events Mapped to MITRE ATTACK by Sub-Techniques Volume<br><sub>Total Threat Events: {subtechniques_df['Event_Count'].sum():,.0f}</sub>",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Number of Events",
        yaxis_title="MITRE ATTACK Sub-Techniques",
        height=500,
        margin=dict(l=300, r=100, t=80, b=60),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgray', tickformat='.2s'),
        yaxis=dict(tickfont=dict(size=10))
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_mitre_attack_landscape():
    """Create a MITRE ATTACK landscape visualization similar to Polus Atlas"""
    
    st.header("🎯 MITRE ATTACK Threat Landscape")
    
    # Interactive filters
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        analytics_type = st.selectbox(
            "Analytics Type",
            ["Threat Landscape by MITRE ATTACK", "Threat Events by Techniques", "Sub-Techniques Analysis"],
            help="Select the type of MITRE ATTACK analysis to display"
        )
    
    with col2:
        date_range = st.selectbox(
            "Date Range",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"],
            index=1
        )
    
    with col3:
        customer_filter = st.multiselect(
            "Customer Filter",
            ["All Customers", "Enterprise", "SMB", "Government"],
            default=["All Customers"]
        )
    
    # Generate synthetic MITRE ATTACK data that matches the visualization
    mitre_data = generate_mitre_attack_data()
    
    if analytics_type == "Threat Landscape by MITRE ATTACK":
        create_tactics_horizontal_chart(mitre_data)
    elif analytics_type == "Threat Events by Techniques":
        create_techniques_volume_chart(mitre_data)
    else:
        create_subtechniques_chart(mitre_data)
    
    # Additional insights panel
    create_threat_insights_panel(mitre_data)

def create_enhanced_ai_reasoning_panel():
    """Create enhanced AI reasoning and decision-making insights"""
    
    st.markdown("#### 🤖 Cortex AI Analysis & Reasoning Engine")
    
    # AI Analysis Tabs
    reasoning_tab, patterns_tab, confidence_tab = st.tabs(["🧠 AI Reasoning", "🔍 Pattern Analysis", "📊 Confidence Scoring"])
    
    with reasoning_tab:
        st.markdown("**Real-time AI Decision Making Process:**")
        
        # Simulate AI reasoning for threat classification
        reasoning_examples = [
            {
                "threat": "suspicious-domain.evil.com",
                "ai_reasoning": """
**AI Analysis Process:**
1. **Domain Structure Analysis**: Identified subdomain pattern 'suspicious-domain' containing threat keywords
2. **TLD Assessment**: '.evil.com' matches known malicious TLD patterns in training data  
3. **Historical Context**: Cross-referenced against 2.3M similar domains in threat database
4. **Behavioral Patterns**: DNS query frequency (15,000/min) exceeds normal thresholds by 400%
5. **Confidence Calculation**: Multiple indicators align (95.7% confidence)

**MITRE ATTACK Mapping Logic:**
- Domain characteristics → TA0042 Resource Development
- DNS tunneling patterns → TA0011 Command and Control
- Volume anomalies → TA0001 Initial Access preparation
                """,
                "confidence": 95.7,
                "mitre_tactic": "TA0042 Resource Development",
                "reasoning_factors": ["Domain keywords", "TLD reputation", "Query volume", "Historical patterns"]
            },
            {
                "threat": "192.168.1.100 → crypto-mining-pool.net",
                "ai_reasoning": """
**AI Analysis Process:**
1. **IP Reputation Check**: Internal IP connecting to known mining pool infrastructure
2. **Traffic Pattern Analysis**: Sustained high-bandwidth connections (2.1 GB/hour)
3. **Protocol Analysis**: TCP connections on non-standard ports (8333, 4444)
4. **Temporal Patterns**: Activity spikes correlate with off-hours (85% after 6 PM)
5. **Threat Classification**: High confidence unauthorized resource usage

**MITRE ATTACK Mapping Logic:**
- Unauthorized resource use → TA0040 Impact
- Persistence mechanisms → TA0003 Persistence  
- Network communication → TA0011 Command and Control
                """,
                "confidence": 89.3,
                "mitre_tactic": "TA0040 Impact",
                "reasoning_factors": ["Traffic volume", "Port usage", "Timing patterns", "IP reputation"]
            }
        ]
        
        for i, example in enumerate(reasoning_examples):
            with st.expander(f"🎯 Case Study {i+1}: {example['threat']}", expanded=i==0):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(example['ai_reasoning'])
                
                with col2:
                    st.metric("AI Confidence", f"{example['confidence']:.1f}%")
                    st.write(f"**Primary Tactic:** {example['mitre_tactic']}")
                    st.write("**Key Factors:**")
                    for factor in example['reasoning_factors']:
                        st.write(f"• {factor}")
    
    with patterns_tab:
        st.markdown("**AI Pattern Recognition & Learning:**")
        
        # Pattern analysis visualization
        pattern_data = {
            "Pattern_Type": [
                "Domain Generation Algorithm",
                "DNS Tunneling", 
                "Command & Control Beaconing",
                "Data Exfiltration Timing",
                "Lateral Movement Sequences"
            ],
            "Patterns_Detected": [2847, 1523, 3891, 892, 445],
            "AI_Accuracy": [97.2, 94.8, 96.1, 91.3, 89.7],
            "Learning_Iterations": [15420, 8930, 12100, 4560, 3210]
        }
        
        pattern_df = pd.DataFrame(pattern_data)
        
        # Create pattern accuracy chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=pattern_df['Patterns_Detected'],
            y=pattern_df['AI_Accuracy'],
            mode='markers+text',
            marker=dict(
                size=pattern_df['Learning_Iterations']/200,
                color=pattern_df['AI_Accuracy'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Accuracy %")
            ),
            text=pattern_df['Pattern_Type'],
            textposition='top center',
            name='Pattern Detection Performance'
        ))
        
        fig.update_layout(
            title="AI Pattern Recognition Performance",
            xaxis_title="Patterns Detected",
            yaxis_title="AI Accuracy (%)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Pattern details
        st.markdown("**Pattern Learning Details:**")
        st.dataframe(pattern_df, use_container_width=True)
        
        st.info("""
        **How AI Learns Patterns:**
        1. **Feature Extraction**: AI identifies key characteristics from threat data
        2. **Pattern Correlation**: Links similar behaviors across different threats
        3. **Confidence Building**: Accuracy improves with more examples (learning iterations)
        4. **Adaptive Classification**: Models update based on new threat intelligence
        """)
    
    with confidence_tab:
        st.markdown("**AI Confidence Scoring Methodology:**")
        
        # Confidence breakdown
        confidence_factors = {
            "Factor": [
                "Historical Data Match",
                "Multi-source Correlation", 
                "Behavioral Consistency",
                "Expert Validation",
                "Pattern Complexity",
                "Real-time Context"
            ],
            "Weight": [0.25, 0.20, 0.18, 0.15, 0.12, 0.10],
            "Current_Score": [94.2, 87.5, 91.8, 96.1, 89.3, 92.7],
            "Impact_on_Final": [23.6, 17.5, 16.5, 14.4, 10.7, 9.3]
        }
        
        conf_df = pd.DataFrame(confidence_factors)
        
        # Confidence factor visualization
        fig = go.Figure(data=[
            go.Bar(
                x=conf_df['Factor'],
                y=conf_df['Impact_on_Final'],
                marker=dict(
                    color=conf_df['Current_Score'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Score %")
                ),
                text=[f"{score:.1f}%" for score in conf_df['Current_Score']],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="AI Confidence Score Composition",
            xaxis_title="Confidence Factors",
            yaxis_title="Contribution to Final Score",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("**Confidence Score Calculation:**")
        final_confidence = conf_df['Impact_on_Final'].sum()
        st.metric("Weighted Final Confidence", f"{final_confidence:.1f}%")
        
        # Detailed factor explanations
        st.markdown("**Factor Explanations:**")
        explanations = {
            "Historical Data Match": "How well current threat matches known patterns in training data",
            "Multi-source Correlation": "Confirmation across multiple threat intelligence feeds", 
            "Behavioral Consistency": "Alignment with expected attack progression sequences",
            "Expert Validation": "Correlation with human analyst classifications",
            "Pattern Complexity": "Sophistication level of attack techniques identified",
            "Real-time Context": "Current threat landscape and emerging attack trends"
        }
        
        for factor, explanation in explanations.items():
            st.write(f"**{factor}**: {explanation}")

def create_threat_insights_panel(data):
    """Create enhanced insights panel with AI reasoning and analysis"""
    
    st.markdown("---")
    st.header("📊 Enhanced Threat Intelligence Insights")
    
    # Traditional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = data['Event_Count'].sum()
        st.metric(
            "Total Threat Events",
            f"{total_events:,.0f}",
            help="Total SecurityEdge threat events processed with MITRE ATTACK classification"
        )
    
    with col2:
        unique_tactics = len(data)
        st.metric(
            "MITRE Tactics Identified",
            unique_tactics,
            help="Number of distinct MITRE ATTACK tactics detected"
        )
    
    with col3:
        avg_confidence = data['Confidence_Score'].mean() if len(data) > 0 else 0.0
        st.metric(
            "Avg Classification Confidence",
            f"{avg_confidence:.1f}%",
            help="Average confidence score for AI-powered MITRE classification"
        )
    
    with col4:
        try:
            high_volume_tactics = len(data[data['Event_Count'] > 1000000])
        except (KeyError, TypeError):
            high_volume_tactics = 0
        st.metric(
            "High-Volume Tactics",
            high_volume_tactics,
            help="Number of tactics with over 1M threat events"
        )
    
    # Enhanced AI reasoning section
    create_enhanced_ai_reasoning_panel()
    
    # AI Analysis Summary
    st.markdown("---")
    st.markdown("#### 📋 AI Analysis Summary & Key Findings")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.markdown("""
        **🤖 Current AI Performance:**
        - **Processing Rate**: 127 decisions/minute with 89.2% avg confidence
        - **Threat Detection**: 15.3% of analyzed events flagged as threats
        - **False Positive Rate**: <2.1% (validated against expert analysis)
        - **Model Accuracy**: 94.2% on MITRE ATTACK classification
        
        **🎯 Top AI Insights:**
        - Resource Development tactics dominating recent attacks (87% increase)
        - DNS tunneling patterns show increased sophistication 
        - Cryptocurrency mining attempts correlate with weekend activity
        - PowerShell-based attacks show highest confidence detection (96.4%)
        """)
    
    with summary_col2:
        st.markdown("""
        **🔍 AI Learning Trends:**
        - **Pattern Recognition**: 97.2% accuracy on domain generation algorithms
        - **Behavioral Analysis**: 91.3% success on timing-based threat detection
        - **Multi-source Correlation**: 94.8% effective cross-reference validation
        - **Adaptive Learning**: Models updated with 15,420 new threat samples
        
        **⚡ Optimization Opportunities:**
        - Implement caching for repeated classifications (30% cost reduction)
        - Switch to `llama3-8b` for simple compliance checks
        - Batch processing during off-peak hours
        - Enhanced pattern matching for known threat families
        """)
    
    # AI confidence trends
    st.markdown("**📈 AI Confidence Trends (Last 24 Hours):**")
    
    # Generate confidence trend data
    hours = list(range(24))
    np.random.seed(42)
    base_confidence = 89.2
    confidence_trend = [base_confidence + np.sin(h/3.8) * 3 + np.random.normal(0, 1.5) for h in hours]
    confidence_trend = [max(75, min(98, c)) for c in confidence_trend]  # Keep within realistic bounds
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=confidence_trend,
        mode='lines+markers',
        name='AI Confidence %',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        fill='tonexty' if len(hours) > 1 else None,
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    # Add target confidence line
    fig.add_hline(y=90, line_dash="dash", line_color="green", 
                  annotation_text="Target: 90%", annotation_position="bottom right")
    
    fig.update_layout(
        title="AI Classification Confidence Over Time",
        xaxis_title="Hour of Day",
        yaxis_title="Confidence %",
        height=300,
        yaxis_range=[75, 100]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_threat_timeline_chart():
    """Create timeline chart showing threat events over time"""
    
    st.header("⏱️ Threat Events Timeline")
    
    # Set random seed for consistent results
    np.random.seed(42)
    
    # Generate sample time series data
    dates = pd.date_range(start='2024-08-01', end='2024-08-05', freq='H')
    
    # Simulate realistic threat event patterns
    base_volume = 1000000
    threat_data = []
    
    for date in dates:
        # Add realistic patterns (higher during business hours, spikes, etc.)
        hour = date.hour
        day_of_week = date.weekday()
        
        # Business hours pattern
        if 8 <= hour <= 18 and day_of_week < 5:
            multiplier = 1.5
        else:
            multiplier = 0.8
            
        # Add some random spikes
        spike = np.random.choice([1, 2, 3], p=[0.8, 0.15, 0.05])
        
        volume = int(base_volume * multiplier * spike * (0.8 + 0.4 * np.random.random()))
        
        threat_data.append({
            'timestamp': date,
            'threat_volume': volume,
            'blocked_events': int(volume * 0.15),
            'high_severity': int(volume * 0.05)
        })
    
    timeline_df = pd.DataFrame(threat_data)
    
    # Create multi-line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timeline_df['timestamp'],
        y=timeline_df['threat_volume'],
        mode='lines+markers',
        name='Total Threats',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=timeline_df['timestamp'],
        y=timeline_df['blocked_events'],
        mode='lines+markers',
        name='Blocked Events',
        line=dict(color='#ff7f0e', width=2),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=timeline_df['timestamp'],
        y=timeline_df['high_severity'],
        mode='lines+markers',
        name='High Severity',
        line=dict(color='#d62728', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title="Threat Events Timeline (Last 5 Days)",
        xaxis_title="Time",
        yaxis_title="Number of Events",
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MAIN APPLICATION ORCHESTRATION
# ============================================================================

def main():
    """Main application function - ready for Snowflake Streamlit deployment"""
    
    # Enhanced page header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ POLUS ATLAS - Enhanced Threat Intelligence Platform</h1>
        <p>Real-time MITRE ATTACK Analysis | AI-Powered Classification | Snowflake Cortex Integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get sidebar filters (this will create the entire sidebar)
    filters = create_polus_atlas_sidebar()
    
    # Main content sections based on selected analytics type
    if filters['analytics_type'] == "🧠 Cortex AI Operations Center":
        # Show Cortex AI visibility and operations
        create_cortex_ai_dashboard()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_query_inspector()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_ai_decision_engine()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_ai_pipeline_visualizer()
        
    elif filters['analytics_type'] == "Threat Timeline Analysis":
        # Show timeline-focused view
        create_threat_volume_cards()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_threat_timeline_chart()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_ai_processing_metrics()
        
    elif filters['analytics_type'] in ["Threat Landscape by MITRE ATTACK", "Threat Events by Techniques Volume", "Sub-Techniques Volume Analysis"]:
        # Show MITRE ATTACK analysis view
        create_threat_volume_cards()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_mitre_attack_landscape()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_ai_processing_metrics()
        
    else:
        # Show comprehensive overview (default)
        create_threat_volume_cards()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_ai_processing_metrics()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_threat_heatmap()
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        create_top_threats_table()
    
    # Key Insights & Recommendations (skip for Cortex AI mode as it has its own insights)
    if filters['analytics_type'] != "🧠 Cortex AI Operations Center":
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.header("🎯 Key Insights & Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Top Threat Patterns Detected:**
            - Resource Development tactics showing 87% increase
            - Command & Scripting techniques dominating attack vectors  
            - Windows Command Shell sub-techniques most prevalent
            - High confidence (94%+) in AI classifications
            """)
        
        with col2:
            st.markdown("""
            **Recommended Actions:**
            - Focus monitoring on T1059 technique variants
            - Enhance detection for TA0042 Resource Development
            - Review Windows environment hardening
            - Implement additional PowerShell monitoring
            """)
    else:
        # AI-specific insights section
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.header("🎯 AI Operations Insights & Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Current AI Performance Patterns:**
            - `llama3-70b` optimal for complex threat analysis
            - Token consumption stable at 1.2M per 5-minute window
            - 94.2% classification accuracy maintained
            - Response times consistently under 150ms SLA
            """)
        
        with col2:
            st.markdown("""
            **AI Optimization Recommendations:**
            - Implement caching for repeated threat classifications
            - Consider `llama3-8b` for simple compliance checks
            - Batch processing can reduce costs by 30%
            - Monitor token usage during peak hours
            """)
    
    # Technical implementation notes
    with st.expander("🔧 Technical Implementation", expanded=False):
        if filters['analytics_type'] == "🧠 Cortex AI Operations Center":
            st.markdown("""
            **Snowflake Cortex AI Integration Architecture:**
            - **Model Selection**: Dynamic switching between llama3-70b, llama3-8b, mistral-7b, mixtral-8x7b
            - **Token Management**: Real-time monitoring and cost optimization
            - **Query Transparency**: Full SQL visibility with AI function calls
            - **Performance Monitoring**: Response time, throughput, and accuracy tracking
            
            **Cost Optimization Features:**
            - **Smart Caching**: AI responses cached for frequently accessed patterns
            - **Batch Processing**: Multiple records processed in single AI calls
            - **Model Routing**: Automatic selection of optimal model for task complexity
            - **Token Budgeting**: Real-time cost monitoring and alerting
            
            **Real-time Processing Pipeline:**
            1. **Data Ingestion**: Raw threat events from SecurityEdge (2.1M/min)
            2. **Pre-processing**: Data cleaning and normalization (1.8M/min)
            3. **Cortex AI Analysis**: AI-powered classification and insights (1.2K/min)
            4. **Post-processing**: Results validation and enrichment
            5. **Storage & Caching**: Optimized for query performance
            6. **Dashboard Updates**: Real-time visualization refresh
            """)
        else:
            st.markdown("""
            **What this demonstrates:**
            - Integration with Snowflake Cortex AI for MITRE ATTACK classification
            - Real-time processing of billions of SecurityEdge DNS events
            - Advanced visualization techniques for threat landscape analysis
            - Interactive filtering and drill-down capabilities
            
            **Data Sources:**
            - SecurityEdge DNS threat events (29B+ events)
            - Akamai threat intelligence feeds
            - Custom threat intelligence overlays
            - MITRE ATTACK framework mappings
            
            **AI Enhancement Process:**
            1. Raw SecurityEdge events ingested at scale
            2. Snowflake Cortex AI analyzes threat characteristics  
            3. MITRE ATTACK tactics/techniques mapped with confidence scoring
            4. Real-time aggregation and visualization updates
            5. Pattern recognition for proactive threat hunting
            """)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()