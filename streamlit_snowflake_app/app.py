import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time
import json

# Page configuration
st.set_page_config(
    page_title="Cortex AI Demo - Streamlit in Snowflake",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #4CAF50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .highlight-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E90FF;
        margin: 1rem 0;
    }
    .ai-box {
        background-color: #f5f5ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #6A5ACD;
        margin: 1rem 0;
    }
    .agent-message {
        background-color: #e8f4fd;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196F3;
    }
    .user-message {
        background-color: #f0f8e8;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Simulated Snowflake connection functions (replace with actual connection in production)
@st.cache_data
def get_cortex_sentiment_data():
    """Simulated customer sentiment analysis using Cortex AI"""
    np.random.seed(42)
    feedback_data = {
        'feedback_id': range(1, 21),
        'customer_id': np.random.randint(1000, 9999, 20),
        'product_name': np.random.choice(['Laptop Pro 15', 'Wireless Mouse', 'Mechanical Keyboard', 'Monitor 27 inch', 'Tablet 10 inch'], 20),
        'review_text': [
            'Absolutely love this laptop! Performance is incredible and battery life exceeds expectations.',
            'Great wireless mouse with excellent tracking. Only complaint is click sound is a bit loud.',
            'This mechanical keyboard has transformed my typing experience. Exceptional build quality.',
            'Disappointed with this purchase. Laptop runs very hot and fan noise is excessive.',
            'Solid USB-C hub with good port selection. Works well with MacBook.',
            'Webcam quality is decent for the price. Video clear in good lighting but struggles in low light.',
            'Outstanding monitor with brilliant color reproduction. Great value for money.',
            'Impressive tablet with smooth performance and beautiful display. Battery life excellent.',
            'Very poor experience with this smartphone. Battery drains quickly and interface is laggy.',
            'These headphones deliver exceptional audio quality. Best purchase this year!',
            'Smart watch with comprehensive health tracking. Interface intuitive and battery impressive.',
            'Fantastic laptop for professional work. Customer service was excellent.',
            'Mouse works adequately but wireless connection occasionally drops. Expected more reliability.',
            'Keyboard enthusiasts will love this product. Responsive switches and customizable backlight.',
            'Hub stopped working after two weeks. Build quality seems poor.',
            'Perfect for gaming and productivity. Highly recommend for demanding users.',
            'Ergonomic design fits perfectly. Great for long work sessions.',
            'Color accuracy is superb for photo editing. Professional grade quality.',
            'Overpriced for what you get. Similar products available for much less.',
            'Excellent customer support helped resolve my issues quickly.'
        ],
        'rating': np.random.randint(1, 6, 20),
        'sentiment_score': np.random.uniform(-0.8, 0.9, 20),
        'sentiment_category': np.random.choice(['Positive', 'Negative', 'Neutral'], 20, p=[0.6, 0.25, 0.15])
    }
    df = pd.DataFrame(feedback_data)
    # Adjust sentiment categories based on scores for realism
    df.loc[df['sentiment_score'] > 0.1, 'sentiment_category'] = 'Positive'
    df.loc[df['sentiment_score'] < -0.1, 'sentiment_category'] = 'Negative'
    df.loc[(df['sentiment_score'] >= -0.1) & (df['sentiment_score'] <= 0.1), 'sentiment_category'] = 'Neutral'
    return df

@st.cache_data
def get_ai_agent_conversations():
    """Simulated AI agent conversation data"""
    conversations = [
        {
            'conversation_id': 'CONV_001',
            'customer_id': 1001,
            'agent_type': 'Sales Assistant',
            'messages': [
                {'type': 'user', 'text': 'I am looking for a laptop for gaming and work. What would you recommend?', 'timestamp': '2024-07-20 10:30:00'},
                {'type': 'assistant', 'text': 'Based on your needs, I recommend the Laptop Pro 15. It offers excellent performance for both gaming and professional work, with outstanding battery life and display quality. Would you like to know more about its specifications?', 'timestamp': '2024-07-20 10:30:15'}
            ],
            'intent': 'product_recommendation',
            'confidence': 0.95,
            'status': 'active'
        },
        {
            'conversation_id': 'CONV_002',
            'customer_id': 1004,
            'agent_type': 'Support Agent',
            'messages': [
                {'type': 'user', 'text': 'My laptop is overheating and making loud fan noises. This is very frustrating!', 'timestamp': '2024-07-20 11:15:00'},
                {'type': 'assistant', 'text': 'I understand your frustration with the overheating issue. This can indeed be concerning. Let me help you troubleshoot this. First, could you tell me what applications you typically run when this happens?', 'timestamp': '2024-07-20 11:15:30'}
            ],
            'intent': 'technical_support',
            'confidence': 0.88,
            'status': 'in_progress'
        },
        {
            'conversation_id': 'CONV_003',
            'customer_id': 1007,
            'agent_type': 'Product Expert',
            'messages': [
                {'type': 'user', 'text': 'Can you explain the difference between your monitors? I need one for photo editing.', 'timestamp': '2024-07-20 14:20:00'},
                {'type': 'assistant', 'text': 'For photo editing, the Monitor 27 inch is perfect! It features exceptional color reproduction with 99% sRGB coverage, making it ideal for professional photo work. The 27-inch size provides ample workspace for editing tools.', 'timestamp': '2024-07-20 14:20:45'}
            ],
            'intent': 'product_comparison',
            'confidence': 0.92,
            'status': 'resolved'
        }
    ]
    return conversations

@st.cache_data
def get_ai_insights_data():
    """Simulated AI-generated business insights"""
    np.random.seed(42)
    insights = {
        'product_insights': [
            {
                'product': 'Laptop Pro 15',
                'ai_summary': 'High-performing product with excellent customer satisfaction. Strong sales in Q2 2024 with 94% positive sentiment. Recommended for upselling to premium customers.',
                'recommendation': 'Increase inventory by 25% and target marketing to professionals',
                'risk_level': 'Low',
                'predicted_demand': 'High'
            },
            {
                'product': 'Wireless Mouse',
                'ai_summary': 'Steady performer with moderate satisfaction. Some complaints about connection reliability. Consider product improvements.',
                'recommendation': 'Address connectivity issues in next version',
                'risk_level': 'Medium',
                'predicted_demand': 'Medium'
            }
        ],
        'customer_intelligence': [
            {
                'segment': 'Premium',
                'ai_profile': 'High-value customers focused on quality over price. Prefer cutting-edge technology and premium support. Average purchase value $1,200.',
                'churn_risk': 'Low',
                'upsell_opportunity': 'High',
                'recommended_actions': 'Offer exclusive products and priority support'
            },
            {
                'segment': 'Standard',
                'ai_profile': 'Price-conscious customers seeking reliable products. Value good customer service and product warranties. Average purchase value $350.',
                'churn_risk': 'Medium',
                'upsell_opportunity': 'Medium',
                'recommended_actions': 'Focus on value propositions and bundle deals'
            }
        ]
    }
    return insights

@st.cache_data
def get_anomaly_detection_data():
    """Simulated anomaly detection results"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=180, freq='D')
    
    # Generate base revenue with trend and seasonality
    base_revenue = 5000 + np.sin(np.arange(180) * 2 * np.pi / 7) * 1000  # Weekly pattern
    base_revenue += np.arange(180) * 10  # Growth trend
    noise = np.random.normal(0, 500, 180)
    daily_revenue = base_revenue + noise
    
    # Add some anomalies
    anomaly_days = [15, 45, 89, 123, 156]
    for day in anomaly_days:
        if day < len(daily_revenue):
            daily_revenue[day] += np.random.choice([-3000, 4000])  # Significant deviation
    
    # Calculate moving averages and detect anomalies
    df = pd.DataFrame({
        'date': dates,
        'daily_revenue': daily_revenue
    })
    
    df['moving_avg'] = df['daily_revenue'].rolling(window=7).mean()
    df['moving_std'] = df['daily_revenue'].rolling(window=7).std()
    df['anomaly_flag'] = (abs(df['daily_revenue'] - df['moving_avg']) > 2 * df['moving_std']).astype(bool)
    
    return df

@st.cache_data
def simulate_semantic_query(query):
    """Simulate natural language query processing"""
    responses = {
        'sales': {
            'data': pd.DataFrame({
                'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'revenue': [45000, 52000, 48000, 61000, 58000],
                'growth': ['-', '15.6%', '-7.7%', '27.1%', '-4.9%']
            }),
            'summary': 'Sales show strong performance with total revenue of $264,000 over 5 months. Peak in April with $61,000.'
        },
        'customers': {
            'data': pd.DataFrame({
                'segment': ['Premium', 'Standard', 'Basic', 'VIP'],
                'count': [150, 450, 300, 50],
                'avg_value': [1200, 350, 150, 2000]
            }),
            'summary': 'Customer base of 950 customers across 4 segments. VIP segment has highest average value at $2,000.'
        },
        'products': {
            'data': pd.DataFrame({
                'product': ['Laptop Pro 15', 'Monitor 27 inch', 'Tablet 10 inch'],
                'units_sold': [120, 89, 156],
                'revenue': [155880, 26699, 62384]
            }),
            'summary': 'Top selling product is Tablet 10 inch with 156 units, but Laptop Pro 15 generates most revenue at $155,880.'
        }
    }
    
    # Simple keyword matching
    if any(word in query.lower() for word in ['sales', 'revenue', 'money']):
        return responses['sales']
    elif any(word in query.lower() for word in ['customer', 'segment', 'user']):
        return responses['customers']
    elif any(word in query.lower() for word in ['product', 'item', 'goods']):
        return responses['products']
    else:
        return responses['sales']  # Default

# Main title
st.markdown('<h1 class="main-header">🧠 Cortex AI Demo: Intelligent Analytics in Snowflake</h1>', unsafe_allow_html=True)

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 AI Overview", 
    "💭 Sentiment Analysis", 
    "🤖 AI Agents", 
    "🔍 Semantic Intelligence",
    "📊 AI Insights & Predictions",
    "⚡ Anomaly Detection",
    "🎮 Interactive Demo"
])

with tab1:
    st.markdown('<h2 class="section-header">🎯 Cortex AI Overview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="ai-box">
        <h3>🧠 Snowflake Cortex AI Platform</h3>
        This comprehensive demo showcases advanced AI capabilities powered by Snowflake's Cortex AI platform,
        including natural language processing, intelligent agents, and predictive analytics.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 🚀 Featured AI Capabilities:
        
        **🤖 Intelligent Agents**
        - Conversational AI for customer support
        - Sales assistance and product recommendations
        - Technical support with context awareness
        
        **💭 Sentiment Analysis**
        - Real-time customer feedback analysis
        - Product sentiment tracking
        - Automated review summarization
        
        **🔍 Semantic Intelligence**
        - Natural language queries to your data
        - Business intelligence through conversation
        - Context-aware data exploration
        
        **📈 Predictive Analytics**
        - AI-powered sales forecasting
        - Customer behavior prediction
        - Anomaly detection and alerts
        
        **🎯 Personalized Insights**
        - Customer segment analysis
        - Product performance optimization
        - Risk assessment and recommendations
        """)
    
    with col2:
        # AI Platform Status
        st.markdown("### 🔧 Platform Status")
        
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🤖 Active Agents", "3", delta="1")
            with col_b:
                st.metric("💭 Sentiment Models", "2", delta="Active")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            col_c, col_d = st.columns(2)
            with col_c:
                st.metric("🔍 Semantic Queries", "1,247", delta="156")
            with col_d:
                st.metric("⚡ Anomalies Detected", "12", delta="-3")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick AI Demo
        st.markdown("### 🎮 Quick AI Demo")
        if st.button("🎲 Generate AI Insight", key="ai_demo"):
            insights = [
                "💡 Customer satisfaction increased 15% after product improvements",
                "📈 Premium segment shows 40% higher lifetime value",
                "🎯 AI agents resolved 89% of queries without human intervention",
                "⚡ Detected unusual sales spike in Electronics category",
                "🔄 Recommended inventory adjustment for Q4 demand"
            ]
            st.success(np.random.choice(insights))

