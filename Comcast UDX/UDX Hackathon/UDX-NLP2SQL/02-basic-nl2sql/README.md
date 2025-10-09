# Lab 02: Basic Natural Language to SQL Translation

## 🎯 Objectives
- Learn to use Cortex AI for translating business questions to SQL
- Understand prompt engineering for accurate query generation
- Practice with common business analytics patterns
- Build confidence in AI-assisted query development

## 📋 Prerequisites
- Completed Labs 01-02 (Environment setup and schema understanding)
- Basic understanding of SQL SELECT statements
- Familiarity with business terminology from Lab 01

## 🧠 Core Concepts

### **Natural Language Understanding**
Cortex AI can interpret business questions and convert them to SQL by understanding:
- **Intent**: What the user wants to know (aggregation, filtering, ranking)
- **Entities**: What data they're asking about (customers, revenue, attractions)
- **Context**: Business rules and relationships between tables
- **Constraints**: Time periods, filters, and conditions

### **Query Pattern Recognition**
Most business questions follow common patterns:
- **"Show me the top N..."** → ORDER BY ... DESC LIMIT N
- **"What is the total/average..."** → SUM() or AVG() aggregation
- **"Compare X between Y and Z..."** → GROUP BY with filtering
- **"Trend over time..."** → Time-series analysis with GROUP BY date

## 🚀 Lab Exercises

### Exercise 1: Simple Aggregations
Learn to translate basic business questions into SQL aggregations.

### Exercise 2: Filtering and Conditions
Add WHERE clauses and business logic to queries.

### Exercise 3: Grouping and Comparisons
Generate GROUP BY queries for comparative analysis.

### Exercise 4: Time-Based Analysis
Handle date ranges and temporal queries.

### Exercise 5: Multi-Table Joins
Combine data from multiple tables using business relationships.

## 🎢 Business Question Categories

### **Revenue Analytics**
- *"What is our total revenue this quarter?"*
- *"Show me average revenue per guest by park"*
- *"Which ticket type generates the most revenue?"*

### **Customer Insights**
- *"Who are our top 10 customers by lifetime value?"*
- *"How many customers do we have in each loyalty tier?"*
- *"What is the average age of VIP customers?"*

### **Operational Performance**
- *"Which park has the highest guest satisfaction?"*
- *"Show me average wait times by attraction type"*
- *"What is our capacity utilization across all parks?"*

### **Marketing Analytics**
- *"Which marketing channels drive the most conversions?"*
- *"What is the ROI of our social media campaigns?"*
- *"Show me campaign performance by target audience"*

## 💡 Prompt Engineering Best Practices

### **Provide Business Context**
```sql
-- Good prompt structure:
"You are a SQL expert for UDX theme park business analytics. 
Convert this business question to Snowflake SQL: [QUESTION]
Available tables: CUSTOMERS, SALES_TRANSACTIONS, PARK_PERFORMANCE
Business context: [RELEVANT CONTEXT]"
```

### **Specify Output Format**
- Request only SQL code without explanations for execution
- Ask for business-friendly column aliases
- Specify optimization preferences (performance, readability)

### **Include Business Rules**
- Mention important constraints (revenue must be positive)
- Specify date ranges and filters
- Include relevant business logic

## 🔧 AI Functions We'll Use

### **SNOWFLAKE.CORTEX.COMPLETE()**
Primary function for generating SQL from natural language:
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Convert to SQL: Show me top 5 customers by revenue'
) as generated_sql;
```

### **Custom Business Functions**
Leverage the functions created in Lab 01:
- `extract_query_intent()` - Parse business questions
- `generate_business_sql()` - Context-aware SQL generation
- `get_conversation_context()` - Multi-turn conversations

## ⚠️ Important Considerations

### **Query Validation**
- Always review AI-generated SQL before execution
- Test with small datasets first
- Verify business logic matches intent

### **Security and Governance**
- AI respects existing table permissions
- Generated queries follow security policies
- Monitor resource usage and costs

### **Business Accuracy**
- Validate results make business sense
- Cross-check calculations with known metrics
- Consider edge cases and data quality issues

## 📊 Success Metrics

By the end of this lab, you should be able to:
- [ ] Generate accurate SQL for simple business questions
- [ ] Understand and modify AI-generated queries
- [ ] Apply business context to improve query accuracy
- [ ] Handle common query patterns confidently
- [ ] Validate results for business reasonableness

## 🎯 Real-World Applications

This lab prepares you for:
- **Self-Service Analytics**: Enable business users to query data independently
- **Rapid Prototyping**: Quickly explore business questions
- **Report Automation**: Generate queries for regular reporting
- **Data Exploration**: Facilitate ad-hoc analysis

## 📖 Additional Resources

- [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Business Glossary](../01-setup/README.md#ai-context-and-metadata)
- [Query Pattern Library](../01-setup/setup.sql#query-pattern-templates)

---

**Next**: Lab 03 - Advanced Query Translation and Complex Business Logic 🧠 