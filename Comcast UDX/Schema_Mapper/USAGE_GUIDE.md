# Schema Mapper - User Guide

## Getting Started

### Prerequisites
- Access to Snowflake environment with Cortex LLM enabled
- Tables exist in `SOURCE_SYSTEMS` and `TARGET_SCHEMA` schemas
- Streamlit-in-Snowflake application deployed

### First Time Setup
1. Launch the application in your Snowflake environment
2. Wait for automatic vector embedding initialization (this may take 1-2 minutes)
3. Look for the "✅ Vector embeddings initialized successfully!" message

## Step-by-Step Usage

### Step 1: Select Your Tables
1. **Choose Input Table**: From the left dropdown, select your source table from the `SOURCE_SYSTEMS` schema
2. **Choose Target Table**: From the right dropdown, select your destination table from the `TARGET_SCHEMA` schema

### Step 2: Review Table Information
- Examine the displayed metadata for both tables:
  - Column names and data types
  - Table comments and tags
  - Sample data (click "📋 Sample Data" to expand)
- Verify you've selected the correct tables before proceeding

### Step 3: Generate Mapping Analysis
1. Click **"🧮 Map to Target Table (with Vector Embeddings)"**
2. Wait for the analysis to complete (typically 30-60 seconds)
3. The system will:
   - Calculate vector similarities between columns
   - Analyze sample data patterns
   - Generate intelligent mapping recommendations

### Step 4: Review Analysis Results

#### Vector Similarity Results
- Expand **"View Detailed Similarity Results"** to see:
  - Top matching columns for each input field
  - Similarity scores (0.0 to 1.0, higher is better)
  - Semantic reasoning for matches

#### LLM Analysis
- Review the comprehensive analysis in **"View Full Analysis"**:
  - Recommended field mappings
  - Confidence scores for each mapping
  - Required data transformations
  - Columns that cannot be mapped

### Step 5: Approve or Provide Feedback

#### Option A: Approve Analysis
1. Click **"✅ Approve Analysis"** if the mappings look correct
2. The system will generate executable SQL
3. Review the generated SQL statement
4. Click **"⚡ Execute SQL and Insert Records"** to perform the data transfer

#### Option B: Provide Feedback
1. Click **"❌ Reject Analysis"** if mappings need improvement
2. In the feedback form, provide specific guidance such as:
   - "Map customer_id to cust_key instead"
   - "Don't map the internal_notes column"
   - "Convert date format from YYYY-MM-DD to MM/DD/YYYY"
3. Click **"🔄 Resubmit with Feedback"**
4. Review the updated analysis

### Step 6: Execute and Verify
1. After approving the analysis, review the generated SQL
2. Click **"⚡ Execute SQL and Insert Records"**
3. Watch for success confirmation and celebration balloons! 🎉
4. Verify data in your target table

## Best Practices

### For Better Results
1. **Provide Good Metadata**: Ensure your tables have meaningful comments
2. **Use Descriptive Names**: Column names that indicate purpose improve matching
3. **Include Sample Data**: Representative data helps with transformation decisions
4. **Review Carefully**: Always review similarity results and analysis before execution

### Feedback Guidelines
- Be specific about incorrect mappings
- Mention business rules or constraints
- Indicate required data transformations
- Point out columns that should be excluded

### Performance Tips
- **Cache Utilization**: Switching between tables is fast due to metadata caching
- **Embedding Persistence**: Vector embeddings persist between sessions
- **Incremental Updates**: Use "🔄 Reinitialize Embeddings" only when schema changes occur

## Troubleshooting

### Common Issues

#### "Embeddings table not found"
- **Solution**: Click "🔄 Reinitialize Embeddings" to rebuild vector embeddings
- **Cause**: First-time usage or embeddings were cleared

#### "No tables found in schema"
- **Solution**: Verify tables exist in `SOURCE_SYSTEMS` and `TARGET_SCHEMA`
- **Cause**: Missing tables or incorrect schema names

#### "Failed to generate analysis"
- **Solution**: Check table metadata and try again
- **Cause**: Insufficient metadata or connectivity issues

#### Low similarity scores
- **Solution**: Provide feedback to guide the mapping process
- **Cause**: Very different naming conventions or limited metadata

### Performance Considerations
- Initial embedding generation takes 1-2 minutes for large schemas
- Subsequent analyses are much faster (30-60 seconds)
- Large tables may have longer sample data loading times

## Understanding Similarity Scores

### Score Interpretation
- **0.9-1.0**: Excellent match, very high confidence
- **0.7-0.9**: Good match, likely correct
- **0.5-0.7**: Moderate match, review recommended
- **0.3-0.5**: Weak match, probably incorrect
- **0.0-0.3**: Poor match, likely unrelated

### What Influences Scores
- **Column Names**: Similar names increase scores
- **Data Types**: Compatible types boost similarity
- **Comments**: Descriptive comments improve matching
- **Context**: Table and schema names provide context

## Advanced Features

### Feedback Learning
- The system learns from your feedback
- Subsequent analyses improve based on corrections
- Feedback history is maintained for the session

### SQL Customization
- Generated SQL includes data type conversions
- NULL handling is automatic
- Comments explain mapping decisions

### Metadata Utilization
- Table tags influence analysis
- Column comments are heavily weighted
- Sample data validates mapping decisions

## Sample Workflow Example

```
1. User selects: SOURCE_SYSTEMS.LEGACY_CUSTOMERS → TARGET_SCHEMA.CUSTOMER_DIM
2. System finds: legacy_cust_id (0.92 similarity) → customer_key
3. LLM analyzes: "High confidence mapping based on naming and sample data patterns"
4. User approves mapping
5. SQL generated: INSERT INTO TARGET_SCHEMA.CUSTOMER_DIM (customer_key, ...) 
                   SELECT legacy_cust_id, ... FROM SOURCE_SYSTEMS.LEGACY_CUSTOMERS
6. Execution successful: 1,000 records transferred
```

## Getting Help

### When to Reinitialize Embeddings
- Schema changes (new tables/columns added)
- Performance issues with similarity matching
- First-time setup or after long periods of inactivity

### Optimization Tips
- Start with well-documented tables for best results
- Use the feedback loop to train the system for your specific use case
- Review vector similarity results to understand the AI's reasoning

### Support
- Check error messages for specific guidance
- Use the feedback system to improve results
- Ensure proper Snowflake permissions for all operations 