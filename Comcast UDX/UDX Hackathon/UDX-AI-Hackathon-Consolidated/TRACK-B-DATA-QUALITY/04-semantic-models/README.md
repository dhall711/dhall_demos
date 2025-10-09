# Lab 05: Semantic Models and Views
## Creating Business-Friendly Data Abstractions for AI

### 🎯 **Lab Objectives**

In this lab, you'll learn to create Semantic Models and Views that bridge the gap between technical data schemas and business understanding. These semantic abstractions enable AI systems to better understand business context and provide more accurate, meaningful insights.

### 📚 **Learning Outcomes**

By the end of this lab, you will be able to:
- Create semantic views with business-friendly dimensions and metrics
- Define relationships between logical tables
- Implement business rules and calculations in semantic models
- Enable AI systems to understand business context
- Prepare data structures for Snowflake Intelligence and Cortex Analyst

### 🏗️ **Architecture Overview**

Semantic Views create a business abstraction layer over raw data:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Raw Theme     │    │   Semantic       │    │   Business      │
│   Park Tables   │───▶│   Models &       │───▶│   Intelligence  │
│   (Technical)   │    │   Views          │    │   (Business)     │
└─────────────────┘    └──────────────────┘              │
                       │                        │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Cortex         │    │   Natural       │
                       │   Analyst        │    │   Language      │
                       └──────────────────┘    │   Queries       │
                                              └─────────────────┘
