# Snowflake Cortex AI Integration Guide
## Enhancing Your Sensitive Data Discovery Application

This guide demonstrates how to leverage Snowflake Cortex AI capabilities to significantly enhance your sensitive data discovery and masking application.

## 🎯 Key Cortex AI Functions for Your Use Case

### 1. **AI_CLASSIFY** - Intelligent Data Classification
Replace pattern-based detection with AI-powered classification:

```sql
-- Multi-label classification for comprehensive analysis
SELECT 
    column_name,
    SNOWFLAKE.CORTEX.AI_CLASSIFY(
        sample_data, 
        ['PII', 'Financial', 'Medical', 'Personal', 'Public', 'Confidential'],
        {'multi_label': true}
    ) as classification_result
FROM your_sample_data;
```

**Benefits:**
- Automatically classifies data into predefined categories
- Supports multi-label classification for complex data
- Provides confidence scores for each classification
- Reduces false positives compared to regex patterns

### 2. **AI_COMPLETE** - Contextual Analysis & Reasoning
Use LLMs for intelligent column analysis:

```sql
-- Contextual analysis with business logic
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-70b',
    CONCAT(
        'Analyze this database column for sensitive data: ',
        'Column: ', column_name, 
        ', Samples: ', sample_values,
        ', Context: ', table_description,
        '. Determine sensitivity level and recommend masking strategy.'
    ),
    {'temperature': 0.1, 'max_tokens': 500}
) as analysis_result;
```

**Benefits:**
- Context-aware analysis considering business logic
- Generates detailed reasoning for classifications
- Recommends specific masking strategies
- Adapts to your organization's data patterns

### 3. **AI_FILTER** - Boolean Sensitivity Detection
Quick true/false filtering for sensitive data:

```sql
-- Filter sensitive columns quickly
SELECT 
    table_name,
    column_name,
    SNOWFLAKE.CORTEX.AI_FILTER(
        sample_data,
        'Contains personally identifiable information or sensitive data'
    ) as is_sensitive
FROM column_samples
WHERE SNOWFLAKE.CORTEX.AI_FILTER(sample_data, 'Contains PII') = TRUE;
```

### 4. **AI_AGG** - Cross-Table Pattern Analysis
Analyze patterns across multiple tables without context limits:

```sql
-- Discover patterns across your entire schema
SELECT SNOWFLAKE.CORTEX.AI_AGG(
    CONCAT(table_name, '.', column_name, ' (', data_type, ')'),
    'Identify sensitive data patterns and relationships across these database columns. Group by risk level and suggest data governance policies.'
) as pattern_analysis
FROM information_schema.columns
WHERE table_schema = 'YOUR_SCHEMA';
```

### 5. **AI_EMBED + AI_SIMILARITY** - Semantic Column Matching
Find similar columns using semantic understanding:

```sql
-- Find semantically similar column names
WITH column_embeddings AS (
    SELECT 
        column_name,
        SNOWFLAKE.CORTEX.AI_EMBED('snowflake-arctic-embed-m', column_name) as embedding
    FROM information_schema.columns
)
SELECT 
    a.column_name as source_column,
    b.column_name as similar_column,
    SNOWFLAKE.CORTEX.AI_SIMILARITY(a.embedding, b.embedding) as similarity_score
FROM column_embeddings a
CROSS JOIN column_embeddings b
WHERE a.column_name != b.column_name
AND SNOWFLAKE.CORTEX.AI_SIMILARITY(a.embedding, b.embedding) > 0.8;
```

## 🚀 Implementation Strategies

### Strategy 1: Enhanced Detection Pipeline

```python
def enhanced_sensitive_data_detection(conn, table_name, schema_name):
    """
    Multi-layered AI-powered detection approach
    """
    results = []
    
    # Step 1: Get all columns
    columns_query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns 
    WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
    """
    
    columns = pd.read_sql(columns_query, conn)
    
    for _, col in columns.iterrows():
        column_name = col['column_name']
        
        # Step 2: Sample data for analysis
        sample_query = f"""
        SELECT DISTINCT {column_name}
        FROM {schema_name}.{table_name}
        WHERE {column_name} IS NOT NULL
        LIMIT 10
        """
        samples = pd.read_sql(sample_query, conn)[column_name].tolist()
        
        if samples:
            # Step 3: Multi-model AI analysis
            ai_analysis = run_multi_model_analysis(conn, column_name, samples, table_name)
            results.append(ai_analysis)
    
    return results

def run_multi_model_analysis(conn, column_name, samples, table_name):
    """
    Run multiple AI models for comprehensive analysis
    """
    sample_text = " | ".join([str(s)[:50] for s in samples if s])
    
    analysis_query = f"""
    SELECT 
        -- Classification
        SNOWFLAKE.CORTEX.AI_CLASSIFY(
            '{sample_text}',
            ['PII', 'Financial', 'Medical', 'Personal', 'Public']
        ) as classification,
        
        -- Boolean sensitivity filter
        SNOWFLAKE.CORTEX.AI_FILTER(
            '{sample_text}',
            'Contains sensitive or personally identifiable information'
        ) as is_sensitive,
        
        -- Detailed LLM analysis
        SNOWFLAKE.CORTEX.COMPLETE(
            'llama3.1-8b',
            'Analyze this data for privacy risks: {sample_text}. Return JSON with sensitivity_level, data_type, confidence, and masking_recommendation.',
            {{'temperature': 0.1}}
        ) as detailed_analysis,
        
        -- Sentiment analysis (useful for detecting personal content)
        SNOWFLAKE.CORTEX.SENTIMENT('{sample_text}') as sentiment_score
    """
    
    result = pd.read_sql(analysis_query, conn).iloc[0]
    
    return {
        'table': table_name,
        'column': column_name,
        'classification': json.loads(result['classification']),
        'is_sensitive': result['is_sensitive'],
        'detailed_analysis': result['detailed_analysis'],
        'sentiment': result['sentiment_score'],
        'samples': samples[:3]  # Keep sample for reference
    }
```

