# Snowflake Cortex AI Functions Reference

## 🎯 Overview

This reference guide covers all Snowflake Cortex AI functions used across both Track A (NLP2SQL) and Track B (Data Quality) learning paths.

## 🧠 Core Cortex AI Functions

### 1. SNOWFLAKE.CORTEX.COMPLETE()

**Purpose**: Generate text completions and analysis using large language models

**Syntax**:
```sql
SNOWFLAKE.CORTEX.COMPLETE(
    model_name,
    prompt,
    options
)
```

**Parameters**:
- `model_name`: STRING - The LLM model to use
- `prompt`: STRING - The input prompt
- `options`: OBJECT - Optional configuration (temperature, max_tokens, etc.)

**Available Models**:
- `llama3-8b`: Fast responses, good for quick analysis
- `mixtral-8x7b`: Balanced performance (recommended default)
- `llama3-70b`: Highest quality, detailed responses
- `snowflake-arctic`: Snowflake's enterprise model

**Track A (NLP2SQL) Usage Examples**:
```sql
-- Generate SQL from natural language
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Convert this business question to SQL: "What were our top 3 parks by revenue last month?"
     Tables: PARKS (park_id, park_name), SALES_TRANSACTIONS (park_id, total_revenue, transaction_date)'
) as generated_sql;

-- Query intent analysis
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-8b',
    'Analyze this query intent and return JSON: "Show me customer satisfaction trends"
     Return: {"query_type": "trend_analysis", "entities": ["customer_satisfaction"], "time_dimension": true}'
) as intent_analysis;
```

**Track B (Data Quality) Usage Examples**:
```sql
-- Data quality issue classification
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-70b',
    'Classify this data quality issue: "Customer email field contains value: xyz123 instead of email format"
     Categories: COMPLETENESS, ACCURACY, CONSISTENCY, VALIDITY, TIMELINESS, UNIQUENESS
     Return only the category name.'
) as quality_classification;

-- Anomaly explanation
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Explain this anomaly in business terms: Revenue dropped 60% on 2024-03-15 compared to previous days.
     Context: Theme park daily revenue data. Provide possible business explanations.'
) as anomaly_explanation;
```

### 2. SNOWFLAKE.CORTEX.EXTRACT_ANSWER()

**Purpose**: Extract specific information from text or data

**Syntax**:
```sql
SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
    text_content,
    question
)
```

**Track A Usage**:
```sql
-- Extract query components
SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
    'Show me the top performing parks in terms of guest satisfaction for the last quarter',
    'What is the main metric being requested?'
) as main_metric;
```

**Track B Usage**:
```sql
-- Extract data quality insights
SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
    error_log_text,
    'What type of validation error occurred?'
) as error_type;
```

### 3. SNOWFLAKE.CORTEX.CLASSIFY()

**Purpose**: Classify text into predefined categories

**Syntax**:
```sql
SNOWFLAKE.CORTEX.CLASSIFY(
    text_to_classify,
    categories
)
```

**Track A Usage**:
```sql
-- Classify query types
SELECT SNOWFLAKE.CORTEX.CLASSIFY(
    'What were our busiest days last month?',
    ['operational_query', 'financial_query', 'customer_query', 'performance_query']
) as query_classification;
```

**Track B Usage**:
```sql
-- Classify data quality issues
SELECT SNOWFLAKE.CORTEX.CLASSIFY(
    data_issue_description,
    ['completeness', 'accuracy', 'consistency', 'validity', 'timeliness', 'uniqueness']
) as quality_dimension;
```

### 4. SNOWFLAKE.CORTEX.SUMMARIZE()

**Purpose**: Create concise summaries of text or data insights

**Syntax**:
```sql
SNOWFLAKE.CORTEX.SUMMARIZE(
    content_to_summarize
)
```

**Track A Usage**:
```sql
-- Executive summary generation
SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
    'Monthly park performance data shows: Universal Studios Florida: $45M revenue, 92% satisfaction; 
     Islands of Adventure: $38M revenue, 89% satisfaction; Universal Studios Hollywood: $52M revenue, 94% satisfaction'
) as executive_summary;
```

**Track B Usage**:
```sql
-- Data quality report summary
SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
    'Data quality assessment results: 98.5% completeness, 3 duplicate records found, 
     email validation failed for 0.2% of customers, revenue calculations accurate'
) as quality_summary;
```

## 🔧 Model Selection Guidelines

### For Track A (NLP2SQL):
- **Simple translations**: `llama3-8b` (fast, efficient)
- **Complex business logic**: `mixtral-8x7b` (balanced)
- **Conversational context**: `llama3-70b` (detailed understanding)
- **Production systems**: `snowflake-arctic` (enterprise grade)

### For Track B (Data Quality):
- **Quick classifications**: `llama3-8b`
- **Anomaly analysis**: `mixtral-8x7b`
- **Detailed explanations**: `llama3-70b`
- **Business reporting**: `snowflake-arctic`

