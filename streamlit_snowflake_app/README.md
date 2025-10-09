# 🧠 Snowflake Cortex AI Demo - Streamlit Application

A comprehensive Streamlit application showcasing advanced Snowflake Cortex AI capabilities including intelligent agents, sentiment analysis, semantic queries, and predictive analytics.

## 🚀 Features

### 🎯 AI Overview
- Real-time AI platform status monitoring
- Active agent tracking
- Semantic query metrics
- Anomaly detection dashboard

### 💭 Sentiment Analysis
- Customer feedback sentiment analysis using `SNOWFLAKE.CORTEX.SENTIMENT()`
- Product sentiment tracking and insights
- AI-powered review summarization
- Sentiment distribution analytics

### 🤖 AI Agents
- Conversational AI agents (Sales, Support, Product Expert)
- Intent detection and confidence scoring
- Agent performance analytics
- Real-time conversation simulation

### 🔍 Semantic Intelligence
- Natural language queries to business data
- AI-powered SQL generation using `SNOWFLAKE.CORTEX.COMPLETE()`
- Context-aware data exploration
- Business intelligence through conversation

### 📊 AI Insights & Predictions
- Product performance intelligence
- Customer segmentation with AI profiles
- Sales forecasting with confidence intervals
- Inventory optimization recommendations

### ⚡ Anomaly Detection
- Real-time sales anomaly monitoring
- AI-powered anomaly explanations
- Statistical deviation analysis
- Configurable sensitivity settings

### 🎮 Interactive Demo
- AI function testing playground
- Custom AI agent builder
- Model performance comparison
- Real-time platform metrics

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Snowflake account with Cortex AI enabled
- Access to create databases and run AI functions

### Option 1: Running in Streamlit in Snowflake (Recommended)

1. **Create the database structure:**
   ```sql
   -- Run in Snowflake worksheet
   -- First, execute sample_database.sql
   -- Then, execute cortex_ai_setup.sql
   ```

2. **Upload the Streamlit app:**
   - Upload `app.py` to your Streamlit in Snowflake environment
   - The app will automatically connect to your Snowflake session

3. **Run the application:**
   - Navigate to your Streamlit app in the Snowflake UI
   - The app will use the built-in connection: `st.connection("snowflake").session()`

### Option 2: External Streamlit Application

1. **Clone this repository:**
   ```bash
   git clone <repository-url>
   cd streamlit_snowflake_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   ```

4. **Set up the database:**
   ```bash
   # Run these SQL scripts in your Snowflake environment:
   # 1. sample_database.sql
   # 2. cortex_ai_setup.sql
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📁 File Structure

```
streamlit_snowflake_app/
├── app.py                          # Main Streamlit application with Cortex AI features
├── cortex_ai_setup.sql            # Cortex AI database setup and functions
├── sample_database.sql            # Enhanced sample database with AI support
├── snowflake_connection_example.py # Connection utilities
├── cortex_ai_integration.py       # Real Cortex AI function implementations
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🧬 Cortex AI Functions Used

### Core AI Functions
- **`SNOWFLAKE.CORTEX.SENTIMENT()`** - Analyze text sentiment
- **`SNOWFLAKE.CORTEX.SUMMARIZE()`** - Generate text summaries
- **`SNOWFLAKE.CORTEX.COMPLETE()`** - LLM completions and chat
- **`SNOWFLAKE.CORTEX.TRANSLATE()`** - Language translation
- **`SNOWFLAKE.CORTEX.CLASSIFY()`** - Content classification

### Available LLM Models
- **Llama3-8B** - Fast general purpose tasks
- **Llama3-70B** - Complex reasoning and analysis
- **Mixtral-8x7B** - Specialized task processing
- **Mistral-7B** - Efficient high-speed processing

## 🔄 Integration Options

### Using Simulated Data (Default)
The app runs with simulated data by default for demonstration purposes. All AI features work with realistic sample data.

### Connecting to Real Cortex AI
To use real Cortex AI functions:

1. **Replace simulated functions:**
   ```python
   # In app.py, replace:
   from app import get_cortex_sentiment_data
   
   # With:
   from cortex_ai_integration import get_real_sentiment_analysis
   ```

2. **Update function calls:**
   ```python
   # Instead of simulated data:
   sentiment_data = get_cortex_sentiment_data()
   
   # Use real Cortex AI:
   sentiment_data = get_real_sentiment_analysis()
   ```

## 📊 Sample Data

The application includes comprehensive sample data:
- **2,500+** sales transactions
- **1,500+** customer records
- **20+** detailed customer reviews
- **10** product catalog items
- **8,000+** web analytics sessions
- **AI agent conversations** and insights

## 🎯 Use Cases

### Business Intelligence
- Natural language queries to business data
- Automated insight generation
- Customer sentiment monitoring
- Sales performance analysis

### Customer Experience
- AI-powered customer support agents
- Sentiment analysis of feedback
- Personalized customer insights
- Proactive issue detection

### Operations
- Sales anomaly detection
- Inventory optimization
- Predictive analytics
- Performance monitoring

## 🔧 Customization

### Adding New AI Agents
```python
# In cortex_ai_integration.py
def create_custom_agent(agent_type: str, personality: List[str]):
    context_prompt = f"You are a {agent_type} with {personality} traits..."
    # Implementation here
```

### Custom Sentiment Analysis
```python
# Add custom sentiment categories
def analyze_custom_sentiment(text: str, categories: List[str]):
    # Use CORTEX.COMPLETE for custom classification
```

### Extending Anomaly Detection
```sql
-- Add new anomaly detection patterns
CREATE VIEW CUSTOM_ANOMALY_DETECTION AS
SELECT *,
    SNOWFLAKE.CORTEX.COMPLETE('llama3-8b', 
        'Analyze this pattern...'
    ) as ai_explanation
FROM your_data_table;
```

## 🚨 Important Notes

### Security
- Use environment variables for credentials
- Implement proper access controls
- Validate AI-generated SQL queries
- Monitor AI function usage and costs

### Performance
- Use `@st.cache_data` for expensive operations
- Implement appropriate TTL for cached data
- Monitor Cortex AI credit consumption
- Optimize query patterns for large datasets

### Cost Management
- Cortex AI functions consume credits
- Monitor usage through Snowflake's resource monitors
- Implement caching strategies to reduce API calls
- Use appropriate models for each use case

## 📚 Additional Resources

- [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Streamlit in Snowflake Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Snowpark Python API](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both simulated and real Cortex AI functions
5. Submit a pull request

## 📝 License

This project is provided as-is for demonstration purposes. Please review Snowflake's terms of service for Cortex AI usage.

---

🧠 **Experience the future of intelligent analytics with Snowflake Cortex AI!** 