```

### 🔍 **Semantic Model Concepts**

#### 1. **Logical Tables** - Business entities (Customers, Orders, Rides)
#### 2. **Dimensions** - Categorical attributes for filtering and grouping
#### 3. **Metrics** - Quantifiable business measures and KPIs
#### 4. **Facts** - Raw measurable values at the record level
#### 5. **Relationships** - How business entities connect to each other

### 🛠️ **Prerequisites**

- Completion of Labs 01-04
- Understanding of business intelligence concepts
- Knowledge of data relationships and joins
- Familiarity with theme park business context

### 📝 **Lab Exercises**

#### **Exercise 1: Creating Your First Semantic View (45 minutes)**

Build a semantic view for theme park operations:

1. **Define the Core Semantic View**
   ```sql
   -- Create semantic view for UDX theme park data quality
   CREATE OR REPLACE SEMANTIC VIEW udx_park_operations_semantic_view
   TABLES (
       PARKS primary key (PARK_ID),
       GUESTS primary key (GUEST_ID),
       RIDES primary key (RIDE_ID),
       RIDE_OPERATIONS primary key (OPERATION_ID),
       TICKETS primary key (TICKET_ID),
       DATA_QUALITY_RESULTS primary key (RESULT_ID)
   )
   RELATIONSHIPS (
       -- Guest to Park relationship
       GUESTS(PARK_ID) references PARKS(PARK_ID),
       -- Ticket to Guest relationship  
       TICKETS(GUEST_ID) references GUESTS(GUEST_ID),
       -- Ride Operations to Rides relationship
       RIDE_OPERATIONS(RIDE_ID) references RIDES(RIDE_ID),
       -- Ride Operations to Parks relationship
       RIDE_OPERATIONS(PARK_ID) references PARKS(PARK_ID),
       -- Data Quality to Parks relationship
       DATA_QUALITY_RESULTS(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       -- Park dimensions
       PARKS.PARK_NAME as "Theme Park",
       PARKS.REGION as "Geographic Region", 
       PARKS.PARK_TYPE as "Park Category",
       
       -- Guest dimensions
       GUESTS.AGE_GROUP as "Guest Age Group",
       GUESTS.GUEST_TYPE as "Guest Category",
       GUESTS.MEMBERSHIP_LEVEL as "Membership Tier",
       
       -- Ride dimensions
       RIDES.RIDE_TYPE as "Ride Category",
       RIDES.THRILL_LEVEL as "Thrill Level",
       
       -- Time dimensions
       RIDE_OPERATIONS.OPERATION_DATE as "Operation Date",
       GUESTS.VISIT_DATE as "Visit Date",
       
       -- Quality dimensions
       DATA_QUALITY_RESULTS.CHECK_TYPE as "Quality Check Type",
       DATA_QUALITY_RESULTS.STATUS as "Quality Status"
   )
   METRICS (
       -- Guest metrics
       TOTAL_GUESTS as COUNT(DISTINCT GUESTS.GUEST_ID),
       AVERAGE_AGE as AVG(GUESTS.AGE),
       
       -- Financial metrics
       TOTAL_REVENUE as SUM(TICKETS.PURCHASE_AMOUNT),
       AVERAGE_TICKET_PRICE as AVG(TICKETS.PURCHASE_AMOUNT),
       
       -- Operational metrics
       AVERAGE_WAIT_TIME as AVG(RIDE_OPERATIONS.WAIT_TIME_MINUTES),
       TOTAL_RIDE_OPERATIONS as COUNT(RIDE_OPERATIONS.OPERATION_ID),
       GUEST_SATISFACTION_SCORE as AVG(RIDE_OPERATIONS.GUEST_SATISFACTION_SCORE),
       
       -- Quality metrics
       QUALITY_SCORE as AVG(DATA_QUALITY_RESULTS.METRIC_VALUE),
       FAILED_QUALITY_CHECKS as COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'FAIL' THEN 1 END),
       QUALITY_CHECK_PASS_RATE as (COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'PASS' THEN 1 END) * 100.0 / COUNT(DATA_QUALITY_RESULTS.RESULT_ID))
   );
   ```

2. **Test Your Semantic View**
   ```sql
   -- Query using semantic view with business-friendly syntax
   SELECT * FROM SEMANTIC_VIEW(
       udx_park_operations_semantic_view
       DIMENSIONS 
           "Theme Park",
           "Geographic Region",
           "Operation Date"
       METRICS 
           TOTAL_GUESTS,
           AVERAGE_WAIT_TIME,
           GUEST_SATISFACTION_SCORE,
           QUALITY_SCORE
       WHERE "Operation Date" >= '2024-01-01'
       AND "Geographic Region" = 'Florida'
   )
   ORDER BY "Operation Date" DESC;
   ```

#### **Exercise 2: Enhanced Business Context (40 minutes)**

Add rich business context to your semantic model:

1. **Add Sample Values and Descriptions**
   ```sql
   -- Enhance semantic view with business context
   CREATE OR REPLACE SEMANTIC VIEW udx_enhanced_semantic_view
   TABLES (
       PARKS primary key (PARK_ID),
       GUESTS primary key (GUEST_ID), 
       RIDE_OPERATIONS primary key (OPERATION_ID)
   )
   RELATIONSHIPS (
       GUESTS(PARK_ID) references PARKS(PARK_ID),
       RIDE_OPERATIONS(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       PARKS.PARK_NAME as "Theme Park" 
           SYNONYMS ("Park Location", "Park Name", "Theme Park Location")
           DESCRIPTION "The specific UDX theme park location"
           SAMPLE_VALUES ("Universal Studios Florida", "Universal Studios Hollywood", "Universal Beijing Resort"),
           
       PARKS.REGION as "Geographic Region"
           SYNONYMS ("Region", "Location", "Geographic Area") 
           DESCRIPTION "The geographic region where the park is located"
           SAMPLE_VALUES ("Florida", "California", "Texas"),
           
       GUESTS.AGE_GROUP as "Guest Age Group"
           SYNONYMS ("Age Category", "Age Range", "Customer Age Group")
           DESCRIPTION "Categorized age groups for theme park guests"
           SAMPLE_VALUES ("Child (0-12)", "Teen (13-17)", "Adult (18-64)", "Senior (65+)"),
           
       RIDE_OPERATIONS.OPERATION_DATE as "Operation Date"
           SYNONYMS ("Date", "Operating Date", "Business Date")
           DESCRIPTION "The date when ride operations occurred"
   )
   METRICS (
       TOTAL_DAILY_GUESTS as COUNT(DISTINCT GUESTS.GUEST_ID)
           SYNONYMS ("Daily Visitors", "Guest Count", "Visitor Count")
           DESCRIPTION "Total number of unique guests visiting the park on a given day",
           
       AVERAGE_WAIT_TIME as AVG(RIDE_OPERATIONS.WAIT_TIME_MINUTES)
           SYNONYMS ("Avg Wait Time", "Average Queue Time", "Mean Wait Duration")
           DESCRIPTION "Average wait time in minutes across all ride operations",
           
       GUEST_SATISFACTION_INDEX as AVG(RIDE_OPERATIONS.GUEST_SATISFACTION_SCORE) * 20
           SYNONYMS ("Satisfaction Score", "Guest Happiness", "Customer Satisfaction")
           DESCRIPTION "Guest satisfaction score converted to 0-100 scale for easier interpretation"
   );
   ```

2. **Create Business Rules and Filters**
   ```sql
   -- Add business filters to semantic view
   ALTER SEMANTIC VIEW udx_enhanced_semantic_view
   ADD FILTERS (
       PEAK_SEASON as MONTH(RIDE_OPERATIONS.OPERATION_DATE) IN (6, 7, 8, 12)
           SYNONYMS ("Peak Season", "Busy Season", "High Season")
           DESCRIPTION "Summer months (June-August) and December holiday season",
           
       FAMILY_FRIENDLY_RIDES as RIDES.THRILL_LEVEL IN ('Low', 'Moderate')
           SYNONYMS ("Family Rides", "Kid-Friendly Rides", "Gentle Rides")
           DESCRIPTION "Rides suitable for families with children",
           
       HIGH_SATISFACTION as RIDE_OPERATIONS.GUEST_SATISFACTION_SCORE >= 4.0
           SYNONYMS ("Happy Guests", "Satisfied Customers", "Positive Feedback")
           DESCRIPTION "Operations with guest satisfaction score of 4.0 or higher out of 5.0"
   );
   ```

#### **Exercise 3: Advanced Semantic Models for Data Quality (45 minutes)**

Create specialized semantic views for data quality management:

1. **Data Quality Semantic View**
   ```sql
   -- Comprehensive data quality semantic view
   CREATE OR REPLACE SEMANTIC VIEW udx_data_quality_semantic_view
   TABLES (
       DATA_QUALITY_RESULTS primary key (RESULT_ID),
       PARKS primary key (PARK_ID),
       ANOMALY_DETECTION_LOG primary key (ANOMALY_ID)
   )
   RELATIONSHIPS (
       DATA_QUALITY_RESULTS(PARK_ID) references PARKS(PARK_ID),
       ANOMALY_DETECTION_LOG(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       -- Location dimensions
       PARKS.PARK_NAME as "Theme Park"
           DESCRIPTION "Theme park location for data quality monitoring"
           SAMPLE_VALUES ("Universal Studios Florida", "Universal Studios Hollywood"),
           
       PARKS.REGION as "Geographic Region"
           DESCRIPTION "Regional grouping for data quality analysis"
           SAMPLE_VALUES ("Florida", "California", "Texas"),
           
       -- Quality dimensions  
       DATA_QUALITY_RESULTS.CHECK_TYPE as "Quality Check Type"
           SYNONYMS ("Check Category", "Validation Type", "Quality Dimension")
           DESCRIPTION "Type of data quality check performed"
           SAMPLE_VALUES ("COMPLETENESS", "ACCURACY", "CONSISTENCY", "VALIDITY"),
           
       DATA_QUALITY_RESULTS.TABLE_NAME as "Data Source"
           SYNONYMS ("Table", "Data Table", "Source System")
           DESCRIPTION "The table or data source being monitored"
           SAMPLE_VALUES ("GUESTS", "RIDES", "TICKETS", "RIDE_OPERATIONS"),
           
       DATA_QUALITY_RESULTS.STATUS as "Quality Status"
           SYNONYMS ("Check Result", "Validation Status", "Quality Outcome")
           DESCRIPTION "Result of the data quality check"
           SAMPLE_VALUES ("PASS", "FAIL", "WARNING"),
           
       -- Anomaly dimensions
       ANOMALY_DETECTION_LOG.SEVERITY as "Anomaly Severity"
           SYNONYMS ("Alert Level", "Issue Severity", "Problem Level")
           DESCRIPTION "Severity level of detected anomalies"
           SAMPLE_VALUES ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
           
       -- Time dimensions
       DATA_QUALITY_RESULTS.CHECK_TIMESTAMP as "Check Date"
           SYNONYMS ("Validation Date", "Quality Check Date", "Monitoring Date")
           DESCRIPTION "When the data quality check was performed"
   )
   METRICS (
       -- Quality scores
       OVERALL_QUALITY_SCORE as AVG(DATA_QUALITY_RESULTS.METRIC_VALUE)
           SYNONYMS ("Quality Score", "Data Health Score", "Quality Rating")
           DESCRIPTION "Average data quality score across all checks (0-100 scale)",
           
       QUALITY_CHECK_COUNT as COUNT(DATA_QUALITY_RESULTS.RESULT_ID)
           SYNONYMS ("Total Checks", "Validation Count", "Quality Tests")
           DESCRIPTION "Total number of data quality checks performed",
           
       FAILED_CHECKS as COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'FAIL' THEN 1 END)
           SYNONYMS ("Failed Validations", "Quality Failures", "Issues Found")
           DESCRIPTION "Number of data quality checks that failed",
           
       PASS_RATE as (COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'PASS' THEN 1 END) * 100.0 / COUNT(DATA_QUALITY_RESULTS.RESULT_ID))
           SYNONYMS ("Success Rate", "Quality Pass Rate", "Validation Success")
           DESCRIPTION "Percentage of data quality checks that passed",
           
       -- Anomaly metrics
       ANOMALY_COUNT as COUNT(ANOMALY_DETECTION_LOG.ANOMALY_ID)
           SYNONYMS ("Anomalies Detected", "Issues Found", "Outliers Identified")
           DESCRIPTION "Total number of anomalies detected",
           
       CRITICAL_ANOMALIES as COUNT(CASE WHEN ANOMALY_DETECTION_LOG.SEVERITY = 'CRITICAL' THEN 1 END)
           SYNONYMS ("Critical Issues", "Severe Anomalies", "High Priority Alerts")
           DESCRIPTION "Number of critical severity anomalies"
   );
   ```

2. **Business Impact Semantic View**
   ```sql
   -- Business impact focused semantic view
   CREATE OR REPLACE SEMANTIC VIEW udx_business_impact_semantic_view
   TABLES (
       PARKS primary key (PARK_ID),
       GUESTS primary key (GUEST_ID),
       TICKETS primary key (TICKET_ID),
       DATA_QUALITY_RESULTS primary key (RESULT_ID)
   )
   RELATIONSHIPS (
       GUESTS(PARK_ID) references PARKS(PARK_ID),
       TICKETS(GUEST_ID) references GUESTS(GUEST_ID),
       DATA_QUALITY_RESULTS(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       PARKS.PARK_NAME as "Business Unit"
           DESCRIPTION "Theme park as a business unit for impact analysis",
           
       GUESTS.VISIT_DATE as "Business Date"
           DESCRIPTION "Date for business impact analysis",
           
       DATA_QUALITY_RESULTS.CHECK_TYPE as "Impact Category"
           DESCRIPTION "Category of data quality impact on business operations"
   )
   METRICS (
       -- Financial impact
       REVENUE_AT_RISK as SUM(CASE 
           WHEN DATA_QUALITY_RESULTS.STATUS = 'FAIL' 
           AND DATA_QUALITY_RESULTS.CHECK_TYPE IN ('ACCURACY', 'COMPLETENESS')
           THEN TICKETS.PURCHASE_AMOUNT * 0.1  -- 10% revenue risk factor
           ELSE 0 
       END)
           SYNONYMS ("Revenue Risk", "Financial Impact", "Revenue Exposure")
           DESCRIPTION "Estimated revenue at risk due to data quality issues",
           
       GUEST_EXPERIENCE_IMPACT as AVG(CASE 
           WHEN DATA_QUALITY_RESULTS.STATUS = 'FAIL' THEN 3.0  -- Reduced satisfaction
           ELSE 5.0  -- Normal satisfaction
       END)
           SYNONYMS ("Customer Impact", "Guest Satisfaction Risk", "Experience Quality")
           DESCRIPTION "Estimated impact on guest experience due to data quality",
           
       OPERATIONAL_EFFICIENCY as (100 - (COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'FAIL' THEN 1 END) * 100.0 / COUNT(DATA_QUALITY_RESULTS.RESULT_ID)))
           SYNONYMS ("Efficiency Score", "Operational Health", "Process Quality")
           DESCRIPTION "Operational efficiency percentage based on data quality"
   );
   ```

#### **Exercise 4: Integrating with Cortex Search (30 minutes)**

Enhance semantic views with intelligent search capabilities:

1. **Create Cortex Search Service**
   ```sql
   -- Create search service for park information
   CREATE OR REPLACE CORTEX SEARCH SERVICE park_information_search
   ON park_documentation
   ATTRIBUTES park_name, facility_type, location, description
   WAREHOUSE = UDX_AI_WAREHOUSE;
   ```

2. **Integrate Search with Semantic View**
   ```sql
   -- Enhance semantic view with search capabilities
   ALTER SEMANTIC VIEW udx_enhanced_semantic_view
   MODIFY DIMENSION "Theme Park" 
   SET CORTEX_SEARCH_SERVICE = (
       SERVICE => 'park_information_search',
       LITERAL_COLUMN => 'park_name'
   );
   ```

3. **Test Natural Language Queries**
   ```sql
   -- Test search-enabled queries
   SELECT * FROM SEMANTIC_VIEW(
       udx_enhanced_semantic_view
       DIMENSIONS "Theme Park"
       METRICS TOTAL_DAILY_GUESTS, AVERAGE_WAIT_TIME
       WHERE "Theme Park" MATCHES 'Orlando theme park with movie studios'
   );
   ```

### 🧠 **Preparing for AI Integration**

Your semantic views are now ready for AI-powered analytics:

```sql
-- Verify semantic view is AI-ready
DESCRIBE SEMANTIC VIEW udx_data_quality_semantic_view;

