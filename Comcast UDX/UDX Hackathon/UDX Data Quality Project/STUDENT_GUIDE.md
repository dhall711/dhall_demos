# UDX AI-Powered Data Quality Hackathon
## Student Guide

---

**Welcome to the Future of Data Quality Management!**

This comprehensive guide will walk you through building an **autonomous, AI-powered data quality system** using Snowflake's latest technologies including **Agents**, **Intelligence**, **Semantic Models**, and **Multimodal AI**.

---

## 📋 **Quick Start Checklist**

Before beginning, ensure you have:

- [ ] Access to Snowflake account with Cortex AI enabled
- [ ] Sufficient compute credits for AI operations
- [ ] UDX sample data loaded (completed in Lab 01)
- [ ] Basic SQL knowledge
- [ ] This student guide open for reference

---

## 🏗️ **Lab Structure Overview**

| Phase | Labs | Focus | Duration |
|-------|------|-------|----------|
| **Foundation** | 01-03 | Data Quality Infrastructure | 2 hours |
| **AI Intelligence** | 04-06 | Semantic Models & Conversational AI | 2 hours |
| **Autonomous Operations** | 07-08 | AI Agents & Orchestration | 2 hours |
| **Advanced AI** | 09-10 | Multimodal AI & Integration | 2 hours |

---

# Lab 02: Data Quality Fundamentals
## Step-by-Step Instructions

### **⏱️ Estimated Time: 45 minutes**

### **🎯 Lab Objectives**
By the end of this lab, you will:
- Understand the six dimensions of data quality
- Implement basic validation rules using SQL
- Create automated quality monitoring systems
- Build foundation for AI-powered analysis

---

## **Exercise 1: Data Profiling and Discovery (15 minutes)**

### **Step 1.1: Open Snowflake Snowsight**

1. **Navigate to your Snowflake account**
   - Open your web browser
   - Go to your Snowflake URL: `https://<account>.snowflakecomputing.com`
   - Log in with your credentials

2. **Access Snowsight Interface**
   - Click on **"Snowsight"** in the top navigation
   - Ensure you're in the correct **Warehouse** and **Database**

   > 📸 **Screenshot Placeholder: Snowsight Homepage**
   > *Show the main Snowsight interface with navigation menu*

### **Step 1.2: Basic Data Volume Analysis**

1. **Create a new worksheet**
   - Click **"+ Worksheet"** in Snowsight
   - Name it: `Lab02_Data_Profiling`

   > 📸 **Screenshot Placeholder: New Worksheet Creation**
   > *Show the new worksheet dialog and naming*

2. **Run the data volume query**
   
   Copy and paste this SQL into your worksheet:

   ```sql
   -- 1.1: Basic Data Volume and Structure Analysis
   SELECT 
       'PARKS' as table_name,
       COUNT(*) as row_count,
       COUNT(DISTINCT park_id) as unique_parks,
       MAX(created_date) as latest_record,
       MIN(created_date) as earliest_record
   FROM PARKS

   UNION ALL

   SELECT 
       'GUESTS' as table_name,
       COUNT(*) as row_count,
       COUNT(DISTINCT guest_id) as unique_guests,
       MAX(visit_date) as latest_record,
       MIN(visit_date) as earliest_record
   FROM GUESTS

   UNION ALL

   SELECT 
       'RIDES' as table_name,
       COUNT(*) as row_count,
       COUNT(DISTINCT ride_id) as unique_rides,
       MAX(last_inspection_date) as latest_record,
       MIN(last_inspection_date) as earliest_record
   FROM RIDES

   UNION ALL

   SELECT 
       'RIDE_OPERATIONS' as table_name,
       COUNT(*) as row_count,
       COUNT(DISTINCT operation_id) as unique_operations,
       MAX(operation_date) as latest_record,
       MIN(operation_date) as earliest_record
   FROM RIDE_OPERATIONS

   UNION ALL

   SELECT 
       'TICKETS' as table_name,
       COUNT(*) as row_count,
       COUNT(DISTINCT ticket_id) as unique_tickets,
       MAX(purchase_date) as latest_record,
       MIN(purchase_date) as earliest_record
   FROM TICKETS;
   ```