## ⚡ Performance Optimization

### Token Management
```sql
-- Use temperature and max_tokens for consistent outputs
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    prompt,
    OBJECT_CONSTRUCT('temperature', 0.1, 'max_tokens', 100)
) as controlled_output;
```

### Cost Optimization
```sql
-- Cache frequent prompts in tables
CREATE OR REPLACE TABLE PROMPT_CACHE AS
SELECT 
    prompt_hash,
    prompt_text,
    ai_response,
    model_used,
    created_timestamp
FROM ai_interactions
WHERE created_timestamp >= CURRENT_DATE() - 7;
```

## 🛡️ Error Handling Patterns

### Safe AI Function Calls
```sql
-- Track A: Safe SQL generation
CREATE OR REPLACE FUNCTION safe_sql_generation(user_question STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    ai_response STRING;
    result VARIANT;
BEGIN
    TRY
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mixtral-8x7b',
            'Convert to SQL: ' || user_question
        ) INTO ai_response;
        
        RETURN OBJECT_CONSTRUCT('status', 'success', 'sql', ai_response);
    EXCEPTION
        WHEN OTHER THEN
            RETURN OBJECT_CONSTRUCT('status', 'error', 'message', 'AI service unavailable');
    END;
END;
$$;
```

### Track B: Safe Quality Analysis
```sql
CREATE OR REPLACE FUNCTION safe_quality_analysis(data_sample VARIANT)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    analysis_result STRING;
BEGIN
    TRY
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-70b',
            'Analyze data quality: ' || data_sample::STRING
        ) INTO analysis_result;
        
        RETURN OBJECT_CONSTRUCT('analysis', analysis_result, 'status', 'completed');
    EXCEPTION
        WHEN OTHER THEN
            RETURN OBJECT_CONSTRUCT('status', 'failed', 'fallback', 'Manual review required');
    END;
END;
$$;
```

## 📊 Usage Tracking

### Monitor AI Function Usage
```sql
-- Track AI model usage across both tracks
CREATE OR REPLACE VIEW AI_USAGE_ANALYTICS AS
SELECT 
    DATE(timestamp) as usage_date,
    track_type,
    ai_model_used,
    COUNT(*) as total_calls,
    AVG(execution_time_ms) as avg_response_time
FROM SHARED_FOUNDATION.QUERY_EXECUTION_LOG
WHERE ai_model_used IS NOT NULL
GROUP BY DATE(timestamp), track_type, ai_model_used
ORDER BY usage_date DESC, total_calls DESC;
```

## 🔮 Advanced Features

### Multi-Model Strategies
```sql
-- Route queries to optimal models based on complexity
CREATE OR REPLACE FUNCTION route_to_optimal_model(query_complexity STRING, use_case STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
    CASE 
        WHEN query_complexity = 'SIMPLE' AND use_case = 'NLP2SQL' THEN 'llama3-8b'
        WHEN query_complexity = 'COMPLEX' AND use_case = 'NLP2SQL' THEN 'mixtral-8x7b'
        WHEN query_complexity = 'SIMPLE' AND use_case = 'DATA_QUALITY' THEN 'llama3-8b'
        WHEN query_complexity = 'COMPLEX' AND use_case = 'DATA_QUALITY' THEN 'llama3-70b'
        ELSE 'mixtral-8x7b'  -- Safe default
    END
$$;
```

### Context-Aware Prompting
```sql
-- Build context-aware prompts for both tracks
CREATE OR REPLACE FUNCTION build_contextual_prompt(
    user_input STRING,
    track_type STRING,
    business_context VARIANT
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    CASE track_type
        WHEN 'NLP2SQL' THEN
            'You are a SQL expert for UDX theme parks. Business context: ' ||
            business_context:business_glossary::STRING ||
            ' User question: ' || user_input ||
            ' Generate accurate SQL using tables: PARKS, CUSTOMERS, SALES_TRANSACTIONS, PARK_PERFORMANCE'
        WHEN 'DATA_QUALITY' THEN
            'You are a data quality expert for UDX theme parks. Business context: ' ||
            business_context:quality_standards::STRING ||
            ' Data issue: ' || user_input ||
            ' Analyze quality problems and suggest business-focused solutions'
        ELSE
            'UDX theme park analytics assistant. Input: ' || user_input
    END
$$;
```

---

## 📚 Next Steps

### For Track A Students:
- Review [NLP2SQL Prompt Engineering Guide](prompt_engineering_guide.md)
- Practice with [SQL Generation Examples](../TRACK-A-NLP2SQL/01-basic-translation/)

### For Track B Students:
- Review [Data Quality AI Patterns](prompt_engineering_guide.md)
- Practice with [Quality Analysis Examples](../TRACK-B-DATA-QUALITY/01-quality-fundamentals/)

### For Both Tracks:
- Explore [Model Selection Guide](model_selection_guide.md)
- Reference [Advanced AI Patterns](../ADVANCED-SHARED/) 