with tab2:
    st.markdown('<h2 class="section-header">💭 Cortex AI Sentiment Analysis</h2>', unsafe_allow_html=True)
    
    # Load sentiment data
    sentiment_data = get_cortex_sentiment_data()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Sentiment Analysis Dashboard")
        
        # Sentiment distribution
        sentiment_counts = sentiment_data['sentiment_category'].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Customer Sentiment Distribution",
            color_discrete_map={'Positive': '#4CAF50', 'Negative': '#f44336', 'Neutral': '#FF9800'}
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Sentiment by product
        sentiment_by_product = sentiment_data.groupby(['product_name', 'sentiment_category']).size().unstack(fill_value=0)
        fig_product = px.bar(
            sentiment_by_product,
            title="Sentiment Analysis by Product",
            color_discrete_map={'Positive': '#4CAF50', 'Negative': '#f44336', 'Neutral': '#FF9800'}
        )
        st.plotly_chart(fig_product, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Sentiment Metrics")
        
        total_reviews = len(sentiment_data)
        avg_sentiment = sentiment_data['sentiment_score'].mean()
        positive_pct = (sentiment_data['sentiment_category'] == 'Positive').mean() * 100
        
        st.metric("📝 Total Reviews", f"{total_reviews:,}")
        st.metric("💗 Average Sentiment", f"{avg_sentiment:.2f}", 
                 delta=f"{avg_sentiment - 0.1:.2f}")
        st.metric("👍 Positive Rate", f"{positive_pct:.1f}%", 
                 delta=f"{positive_pct - 55:.1f}%")
        
        # Product selector for detailed analysis
        st.markdown("### 🔍 Product Deep Dive")
        selected_product = st.selectbox(
            "Select Product:",
            sentiment_data['product_name'].unique()
        )
        
        product_data = sentiment_data[sentiment_data['product_name'] == selected_product]
        if len(product_data) > 0:
            st.write(f"**{selected_product}**")
            st.write(f"Reviews: {len(product_data)}")
            st.write(f"Avg Sentiment: {product_data['sentiment_score'].mean():.2f}")
            st.write(f"Avg Rating: {product_data['rating'].mean():.1f}/5")
    
    # Recent reviews with AI analysis
    st.markdown("### 📋 Recent Customer Reviews with AI Analysis")
    
    for idx, review in sentiment_data.head(5).iterrows():
        with st.expander(f"Review #{review['feedback_id']} - {review['product_name']} ({review['sentiment_category']})"):
            st.write(f"**Customer:** {review['customer_id']}")
            st.write(f"**Rating:** {'⭐' * review['rating']} ({review['rating']}/5)")
            st.write(f"**Sentiment Score:** {review['sentiment_score']:.2f}")
            st.write(f"**Review:** {review['review_text']}")
            
            # Simulated AI insights
            if review['sentiment_score'] > 0.3:
                st.success("🎯 **AI Insight:** Highly positive feedback highlighting product strengths")
            elif review['sentiment_score'] < -0.3:
                st.error("⚠️ **AI Alert:** Negative feedback requiring immediate attention")
            else:
                st.info("📝 **AI Note:** Neutral feedback with balanced perspective")

with tab3:
    st.markdown('<h2 class="section-header">🤖 AI Agents & Conversations</h2>', unsafe_allow_html=True)
    
    conversations = get_ai_agent_conversations()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Live Agent Conversations")
        
        # Agent performance metrics
        agent_metrics = pd.DataFrame({
            'Agent Type': ['Sales Assistant', 'Support Agent', 'Product Expert'],
            'Conversations': [45, 23, 31],
            'Resolved': [38, 18, 29],
            'Avg Response Time': ['12s', '18s', '15s'],
            'Satisfaction': [4.2, 3.8, 4.5]
        })
        
        st.dataframe(agent_metrics, use_container_width=True)
        
        # Conversation simulator
        st.markdown("### 🎭 AI Agent Simulator")
        
        agent_type = st.selectbox("Choose Agent Type:", 
                                ["Sales Assistant", "Support Agent", "Product Expert"])
        
        user_query = st.text_area("Enter your question:", 
                                placeholder="e.g., I need help with my laptop overheating...")
        
        if st.button("💬 Send to AI Agent"):
            # Simulate AI response based on agent type
            responses = {
                "Sales Assistant": f"Thank you for your interest! Based on your query about '{user_query[:50]}...', I'd recommend checking our latest products. Our AI analysis suggests you might be interested in our premium laptop series with advanced cooling systems.",
                "Support Agent": f"I understand your concern about '{user_query[:50]}...'. Let me help you troubleshoot this issue. Our AI diagnostics suggest this might be related to thermal management. Here are the steps we can try...",
                "Product Expert": f"Great question about '{user_query[:50]}...'. Based on our AI knowledge base, here are the technical specifications and comparisons that would be most relevant to your needs..."
            }
            
            st.markdown(f"""
            <div class="agent-message">
            <strong>🤖 {agent_type}</strong><br>
            {responses[agent_type]}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Agent Analytics")
        
        # Daily agent activity
        activity_data = pd.DataFrame({
            'Hour': range(9, 18),
            'Conversations': np.random.poisson(8, 9)
        })
        
        fig_activity = px.line(activity_data, x='Hour', y='Conversations',
                              title="Hourly Agent Activity")
        st.plotly_chart(fig_activity, use_container_width=True)
        
        # Intent detection
        intent_data = pd.DataFrame({
            'Intent': ['Product Inquiry', 'Technical Support', 'Billing', 'General'],
            'Count': [45, 32, 18, 12],
            'Confidence': [0.92, 0.87, 0.94, 0.78]
        })
        
        fig_intent = px.bar(intent_data, x='Intent', y='Count',
                           title="AI Intent Detection")
        st.plotly_chart(fig_intent, use_container_width=True)
    
    # Sample conversations
    st.markdown("### 📝 Sample AI Conversations")
    
    for conv in conversations:
        with st.expander(f"🔤 {conv['conversation_id']} - {conv['agent_type']} ({conv['status']})"):
            st.write(f"**Customer ID:** {conv['customer_id']}")
            st.write(f"**Intent:** {conv['intent']} (Confidence: {conv['confidence']:.1%})")
            st.write(f"**Status:** {conv['status']}")
            
            for message in conv['messages']:
                if message['type'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                    <strong>👤 Customer:</strong> {message['text']}
                    <br><small>{message['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="agent-message">
                    <strong>🤖 AI Agent:</strong> {message['text']}
                    <br><small>{message['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)

with tab4:
    st.markdown('<h2 class="section-header">🔍 Semantic Intelligence & Natural Language Queries</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🗣️ Ask Your Data Anything")
        
        st.markdown("""
        <div class="ai-box">
        <h4>💡 How it works</h4>
        Snowflake's Cortex Analyst allows you to query your data using natural language. 
        The AI understands business context and translates your questions into SQL queries automatically.
        </div>
        """, unsafe_allow_html=True)
        
        # Natural language query interface
        query = st.text_area(
            "🎯 Ask a question about your business data:",
            placeholder="e.g., What were our sales last month by region?\nWhich customers have the highest lifetime value?\nShow me product performance trends...",
            height=100
        )
        
        col_a, col_b = st.columns([1, 3])
        with col_a:
            ask_button = st.button("🔍 Analyze", type="primary")
        with col_b:
            if st.button("💡 Example Queries"):
                examples = [
                    "What were the top selling products last quarter?",
                    "Show me customer segments by revenue",
                    "Which regions have declining sales?",
                    "What's the average order value by customer segment?"
                ]
                st.info("Try these examples:\n• " + "\n• ".join(examples))
        
        if ask_button and query:
            with st.spinner("🧠 AI is analyzing your query..."):
                time.sleep(2)  # Simulate processing time
                
                result = simulate_semantic_query(query)
                
                st.success("✅ Query processed successfully!")
                
                # Show AI interpretation
                st.markdown("### 🎯 AI Understanding")
                st.info(f"**Interpreted as:** {result['summary']}")
                
                # Show results
                st.markdown("### 📊 Results")
                st.dataframe(result['data'], use_container_width=True)
                
                # Generate visualization if appropriate
                if 'revenue' in result['data'].columns:
                    fig = px.bar(result['data'], x=result['data'].columns[0], y='revenue',
                                title="Revenue Analysis")
                    st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Query Insights")
        
        # Query statistics
        st.metric("📈 Queries Today", "47", delta="12")
        st.metric("⚡ Avg Response Time", "1.2s", delta="-0.3s")
        st.metric("🎯 Success Rate", "94%", delta="2%")
        
        # Popular query types
        st.markdown("### 🔥 Popular Query Types")
        query_types = pd.DataFrame({
            'Type': ['Sales Analysis', 'Customer Insights', 'Product Performance', 'Financial Reports'],
            'Count': [23, 18, 15, 12]
        })
        
        fig_types = px.pie(query_types, values='Count', names='Type',
                          title="Query Distribution")
        st.plotly_chart(fig_types, use_container_width=True)
        
        # Semantic model info
        st.markdown("### 📚 Available Data Models")
        st.markdown("""
        **🏢 Business Model**
        - Sales transactions
        - Customer demographics
        - Product catalog
        - Regional data
        
        **📊 Analytics Model**
        - Time series data
        - Performance metrics
        - Trend analysis
        - Forecasting data
        """)

with tab5:
    st.markdown('<h2 class="section-header">📊 AI Insights & Predictive Analytics</h2>', unsafe_allow_html=True)
    
    insights_data = get_ai_insights_data()
    
    # AI-generated insights dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Product Intelligence")
        
        for insight in insights_data['product_insights']:
            st.markdown(f"""
            <div class="ai-box">
            <h4>📦 {insight['product']}</h4>
            <p><strong>AI Summary:</strong> {insight['ai_summary']}</p>
            <p><strong>Recommendation:</strong> {insight['recommendation']}</p>
            <p><strong>Risk Level:</strong> <span style="color: {'green' if insight['risk_level'] == 'Low' else 'orange'}">
            {insight['risk_level']}</span></p>
            <p><strong>Predicted Demand:</strong> {insight['predicted_demand']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 👥 Customer Intelligence")
        
        for insight in insights_data['customer_intelligence']:
            st.markdown(f"""
            <div class="ai-box">
            <h4>🎭 {insight['segment']} Segment</h4>
            <p><strong>AI Profile:</strong> {insight['ai_profile']}</p>
            <p><strong>Churn Risk:</strong> <span style="color: {'green' if insight['churn_risk'] == 'Low' else 'orange'}">
            {insight['churn_risk']}</span></p>
            <p><strong>Upsell Opportunity:</strong> {insight['upsell_opportunity']}</p>
            <p><strong>Actions:</strong> {insight['recommended_actions']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Predictive analytics
    st.markdown("### 🔮 AI-Powered Predictions")
    
    prediction_col1, prediction_col2, prediction_col3 = st.columns(3)
    
    with prediction_col1:
        st.markdown("#### 📈 Sales Forecast")
        # Generate forecast data
        forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        base_forecast = 5000 + np.sin(np.arange(30) * 2 * np.pi / 7) * 1000
        forecast_values = base_forecast + np.random.normal(0, 200, 30)
        
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Predicted_Revenue': forecast_values,
            'Confidence_Lower': forecast_values * 0.9,
            'Confidence_Upper': forecast_values * 1.1
        })
        
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df['Date'], y=forecast_df['Predicted_Revenue'],
            mode='lines', name='Forecast'
        ))
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df['Date'], y=forecast_df['Confidence_Upper'],
            fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False
        ))
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df['Date'], y=forecast_df['Confidence_Lower'],
            fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)',
            name='Confidence Interval'
        ))
        fig_forecast.update_layout(title="30-Day Revenue Forecast", height=300)
        st.plotly_chart(fig_forecast, use_container_width=True)
    
    with prediction_col2:
        st.markdown("#### 👥 Customer Behavior")
        behavior_data = pd.DataFrame({
            'Behavior': ['Will Purchase', 'Will Churn', 'Will Upgrade', 'Will Return'],
            'Probability': [0.73, 0.12, 0.45, 0.89],
            'Impact': ['High', 'High', 'Medium', 'Low']
        })
        
        fig_behavior = px.bar(behavior_data, x='Behavior', y='Probability',
                             title="Customer Behavior Predictions",
                             color='Impact')
        fig_behavior.update_layout(height=300)
        st.plotly_chart(fig_behavior, use_container_width=True)
    
    with prediction_col3:
        st.markdown("#### 📦 Inventory Optimization")
        inventory_data = pd.DataFrame({
            'Product': ['Laptop Pro', 'Mouse', 'Keyboard', 'Monitor'],
            'Current': [150, 500, 200, 75],
            'Optimal': [180, 450, 250, 90],
            'Status': ['Restock', 'Reduce', 'Increase', 'Restock']
        })
        
        fig_inventory = px.bar(inventory_data, x='Product', y=['Current', 'Optimal'],
                              title="Inventory Optimization",
                              barmode='group')
        fig_inventory.update_layout(height=300)
        st.plotly_chart(fig_inventory, use_container_width=True)

with tab6:
    st.markdown('<h2 class="section-header">⚡ AI-Powered Anomaly Detection</h2>', unsafe_allow_html=True)
    
    anomaly_data = get_anomaly_detection_data()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📊 Real-time Anomaly Monitoring")
        
        # Main anomaly detection chart
        fig_anomaly = go.Figure()
        
        # Normal data points
        normal_data = anomaly_data[~anomaly_data['anomaly_flag']]
        fig_anomaly.add_trace(go.Scatter(
            x=normal_data['date'], y=normal_data['daily_revenue'],
            mode='markers', name='Normal', marker=dict(color='blue', size=4)
        ))
        
        # Anomaly data points
        anomaly_points = anomaly_data[anomaly_data['anomaly_flag']]
        fig_anomaly.add_trace(go.Scatter(
            x=anomaly_points['date'], y=anomaly_points['daily_revenue'],
            mode='markers', name='Anomaly Detected', 
            marker=dict(color='red', size=8, symbol='diamond')
        ))
        
        # Moving average line
        fig_anomaly.add_trace(go.Scatter(
            x=anomaly_data['date'], y=anomaly_data['moving_avg'],
            mode='lines', name='7-Day Average', line=dict(color='green', width=2)
        ))
        
        fig_anomaly.update_layout(
            title="Daily Revenue with Anomaly Detection",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            height=400
        )
        st.plotly_chart(fig_anomaly, use_container_width=True)
        
        # Anomaly details
        if len(anomaly_points) > 0:
            st.markdown("### 🚨 Detected Anomalies")
            
            for idx, row in anomaly_points.iterrows():
                deviation = ((row['daily_revenue'] - row['moving_avg']) / row['moving_avg']) * 100
                
                if deviation > 0:
                    alert_type = "success"
                    icon = "📈"
                    message = f"Positive anomaly: Revenue spike of {deviation:.1f}% above average"
                else:
                    alert_type = "error" 
                    icon = "📉"
                    message = f"Negative anomaly: Revenue drop of {abs(deviation):.1f}% below average"
                
                if alert_type == "success":
                    st.success(f"{icon} **{row['date'].strftime('%Y-%m-%d')}:** {message}")
                else:
                    st.error(f"{icon} **{row['date'].strftime('%Y-%m-%d')}:** {message}")
                
                # AI explanation
                explanations = {
                    "positive": [
                        "Possible promotional campaign effect",
                        "Seasonal demand increase detected",
                        "New product launch impact",
                        "Market expansion success"
                    ],
                    "negative": [
                        "Potential system outage impact",
                        "Competitive market pressure",
                        "Supply chain disruption",
                        "Economic factors influence"
                    ]
                }
                
                explanation = np.random.choice(explanations["positive" if deviation > 0 else "negative"])
                st.info(f"🤖 **AI Insight:** {explanation}")
    
    with col2:
        st.markdown("### 📈 Anomaly Statistics")
        
        total_days = len(anomaly_data)
        anomaly_count = anomaly_data['anomaly_flag'].sum()
        anomaly_rate = (anomaly_count / total_days) * 100
        
        st.metric("📅 Days Monitored", f"{total_days:,}")
        st.metric("🚨 Anomalies Found", f"{anomaly_count:,}")
        st.metric("📊 Anomaly Rate", f"{anomaly_rate:.1f}%")
        
        # Anomaly types
        if anomaly_count > 0:
            positive_anomalies = len(anomaly_points[anomaly_points['daily_revenue'] > anomaly_points['moving_avg']])
            negative_anomalies = anomaly_count - positive_anomalies
            
            st.markdown("### 🎯 Anomaly Breakdown")
            st.write(f"📈 Positive: {positive_anomalies}")
            st.write(f"📉 Negative: {negative_anomalies}")
        
        # Detection settings
        st.markdown("### ⚙️ Detection Settings")
        sensitivity = st.slider("Sensitivity Level", 1, 5, 3)
        st.write(f"Current: {2 + sensitivity * 0.5}σ threshold")
        
        if st.button("🔄 Recalibrate Model"):
            st.success("Model recalibrated with new sensitivity!")

with tab7:
    st.markdown('<h2 class="section-header">🎮 Interactive AI Demo Playground</h2>', unsafe_allow_html=True)
    
    # Interactive demo sections
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        st.markdown("### 🎯 AI Function Tester")
        
        function_type = st.selectbox(
            "Choose AI Function:",
            ["Sentiment Analysis", "Text Summarization", "Translation", "Classification"]
        )
        
        if function_type == "Sentiment Analysis":
            text_input = st.text_area("Enter text to analyze:", 
                                    placeholder="e.g., This product is amazing! I love it.")
            if st.button("Analyze Sentiment") and text_input:
                # Simulate sentiment analysis
                sentiment_score = np.random.uniform(-1, 1)
                if sentiment_score > 0.1:
                    sentiment = "Positive 😊"
                    color = "green"
                elif sentiment_score < -0.1:
                    sentiment = "Negative 😞" 
                    color = "red"
                else:
                    sentiment = "Neutral 😐"
                    color = "orange"
                
                st.markdown(f"**Result:** <span style='color: {color}'>{sentiment}</span>", 
                           unsafe_allow_html=True)
                st.write(f"**Score:** {sentiment_score:.3f}")
        
        elif function_type == "Text Summarization":
            text_input = st.text_area("Enter text to summarize:", 
                                    placeholder="Enter a long text that you want to summarize...")
            if st.button("Generate Summary") and text_input:
                # Simulate summarization
                summary = f"AI Summary: This text discusses key points about {text_input.split()[0] if text_input.split() else 'the topic'} and provides insights on related concepts."
                st.success(summary)
        
        elif function_type == "Translation":
            text_input = st.text_area("Enter text to translate:", 
                                    placeholder="Hello, how are you today?")
            target_lang = st.selectbox("Target Language:", ["Spanish", "French", "German", "Japanese"])
            if st.button("Translate") and text_input:
                translations = {
                    "Spanish": "Hola, ¿cómo estás hoy?",
                    "French": "Bonjour, comment allez-vous aujourd'hui?",
                    "German": "Hallo, wie geht es Ihnen heute?",
                    "Japanese": "こんにちは、今日はいかがですか？"
                }
                st.success(f"**Translation:** {translations.get(target_lang, 'Translation would appear here')}")
        
        else:  # Classification
            text_input = st.text_area("Enter text to classify:", 
                                    placeholder="I need help with my order...")
            if st.button("Classify") and text_input:
                categories = ["Customer Service", "Product Inquiry", "Technical Support", "Billing", "General"]
                category = np.random.choice(categories)
                confidence = np.random.uniform(0.75, 0.99)
                st.success(f"**Category:** {category}")
                st.write(f"**Confidence:** {confidence:.1%}")
    
    with demo_col2:
        st.markdown("### 🤖 Custom AI Agent Builder")
        
        agent_name = st.text_input("Agent Name:", placeholder="My Custom Agent")
        agent_role = st.selectbox("Agent Role:", 
                                ["Customer Support", "Sales Assistant", "Technical Expert", "Data Analyst"])
        
        agent_personality = st.multiselect("Personality Traits:",
                                        ["Friendly", "Professional", "Technical", "Empathetic", "Concise"])
        
        knowledge_base = st.multiselect("Knowledge Areas:",
                                      ["Product Catalog", "Customer Data", "Sales History", "Technical Docs"])
        
        if st.button("🚀 Create Agent") and agent_name:
            st.success(f"✅ Created agent '{agent_name}' with {agent_role} role!")
            
            st.markdown("**Agent Configuration:**")
            st.json({
                "name": agent_name,
                "role": agent_role,
                "personality": agent_personality,
                "knowledge": knowledge_base,
                "status": "Active",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    
    # AI Model Performance Comparison
    st.markdown("### 📊 AI Model Performance Comparison")
    
    model_performance = pd.DataFrame({
        'Model': ['Llama3-8B', 'Llama3-70B', 'Mixtral-8x7B', 'Mistral-7B'],
        'Accuracy': [0.89, 0.94, 0.91, 0.87],
        'Speed (tokens/sec)': [150, 80, 120, 180],
        'Use Case': ['General', 'Complex Analysis', 'Reasoning', 'Fast Response']
    })
    
    col_perf1, col_perf2 = st.columns(2)
    
    with col_perf1:
        fig_acc = px.bar(model_performance, x='Model', y='Accuracy',
                        title="Model Accuracy Comparison")
        st.plotly_chart(fig_acc, use_container_width=True)
    
    with col_perf2:
        fig_speed = px.bar(model_performance, x='Model', y='Speed (tokens/sec)',
                          title="Model Speed Comparison")
        st.plotly_chart(fig_speed, use_container_width=True)
    
    # Real-time AI Metrics
    st.markdown("### ⚡ Real-time AI Platform Metrics")
    
    if st.button("🔄 Refresh Metrics"):
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("🧠 AI Requests/min", f"{np.random.randint(50, 200)}", 
                     delta=f"{np.random.randint(-20, 30)}")
        
        with metric_col2:
            st.metric("⚡ Avg Response Time", f"{np.random.uniform(0.5, 2.0):.1f}s", 
                     delta=f"{np.random.uniform(-0.3, 0.2):.1f}s")
        
        with metric_col3:
            st.metric("🎯 Success Rate", f"{np.random.uniform(92, 98):.1f}%", 
                     delta=f"{np.random.uniform(-1, 2):.1f}%")
        
        with metric_col4:
            st.metric("🔥 Active Models", f"{np.random.randint(3, 8)}", 
                     delta=f"{np.random.randint(-1, 2)}")

# Sidebar with Cortex AI info
with st.sidebar:
    st.markdown("---")
    st.subheader("🧠 Cortex AI Platform")
    st.write("""
    **Snowflake Cortex AI** provides industry-leading LLM functions 
    and intelligent capabilities directly in your data cloud.
    """)
    
    st.markdown("---")
    st.subheader("🛠️ AI Functions Used")
    st.markdown("""
    - **SENTIMENT()** - Emotion analysis
    - **SUMMARIZE()** - Text summarization  
    - **COMPLETE()** - LLM completions
    - **TRANSLATE()** - Language translation
    - **CLASSIFY()** - Content classification
    """)
    
    st.markdown("---")
    st.subheader("🎯 Featured Models")
    st.markdown("""
    - **Llama3-8B** - Fast general purpose
    - **Llama3-70B** - Advanced reasoning
    - **Mixtral-8x7B** - Specialized tasks
    - **Mistral-7B** - Efficient processing
    """)
    
    st.markdown("---")
    st.subheader("🚀 Platform Status")
    
    if st.button("🔍 System Health Check"):
        st.success("✅ All AI services operational")
        st.info("📊 Processing 156 requests/min")
        st.info("⚡ Average latency: 1.2s")
    
    # Session state for demo
    if 'ai_demo_count' not in st.session_state:
        st.session_state.ai_demo_count = 0
    
    if st.button("🎲 Random AI Insight"):
        st.session_state.ai_demo_count += 1
        insights = [
            "🎯 Customer satisfaction up 15%",
            "📈 Premium segment drives 40% of revenue", 
            "🤖 AI resolved 89% of support tickets",
            "⚡ Unusual spike detected in Electronics",
            "🔄 Inventory optimization saved $50K"
        ]
        st.success(f"Insight #{st.session_state.ai_demo_count}: {np.random.choice(insights)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🧠 Powered by Snowflake Cortex AI | 🚀 Intelligent Analytics Platform</p>
    <p>⭐ Experience the future of data-driven AI applications!</p>
</div>
""", unsafe_allow_html=True) 