3. **Execute the query**
   - Click the **"Run"** button (▶️) or press `Ctrl+Enter`
   - Review the results in the output panel

   > 📸 **Screenshot Placeholder: Query Results**
   > *Show the table volume analysis results with row counts*

### **Step 1.3: Completeness Analysis**

1. **Add completeness analysis query**
   
   In the same worksheet, add this query:

   ```sql
   -- 1.2: Completeness Analysis Across All Tables
   WITH completeness_analysis AS (
       SELECT 
           'GUESTS' as table_name,
           'EMAIL' as column_name,
           COUNT(*) as total_records,
           COUNT(email) as populated_records,
           COUNT(*) - COUNT(email) as missing_records,
           ROUND((COUNT(email) * 100.0 / COUNT(*)), 2) as completeness_percentage
       FROM GUESTS
       
       UNION ALL
       
       SELECT 
           'GUESTS' as table_name,
           'PHONE' as column_name,
           COUNT(*) as total_records,
           COUNT(phone) as populated_records,
           COUNT(*) - COUNT(phone) as missing_records,
           ROUND((COUNT(phone) * 100.0 / COUNT(*)), 2) as completeness_percentage
       FROM GUESTS
       
       UNION ALL
       
       SELECT 
           'RIDES' as table_name,
           'SAFETY_RATING' as column_name,
           COUNT(*) as total_records,
           COUNT(safety_rating) as populated_records,
           COUNT(*) - COUNT(safety_rating) as missing_records,
           ROUND((COUNT(safety_rating) * 100.0 / COUNT(*)), 2) as completeness_percentage
       FROM RIDES
   )
   SELECT 
       table_name,
       column_name,
       total_records,
       populated_records,
       missing_records,
       completeness_percentage,
       CASE 
           WHEN completeness_percentage >= 95 THEN 'EXCELLENT'
           WHEN completeness_percentage >= 85 THEN 'GOOD'
           WHEN completeness_percentage >= 70 THEN 'ACCEPTABLE'
           ELSE 'POOR'
       END as completeness_grade
   FROM completeness_analysis
   ORDER BY completeness_percentage ASC;
   ```

2. **Execute and analyze results**
   - Run the query
   - Note which columns have poor completeness
   - Identify data quality issues

   > 📸 **Screenshot Placeholder: Completeness Analysis Results**
   > *Show completeness percentages and grades for different columns*

### **💡 Key Observations to Note:**
- Which tables have the most/least data?
- What completeness issues do you see?
- How might these impact business operations?

---

## **Exercise 2: Creating Validation Rules (15 minutes)**

### **Step 2.1: Create Reusable Functions**

1. **Create a new worksheet section**
   - Add a comment header in your worksheet:
   ```sql
   -- =====================================================
   -- EXERCISE 2: VALIDATION RULES
   -- =====================================================
   ```

2. **Create completeness check function**
   
   ```sql
   -- 2.1: Create Reusable Completeness Check Function
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
       missing_records INTEGER,
       recommendation STRING
   )
   LANGUAGE SQL
   AS
   $$
       SELECT 
           table_name || '.' || column_name as check_name,
           CASE 
               WHEN completeness_pct >= threshold THEN 'PASS'
               ELSE 'FAIL'
           END as status,
           completeness_pct as completeness_percentage,
           threshold as threshold_value,
           total_records as records_checked,
           total_records - populated_records as missing_records,
           CASE 
               WHEN completeness_pct >= threshold THEN 'No action required'
               WHEN completeness_pct >= 80 THEN 'Review data collection process'
               ELSE 'Immediate investigation required'
           END as recommendation
       FROM (
           SELECT 
               COUNT(*) as total_records,
               COUNT(CASE WHEN column_name IS NOT NULL THEN 1 END) as populated_records,
               ROUND((COUNT(CASE WHEN column_name IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)), 2) as completeness_pct
           FROM IDENTIFIER(table_name)
       )
   $$;
   ```

   > 📸 **Screenshot Placeholder: Function Creation**
   > *Show successful function creation message*

### **Step 2.2: Test the Function**

1. **Test completeness function**
   ```sql
   -- Test the completeness function
   SELECT * FROM check_completeness('GUESTS', 'email', 90.0);
   SELECT * FROM check_completeness('GUESTS', 'phone', 80.0);
   SELECT * FROM check_completeness('RIDE_OPERATIONS', 'guest_satisfaction_score', 85.0);
   ```