-- Enable for Snowflake Intelligence
ALTER SEMANTIC VIEW udx_data_quality_semantic_view 
SET INTELLIGENCE_ENABLED = TRUE;

-- Test with Cortex Analyst (preparation for Lab 06)
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'anthropic.claude-3-5-sonnet',
    CONCAT(
        'Using this semantic view structure: ',
        (SELECT LISTAGG(column_name, ', ') FROM INFORMATION_SCHEMA.SEMANTIC_DIMENSIONS 
         WHERE semantic_view_name = 'UDX_DATA_QUALITY_SEMANTIC_VIEW'),
        '. Suggest 5 business questions that executives might ask about theme park data quality.'
    )
) as suggested_questions;
```

### 🎯 **Success Criteria**

By the end of this lab, you should have:

✅ **Created** semantic views with business-friendly names and descriptions  
✅ **Defined** proper relationships between logical tables  
✅ **Implemented** business metrics and KPIs  
✅ **Added** sample values and business context  
✅ **Integrated** Cortex Search for enhanced queries  
✅ **Prepared** views for AI-powered analytics  

### 📊 **Testing Your Semantic Views**

Run these validation queries to ensure your semantic views work correctly:

```sql
-- Test 1: Basic semantic query
SELECT * FROM SEMANTIC_VIEW(
    udx_park_operations_semantic_view
    DIMENSIONS "Theme Park", "Geographic Region"
    METRICS TOTAL_GUESTS, QUALITY_SCORE
) LIMIT 10;

