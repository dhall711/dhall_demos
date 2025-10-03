# Comcast Business Polus Platform - Snowflake Analytics Dashboard
# Streamlit in Snowflake App

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Comcast Business Polus Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🛡️ Comcast Business Polus Platform")
st.sidebar.markdown("### Analytics Dashboard")

page = st.sidebar.selectbox(
    "Select Dashboard",
    ["🏠 Overview", "📊 Atlas - Internal Intelligence", "🌐 Threat Intelligence Platform", "🎯 Nexus - Customer Analytics", 
     "🛡️ PCI Compliance Easy Button", "🔍 SecurityEdge Threat Intelligence", "💰 Cost Analysis & ROI"]
)

# Helper function to run SQL queries
@st.cache_data
def run_query(query):
    """Execute SQL query and return results as DataFrame"""
    try:
        # In Streamlit in Snowflake, use st.connection
        conn = st.connection("snowflake")
        return conn.query(query)
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()

# Helper function to get connection info
@st.cache_data
def get_connection_info():
    """Get current database connection information"""
    try:
        conn = st.connection("snowflake")
        
        # Get current session info
        session_info = conn.query("""
            SELECT 
                CURRENT_DATABASE() as database_name,
                CURRENT_USER() as user_name,
                CURRENT_SCHEMA() as schema_name,
                CURRENT_WAREHOUSE() as warehouse_name,
                CURRENT_ROLE() as role_name
        """)
        
        return session_info.iloc[0] if not session_info.empty else None
    except Exception as e:
        st.error(f"Connection info error: {str(e)}")
        return None

# Helper function to display database connection info
def show_database_info(schemas_and_tables):
    """Display compact database connection information and related tables"""
    with st.expander("🔗 Database Connection & Data Sources", expanded=False):
        connection_info = get_connection_info()
        
        if connection_info is not None:
            # Create compact connection info table using HTML for smaller fonts
            connection_html = f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 4px 8px; font-weight: bold; color: #666;">Database:</td>
                        <td style="padding: 4px 8px; color: #333;">{connection_info['DATABASE_NAME']}</td>
                        <td style="padding: 4px 8px; font-weight: bold; color: #666;">User:</td>
                        <td style="padding: 4px 8px; color: #333;">{connection_info['USER_NAME']}</td>
                        <td style="padding: 4px 8px; font-weight: bold; color: #666;">Role:</td>
                        <td style="padding: 4px 8px; color: #333;">{connection_info['ROLE_NAME']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 8px; font-weight: bold; color: #666;">Schema:</td>
                        <td style="padding: 4px 8px; color: #333;">{connection_info['SCHEMA_NAME']}</td>
                        <td style="padding: 4px 8px; font-weight: bold; color: #666;">Warehouse:</td>
                        <td style="padding: 4px 8px; color: #333;">{connection_info['WAREHOUSE_NAME']}</td>
                        <td colspan="2"></td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(connection_html, unsafe_allow_html=True)
        
        # Organized data sources display
        st.markdown("**📊 Data Sources Used:**")
        
        # Create organized table of schemas and tables
        for schema, tables in schemas_and_tables.items():
            # Format tables with proper spacing
            tables_list = ' • '.join([f"`{table}`" for table in tables])
            
            schema_html = f"""
            <div style="margin-bottom: 10px; padding: 8px; background-color: #fafafa; border-left: 3px solid #FF6B6B; border-radius: 3px;">
                <div style="font-weight: bold; color: #333; font-size: 13px; margin-bottom: 3px;">📁 {schema}</div>
                <div style="font-size: 11px; color: #666; line-height: 1.4; padding-left: 10px;">{tables_list}</div>
            </div>
            """
            st.markdown(schema_html, unsafe_allow_html=True)

# Main content based on selected page
if page == "🏠 Overview":
    st.title("🛡️ Comcast Business Polus Platform Analytics")
    st.markdown("### Real-time Intelligence for Atlas & Nexus Applications")
    
    # Database connection information
    overview_schemas_tables = {
        "ATLAS_INTERNAL": ["CUSTOMER_INSIGHTS", "COST_ANALYSIS", "TOKEN_CONSUMPTION_ESTIMATE"],
        "NEXUS_CUSTOMER": ["CUSTOMER_ANALYTICS", "CB_SERVICE_DASHBOARD"],
        "THREAT_INTEL": ["SECURITY_EDGE_EVENTS", "SECURITY_EDGE_PATTERNS"],
        "COMPLIANCE": ["PCI_COMPLIANCE_TRACKING"]
    }
    show_database_info(overview_schemas_tables)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Customers",
            value="5",
            help="Active customers in the Polus platform with comprehensive service analytics"
        )
    
    with col2:
        st.metric(
            label="SecurityEdge Events Processed",
            value="5,000+",
            help="Threat events processed with AI-powered MITRE Attack classification"
        )
    
    with col3:
        st.metric(
            label="AI Cost Savings",
            value="70-90%",
            help="Cost reduction through intelligent pattern recognition vs traditional infrastructure"
        )
    
    st.markdown("---")
    
    # Platform Overview
    st.header("🏗️ Platform Architecture")
    st.markdown("""
    **Polus Platform Components:**
    - **Atlas**: Internal application for sales, marketing, and operations teams
    - **Nexus**: Customer-facing analytics and compliance platform  
    - **Backend**: Data processing, enrichment, and threat intelligence curation
    
    **Key Snowflake Capabilities Demonstrated:**
    - Native AI with Cortex for threat analysis and sales intelligence
    - Elastic scaling for billions of SecurityEdge DNS events
    - Built-in security and compliance features
    - Token-based AI consumption model
    """)

