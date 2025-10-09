# Lab 02: Data Quality Fundamentals
## Building Your Foundation for AI-Powered Data Quality

### 🎯 **Lab Objectives**

In this foundational lab, you'll learn essential data quality concepts and implement basic validation rules that form the backbone of any robust data quality system. These fundamentals will prepare you for the advanced AI technologies introduced in later labs.

### 📚 **Learning Outcomes**

By the end of this lab, you will be able to:
- Understand the six dimensions of data quality
- Implement basic data validation rules using SQL
- Create data quality scorecards and metrics
- Design alerts for data quality violations
- Build foundation tables for AI-powered analysis

### 🏗️ **Architecture Overview**

This lab focuses on traditional data quality techniques that provide the foundation for AI enhancement:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Raw Theme     │    │  Data Quality    │    │   Quality       │
│   Park Data     │───▶│  Validation      │───▶│   Metrics       │
│                 │    │  Rules           │    │   Dashboard     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🔍 **The Six Dimensions of Data Quality**

#### 1. **Completeness** - Are all required fields populated?
#### 2. **Accuracy** - Is the data correct and factual?
#### 3. **Consistency** - Is data uniform across systems?
#### 4. **Validity** - Does data conform to defined formats?
#### 5. **Uniqueness** - Are there inappropriate duplicates?
#### 6. **Timeliness** - Is data current and up-to-date?

### 🛠️ **Prerequisites**

- Completion of Lab 01 (Setup)
- Access to UDX theme park sample data
- Basic SQL knowledge
- Understanding of data warehousing concepts

### 📝 **Lab Exercises**

#### **Exercise 1: Data Profiling and Discovery (30 minutes)**

Explore the theme park data to understand quality issues:

1. **Data Volume Analysis**
   ```sql
   -- Analyze data volume across tables
   SELECT 
       table_name,
       row_count,
       column_count,
       last_updated
   FROM table_profile_summary;
   ```

2. **Missing Data Assessment**
   ```sql
   -- Identify completeness issues
   SELECT 
       'GUESTS' as table_name,
       'EMAIL' as column_name,
       COUNT(*) as total_records,
       COUNT(email) as populated_records,
       COUNT(*) - COUNT(email) as missing_records,
       ROUND((COUNT(email) * 100.0 / COUNT(*)), 2) as completeness_percentage
   FROM GUESTS;
   ```

3. **Data Distribution Analysis**
   ```sql
   -- Understand data patterns
   SELECT 
       guest_type,
       COUNT(*) as frequency,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
   FROM GUESTS
   GROUP BY guest_type
   ORDER BY frequency DESC;
   ```

#### **Exercise 2: Basic Validation Rules (45 minutes)**

Implement fundamental data quality checks:

1. **Completeness Validation**
   ```sql
   -- Create completeness check function
   CREATE OR REPLACE FUNCTION check_completeness(
       table_name STRING,
       column_name STRING,
       threshold FLOAT DEFAULT 95.0
   )
   RETURNS TABLE (
       check_name STRING,
       status STRING,
       completeness_percentage FLOAT,
       threshold_value FLOAT,
       records_checked INTEGER,
       missing_records INTEGER
   );
   ```

2. **Format Validation**
   ```sql
   -- Email format validation
   SELECT 
       guest_id,
       email,
       CASE 
           WHEN email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' 
           THEN 'VALID'
           ELSE 'INVALID'
       END as email_format_status
   FROM GUESTS
   WHERE email IS NOT NULL;
   ```

3. **Business Rule Validation**
   ```sql
   -- Age validation for theme park guests
   SELECT 
       guest_id,
       age,
       CASE 
           WHEN age < 0 OR age > 120 THEN 'INVALID'
           WHEN age BETWEEN 0 AND 17 THEN 'MINOR'
           WHEN age BETWEEN 18 AND 64 THEN 'ADULT'
           WHEN age >= 65 THEN 'SENIOR'
       END as age_category,
       CASE 
           WHEN age < 0 OR age > 120 THEN 'Age outside realistic range'
           ELSE 'Valid age'
       END as validation_message
   FROM GUESTS;
   ```

#### **Exercise 3: Data Quality Metrics Framework (45 minutes)**

Build a comprehensive metrics system:

1. **Create Quality Results Table**
   ```sql
   CREATE OR REPLACE TABLE DATA_QUALITY_RESULTS (
       result_id STRING DEFAULT UUID_STRING(),
       check_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
       table_name STRING NOT NULL,
       column_name STRING,
       check_type STRING NOT NULL,
       check_name STRING NOT NULL,
       status STRING NOT NULL,
       metric_value FLOAT,
       threshold_value FLOAT,
       records_checked INTEGER,
       failed_records INTEGER,
       error_message STRING,
       created_by STRING DEFAULT CURRENT_USER()
   );
   ```