-- Test 2: Business filter usage
SELECT * FROM SEMANTIC_VIEW(
    udx_enhanced_semantic_view
    DIMENSIONS "Theme Park", "Operation Date"  
    METRICS TOTAL_DAILY_GUESTS, GUEST_SATISFACTION_INDEX
    WHERE PEAK_SEASON = TRUE
    AND HIGH_SATISFACTION = TRUE
);

-- Test 3: Quality-focused analysis
SELECT * FROM SEMANTIC_VIEW(
    udx_data_quality_semantic_view
    DIMENSIONS "Theme Park", "Quality Check Type"
    METRICS OVERALL_QUALITY_SCORE, PASS_RATE, CRITICAL_ANOMALIES
    WHERE "Quality Check Type" = 'COMPLETENESS'
);
```

### 🔄 **Common Issues and Troubleshooting**

#### **Issue**: "Semantic view compilation failed"
**Solution**: Check that all referenced tables exist and relationships are properly defined
```sql
-- Validate table existence
SELECT table_name 
FROM INFORMATION_SCHEMA.TABLES 
WHERE table_name IN ('PARKS', 'GUESTS', 'RIDES', 'RIDE_OPERATIONS');
```

#### **Issue**: "Relationship cannot be established"
**Solution**: Ensure primary keys are correctly defined and foreign key relationships exist
```sql
-- Check relationship integrity
SELECT COUNT(*) as orphaned_records
FROM GUESTS g
LEFT JOIN PARKS p ON g.park_id = p.park_id
WHERE p.park_id IS NULL;
```

### 🚀 **Next Steps**

In **Lab 06: Snowflake Intelligence**, you'll learn:
- Natural language querying of your semantic views
- Conversational data analytics
- Business user self-service insights
- AI-powered data exploration

Your semantic views will become the foundation for natural language data conversations!

### 📚 **Additional Resources**

- [Semantic View Documentation](link-to-resource)
- [Business Intelligence Best Practices](link-to-resource)
- [Cortex Search Integration Guide](link-to-resource)

---

**Continue to Lab 06 to enable natural language conversations with your business data!** 