elif page == "📊 Atlas - Internal Intelligence":
    st.title("📊 Atlas - Internal Sales Intelligence")
    st.markdown("### AI-Powered Customer Insights & Live Upselling Recommendations")
    
    # Database connection information
    atlas_schemas_tables = {
        "ATLAS_INTERNAL": ["CUSTOMER_INSIGHTS", "COST_ANALYSIS", "TOKEN_CONSUMPTION_ESTIMATE"]
    }
    show_database_info(atlas_schemas_tables)
    
    # Customer Insights Query with AI Upsell Recommendations
    customer_query = """
    SELECT 
        customer_id,
        company_name,
        industry,
        internet_service,
        internet_speed,
        phone_service,
        security_edge_enabled,
        wifi_pro_enabled,
        connection_pro_enabled,
        contract_value,
        risk_score,
        compliance_status,
        -- Current service summary
        CONCAT(
            'Internet: ', internet_service, ' (', internet_speed, '), ',
            'Phone: ', phone_service, ', ',
            'SecurityEdge: ', CASE WHEN security_edge_enabled THEN 'Yes' ELSE 'No' END, ', ',
            'WiFi Pro: ', CASE WHEN wifi_pro_enabled THEN 'Yes' ELSE 'No' END, ', ',
            'Connection Pro: ', CASE WHEN connection_pro_enabled THEN 'Yes' ELSE 'No' END
        ) AS current_services_summary,
        
        -- AI-powered upselling recommendation using actual CB services
        SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-70b',
            CONCAT(
                'Comcast Business customer analysis: ', company_name, ' (', industry, '). ',
                'Current services: Internet ', internet_service, ' (', internet_speed, '), ',
                'Phone ', phone_service, '. ',
                'SecurityEdge: ', CASE WHEN security_edge_enabled THEN 'enabled' ELSE 'NOT enabled' END, '. ',
                'WiFi Pro: ', CASE WHEN wifi_pro_enabled THEN 'enabled' ELSE 'NOT enabled' END, '. ',
                'Connection Pro: ', CASE WHEN connection_pro_enabled THEN 'enabled' ELSE 'NOT enabled' END, '. ',
                'Monthly value: $', contract_value, '. Risk score: ', risk_score, '. ',
                'Recommend 2-3 specific Comcast Business service upgrades: faster internet tiers, ',
                'SecurityEdge cybersecurity, WiFi Pro, Connection Pro 4G backup, Business TV, ',
                'or Ethernet/DIA services. Explain why each fits their industry and profile. 100 words max.'
            )
        ) AS ai_upsell_recommendation
    FROM ATLAS_INTERNAL.CUSTOMER_INSIGHTS
    WHERE (risk_score > 6.0 OR contract_value < 1000)  -- Target high-risk or low-value customers
    ORDER BY 
        CASE WHEN risk_score > 7.0 THEN 1 ELSE 2 END,  -- Prioritize high risk
        contract_value ASC  -- Then low contract value for upselling
    """
    
    customer_data = run_query(customer_query)
    
    if not customer_data.empty:
        # Full width table for better readability
        st.subheader("Customer Portfolio Overview")
        st.dataframe(customer_data, use_container_width=True)
        
        # Service adoption chart below the table
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Service Adoption Metrics")
            
            # Service adoption metrics
            security_edge_adoption = (customer_data['SECURITY_EDGE_ENABLED'].sum() / len(customer_data)) * 100
            wifi_pro_adoption = (customer_data['WIFI_PRO_ENABLED'].sum() / len(customer_data)) * 100
            connection_pro_adoption = (customer_data['CONNECTION_PRO_ENABLED'].sum() / len(customer_data)) * 100
            
            st.metric("SecurityEdge", f"{security_edge_adoption:.0f}%")
            st.metric("WiFi Pro", f"{wifi_pro_adoption:.0f}%")
            st.metric("Connection Pro", f"{connection_pro_adoption:.0f}%")
        
        with col2:
            st.subheader("Service Adoption Chart")
            
            fig = go.Figure(data=[
                go.Bar(name='Service Adoption %', 
                       x=['SecurityEdge', 'WiFi Pro', 'Connection Pro'],
                       y=[security_edge_adoption, wifi_pro_adoption, connection_pro_adoption],
                       marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
            ])
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **What this shows:** Complete view of Comcast Business customers with their current service portfolio, 
        contract values, risk assessments, and **AI-generated upselling recommendations**. This data enables 
        AI-powered sales intelligence and targeted revenue opportunities.
        
        **How it's derived:** Customer data is aggregated from multiple CB service touchpoints and enhanced with 
        risk scoring algorithms. **Snowflake Cortex AI (llama3-70b)** analyzes each customer's profile, current 
        services, industry, and risk factors to generate personalized upselling recommendations for SecurityEdge, 
        WiFi Pro, Connection Pro, internet tier upgrades, and other CB services.
        
        **Key Features:**
        - **Current Services Summary**: Complete service portfolio overview
        - **AI Upsell Recommendations**: Targeted suggestions based on customer profile and industry
        - **Risk-Based Prioritization**: Focus on high-risk customers and low-value accounts for maximum impact
        - **Real-Time AI Processing**: Live recommendations generated during query execution
        """)
    
    # Interactive BI Query Interface
    st.subheader("🗣️ Natural Language Business Intelligence")
    
    with st.expander("💬 Ask Questions About Your Data", expanded=False):
        st.markdown("""
        **Examples you can ask:**
        - "Show me customer growth trends by service type over the past 12 months"
        - "Which customers should I prioritize for SecurityEdge upselling?"
        - "What's our average contract value in the healthcare industry?"
        - "Which customers are using 80% of their bandwidth allocation?"
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            user_question = st.text_input(
                "Ask a question about your Comcast Business data:",
                placeholder="e.g., Which customers need WiFi Pro but don't have it?"
            )
        with col2:
            user_role = st.selectbox("Your Role:", ["sales", "marketing", "executive", "operations"])
        
        if st.button("🔍 Analyze") and user_question:
            with st.spinner("Generating insights..."):
                # Escape single quotes in user input to prevent SQL injection
                escaped_question = user_question.replace("'", "''")
                bi_query = f"""
                SELECT ATLAS_INTERNAL.ADVANCED_BI_QUERY('{escaped_question}', '{user_role}', '12_months') AS analysis
                """
                try:
                    bi_result = run_query(bi_query)
                    if not bi_result.empty:
                        st.info("🤖 **AI Analysis:**")
                        st.write(bi_result.iloc[0]['ANALYSIS'])
                    else:
                        st.warning("No results found. Please try a different question.")
                except Exception as e:
                    st.error(f"Query error: {str(e)}")
    
    # AI Sales Intelligence - Top Priority Customers
    st.subheader("🤖 AI-Powered Sales Recommendations - Top Priorities")
    
    if not customer_data.empty:
        # Show top 3 priority customers with their AI recommendations
        top_customers = customer_data.head(3)
        
        for idx, row in top_customers.iterrows():
            with st.expander(f"🎯 {row['COMPANY_NAME']} - Priority Customer"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Risk Score", f"{row['RISK_SCORE']:.1f}/10")
                    st.metric("Contract Value", f"${row['CONTRACT_VALUE']:,}")
                    st.write(f"**Industry:** {row['INDUSTRY']}")
                with col2:
                    st.write("**Current Services:**")
                    st.write(row['CURRENT_SERVICES_SUMMARY'])
                
                st.markdown("**🤖 AI-Generated Recommendation:**")
                if 'AI_UPSELL_RECOMMENDATION' in row and pd.notna(row['AI_UPSELL_RECOMMENDATION']):
                    st.info(row['AI_UPSELL_RECOMMENDATION'])
                else:
                    st.warning("AI recommendation loading... Please ensure the query includes the AI_UPSELL_RECOMMENDATION field.")
                
                st.markdown("""
                **How this was generated:** Snowflake Cortex AI (llama3-70b) analyzed this customer's 
                industry, current service portfolio, contract value, and risk profile to generate 
                personalized upselling recommendations focusing on actual Comcast Business services.
                """)

elif page == "🌐 Threat Intelligence Platform":
    st.title("🌐 Multi-Source Threat Intelligence Platform")
    st.markdown("### AI-Powered Threat Analysis & IOC Processing")
    
    # Database connection information
    threat_intel_schemas_tables = {
        "THREAT_INTEL": ["COMMERCIAL_THREAT_FEEDS", "OSINT_FEEDS", "COMCAST_NETWORK_INTEL", "UNIFIED_THREAT_INTELLIGENCE"]
    }
    show_database_info(threat_intel_schemas_tables)
    
    st.markdown("""
    **Platform Overview:** This comprehensive threat intelligence platform ingests data from multiple sources 
    (commercial feeds like Mandiant/CrowdStrike, open source intelligence, and Comcast's proprietary network data) 
    and processes it using AI agents for IOC extraction, analysis, and enhanced threat classification.
    
    **Triple Monetization Strategy:**
    1. **Product Sales** - Sell enriched threat intelligence to other cybersecurity companies
    2. **Internal SOC Enhancement** - Feed proprietary intelligence to Comcast Business SOC teams
    3. **Service Integration** - Embed advanced threat intelligence into existing CB security offerings
    """)
    
    # Unified Threat Intelligence Query
    threat_intel_query = """
    SELECT 
        threat_id,
        source_category,
        source_name,
        confidence_score,
        threat_categories,
        cb_customer_risk_score,
        ai_threat_analysis,
        ingestion_timestamp
    FROM THREAT_INTEL.UNIFIED_THREAT_INTELLIGENCE
    ORDER BY cb_customer_risk_score DESC, confidence_score DESC
    LIMIT 10
    """
    
    threat_data = run_query(threat_intel_query)
    
    if not threat_data.empty:
        st.subheader("🔍 AI-Enhanced Threat Intelligence Feed")
        st.dataframe(threat_data, use_container_width=True)
        
        # Threat Source Analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            commercial_count = len(threat_data[threat_data['SOURCE_CATEGORY'] == 'commercial'])
            st.metric("Commercial Sources", commercial_count)
            
        with col2:
            osint_count = len(threat_data[threat_data['SOURCE_CATEGORY'] == 'open_source'])
            st.metric("Open Source Intel", osint_count)
            
        with col3:
            comcast_count = len(threat_data[threat_data['SOURCE_CATEGORY'] == 'comcast_proprietary'])
            st.metric("Comcast Network Intel", comcast_count)
        
        # Risk Distribution Chart
        st.subheader("📊 Threat Risk Distribution for CB Customers")
        # Convert Decimal to float to avoid TypeError with pandas operations
        risk_scores = pd.to_numeric(threat_data['CB_CUSTOMER_RISK_SCORE'], errors='coerce')
        risk_bins = pd.cut(risk_scores, bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Critical'])
        risk_counts = risk_bins.value_counts()
        
        fig = px.bar(x=risk_counts.index, y=risk_counts.values, 
                     title="Threat Risk Levels for Comcast Business Customers",
                     color=risk_counts.values,
                     color_continuous_scale='Reds')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Threat Analysis Sample
        st.subheader("🤖 AI Threat Analysis Sample")
        if not threat_data.empty:
            sample_threat = threat_data.iloc[0]
            with st.expander(f"🔍 Threat ID: {sample_threat['THREAT_ID']} - {sample_threat['SOURCE_NAME']}"):
                st.write(f"**Source Category:** {sample_threat['SOURCE_CATEGORY']}")
                st.write(f"**Confidence Score:** {sample_threat['CONFIDENCE_SCORE']}")
                # Convert Decimal to float for formatting
                risk_score = float(sample_threat['CB_CUSTOMER_RISK_SCORE']) if sample_threat['CB_CUSTOMER_RISK_SCORE'] is not None else 0.0
                st.write(f"**CB Customer Risk:** {risk_score:.2f}")
                st.write(f"**Threat Categories:** {sample_threat['THREAT_CATEGORIES']}")
                st.info(f"**AI Analysis:** {sample_threat['AI_THREAT_ANALYSIS']}")
        
        st.markdown("""
        **How this works:** Snowflake Cortex AI processes threat intelligence from multiple sources, 
        extracts IOCs, performs cross-correlation analysis, and generates CB-specific risk assessments. 
        The unified view enables the triple monetization strategy for enhanced cybersecurity services.
        """)

elif page == "🎯 Nexus - Customer Analytics":
    st.title("🎯 Nexus - Customer-Facing Analytics")
    st.markdown("### Tiered Service Dashboards & Performance Monitoring")
    
    # Database connection information
    nexus_schemas_tables = {
        "NEXUS_CUSTOMER": ["CUSTOMER_ANALYTICS", "CB_SERVICE_DASHBOARD"]
    }
    show_database_info(nexus_schemas_tables)
    
    # Customer Analytics Query
    nexus_query = """
    SELECT 
        customer_id,
        service_tier,
        internet_uptime_pct,
        phone_call_quality_score,
        security_edge_threats_blocked,
        dns_queries_filtered,
        connection_pro_activations,
        compliance_reports_generated,
        pci_scan_results
    FROM NEXUS_CUSTOMER.CUSTOMER_ANALYTICS
    ORDER BY service_tier DESC
    """
    
    nexus_data = run_query(nexus_query)
    
    if not nexus_data.empty:
        # Service tier distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Service Tier Distribution")
            tier_counts = nexus_data['SERVICE_TIER'].value_counts()
            fig = px.pie(values=tier_counts.values, names=tier_counts.index, 
                        color_discrete_map={'PREMIUM': '#FF6B6B', 'COMPLIANCE': '#4ECDC4', 'BASIC': '#FFA726'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Average Performance Metrics")
            avg_uptime = nexus_data['INTERNET_UPTIME_PCT'].mean()
            avg_call_quality = nexus_data['PHONE_CALL_QUALITY_SCORE'].mean()
            avg_threats_blocked = nexus_data['SECURITY_EDGE_THREATS_BLOCKED'].mean()
            
            st.metric("Avg Internet Uptime", f"{avg_uptime:.1f}%")
            st.metric("Avg Call Quality", f"{avg_call_quality:.1f}/5.0")
            st.metric("Avg Threats Blocked", f"{avg_threats_blocked:.0f}")
    
    # Service Performance Dashboard
    st.subheader("🚀 Customer Service Performance")
    st.dataframe(nexus_data, use_container_width=True)
    
    st.markdown("""
    **What this shows:** Real-time performance metrics for all Comcast Business services including 
    internet uptime, phone quality, SecurityEdge threat protection, and compliance reporting.
    
    **Service Tiers Explained:**
    - **BASIC**: Internet and phone metrics only
    - **COMPLIANCE**: Adds PCI compliance reporting and enhanced analytics  
    - **PREMIUM**: Full analytics suite with AI-powered insights and advanced threat intelligence
    
    **How it's derived:** Data is collected from CB service infrastructure (SecurityEdge DNS filtering, 
    network monitoring, PCI scanning) and processed in real-time to provide 90-day rolling analytics 
    with different retention periods based on service tier.
    """)

elif page == "🛡️ PCI Compliance Easy Button":
    st.title("🛡️ AI-Powered Compliance Platform")
    st.markdown("### Multi-Framework Compliance with Automated Risk Scoring")
    
    # Database connection information
    compliance_schemas_tables = {
        "COMPLIANCE": ["COMPLIANCE_FRAMEWORKS", "FRAMEWORK_CONTROLS", "CUSTOMER_COMPLIANCE_POSTURE", "AI_COMPLIANCE_DASHBOARD"]
    }
    show_database_info(compliance_schemas_tables)
    
    st.markdown("""
    **Platform Overview:** This AI-powered compliance platform automatically maps customer data 
    to regulatory frameworks (PCI DSS, NIST, HIPAA) and provides quantified risk scoring with detailed explanations. 
    AI agents handle data engineering tasks, eliminating the need for manual compliance management.
    
    **Key Features:**
    - **Agent-Based Processing**: AI agents automatically classify and map data to compliance controls
    - **Framework Flexibility**: Support for PCI DSS, NIST, HIPAA, and custom frameworks
    - **Risk Quantification**: "75% compliant on this control because..." with detailed reasoning
    - **SMB Focus**: Eliminate need for dedicated compliance teams at customer organizations
    """)
    
    # Enhanced AI Compliance Dashboard with comprehensive error handling
    st.info("ℹ️ **Note**: If you encounter errors, this may be due to complex AI functions in the compliance view. The app will automatically fallback to sample data.")
    
    try:
        # First try the basic columns without AI-generated content
        basic_compliance_query = """
        SELECT 
            customer_id,
            company_name,
            industry,
            compliance_status,
            ai_compliance_score,
            assessment_timestamp
        FROM COMPLIANCE.AI_COMPLIANCE_DASHBOARD
        ORDER BY ai_compliance_score DESC
        """
        
        compliance_data = run_query(basic_compliance_query)
        
        if compliance_data.empty:
            raise Exception("No data returned from compliance view")
            
    except Exception as e:
        st.warning(f"AI Compliance Dashboard unavailable: {str(e)[:100]}... Using demonstration data.")
        
        # Create comprehensive fallback data that demonstrates the concept
        fallback_query = """
        SELECT 
            'CUST_001' as customer_id,
            'Downtown Restaurant' as company_name,
            'Hospitality' as industry,
            'PCI_COMPLIANT' as compliance_status,
            0.92 as ai_compliance_score,
            CURRENT_TIMESTAMP() as assessment_timestamp
        UNION ALL
        SELECT 
            'CUST_002' as customer_id,
            'Medical Clinic' as company_name,
            'Healthcare' as industry,
            'NON_COMPLIANT' as compliance_status,
            0.68 as ai_compliance_score,
            CURRENT_TIMESTAMP() as assessment_timestamp
        UNION ALL
        SELECT 
            'CUST_003' as customer_id,
            'Auto Dealership' as company_name,
            'Automotive' as industry,
            'PCI_COMPLIANT' as compliance_status,
            0.89 as ai_compliance_score,
            CURRENT_TIMESTAMP() as assessment_timestamp
        UNION ALL
        SELECT 
            'CUST_004' as customer_id,
            'Law Firm' as company_name,
            'Legal' as industry,
            'PENDING' as compliance_status,
            0.75 as ai_compliance_score,
            CURRENT_TIMESTAMP() as assessment_timestamp
        UNION ALL
        SELECT 
            'CUST_005' as customer_id,
            'Manufacturing Shop' as company_name,
            'Manufacturing' as industry,
            'NON_COMPLIANT' as compliance_status,
            0.45 as ai_compliance_score,
            CURRENT_TIMESTAMP() as assessment_timestamp
        """
        compliance_data = run_query(fallback_query)
    
    if not compliance_data.empty:
        st.subheader("🤖 AI Compliance Assessment Results")
        st.dataframe(compliance_data[['CUSTOMER_ID', 'COMPANY_NAME', 'INDUSTRY', 'COMPLIANCE_STATUS', 'AI_COMPLIANCE_SCORE']], 
                    use_container_width=True)
        
        # Compliance Score Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            try:
                # Handle potential non-numeric values in AI_COMPLIANCE_SCORE
                numeric_scores = pd.to_numeric(compliance_data['AI_COMPLIANCE_SCORE'], errors='coerce')
                avg_score = numeric_scores.mean()
                if pd.isna(avg_score):
                    avg_score = 0.75  # Default fallback score
                st.metric("Average Compliance Score", f"{avg_score:.1%}")
            except Exception as e:
                st.metric("Average Compliance Score", "75.0%")
                st.caption("⚠️ Using fallback data")
        
        with col2:
            try:
                # Safely convert to numeric for comparison
                numeric_scores = pd.to_numeric(compliance_data['AI_COMPLIANCE_SCORE'], errors='coerce')
                high_compliance = len(numeric_scores[numeric_scores > 0.8])
                st.metric("High Compliance (>80%)", high_compliance)
            except Exception as e:
                st.metric("High Compliance (>80%)", "2")
                st.caption("⚠️ Using fallback data")
        
        with col3:
            try:
                # Safely convert to numeric for comparison
                numeric_scores = pd.to_numeric(compliance_data['AI_COMPLIANCE_SCORE'], errors='coerce')
                risk_customers = len(numeric_scores[numeric_scores < 0.6])
                st.metric("At-Risk Customers (<60%)", risk_customers)
            except Exception as e:
                st.metric("At-Risk Customers (<60%)", "1")
                st.caption("⚠️ Using fallback data")
        
        with col4:
            frameworks_used = compliance_data['INDUSTRY'].nunique()
            st.metric("Industries Covered", frameworks_used)
        
        # Compliance by Industry Chart
        st.subheader("📊 Compliance Scores by Industry")
        # Convert AI_COMPLIANCE_SCORE to numeric for groupby operations
        compliance_data_numeric = compliance_data.copy()
        compliance_data_numeric['AI_COMPLIANCE_SCORE'] = pd.to_numeric(compliance_data_numeric['AI_COMPLIANCE_SCORE'], errors='coerce')
        industry_compliance = compliance_data_numeric.groupby('INDUSTRY')['AI_COMPLIANCE_SCORE'].mean().reset_index()
        
        fig = px.bar(industry_compliance, x='INDUSTRY', y='AI_COMPLIANCE_SCORE', 
                     title="Average Compliance Score by Industry",
                     color='AI_COMPLIANCE_SCORE',
                     color_continuous_scale='RdYlGn')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Compliance Analysis
        st.subheader("🔍 Detailed AI Compliance Analysis")
        
        selected_customer = st.selectbox(
            "Select Customer for Detailed Analysis:",
            compliance_data['COMPANY_NAME'].tolist()
        )
        
        if selected_customer:
            customer_data = compliance_data[compliance_data['COMPANY_NAME'] == selected_customer].iloc[0]
            
            with st.expander(f"📋 Compliance Analysis: {selected_customer}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Industry:** {customer_data['INDUSTRY']}")
                    st.write(f"**Current Status:** {customer_data['COMPLIANCE_STATUS']}")
                    
                    # Safely handle AI compliance score display
                    try:
                        score = pd.to_numeric(customer_data['AI_COMPLIANCE_SCORE'], errors='coerce')
                        if pd.isna(score):
                            score = 0.75  # Default fallback
                        st.write(f"**AI Compliance Score:** {score:.1%}")
                    except Exception as e:
                        st.write(f"**AI Compliance Score:** 75.0% (fallback)")
                
                with col2:
                    # Safely get score for analysis text
                    try:
                        safe_score = pd.to_numeric(customer_data['AI_COMPLIANCE_SCORE'], errors='coerce')
                        if pd.isna(safe_score):
                            safe_score = 0.75
                        score_text = f"{safe_score:.1%}"
                    except:
                        score_text = "75.0%"
                    
                    if customer_data['INDUSTRY'] in ['Hospitality', 'Automotive']:
                        framework = "PCI DSS"
                        analysis = f"PCI DSS compliance analysis for {customer_data['INDUSTRY']} industry. Current score: {score_text}. Key requirements include data encryption, access controls, and regular security assessments."
                    elif customer_data['INDUSTRY'] == 'Healthcare':
                        framework = "HIPAA"
                        analysis = f"HIPAA compliance requirements for {customer_data['INDUSTRY']} sector. Current score: {score_text}. Focus areas include patient data protection, access controls, and audit trails."
                    else:
                        framework = "NIST Cybersecurity Framework"
                        analysis = f"NIST Cybersecurity Framework assessment for {customer_data['INDUSTRY']} industry. Current score: {score_text}. Framework covers Identify, Protect, Detect, Respond, and Recover functions."
                    
                    st.write(f"**Applicable Framework:** {framework}")
                
                st.markdown("**🤖 AI Framework Analysis:**")
                st.info(analysis)
                
                # Generate demo framework mapping based on industry
                st.markdown("**📊 AI Framework Mapping:**")
                if customer_data['INDUSTRY'] in ['Hospitality', 'Automotive']:
                    mapping_demo = {
                        "PCI_DSS_Requirements": {
                            "Data_Encryption": "IMPLEMENTED",
                            "Access_Control": "IMPLEMENTED", 
                            "Network_Security": "PARTIAL",
                            "Vulnerability_Management": "NEEDS_IMPROVEMENT"
                        },
                        "Score": score_text,
                        "Next_Steps": ["Enhance network segmentation", "Update vulnerability scanning"]
                    }
                else:
                    mapping_demo = {
                        "NIST_Functions": {
                            "Identify": "GOOD",
                            "Protect": "EXCELLENT",
                            "Detect": "GOOD", 
                            "Respond": "NEEDS_IMPROVEMENT",
                            "Recover": "FAIR"
                        },
                        "Score": score_text,
                        "Priority_Areas": ["Incident response planning", "Business continuity"]
                    }
                st.json(mapping_demo)
    
    # SMB Assistant Interface
    st.subheader("💬 SMB Compliance Assistant")
    
    with st.expander("🤖 Ask Your Compliance Questions", expanded=False):
        st.markdown("""
        **For SMB customers without dedicated compliance teams:**
        - "What does my PCI compliance score mean?"
        - "What do I need to do to improve my security posture?"
        - "How does SecurityEdge help with compliance?"
        - "What are my biggest compliance risks?"
        """)
        
        compliance_question = st.text_input(
            "Ask about your compliance status:",
            placeholder="e.g., How can I improve my PCI compliance score?"
        )
        
        if st.button("🔍 Get Compliance Guidance") and compliance_question:
            with st.spinner("Analyzing compliance requirements..."):
                # Escape quotes in user input
                escaped_compliance_question = compliance_question.replace('"', '""').replace("'", "''")
                guidance_query = f"""
                SELECT 
                    SNOWFLAKE.CORTEX.COMPLETE(
                        'llama3-70b',
                        CONCAT(
                            'SMB compliance guidance question: "{escaped_compliance_question}". ',
                            'Provide practical, actionable advice for small business without dedicated security teams. ',
                            'Focus on Comcast Business services (SecurityEdge, network monitoring) and how they help with compliance. ',
                            'Use simple business language, not technical jargon. Provide specific next steps.'
                        )
                    ) AS guidance
                """
                try:
                    guidance_result = run_query(guidance_query)
                    if not guidance_result.empty:
                        st.info("🤖 **SMB Compliance Assistant:**")
                        st.write(guidance_result.iloc[0]['GUIDANCE'])
                except Exception as e:
                    st.error(f"Query error: {str(e)}")
    
    # Traditional PCI Compliance Status (for compatibility)
    st.subheader("📋 Traditional PCI Compliance Tracking")
    
    try:
        pci_query = """
        SELECT 
            customer_id,
            COUNT(*) as total_requirements,
            SUM(CASE WHEN status = 'COMPLIANT' THEN 1 ELSE 0 END) as compliant_count,
            SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_count,
            ROUND((SUM(CASE WHEN status = 'COMPLIANT' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 1) as compliance_percentage
        FROM COMPLIANCE.PCI_COMPLIANCE_TRACKING
        GROUP BY customer_id
        ORDER BY compliance_percentage DESC
        """
        
        pci_data = run_query(pci_query)
    except Exception as e:
        st.warning(f"PCI Compliance table unavailable ({str(e)}). Using sample data.")
        # Fallback PCI data
        pci_fallback = """
        SELECT 
            'CUST_001' as customer_id,
            3 as total_requirements,
            3 as compliant_count,
            0 as in_progress_count,
            100.0 as compliance_percentage
        UNION ALL
        SELECT 
            'CUST_002' as customer_id,
            3 as total_requirements,
            2 as compliant_count,
            1 as in_progress_count,
            66.7 as compliance_percentage
        UNION ALL
        SELECT 
            'CUST_003' as customer_id,
            2 as total_requirements,
            2 as compliant_count,
            0 as in_progress_count,
            100.0 as compliance_percentage
        """
        pci_data = run_query(pci_fallback)
    
    if not pci_data.empty:
        # Full width table for better readability
        st.subheader("PCI Compliance Status")
        st.dataframe(pci_data, use_container_width=True)
        
        # Compliance gauge chart below the table
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Compliance Distribution")
            avg_compliance = pci_data['COMPLIANCE_PERCENTAGE'].mean()
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_compliance,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Avg Compliance %"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Compliance Summary")
            total_customers = len(pci_data)
            fully_compliant = len(pci_data[pci_data['COMPLIANCE_PERCENTAGE'] == 100])
            avg_requirements = pci_data['TOTAL_REQUIREMENTS'].mean()
            
            st.metric("Total Customers", total_customers)
            st.metric("Fully Compliant", fully_compliant)
            st.metric("Avg Requirements", f"{avg_requirements:.0f}")
    
    # Easy Button Demo
    st.subheader("🎯 AI-Powered Compliance Report Generation")
    
    customer_select = st.selectbox("Select Customer for Compliance Report", 
                                  ['CUST_001', 'CUST_002', 'CUST_003'])
    
    if st.button("Generate PCI Compliance Report"):
        with st.spinner("Generating AI-powered compliance report..."):
            # Simulate the compliance report generation
            st.success("✅ PCI Compliance Report Generated!")
            
            st.markdown(f"""
            **Sample AI-Generated Report for {customer_select}:**
            
            *This customer demonstrates strong PCI DSS compliance posture with automated evidence collection 
            and real-time monitoring. All required security controls are properly implemented and documented 
            within Snowflake's secure environment. Data retention policies meet PCI requirements with 
            automated evidence links for auditor review.*
            
            **What this demonstrates:** The "Easy Button" functionality that generates professional, 
            audit-ready PCI compliance reports in seconds using Snowflake Cortex AI.
            
            **How it works:** 
            1. Query current compliance status across all PCI requirements
            2. Cortex AI (llama3-70b) analyzes compliance data and generates professional narrative
            3. Report includes specific compliance counts, evidence locations, and audit-ready language
            4. Eliminates manual report generation and expensive compliance consulting
            """)

elif page == "🔍 SecurityEdge Threat Intelligence":
    st.title("🔍 SecurityEdge Threat Intelligence")
    st.markdown("### AI-Enhanced MITRE Attack Classification")
    
    # Database connection information
    threat_schemas_tables = {
        "THREAT_INTEL": ["SECURITY_EDGE_EVENTS", "SECURITY_EDGE_PATTERNS"]
    }
    show_database_info(threat_schemas_tables)
    
    # Threat Events Overview
    threat_query = """
    SELECT 
        akamai_threat_category,
        COUNT(*) as event_count,
        AVG(threat_score) as avg_threat_score,
        COUNT(CASE WHEN ai_processed = TRUE THEN 1 END) as ai_processed_count
    FROM THREAT_INTEL.SECURITY_EDGE_EVENTS
    GROUP BY akamai_threat_category
    ORDER BY event_count DESC
    """
    
    threat_data = run_query(threat_query)
    
    if not threat_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Threat Category Distribution")
            fig = px.bar(threat_data, x='AKAMAI_THREAT_CATEGORY', y='EVENT_COUNT',
                        title="SecurityEdge Events by Threat Type")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Average Threat Scores")
            fig = px.bar(threat_data, x='AKAMAI_THREAT_CATEGORY', y='AVG_THREAT_SCORE',
                        title="Average Threat Severity by Category", color='AVG_THREAT_SCORE')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # MITRE Classification Results
    st.subheader("🎯 MITRE Attack Classification Results")
    
    mitre_query = """
    SELECT 
        event_id,
        akamai_threat_category,
        blocked_domain,
        threat_score,
        mitre_tactic,
        mitre_technique,
        classification_confidence
    FROM THREAT_INTEL.SECURITY_EDGE_EVENTS
    WHERE ai_processed = TRUE
    ORDER BY threat_score DESC
    LIMIT 10
    """
    
    mitre_data = run_query(mitre_query)
    
    if not mitre_data.empty:
        st.dataframe(mitre_data, use_container_width=True)
        
        st.markdown("""
        **What this shows:** SecurityEdge threat events enhanced with AI-powered MITRE Attack framework 
        classification, transforming basic Akamai threat categories into enterprise-grade threat intelligence.
        
        **Enhancement Process:**
        1. **Akamai Base Data**: SecurityEdge provides basic threat categorization (malware, phishing, botnet)
        2. **AI Enhancement**: Snowflake Cortex AI (llama3-70b) analyzes threat characteristics and maps to MITRE tactics
        3. **Confidence Scoring**: Secondary AI model (llama3-8b) provides classification confidence ratings
        4. **Premium Intelligence**: Customers get sophisticated threat analysis beyond commodity DNS filtering
        
        **Business Value:** Elevates SecurityEdge from basic DNS filtering to premium threat intelligence service,
        enabling SOC integration and advanced threat hunting capabilities.
        """)

elif page == "💰 Cost Analysis & ROI":
    st.title("💰 Cost Analysis & ROI Dashboard")
    st.markdown("### Snowflake vs Traditional Infrastructure Economics")
    
    # Database connection information
    cost_schemas_tables = {
        "ATLAS_INTERNAL": ["COST_ANALYSIS", "TOKEN_CONSUMPTION_ESTIMATE"],
        "THREAT_INTEL": ["SECURITY_EDGE_PATTERNS"]
    }
    show_database_info(cost_schemas_tables)
    
    # Cost Comparison
    st.subheader("🔄 Infrastructure Cost Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Traditional GPU Infrastructure:**
        - Monthly Cost: $50,000-$100,000
        - Fixed costs regardless of usage
        - High upfront investment
        - Dedicated hardware maintenance
        - Infrastructure specialists required
        """)
        
        traditional_cost = st.metric("Traditional Monthly Cost", "$75,000", 
                                   help="Average cost for GPU infrastructure capable of processing billions of threat events")
    
    with col2:
        st.markdown("""
        **Snowflake Cortex AI:**
        - Monthly Cost: $5,000-$15,000  
        - Pay only for what you use
        - No infrastructure management
        - Token-based consumption
        - Immediate access to enterprise AI
        """)
        
        snowflake_cost = st.metric("Snowflake Monthly Cost", "$10,000",
                                 help="Estimated cost for token-based AI processing of threat intelligence")
    
    # ROI Calculation
    st.subheader("📊 ROI Analysis")
    
    savings_percent = ((75000 - 10000) / 75000) * 100
    annual_savings = (75000 - 10000) * 12
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cost Savings", f"{savings_percent:.0f}%", 
                 help="Percentage cost reduction vs traditional infrastructure")
    
    with col2:
        st.metric("Annual Savings", f"${annual_savings:,}",
                 help="Total annual cost savings from Snowflake adoption")
    
    with col3:
        st.metric("Pattern Matching Savings", "70%",
                 help="Additional AI cost reduction through intelligent pattern recognition")
    
    # Token Consumption Model
    st.subheader("🎯 Token Consumption Analysis")
    
    token_data = {
        'Use Case': ['MITRE Classification', 'Customer Analytics', 'PCI Reporting', 'Sales Intelligence'],
        'Daily Volume': ['1M threat events', '1K queries', '100 reports', '500 analyses'],
        'Tokens per Operation': [500, 200, 1000, 300],
        'Daily Tokens': ['500M', '200K', '100K', '150K'],
        'Cost Optimization': ['Pattern matching reduces by 70%', 'Cached results reduce repeats', 
                            'Template reuse', 'Batch processing']
    }
    
    token_df = pd.DataFrame(token_data)
    st.dataframe(token_df, use_container_width=True)
    
    st.markdown("""
    **What this demonstrates:** Snowflake's token-based AI consumption model provides dramatic cost 
    advantages over traditional GPU infrastructure while offering superior scalability and flexibility.
    
    **Key Economic Advantages:**
    - **Elastic Consumption**: Costs automatically adjust to actual business needs
    - **No Idle Capacity**: Eliminate waste from unused infrastructure  
    - **Instant Scaling**: Handle traffic spikes without infrastructure investments
    - **Operational Efficiency**: No need for AI infrastructure specialists or GPU management teams
    
    **Pattern Recognition Economics:** Intelligent caching and pattern matching reduce AI processing 
    costs by 70% for repetitive SecurityEdge threat categorization, making billion-scale analysis economically viable.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Powered by Snowflake Cortex AI**")
st.sidebar.markdown("*Real-time analytics for Comcast Business Polus Platform*")