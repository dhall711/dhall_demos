# AI-Powered Customer Call Analysis with Snowflake Cortex

A comprehensive demonstration of Snowflake's AI/ML capabilities for intelligent customer service call analysis, featuring automated transcription, contextual filtering, sentiment analysis, and real-time alerting.

## 🎯 Overview

This project showcases an end-to-end AI-powered workflow for analyzing customer service calls using Snowflake Cortex functions. The system automatically processes audio recordings, extracts insights, and flags critical situations for management attention.

### Key Business Use Case
- **Scenario**: Customer service center with inbound calls requiring automated analysis
- **Goal**: Identify specific topics (e.g., "baseball programs") mentioned in calls
- **Challenge**: Filter relevant mentions while excluding unrelated contexts (e.g., "soccer")
- **Solution**: AI-driven proximity analysis and contextual understanding

## 🚀 Features

### Core Capabilities
- **🎵 Audio Transcription**: Convert call recordings to searchable text using `SNOWFLAKE.CORTEX.TRANSCRIBE()`
- **📊 Content Classification**: Categorize calls by topic and urgency with `SNOWFLAKE.CORTEX.CLASSIFY()`
- **🎯 Contextual Filtering**: Identify relevant keyword mentions with exclusion logic
- **📏 Proximity Analysis**: Detect keyword relationships within specified word distances
- **💭 Sentiment Analysis**: Assess customer emotion using `SNOWFLAKE.CORTEX.SENTIMENT()`
- **🔔 Alert Generation**: Create actionable escalations for management review
- **⚡ Real-time Processing**: Automated workflows for processing calls as they arrive

### AI Functions Demonstrated
| Function | Purpose | Example Use Case |
|----------|---------|------------------|
| `TRANSCRIBE()` | Audio → Text conversion | Convert call recordings to searchable transcripts |
| `CLASSIFY()` | Topic categorization | Label calls as "Sales", "Support", "Complaint", etc. |
| `COMPLETE()` | Custom AI analysis | Proximity analysis, custom filtering logic |
| `SUMMARIZE()` | Content summarization | Generate executive summaries for flagged calls |
| `SENTIMENT()` | Emotion detection | Identify frustrated or satisfied customers |
| `EXTRACT_ANSWER()` | Information extraction | Pull specific data points from conversations |

## 📋 Prerequisites

### Snowflake Requirements
- Snowflake account with Cortex AI functions enabled
- Appropriate role permissions for:
  - Creating stages, tables, views
  - Executing Cortex AI functions
  - Managing tasks and streams (for automation)

### Access Requirements
Ensure your role has access to these Cortex functions:
```sql
-- Required Cortex functions
SNOWFLAKE.CORTEX.TRANSCRIBE()
SNOWFLAKE.CORTEX.CLASSIFY()
SNOWFLAKE.CORTEX.COMPLETE()
SNOWFLAKE.CORTEX.SUMMARIZE()
SNOWFLAKE.CORTEX.SENTIMENT()
SNOWFLAKE.CORTEX.EXTRACT_ANSWER()
```

## 🛠 Setup Instructions

### 1. Environment Setup
```sql
-- Create stage for audio files
CREATE OR REPLACE STAGE call_center_audio;

-- Upload sample audio files
PUT file:///path/to/sample_call.wav @call_center_audio;
PUT file:///path/to/baseball_inquiry.wav @call_center_audio;
PUT file:///path/to/soccer_discussion.wav @call_center_audio;
```

### 2. Database Schema
The project uses three main tables:

#### Call Transcriptions
```sql
CREATE OR REPLACE TABLE call_transcriptions (
    call_id STRING DEFAULT UUIDSTRING(),
    audio_file_name STRING,
    transcription TEXT,
    call_duration_seconds INTEGER,
    agent_id STRING,
    customer_phone STRING,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
```

