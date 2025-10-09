# Lab 03: Advanced Data Validation
## Statistical Analysis and Cross-Table Quality Checks

### 🎯 **Lab Objectives**

In this advanced lab, you'll implement sophisticated data validation techniques using statistical analysis, cross-table relationships, and pattern-based anomaly detection. These advanced techniques bridge traditional data quality with AI-powered analytics introduced in Lab 04.

### 📚 **Learning Outcomes**

By the end of this lab, you will be able to:
- Implement statistical anomaly detection using SQL
- Create complex cross-table validation rules
- Build data lineage tracking systems
- Design pattern-based quality checks
- Establish baseline metrics for AI comparison

### 🏗️ **Architecture Overview**

This lab extends basic validation with advanced analytical techniques:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Multi-Table   │    │  Statistical     │    │   Advanced      │
│   Data Sources  │───▶│  Analysis &      │───▶│   Quality       │
│                 │    │  Cross-Table     │    │   Intelligence  │
└─────────────────┘    │  Validation      │    └─────────────────┘
                       └──────────────────┘              │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Pattern        │    │    Anomaly      │
                       │   Detection      │    │    Detection    │
                       └──────────────────┘    └─────────────────┘
```

### 🔍 **Advanced Validation Concepts**

#### 1. **Statistical Validation** - Using math to detect anomalies
#### 2. **Cross-Table Consistency** - Ensuring referential integrity
#### 3. **Pattern Recognition** - Identifying unusual data patterns
#### 4. **Temporal Analysis** - Time-based quality trends
#### 5. **Correlation Analysis** - Understanding data relationships

### 🛠️ **Prerequisites**

- Completion of Labs 01-02
- Understanding of statistical concepts (mean, standard deviation, percentiles)
- Advanced SQL knowledge (window functions, CTEs)
- Familiarity with data relationships

### 📝 **Lab Exercises**

#### **Exercise 1: Statistical Anomaly Detection (45 minutes)**

Implement statistical methods to identify data outliers:

1. **Z-Score Based Anomaly Detection**
   ```sql
   -- Detect statistical outliers in ride wait times
   CREATE OR REPLACE VIEW RIDE_WAIT_OUTLIERS AS
   WITH wait_time_stats AS (
       SELECT 
           ride_id,
           AVG(wait_time_minutes) as mean_wait,
           STDDEV(wait_time_minutes) as stddev_wait,
           COUNT(*) as sample_size
       FROM RIDE_OPERATIONS
       WHERE operation_date >= DATEADD('day', -30, CURRENT_DATE())
       GROUP BY ride_id
       HAVING COUNT(*) >= 20 -- Minimum sample size
   )
   SELECT 
       ro.operation_id,
       ro.ride_id,
       ro.wait_time_minutes,
       wts.mean_wait,
       wts.stddev_wait,
       -- Calculate Z-score
       (ro.wait_time_minutes - wts.mean_wait) / NULLIF(wts.stddev_wait, 0) as z_score,
       CASE 
           WHEN ABS((ro.wait_time_minutes - wts.mean_wait) / NULLIF(wts.stddev_wait, 0)) > 3 
           THEN 'EXTREME_OUTLIER'
           WHEN ABS((ro.wait_time_minutes - wts.mean_wait) / NULLIF(wts.stddev_wait, 0)) > 2 
           THEN 'MODERATE_OUTLIER'
           ELSE 'NORMAL'
       END as outlier_classification,
       ro.operation_date,
       ro.operation_timestamp
   FROM RIDE_OPERATIONS ro
   JOIN wait_time_stats wts ON ro.ride_id = wts.ride_id
   WHERE ro.operation_date >= DATEADD('day', -7, CURRENT_DATE())
   ORDER BY ABS((ro.wait_time_minutes - wts.mean_wait) / NULLIF(wts.stddev_wait, 0)) DESC;
   ```

2. **Interquartile Range (IQR) Method**
   ```sql
   -- IQR-based outlier detection for ticket prices
   CREATE OR REPLACE FUNCTION detect_price_outliers()
   RETURNS TABLE (
       ticket_id STRING,
       purchase_amount FLOAT,
       q1 FLOAT,
       q3 FLOAT,
       iqr FLOAT,
       lower_bound FLOAT,
       upper_bound FLOAT,
       outlier_status STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH price_quartiles AS (
       SELECT 
           PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY purchase_amount) as q1,
           PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY purchase_amount) as q3
       FROM TICKETS
       WHERE purchase_date >= DATEADD('day', -90, CURRENT_DATE())
   )
   SELECT 
       t.ticket_id,
       t.purchase_amount,
       pq.q1,
       pq.q3,
       (pq.q3 - pq.q1) as iqr,
       (pq.q1 - 1.5 * (pq.q3 - pq.q1)) as lower_bound,
       (pq.q3 + 1.5 * (pq.q3 - pq.q1)) as upper_bound,
       CASE 
           WHEN t.purchase_amount < (pq.q1 - 1.5 * (pq.q3 - pq.q1)) 
           OR t.purchase_amount > (pq.q3 + 1.5 * (pq.q3 - pq.q1))
           THEN 'OUTLIER'
           ELSE 'NORMAL'
       END as outlier_status
   FROM TICKETS t
   CROSS JOIN price_quartiles pq
   WHERE t.purchase_date >= DATEADD('day', -30, CURRENT_DATE())
   $$;
   ```

3. **Moving Average Anomaly Detection**
   ```sql
   -- Detect anomalies using moving averages
   WITH daily_guest_counts AS (
       SELECT 
           visit_date,
           park_id,
           COUNT(*) as daily_visitors,
           -- 7-day moving average
           AVG(COUNT(*)) OVER (
               PARTITION BY park_id 
               ORDER BY visit_date 
               ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
           ) as moving_avg_7day
       FROM GUESTS
       WHERE visit_date >= DATEADD('day', -60, CURRENT_DATE())
       GROUP BY visit_date, park_id
   )
   SELECT 
       visit_date,
       park_id,
       daily_visitors,
       moving_avg_7day,
       daily_visitors - moving_avg_7day as deviation,
       CASE 
           WHEN ABS(daily_visitors - moving_avg_7day) > (moving_avg_7day * 0.3)
           THEN 'ANOMALY'
           ELSE 'NORMAL'
       END as anomaly_flag
   FROM daily_guest_counts
   WHERE moving_avg_7day IS NOT NULL
   ORDER BY visit_date DESC, park_id;
   ```

#### **Exercise 2: Cross-Table Validation Rules (45 minutes)**

Implement complex validation across multiple related tables:

1. **Referential Integrity with Business Logic**
   ```sql
   -- Validate guest-ticket-visit relationships
   CREATE OR REPLACE VIEW CROSS_TABLE_VALIDATION AS
   WITH validation_checks AS (
       SELECT 
           'ORPHANED_TICKETS' as check_type,
           COUNT(*) as violation_count,
           'Tickets without corresponding guests' as description
       FROM TICKETS t
       LEFT JOIN GUESTS g ON t.guest_id = g.guest_id
       WHERE g.guest_id IS NULL
       
       UNION ALL
       
       SELECT 
           'FUTURE_VISIT_PURCHASES' as check_type,
           COUNT(*) as violation_count,
           'Tickets purchased after visit date' as description
       FROM TICKETS t
       JOIN GUESTS g ON t.guest_id = g.guest_id
       WHERE t.purchase_date > g.visit_date
       
       UNION ALL
       
       SELECT 
           'CAPACITY_VIOLATIONS' as check_type,
           COUNT(*) as violation_count,
           'Ride operations exceeding maximum capacity' as description
       FROM RIDE_OPERATIONS ro
       JOIN RIDES r ON ro.ride_id = r.ride_id
       WHERE ro.current_riders > r.max_capacity
   )
   SELECT 
       check_type,
       violation_count,
       description,
       CASE 
           WHEN violation_count = 0 THEN 'PASS'
           WHEN violation_count < 10 THEN 'WARNING'
           ELSE 'FAIL'
       END as status
   FROM validation_checks;
   ```

2. **Revenue Reconciliation Validation**
   ```sql
   -- Validate financial consistency across systems
   CREATE OR REPLACE PROCEDURE validate_revenue_reconciliation()
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
   DECLARE
       ticket_revenue FLOAT;
       reported_revenue FLOAT;
       variance_percentage FLOAT;
       result_message STRING;
   BEGIN
       -- Calculate revenue from ticket sales
       SELECT SUM(purchase_amount) INTO ticket_revenue
       FROM TICKETS
       WHERE purchase_date = CURRENT_DATE() - 1;
       
       -- Get reported revenue from financial system
       SELECT daily_revenue INTO reported_revenue
       FROM FINANCIAL_SUMMARY
       WHERE report_date = CURRENT_DATE() - 1;
       
       -- Calculate variance
       SET variance_percentage = ABS(ticket_revenue - reported_revenue) / NULLIF(reported_revenue, 0) * 100;
       
       -- Log validation result
       INSERT INTO DATA_QUALITY_RESULTS (
           table_name, check_type, check_name, status, metric_value, threshold_value
       )
       VALUES (
           'REVENUE_RECONCILIATION',
           'CROSS_TABLE',
           'DAILY_REVENUE_VARIANCE',
           CASE WHEN variance_percentage <= 2.0 THEN 'PASS' ELSE 'FAIL' END,
           variance_percentage,
           2.0
       );
       
       SET result_message = 'Revenue reconciliation completed. Variance: ' || ROUND(variance_percentage, 2) || '%';
       RETURN result_message;
   END;
   $$;
   ```

#### **Exercise 3: Pattern-Based Quality Detection (40 minutes)**

Identify suspicious patterns that indicate data quality issues:

1. **Duplicate Pattern Detection**
   ```sql
   -- Advanced duplicate detection with fuzzy matching
   CREATE OR REPLACE VIEW GUEST_DUPLICATE_ANALYSIS AS
   WITH potential_duplicates AS (
       SELECT 
           g1.guest_id as guest_id_1,
           g2.guest_id as guest_id_2,
           g1.first_name as name_1,
           g2.first_name as name_2,
           g1.email as email_1,
           g2.email as email_2,
           -- Levenshtein distance for name similarity
           EDITDISTANCE(UPPER(g1.first_name || g1.last_name), 
                       UPPER(g2.first_name || g2.last_name)) as name_distance,
           -- Email domain comparison
           SPLIT_PART(g1.email, '@', 2) as domain_1,
           SPLIT_PART(g2.email, '@', 2) as domain_2
       FROM GUESTS g1
       JOIN GUESTS g2 ON g1.guest_id < g2.guest_id
       WHERE (
           -- Exact email match
           g1.email = g2.email
           OR
           -- Similar names with same phone
           (EDITDISTANCE(UPPER(g1.first_name || g1.last_name), 
                        UPPER(g2.first_name || g2.last_name)) <= 2
            AND g1.phone = g2.phone)
           OR
           -- Same name, similar email
           (UPPER(g1.first_name) = UPPER(g2.first_name)
            AND UPPER(g1.last_name) = UPPER(g2.last_name)
            AND SPLIT_PART(g1.email, '@', 2) = SPLIT_PART(g2.email, '@', 2))
       )
   )
   SELECT 
       guest_id_1,
       guest_id_2,
       name_1,
       name_2,
       email_1,
       email_2,
       name_distance,
       CASE 
           WHEN email_1 = email_2 THEN 'EXACT_EMAIL_MATCH'
           WHEN domain_1 = domain_2 AND name_distance <= 2 THEN 'LIKELY_DUPLICATE'
           ELSE 'POSSIBLE_DUPLICATE'
       END as duplicate_confidence
   FROM potential_duplicates;
   ```

2. **Sequential Pattern Anomalies**
   ```sql
   -- Detect unusual sequences in time-series data
   WITH ride_sequence_analysis AS (
       SELECT 
           ride_id,
           operation_timestamp,
           wait_time_minutes,
           LAG(wait_time_minutes) OVER (PARTITION BY ride_id ORDER BY operation_timestamp) as prev_wait,
           LAG(operation_timestamp) OVER (PARTITION BY ride_id ORDER BY operation_timestamp) as prev_timestamp,
           -- Calculate rate of change
           (wait_time_minutes - LAG(wait_time_minutes) OVER (PARTITION BY ride_id ORDER BY operation_timestamp)) 
           / NULLIF(DATEDIFF('minute', LAG(operation_timestamp) OVER (PARTITION BY ride_id ORDER BY operation_timestamp), operation_timestamp), 0) 
           as wait_change_rate
       FROM RIDE_OPERATIONS
       WHERE operation_date >= DATEADD('day', -7, CURRENT_DATE())
   )
   SELECT 
       ride_id,
       operation_timestamp,
       wait_time_minutes,
       prev_wait,
       wait_change_rate,
       CASE 
           WHEN ABS(wait_change_rate) > 5 THEN 'EXTREME_CHANGE'
           WHEN ABS(wait_change_rate) > 2 THEN 'RAPID_CHANGE'
           ELSE 'NORMAL'
       END as change_classification
   FROM ride_sequence_analysis
   WHERE prev_wait IS NOT NULL
   AND ABS(wait_change_rate) > 1
   ORDER BY ABS(wait_change_rate) DESC;
   ```

#### **Exercise 4: Data Lineage and Impact Analysis (30 minutes)**

Track data flow and understand quality impact:

1. **Create Data Lineage Framework**
   ```sql
   -- Data lineage tracking table
   CREATE OR REPLACE TABLE DATA_LINEAGE (
       lineage_id STRING DEFAULT UUID_STRING(),
       source_table STRING NOT NULL,
       source_column STRING,
       target_table STRING NOT NULL,
       target_column STRING,
       transformation_type STRING NOT NULL, -- 'DIRECT', 'AGGREGATED', 'CALCULATED', 'DERIVED'
       transformation_logic STRING,
       dependency_level INTEGER,
       created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
   );
   
   -- Insert lineage relationships
   INSERT INTO DATA_LINEAGE (source_table, source_column, target_table, target_column, transformation_type, transformation_logic, dependency_level)
   VALUES 
   ('GUESTS', 'AGE', 'GUEST_DEMOGRAPHICS', 'AGE_GROUP', 'CALCULATED', 'CASE WHEN age < 18 THEN ''MINOR'' ELSE ''ADULT'' END', 1),
   ('TICKETS', 'PURCHASE_AMOUNT', 'DAILY_REVENUE_SUMMARY', 'TOTAL_REVENUE', 'AGGREGATED', 'SUM(purchase_amount)', 1),
   ('RIDE_OPERATIONS', 'WAIT_TIME_MINUTES', 'PARK_EFFICIENCY_METRICS', 'AVG_WAIT_TIME', 'AGGREGATED', 'AVG(wait_time_minutes)', 1);
   ```

2. **Quality Impact Propagation Analysis**
   ```sql
   -- Analyze how quality issues propagate through data lineage
   CREATE OR REPLACE VIEW QUALITY_IMPACT_ANALYSIS AS
   WITH quality_issues AS (
       SELECT DISTINCT table_name, column_name
       FROM DATA_QUALITY_RESULTS
       WHERE status = 'FAIL'
       AND check_timestamp >= DATEADD('day', -1, CURRENT_DATE())
   ),
   impacted_targets AS (
       SELECT 
           qi.table_name as source_with_issues,
           qi.column_name as source_column_with_issues,
           dl.target_table,
           dl.target_column,
           dl.transformation_type,
           dl.dependency_level
       FROM quality_issues qi
       JOIN DATA_LINEAGE dl ON qi.table_name = dl.source_table 
       AND (qi.column_name = dl.source_column OR dl.source_column IS NULL)
   )
   SELECT 
       source_with_issues,
       source_column_with_issues,
       target_table,
       target_column,
       transformation_type,
       dependency_level,
       CASE 
           WHEN dependency_level = 1 THEN 'DIRECT_IMPACT'
           WHEN dependency_level <= 3 THEN 'INDIRECT_IMPACT'
           ELSE 'DISTANT_IMPACT'
       END as impact_severity
   FROM impacted_targets
   ORDER BY dependency_level, target_table;
   ```

### 🔬 **Advanced Analytics Setup**

Prepare foundation for AI integration:

```sql
-- Create comprehensive quality metrics for AI training
CREATE OR REPLACE VIEW AI_TRAINING_METRICS AS
WITH comprehensive_metrics AS (
    SELECT 
        table_name,
        check_timestamp,
        -- Quality dimensions
        AVG(CASE WHEN check_type = 'COMPLETENESS' THEN metric_value END) as completeness_score,
        AVG(CASE WHEN check_type = 'ACCURACY' THEN metric_value END) as accuracy_score,
        AVG(CASE WHEN check_type = 'CONSISTENCY' THEN metric_value END) as consistency_score,
        AVG(CASE WHEN check_type = 'VALIDITY' THEN metric_value END) as validity_score,
        -- Statistical measures
        COUNT(CASE WHEN status = 'FAIL' THEN 1 END) as failed_checks,
        COUNT(*) as total_checks,
        -- Trend indicators
        LAG(AVG(metric_value)) OVER (PARTITION BY table_name ORDER BY check_timestamp) as previous_avg_score
    FROM DATA_QUALITY_RESULTS
    WHERE check_timestamp >= DATEADD('day', -90, CURRENT_DATE())
    GROUP BY table_name, check_timestamp
)
SELECT 
    *,
    -- Overall quality score
    (COALESCE(completeness_score, 100) + COALESCE(accuracy_score, 100) + 
     COALESCE(consistency_score, 100) + COALESCE(validity_score, 100)) / 4 as overall_quality_score,
    -- Trend calculation
    CASE 
        WHEN previous_avg_score IS NULL THEN 'NO_TREND'
        WHEN overall_quality_score > previous_avg_score THEN 'IMPROVING'
        WHEN overall_quality_score < previous_avg_score THEN 'DECLINING'
        ELSE 'STABLE'
    END as quality_trend