2. **Review results**
   - Note which checks pass or fail
   - Read the recommendations

   > 📸 **Screenshot Placeholder: Function Test Results**
   > *Show the function results with pass/fail status and recommendations*

### **Step 2.3: Format Validation Views**

1. **Create email format validation**
   ```sql
   -- 2.2: Email format validation
   CREATE OR REPLACE VIEW email_format_validation AS
   SELECT 
       guest_id,
       email,
       CASE 
           WHEN email IS NULL THEN 'MISSING'
           WHEN email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' THEN 'VALID'
           ELSE 'INVALID'
       END as email_format_status,
       CASE 
           WHEN email IS NULL THEN 'Email address is missing'
           WHEN email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' THEN 'Valid email format'
           ELSE 'Invalid email format - does not match standard pattern'
       END as validation_message
   FROM GUESTS;
   ```

2. **Test the validation view**
   ```sql
   -- Check email validation results
   SELECT 
       email_format_status,
       COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
   FROM email_format_validation
   GROUP BY email_format_status
   ORDER BY count DESC;
   ```

   > 📸 **Screenshot Placeholder: Email Validation Results**
   > *Show distribution of valid/invalid/missing emails*

---

## **Exercise 3: Quality Metrics Framework (10 minutes)**

### **Step 3.1: Create Quality Results Table**

1. **Create the main quality tracking table**
   ```sql
   -- 3.1: Create comprehensive data quality results table
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
       business_impact STRING,
       severity_level STRING DEFAULT 'MEDIUM',
       created_by STRING DEFAULT CURRENT_USER()
   );
   ```

   > 📸 **Screenshot Placeholder: Table Creation Success**
   > *Show successful table creation message*

### **Step 3.2: Create Assessment Procedure**

1. **Create automated quality assessment**
   ```sql
   -- 3.2: Comprehensive quality assessment procedure
   CREATE OR REPLACE PROCEDURE run_comprehensive_quality_assessment()
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
   DECLARE
       total_checks INTEGER DEFAULT 0;
       passed_checks INTEGER DEFAULT 0;
       failed_checks INTEGER DEFAULT 0;
   BEGIN
       -- Clear previous results for today
       DELETE FROM DATA_QUALITY_RESULTS 
       WHERE check_timestamp::DATE = CURRENT_DATE();
       
       -- Completeness checks
       INSERT INTO DATA_QUALITY_RESULTS 
       (table_name, column_name, check_type, check_name, status, metric_value, threshold_value, records_checked, failed_records, business_impact, severity_level)
       SELECT 
           'GUESTS' as table_name,
           'EMAIL' as column_name,
           'COMPLETENESS' as check_type,
           'GUEST_EMAIL_COMPLETENESS' as check_name,
           CASE WHEN completeness_pct >= 90 THEN 'PASS' ELSE 'FAIL' END as status,
           completeness_pct as metric_value,
           90.0 as threshold_value,
           total_records,
           total_records - populated_records as failed_records,
           'Missing guest emails affect marketing and communication' as business_impact,
           CASE WHEN completeness_pct < 70 THEN 'HIGH' ELSE 'MEDIUM' END as severity_level
       FROM (
           SELECT 
               COUNT(*) as total_records,
               COUNT(email) as populated_records,
               ROUND((COUNT(email) * 100.0 / COUNT(*)), 2) as completeness_pct
           FROM GUESTS
       );
       
       -- Calculate summary statistics
       SELECT COUNT(*) INTO total_checks FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE();
       SELECT COUNT(*) INTO passed_checks FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE() AND status = 'PASS';
       SET failed_checks = total_checks - passed_checks;
       
       RETURN 'Quality assessment completed. Total checks: ' || total_checks || ', Passed: ' || passed_checks || ', Failed: ' || failed_checks;
   END;
   $$;
   ```

### **Step 3.3: Execute and View Results**

1. **Run the quality assessment**
   ```sql
   -- Execute the comprehensive quality assessment
   CALL run_comprehensive_quality_assessment();
   ```

   > 📸 **Screenshot Placeholder: Procedure Execution**
   > *Show the procedure execution results with summary statistics*