### Strategy 2: Intelligent Masking Strategy Generation

```python
def generate_ai_masking_strategy(conn, column_analysis, compliance_reqs):
    """
    Generate intelligent masking strategies using AI
    """
    context = f"""
    Column Analysis: {json.dumps(column_analysis, indent=2)}
    Compliance Requirements: {', '.join(compliance_reqs)}
    
    Design an optimal data masking strategy considering:
    1. Data sensitivity level and type
    2. Business usage requirements  
    3. Compliance regulations (GDPR, CCPA, HIPAA)
    4. Performance implications
    5. Data utility preservation
    
    Provide specific DDL and implementation guidance.
    """
    
    strategy_query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'claude-3-5-sonnet',
        '{context}',
        {{'temperature': 0.2, 'max_tokens': 1000}}
    ) as masking_strategy
    """
    
    result = pd.read_sql(strategy_query, conn)
    return result.iloc[0]['masking_strategy']
```

### Strategy 3: Automated Compliance Reporting

```python
def generate_ai_compliance_report(conn, findings, regulations):
    """
    Generate comprehensive compliance reports using AI
    """
    findings_summary = json.dumps(findings[:50], indent=2)
    
    report_query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'claude-3-5-sonnet',
        'Generate a comprehensive data privacy compliance report based on these findings: {findings_summary}. Target regulations: {", ".join(regulations)}. Include executive summary, risk assessment, recommendations, and implementation timeline.',
        {{'temperature': 0.1, 'max_tokens': 2000}}
    ) as compliance_report
    """
    
    result = pd.read_sql(report_query, conn)
    return result.iloc[0]['compliance_report']
```

## 🏗️ Production Implementation Patterns

### 1. Real-time Sensitive Data Monitoring

```sql
-- Create stream for monitoring new data
CREATE OR REPLACE STREAM sensitive_data_monitor ON TABLE your_data_table;

-- Automated task for AI-powered monitoring
CREATE OR REPLACE TASK monitor_sensitive_data
WAREHOUSE = 'AI_WAREHOUSE'
SCHEDULE = 'USING CRON 0 */10 * * * UTC'
WHEN SYSTEM$STREAM_HAS_DATA('sensitive_data_monitor')
AS
INSERT INTO sensitive_data_alerts
SELECT 
    table_name,
    column_name,
    SNOWFLAKE.CORTEX.AI_CLASSIFY(column_value, ['PII', 'Financial']) as classification,
    SNOWFLAKE.CORTEX.AI_FILTER(column_value, 'Contains sensitive information') as is_sensitive,
    CURRENT_TIMESTAMP() as detected_at
FROM sensitive_data_monitor
WHERE SNOWFLAKE.CORTEX.AI_FILTER(column_value, 'Contains PII or sensitive data');
```

### 2. Automated Policy Generation

```sql
-- AI-powered masking policy generation
CREATE OR REPLACE PROCEDURE generate_ai_policies()
RETURNS STRING
LANGUAGE PYTHON
AS $$
def main(session):
    # Analyze columns and generate policies
    analysis_query = """
    SELECT 
        table_name,
        column_name,
        SNOWFLAKE.CORTEX.AI_COMPLETE(
            'mistral-large2',
            CONCAT('Generate masking policy for column: ', column_name, 
                   ' with data type: ', data_type, 
                   '. Provide policy name and masking logic.'),
            {'temperature': 0.1}
        ) as policy_recommendation
    FROM information_schema.columns
    WHERE table_schema = 'PRODUCTION'
    """
    
    results = session.sql(analysis_query).collect()
    
    policies = []
    for row in results:
        policy_rec = row['POLICY_RECOMMENDATION']
        # Parse and generate DDL
        policies.append(f"-- Policy for {row['TABLE_NAME']}.{row['COLUMN_NAME']}")
        policies.append(policy_rec)
        
    return '\n'.join(policies)
$$;
```

