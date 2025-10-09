# Lab 01: Environment Setup for NLP2SQL Analytics

## 🎯 Objectives
- Set up Snowflake database optimized for business analytics
- Load comprehensive UDX business datasets
- Create schema documentation for AI understanding
- Establish foundation for natural language query translation

## 📋 Prerequisites
- Snowflake account with ACCOUNTADMIN or similar privileges
- Cortex AI enabled (contact your Snowflake rep if needed)
- Understanding of basic business intelligence concepts

## 🏗️ What We're Building

A complete business analytics environment with:
- **6 UDX Theme Parks** with comprehensive operational data
- **Business-Optimized Tables** designed for common analytics queries
- **Rich Metadata** to help AI understand business context
- **Sample Query Library** covering typical business questions
- **Security Framework** for governed self-service access

## 🚀 Setup Steps

### 1. Run Initial Setup
Execute `setup.sql` to create:
- `UDX_NLP2SQL` database with business analytics focus
- `BUSINESS_ANALYTICS` schema for core datasets
- `METADATA` schema for AI context and documentation
- Virtual warehouse optimized for analytics workloads

### 2. Load Business Data
Execute `../sample-data/load_business_data.sql` to populate:
- Customer analytics and segmentation data
- Revenue and financial performance metrics
- Operational efficiency and guest experience data
- Marketing and loyalty program analytics
- Seasonal trends and forecasting data

### 3. Create AI Context
Execute the metadata setup to provide AI with:
- Business glossary and terminology
- Table relationships and join patterns
- Common business metrics and calculations
- Sample questions and expected SQL patterns

## 📊 Business Analytics Dataset Overview

| Dataset | Records | Business Purpose | Example Queries |
|---------|---------|------------------|-----------------|
| **CUSTOMERS** | 50,000 | Guest demographics and loyalty | *"Show me our top 10% most valuable customers"* |
| **SALES_TRANSACTIONS** | 500,000 | Revenue and purchase behavior | *"What's our average revenue per guest this quarter?"* |
| **PARK_PERFORMANCE** | 2,000 | Daily operational metrics | *"Which park had the best guest satisfaction last month?"* |
| **ATTRACTION_ANALYTICS** | 100,000 | Ride popularity and efficiency | *"What are our most popular attractions by age group?"* |
| **MARKETING_CAMPAIGNS** | 200 | Campaign effectiveness | *"Which marketing channels drive highest ticket sales?"* |
| **FINANCIAL_SUMMARY** | 365 | Daily financial rollups | *"Show me year-over-year revenue growth by park"* |

## 🧠 AI Context and Metadata

### Business Terminology Mapping
- **Guest** = Customer visiting theme parks
- **Attraction** = Rides and entertainment experiences  
- **Throughput** = Number of guests served per hour
- **ADR** = Average Daily Revenue per guest
- **NPS** = Net Promoter Score for satisfaction
- **FastPass** = Premium line-skipping service

### Common Business Metrics
- **Revenue Per Guest**: Total revenue divided by unique visitors
- **Guest Satisfaction**: Average rating across all touchpoints
- **Operational Efficiency**: Actual vs. theoretical hourly capacity
- **Market Penetration**: Ticket sales by demographic segments
- **Seasonal Index**: Performance relative to annual average

### Key Performance Indicators (KPIs)
- **Daily/Monthly/Quarterly Revenue Trends**
- **Guest Satisfaction Scores by Park and Attraction**
- **Capacity Utilization and Wait Time Optimization**
- **Customer Lifetime Value and Loyalty Metrics**
- **Marketing ROI and Campaign Effectiveness**

## 🔧 Configuration for Natural Language Queries

### Warehouse Sizing for Analytics
- **SMALL**: Basic reporting and simple aggregations
- **MEDIUM**: Complex joins and time-series analysis
- **LARGE**: Advanced analytics and ML workloads

### Cortex AI Models for NLP2SQL
- **llama3-8b**: Fast query translation for simple questions
- **mixtral-8x7b**: Balanced performance for most business queries
- **llama3-70b**: Complex multi-table analysis and calculations

### Security and Governance Setup
- **Role-Based Access**: Different data access levels by user type
- **Query Governance**: Limits on resource usage and complexity
- **Audit Logging**: Track all AI-generated queries for compliance
- **Data Masking**: Protect sensitive customer information

## 📈 Sample Business Questions We'll Address

### **Executive Level**
- *"Show me quarterly revenue trends across all parks"*
- *"Which region is performing best this year?"*
- *"What's our customer acquisition cost by marketing channel?"*

### **Operations Management**
- *"What attractions have the highest guest satisfaction?"*
- *"Show me capacity utilization by park and day of week"*
- *"Which rides need maintenance attention based on downtime?"*

### **Marketing & Customer Analytics**
- *"Who are our most loyal customers by demographic?"*
- *"What's the lifetime value of VIP pass holders?"*
- *"How do weather conditions affect attendance?"*

### **Financial Analysis**
- *"Calculate profit margins by park and ticket type"*
- *"Show me the impact of discounts on total revenue"*
- *"What's our break-even point for new attraction investments?"*

## ✅ Success Criteria

- [ ] Database and schema created with business focus
- [ ] All business analytics tables loaded with realistic data
- [ ] AI metadata and context documentation in place
- [ ] Sample queries validate business question patterns
- [ ] Security and governance framework established

## 🔍 Validation Queries

Run these queries to verify your setup:

```sql
-- Verify business data is loaded correctly
SELECT 
    'Business Analytics Setup Validation' as check_type,
    (SELECT COUNT(*) FROM CUSTOMERS) as customer_records,
    (SELECT COUNT(*) FROM SALES_TRANSACTIONS) as transaction_records,
    (SELECT COUNT(*) FROM PARK_PERFORMANCE) as performance_records,
    (SELECT SUM(daily_revenue) FROM FINANCIAL_SUMMARY) as total_revenue_loaded;

-- Test AI context understanding
SELECT 
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'I need to query UDX theme park business data. Our main tables are CUSTOMERS, SALES_TRANSACTIONS, PARK_PERFORMANCE, and ATTRACTION_ANALYTICS. Help me understand how to find our most profitable customer segments.'
    ) as ai_context_test;
```

## ⚠️ Important Setup Notes

### Data Privacy Considerations
- Customer PII is synthetic - no real personal information
- Revenue figures are realistic but not actual UDX data
- Use proper data masking in production implementations

### Performance Optimization
- Tables are pre-optimized with clustering keys for analytics
- Consider partitioning for large-scale production deployments
- Monitor warehouse auto-scaling during AI query generation

### AI Model Selection
- Start with `mixtral-8x7b` for balanced performance
- Use `llama3-70b` for complex business logic translation
- Consider `llama3-8b` for high-frequency, simple queries

**Next**: Proceed to Lab 02 for basic NLP2SQL translation! 