#### AI Analysis Results
```sql
CREATE OR REPLACE TABLE call_analysis (
    call_id STRING,
    call_category STRING,
    sentiment_score FLOAT,
    sentiment_label STRING,
    urgency_level STRING,
    key_topics ARRAY,
    customer_satisfaction_score FLOAT,
    requires_escalation BOOLEAN,
    analysis_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
```

#### Alert Management
```sql
CREATE OR REPLACE TABLE call_alerts (
    alert_id STRING DEFAULT UUIDSTRING(),
    call_id STRING,
    alert_type STRING,
    alert_reason TEXT,
    priority_level STRING,
    assigned_to STRING,
    status STRING DEFAULT 'OPEN',
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    resolved_at TIMESTAMP_LTZ
);
```

## 📖 Usage Guide

### Basic Workflow

1. **Upload Audio Files**: Place call recordings in the Snowflake stage
2. **Run Transcription**: Execute the notebook cells to convert audio to text
3. **Analyze Content**: Apply AI classification and sentiment analysis
4. **Filter Results**: Use proximity analysis to identify relevant calls
5. **Generate Alerts**: Create escalations for management review

### Key Analysis Examples

#### Baseball Program Detection
```sql
-- Find calls mentioning "baseball" near "program" or "schedule"
SELECT call_id, summary
FROM baseball_alerts
WHERE is_baseball_near_program = 'Yes';
```

#### Sentiment-Based Escalation
```sql
-- Identify highly negative calls requiring immediate attention
SELECT * FROM call_analysis
WHERE sentiment_score < -0.7 AND requires_escalation = TRUE;
```

## 🔍 Key Features Explained

### Proximity Analysis
The system uses AI to detect when keywords appear within a specified distance:
- **Requirement**: "Baseball" mentioned within 50 words of "program" or "schedule"
- **Implementation**: Uses `SNOWFLAKE.CORTEX.COMPLETE()` with custom prompts
- **Output**: Binary Yes/No classification for filtering

### Exclusion Logic
Smart filtering that includes relevant mentions while excluding noise:
- **Include**: Calls mentioning "baseball"
- **Exclude**: Calls that also mention "soccer" (irrelevant context)
- **Result**: Focused dataset for analysis

### Real-time Processing
Automated workflow components:
- **Streams**: Detect new audio files in the stage
- **Tasks**: Automatically process new recordings
- **Alerts**: Send notifications for flagged calls

## 📊 Expected Outputs

### Dashboard Metrics
- Total calls processed
- Classification distribution
- Sentiment trends over time
- Alert volume and resolution rates

### Actionable Insights
- High-priority escalations requiring immediate attention
- Trending topics in customer conversations
- Agent performance indicators
- Customer satisfaction patterns

## 🔧 Customization Options

### Keyword Configuration
Easily modify the analysis by updating:
- Target keywords (currently "baseball")
- Exclusion terms (currently "soccer")
- Proximity distance (currently 50 words)

### Classification Categories
Adjust call categories based on your business needs:
```sql
['Sales Inquiry', 'Technical Support', 'Billing Question', 
 'Complaint', 'General Conversation', 'Baseball Program Inquiry']
```

### Alert Thresholds
Configure when escalations are created:
- Sentiment score thresholds
- Keyword combinations
- Customer satisfaction levels

## 📈 Performance Considerations

- **Batch Processing**: Process multiple files simultaneously for efficiency
- **Indexing**: Create indexes on frequently queried columns
- **Partitioning**: Consider partitioning large tables by date
- **Caching**: Leverage Snowflake's result caching for repeated queries

## 🤝 Contributing

This notebook serves as a template for AI-powered call analysis. Customize it for your specific:
- Industry requirements
- Keyword lists
- Business rules
- Alert mechanisms

## 📄 License

This project is designed for demonstration and educational purposes as part of Snowflake AI/ML showcases.

## 🆘 Support

For questions or issues:
1. Review the Snowflake Cortex documentation
2. Check function permissions and access
3. Validate audio file formats and stage access
4. Test with sample data before processing production calls

---

**Next Steps**: Open `transcribe.ipynb` in Snowflake and execute the cells to see the AI analysis in action!