2. **View the quality results**
   ```sql
   -- View the results
   SELECT * FROM DATA_QUALITY_RESULTS 
   ORDER BY check_timestamp DESC;
   ```

   > 📸 **Screenshot Placeholder: Quality Results Table**
   > *Show the populated quality results with various checks and their status*

---

## **Exercise 4: Quality Dashboard Creation (5 minutes)**

### **Step 4.1: Create Quality Dashboard View**

1. **Create comprehensive dashboard**
   ```sql
   -- 4.4: Quality dashboard summary
   CREATE OR REPLACE VIEW QUALITY_DASHBOARD_SUMMARY AS
   WITH latest_results AS (
       SELECT 
           table_name,
           COUNT(*) as total_checks,
           COUNT(CASE WHEN status = 'PASS' THEN 1 END) as passed_checks,
           COUNT(CASE WHEN severity_level = 'CRITICAL' THEN 1 END) as critical_issues,
           AVG(metric_value) as avg_quality_score
       FROM DATA_QUALITY_RESULTS
       WHERE check_timestamp::DATE = CURRENT_DATE()
       GROUP BY table_name
   ),
   overall_summary AS (
       SELECT 
           'OVERALL' as table_name,
           SUM(total_checks) as total_checks,
           SUM(passed_checks) as passed_checks,
           SUM(critical_issues) as critical_issues,
           AVG(avg_quality_score) as avg_quality_score
       FROM latest_results
   )
   SELECT 
       table_name,
       total_checks,
       passed_checks,
       total_checks - passed_checks as failed_checks,
       ROUND((passed_checks * 100.0 / total_checks), 1) as pass_rate_percent,
       critical_issues,
       ROUND(avg_quality_score, 1) as avg_quality_score,
       CASE 
           WHEN critical_issues > 0 THEN 'CRITICAL'
           WHEN (passed_checks * 100.0 / total_checks) < 85 THEN 'WARNING'
           ELSE 'HEALTHY'
       END as overall_status
   FROM latest_results

   UNION ALL

   SELECT * FROM overall_summary
   ORDER BY table_name;
   ```

2. **View your dashboard**
   ```sql
   SELECT * FROM QUALITY_DASHBOARD_SUMMARY;
   ```

   > 📸 **Screenshot Placeholder: Quality Dashboard**
   > *Show the dashboard summary with pass rates and overall status*

---

## **🎯 Lab 02 Checkpoint**

### **What You've Accomplished:**
- [x] Analyzed data volume and completeness across all tables
- [x] Created reusable validation functions
- [x] Implemented format validation rules
- [x] Built a comprehensive quality metrics framework
- [x] Created automated quality assessment procedures
- [x] Developed a quality monitoring dashboard

### **Key Takeaways:**
1. **Data Quality Dimensions**: Understanding completeness, validity, and consistency
2. **Automation**: Building reusable functions and procedures
3. **Business Context**: Connecting quality metrics to business impact
4. **Monitoring**: Creating dashboards for ongoing oversight

### **Prepare for Lab 03:**
Your quality foundation is now ready for advanced statistical analysis and AI integration!

---

## **🔍 Troubleshooting Common Issues**

### **Issue: "Object does not exist" errors**
**Solution:** 
- Ensure you're in the correct database and schema
- Check your warehouse is running
- Verify table names match exactly

### **Issue: Function creation fails**
**Solution:**
- Check SQL syntax carefully
- Ensure you have CREATE FUNCTION privileges
- Try running parts of the function separately first

### **Issue: No data in results**
**Solution:**
- Verify sample data was loaded in Lab 01
- Check table names and column names
- Use `SELECT * FROM table_name LIMIT 10` to verify data exists

---

## **📚 Additional Resources**

- **Snowflake Documentation**: [Cortex AI Functions](https://docs.snowflake.com/en/sql-reference/functions-ai)
- **SQL Reference**: [Data Quality Patterns](https://docs.snowflake.com/en/sql-reference)
- **Best Practices**: [Data Quality Implementation](https://docs.snowflake.com/en/user-guide/data-quality)

---

**🎉 Congratulations! You've completed Lab 02 and built a solid foundation for AI-powered data quality management.**

**Next**: Continue to **Lab 03: Advanced Data Validation** to learn statistical anomaly detection and cross-table validation techniques.

--- 