2. **Implement Quality Score Calculation**
   ```sql
   -- Calculate overall quality score
   CREATE OR REPLACE VIEW QUALITY_SCORECARD AS
   WITH quality_metrics AS (
       SELECT 
           table_name,
           check_type,
           COUNT(*) as total_checks,
           COUNT(CASE WHEN status = 'PASS' THEN 1 END) as passed_checks,
           AVG(metric_value) as avg_metric_value
       FROM DATA_QUALITY_RESULTS
       WHERE check_timestamp >= DATEADD('day', -7, CURRENT_DATE())
       GROUP BY table_name, check_type
   )
   SELECT 
       table_name,
       check_type,
       total_checks,
       passed_checks,
       ROUND((passed_checks * 100.0 / total_checks), 2) as pass_rate,
       ROUND(avg_metric_value, 2) as avg_score,
       CASE 
           WHEN (passed_checks * 100.0 / total_checks) >= 95 THEN 'EXCELLENT'
           WHEN (passed_checks * 100.0 / total_checks) >= 85 THEN 'GOOD'
           WHEN (passed_checks * 100.0 / total_checks) >= 70 THEN 'FAIR'
           ELSE 'POOR'
       END as quality_grade
   FROM quality_metrics;
   ```

#### **Exercise 4: Automated Quality Monitoring (30 minutes)**

Set up basic monitoring and alerting:

1. **Create Monitoring Procedures**
   ```sql
   -- Daily quality check procedure
   CREATE OR REPLACE PROCEDURE run_daily_quality_checks()
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
   BEGIN
       -- Completeness checks
       INSERT INTO DATA_QUALITY_RESULTS (table_name, check_type, check_name, status, metric_value, threshold_value, records_checked)
       SELECT 
           'GUESTS' as table_name,
           'COMPLETENESS' as check_type,
           'EMAIL_COMPLETENESS' as check_name,
           CASE WHEN completeness_pct >= 95 THEN 'PASS' ELSE 'FAIL' END as status,
           completeness_pct as metric_value,
           95.0 as threshold_value,
           total_records
       FROM (
           SELECT 
               COUNT(*) as total_records,
               ROUND((COUNT(email) * 100.0 / COUNT(*)), 2) as completeness_pct
           FROM GUESTS
       );
       
       RETURN 'Daily quality checks completed successfully';
   END;
   $$;
   ```

2. **Quality Alerts Setup**
   ```sql
   -- Create alert conditions
   CREATE OR REPLACE VIEW QUALITY_ALERTS AS
   SELECT 
       table_name,
       check_name,
       status,
       metric_value,
       threshold_value,
       check_timestamp,
       'Data quality threshold exceeded' as alert_message,
       CASE 
           WHEN metric_value < (threshold_value * 0.5) THEN 'CRITICAL'
           WHEN metric_value < (threshold_value * 0.8) THEN 'WARNING'
           ELSE 'INFO'
       END as alert_severity
   FROM DATA_QUALITY_RESULTS
   WHERE status = 'FAIL'
   AND check_timestamp >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
   ORDER BY check_timestamp DESC;
   ```

### 🎯 **Success Criteria**

By the end of this lab, you should have:

✅ **Implemented** basic data quality validation rules across all six dimensions  
✅ **Created** a quality metrics framework with scoring  
✅ **Built** automated monitoring procedures  
✅ **Established** alert mechanisms for quality violations  
✅ **Generated** quality scorecards and dashboards  

### 🔄 **Common Issues and Troubleshooting**

#### **Issue**: Quality checks taking too long on large tables
**Solution**: Implement sampling strategies for large datasets
```sql
-- Sample-based quality check
SELECT COUNT(*) * 100 as estimated_total
FROM GUESTS SAMPLE (1) -- 1% sample
WHERE email IS NULL;
```

#### **Issue**: Too many false positive alerts
**Solution**: Implement dynamic thresholds based on historical patterns
```sql
-- Dynamic threshold based on historical average
WITH historical_avg AS (
    SELECT AVG(metric_value) as avg_score
    FROM DATA_QUALITY_RESULTS
    WHERE check_name = 'EMAIL_COMPLETENESS'
    AND check_timestamp >= DATEADD('day', -30, CURRENT_DATE())
)
SELECT 
    current_score,
    avg_score,
    CASE WHEN current_score < (avg_score * 0.9) THEN 'ALERT' ELSE 'OK' END as status
FROM current_metrics, historical_avg;
```

### 📈 **Key Performance Indicators**

Monitor these metrics to track your data quality program:

- **Overall Quality Score**: Target >95%
- **Critical Issues**: <1% of total checks
- **Resolution Time**: <4 hours for critical issues
- **Coverage**: 100% of business-critical tables monitored
- **Trend**: Quality scores improving over time

### 🚀 **Next Steps**

In **Lab 03: Advanced Data Validation**, you'll learn:
- Complex cross-table validation rules
- Statistical anomaly detection
- Data lineage tracking
- Automated data profiling

### 📚 **Additional Resources**

- [Data Quality Dimensions Best Practices](link-to-resource)
- [SQL Quality Check Patterns](link-to-resource)
- [Threshold Setting Guidelines](link-to-resource)

---

**Continue to Lab 03 to build advanced validation capabilities that will prepare you for AI-powered data quality management!** 