### 3. Cross-Schema Pattern Discovery

```sql
-- Discover sensitive data patterns across schemas
CREATE OR REPLACE VIEW ai_sensitivity_patterns AS
SELECT 
    schema_name,
    table_name,
    column_name,
    data_type,
    SNOWFLAKE.CORTEX.AI_CLASSIFY(
        sample_values, 
        ['SSN', 'EMAIL', 'PHONE', 'CREDIT_CARD', 'ADDRESS', 'NAME']
    ) as sensitivity_classification
FROM (
    SELECT 
        table_schema as schema_name,
        table_name,
        column_name,
        data_type,
        LISTAGG(DISTINCT sample_value, ' | ') as sample_values
    FROM your_sample_data_view
    GROUP BY table_schema, table_name, column_name, data_type
);
```

## 📊 Enhanced UI Integration

### Streamlit Integration Example

```python
def cortex_ai_analysis_section():
    """
    Enhanced AI analysis section for Streamlit app
    """
    st.subheader("🤖 AI-Powered Sensitivity Analysis")
    
    with st.expander("🎯 Intelligent Classification", expanded=True):
        if st.button("Run AI Analysis"):
            with st.spinner("Analyzing with multiple AI models..."):
                
                # Multi-model analysis
                results = run_enhanced_ai_analysis(selected_tables)
                
                # Display results with confidence metrics
                if results:
                    df = pd.DataFrame(results)
                    
                    # Interactive results with confidence visualization
                    st.dataframe(
                        df,
                        column_config={
                            "ai_confidence": st.column_config.ProgressColumn(
                                "AI Confidence",
                                min_value=0,
                                max_value=1,
                            ),
                            "sensitivity_score": st.column_config.NumberColumn(
                                "Sensitivity Score",
                                format="%.2f"
                            )
                        }
                    )
                    
                    # AI-generated insights
                    if st.checkbox("Show AI Reasoning"):
                        for result in results:
                            with st.expander(f"🔍 {result['table']}.{result['column']}"):
                                st.write("**AI Classification:**", result['classification'])
                                st.write("**Reasoning:**", result['reasoning'])
                                st.write("**Recommended Action:**", result['recommendation'])
    
    with st.expander("📊 Cross-Table Pattern Analysis"):
        if st.button("Discover Patterns"):
            pattern_analysis = run_cross_table_analysis(selected_tables)
            st.info(pattern_analysis)
    
    with st.expander("🎯 Semantic Similarity"):
        col1, col2 = st.columns(2)
        with col1:
            source_cols = st.multiselect("Source Columns", available_columns)
        with col2:
            target_cols = st.multiselect("Target Columns", available_columns)
        
        if st.button("Find Similar Columns") and source_cols and target_cols:
            similarities = find_semantic_similarities(source_cols, target_cols)
            st.dataframe(similarities)
```

## 🔧 Configuration and Best Practices

### Model Selection Guide

- **AI_CLASSIFY**: Use for quick, consistent classification
- **llama3.1-8b**: Fast analysis for simple patterns
- **llama3.1-70b**: Balanced performance for most use cases
- **claude-3-5-sonnet**: Most capable for complex reasoning
- **mistral-large2**: Excellent for structured outputs and compliance

### Cost Optimization Tips

1. **Cache Results**: Store AI analysis results to avoid re-computation
2. **Batch Processing**: Process multiple columns together when possible  
3. **Smart Sampling**: Use representative samples rather than full datasets
4. **Model Right-sizing**: Use appropriate models for task complexity
5. **Async Processing**: Use Snowflake tasks for background AI analysis

### Security Considerations

1. **Data Governance**: Ensure AI analysis complies with data policies
2. **Access Control**: Restrict Cortex AI usage to authorized users
3. **Audit Trail**: Log all AI analysis activities
4. **Privacy**: Don't expose sensitive data in AI prompts unnecessarily

## 🎯 Key Benefits Summary

| Traditional Approach | Cortex AI Enhanced |
|---------------------|-------------------|
| Pattern-based detection | Intelligent classification |
| High false positives | Context-aware accuracy |
| Manual rule updates | Self-adapting analysis |
| Basic reporting | AI-generated insights |
| Static masking strategies | Dynamic recommendations |

## 🚀 Getting Started Checklist

- [ ] Enable Cortex AI functions in your Snowflake account
- [ ] Test AI_CLASSIFY on sample data
- [ ] Implement enhanced detection pipeline
- [ ] Add AI analysis to your Streamlit app
- [ ] Set up automated monitoring with AI
- [ ] Generate AI-powered compliance reports
- [ ] Optimize for cost and performance
- [ ] Train team on AI-enhanced capabilities

This integration will transform your sensitive data discovery application from a rule-based system to an intelligent, adaptive platform that leverages the full power of modern AI for data privacy and compliance. 