FROM comprehensive_metrics;
```

### 🎯 **Success Criteria**

By the end of this lab, you should have:

✅ **Implemented** statistical anomaly detection using Z-scores and IQR  
✅ **Created** cross-table validation rules for complex business logic  
✅ **Built** pattern recognition for duplicate and sequential anomalies  
✅ **Established** data lineage tracking and impact analysis  
✅ **Prepared** comprehensive metrics for AI training data  

### 📊 **Advanced Quality Metrics Dashboard**

```sql
-- Executive quality dashboard with advanced metrics
CREATE OR REPLACE VIEW ADVANCED_QUALITY_DASHBOARD AS
SELECT 
    'Statistical Outliers' as metric_category,
    COUNT(*) as metric_value,
    'High Priority' as priority_level
FROM RIDE_WAIT_OUTLIERS 
WHERE outlier_classification IN ('EXTREME_OUTLIER', 'MODERATE_OUTLIER')
AND operation_date >= CURRENT_DATE() - 1

UNION ALL

SELECT 
    'Cross-Table Violations',
    SUM(violation_count),
    CASE WHEN SUM(violation_count) > 50 THEN 'Critical' ELSE 'Medium' END
FROM CROSS_TABLE_VALIDATION
WHERE status = 'FAIL'

UNION ALL

SELECT 
    'Potential Duplicates',
    COUNT(*),
    'Medium Priority'
FROM GUEST_DUPLICATE_ANALYSIS
WHERE duplicate_confidence = 'LIKELY_DUPLICATE';
```

### 🚀 **Next Steps**

In **Lab 04: Basic Cortex AI Integration**, you'll learn:
- Introduction to Snowflake Cortex AI functions
- AI-powered data analysis and insights
- Automated anomaly explanation
- Natural language processing for data quality

### 📚 **Additional Resources**

- [Statistical Methods for Data Quality](link-to-resource)
- [Cross-Table Validation Best Practices](link-to-resource)
- [Data Lineage Implementation Guide](link-to-resource)

---

**Continue to Lab 04 to begin your journey into AI-powered data quality management!** 