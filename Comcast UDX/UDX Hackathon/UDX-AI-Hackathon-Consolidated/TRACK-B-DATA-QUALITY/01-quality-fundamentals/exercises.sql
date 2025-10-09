-- =====================================================================================
-- Lab 02: Data Quality Fundamentals - SQL Exercises
-- Building Foundation for AI-Powered Data Quality Management
-- =====================================================================================

-- =====================================================================================
-- EXERCISE 1: Data Profiling and Discovery
-- Goal: Understand the structure and quality characteristics of UDX theme park data
-- =====================================================================================

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
    
    UNION ALL
    
    SELECT 
        'RIDE_OPERATIONS' as table_name,
        'GUEST_SATISFACTION_SCORE' as column_name,
        COUNT(*) as total_records,
        COUNT(guest_satisfaction_score) as populated_records,
        COUNT(*) - COUNT(guest_satisfaction_score) as missing_records,
        ROUND((COUNT(guest_satisfaction_score) * 100.0 / COUNT(*)), 2) as completeness_percentage
    FROM RIDE_OPERATIONS
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

-- 1.3: Data Distribution Analysis
-- Analyze guest demographics distribution
SELECT 
    'Guest Age Distribution' as analysis_type,
    CASE 
        WHEN age BETWEEN 0 AND 12 THEN 'Child (0-12)'
        WHEN age BETWEEN 13 AND 17 THEN 'Teen (13-17)'
        WHEN age BETWEEN 18 AND 35 THEN 'Young Adult (18-35)'
        WHEN age BETWEEN 36 AND 55 THEN 'Adult (36-55)'
        WHEN age BETWEEN 56 AND 70 THEN 'Senior (56-70)'
        WHEN age > 70 THEN 'Elderly (70+)'
        ELSE 'Unknown'
    END as category,
    COUNT(*) as frequency,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM GUESTS
WHERE age IS NOT NULL
GROUP BY 
    CASE 
        WHEN age BETWEEN 0 AND 12 THEN 'Child (0-12)'
        WHEN age BETWEEN 13 AND 17 THEN 'Teen (13-17)'
        WHEN age BETWEEN 18 AND 35 THEN 'Young Adult (18-35)'
        WHEN age BETWEEN 36 AND 55 THEN 'Adult (36-55)'
        WHEN age BETWEEN 56 AND 70 THEN 'Senior (56-70)'
        WHEN age > 70 THEN 'Elderly (70+)'
        ELSE 'Unknown'
    END

UNION ALL

-- Analyze ride wait time distribution
SELECT 
    'Wait Time Distribution' as analysis_type,
    CASE 
        WHEN wait_time_minutes <= 15 THEN 'Short (≤15 min)'
        WHEN wait_time_minutes BETWEEN 16 AND 30 THEN 'Moderate (16-30 min)'
        WHEN wait_time_minutes BETWEEN 31 AND 60 THEN 'Long (31-60 min)'
        WHEN wait_time_minutes > 60 THEN 'Very Long (>60 min)'
        ELSE 'Unknown'
    END as category,
    COUNT(*) as frequency,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM RIDE_OPERATIONS
WHERE wait_time_minutes IS NOT NULL
GROUP BY 
    CASE 
        WHEN wait_time_minutes <= 15 THEN 'Short (≤15 min)'
        WHEN wait_time_minutes BETWEEN 16 AND 30 THEN 'Moderate (16-30 min)'
        WHEN wait_time_minutes BETWEEN 31 AND 60 THEN 'Long (31-60 min)'
        WHEN wait_time_minutes > 60 THEN 'Very Long (>60 min)'
        ELSE 'Unknown'
    END
ORDER BY analysis_type, frequency DESC;

-- =====================================================================================
-- EXERCISE 2: Basic Validation Rules Implementation
-- Goal: Create fundamental data quality validation checks
-- =====================================================================================

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

-- Test the completeness function
SELECT * FROM check_completeness('GUESTS', 'email', 90.0);
SELECT * FROM check_completeness('GUESTS', 'phone', 80.0);
SELECT * FROM check_completeness('RIDE_OPERATIONS', 'guest_satisfaction_score', 85.0);

-- 2.2: Format Validation Rules
-- Email format validation
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

-- Phone format validation (assuming US format)
CREATE OR REPLACE VIEW phone_format_validation AS
SELECT 
    guest_id,
    phone,
    CASE 
        WHEN phone IS NULL THEN 'MISSING'
        WHEN phone RLIKE '^\\+?1?[2-9]\\d{2}[2-9]\\d{2}\\d{4}$' THEN 'VALID'
        WHEN phone RLIKE '^\\(?[2-9]\\d{2}\\)?[\\s.-]?[2-9]\\d{2}[\\s.-]?\\d{4}$' THEN 'VALID_FORMATTED'
        ELSE 'INVALID'
    END as phone_format_status,
    CASE 
        WHEN phone IS NULL THEN 'Phone number is missing'
        WHEN phone RLIKE '^\\+?1?[2-9]\\d{2}[2-9]\\d{2}\\d{4}$' THEN 'Valid phone number'
        WHEN phone RLIKE '^\\(?[2-9]\\d{2}\\)?[\\s.-]?[2-9]\\d{2}[\\s.-]?\\d{4}$' THEN 'Valid phone number with formatting'
        ELSE 'Invalid phone number format'
    END as validation_message
FROM GUESTS;

-- 2.3: Business Rule Validation
-- Age validation for theme park guests
CREATE OR REPLACE VIEW age_validation AS
SELECT 
    guest_id,
    age,
    CASE 
        WHEN age IS NULL THEN 'MISSING'
        WHEN age < 0 THEN 'INVALID_NEGATIVE'
        WHEN age > 120 THEN 'INVALID_TOO_HIGH'
        WHEN age BETWEEN 0 AND 17 THEN 'MINOR'
        WHEN age BETWEEN 18 AND 64 THEN 'ADULT'
        WHEN age >= 65 THEN 'SENIOR'
        ELSE 'UNKNOWN'
    END as age_category,
    CASE 
        WHEN age IS NULL THEN 'Age is missing'
        WHEN age < 0 THEN 'Age cannot be negative'
        WHEN age > 120 THEN 'Age seems unrealistic (>120 years)'
        ELSE 'Valid age'
    END as validation_message,
    CASE 
        WHEN age IS NULL OR age < 0 OR age > 120 THEN 'FAIL'
        ELSE 'PASS'
    END as validation_status
FROM GUESTS;

-- Ride capacity validation
CREATE OR REPLACE VIEW ride_capacity_validation AS
SELECT 
    ro.operation_id,
    ro.ride_id,
    r.ride_name,
    r.max_capacity,
    ro.current_riders,
    CASE 
        WHEN ro.current_riders IS NULL THEN 'MISSING_DATA'
        WHEN ro.current_riders > r.max_capacity THEN 'OVER_CAPACITY'
        WHEN ro.current_riders < 0 THEN 'INVALID_NEGATIVE'
        WHEN ro.current_riders = 0 THEN 'EMPTY'
        ELSE 'VALID'
    END as capacity_status,
    CASE 
        WHEN ro.current_riders IS NULL THEN 'Current riders count is missing'
        WHEN ro.current_riders > r.max_capacity THEN 'Safety violation: Riders exceed maximum capacity'
        WHEN ro.current_riders < 0 THEN 'Invalid negative rider count'
        WHEN ro.current_riders = 0 THEN 'Ride is empty'
        ELSE 'Normal capacity'
    END as validation_message
FROM RIDE_OPERATIONS ro
JOIN RIDES r ON ro.ride_id = r.ride_id;

-- Date validation (ensure dates are realistic)
CREATE OR REPLACE VIEW date_validation AS
SELECT 
    'GUESTS' as table_name,
    guest_id as record_id,
    'VISIT_DATE' as date_field,
    visit_date as date_value,
    CASE 
        WHEN visit_date IS NULL THEN 'MISSING'
        WHEN visit_date > CURRENT_DATE() THEN 'FUTURE_DATE'
        WHEN visit_date < '2020-01-01' THEN 'TOO_OLD'
        ELSE 'VALID'
    END as date_status
FROM GUESTS

UNION ALL

SELECT 
    'RIDE_OPERATIONS' as table_name,
    operation_id as record_id,
    'OPERATION_DATE' as date_field,
    operation_date as date_value,
    CASE 
        WHEN operation_date IS NULL THEN 'MISSING'
        WHEN operation_date > CURRENT_DATE() THEN 'FUTURE_DATE'
        WHEN operation_date < '2020-01-01' THEN 'TOO_OLD'
        ELSE 'VALID'
    END as date_status
FROM RIDE_OPERATIONS;

-- =====================================================================================
-- EXERCISE 3: Data Quality Metrics Framework
-- Goal: Build comprehensive quality measurement and scoring system
-- =====================================================================================

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
    
    -- Format validation checks
    INSERT INTO DATA_QUALITY_RESULTS 
    (table_name, column_name, check_type, check_name, status, metric_value, threshold_value, records_checked, failed_records, business_impact, severity_level)
    SELECT 
        'GUESTS' as table_name,
        'EMAIL' as column_name,
        'VALIDITY' as check_type,
        'EMAIL_FORMAT_VALIDATION' as check_name,
        CASE WHEN valid_pct >= 95 THEN 'PASS' ELSE 'FAIL' END as status,
        valid_pct as metric_value,
        95.0 as threshold_value,
        total_emails,
        invalid_emails,
        'Invalid email formats prevent successful communication' as business_impact,
        'HIGH' as severity_level
    FROM (
        SELECT 
            COUNT(*) as total_emails,
            COUNT(CASE WHEN email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' THEN 1 END) as valid_emails,
            COUNT(*) - COUNT(CASE WHEN email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' THEN 1 END) as invalid_emails,
            ROUND((COUNT(CASE WHEN email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' THEN 1 END) * 100.0 / COUNT(*)), 2) as valid_pct
        FROM GUESTS
        WHERE email IS NOT NULL
    );
    
    -- Business rule validation
    INSERT INTO DATA_QUALITY_RESULTS 
    (table_name, column_name, check_type, check_name, status, metric_value, threshold_value, records_checked, failed_records, business_impact, severity_level)
    SELECT 
        'RIDE_OPERATIONS' as table_name,
        'CURRENT_RIDERS' as column_name,
        'BUSINESS_RULE' as check_type,
        'RIDE_CAPACITY_COMPLIANCE' as check_name,
        CASE WHEN compliance_pct >= 100 THEN 'PASS' ELSE 'FAIL' END as status,
        compliance_pct as metric_value,
        100.0 as threshold_value,
        total_operations,
        violations,
        'Capacity violations pose serious safety risks' as business_impact,
        'CRITICAL' as severity_level
    FROM (
        SELECT 
            COUNT(*) as total_operations,
            COUNT(CASE WHEN ro.current_riders > r.max_capacity THEN 1 END) as violations,
            ROUND(((COUNT(*) - COUNT(CASE WHEN ro.current_riders > r.max_capacity THEN 1 END)) * 100.0 / COUNT(*)), 2) as compliance_pct
        FROM RIDE_OPERATIONS ro
        JOIN RIDES r ON ro.ride_id = r.ride_id
        WHERE ro.current_riders IS NOT NULL
    );
    
    -- Calculate summary statistics
    SELECT COUNT(*) INTO total_checks FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE();
    SELECT COUNT(*) INTO passed_checks FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE() AND status = 'PASS';
    SET failed_checks = total_checks - passed_checks;
    
    RETURN 'Quality assessment completed. Total checks: ' || total_checks || ', Passed: ' || passed_checks || ', Failed: ' || failed_checks;
END;
$$;

-- 3.3: Quality scorecard view
CREATE OR REPLACE VIEW QUALITY_SCORECARD AS
WITH quality_metrics AS (
    SELECT 
        table_name,
        check_type,
        COUNT(*) as total_checks,
        COUNT(CASE WHEN status = 'PASS' THEN 1 END) as passed_checks,
        AVG(metric_value) as avg_metric_value,
        MIN(metric_value) as min_metric_value,
        MAX(metric_value) as max_metric_value
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
    ROUND(min_metric_value, 2) as min_score,
    ROUND(max_metric_value, 2) as max_score,
    CASE 
        WHEN (passed_checks * 100.0 / total_checks) >= 95 THEN 'EXCELLENT'
        WHEN (passed_checks * 100.0 / total_checks) >= 85 THEN 'GOOD'
        WHEN (passed_checks * 100.0 / total_checks) >= 70 THEN 'FAIR'
        ELSE 'POOR'
    END as quality_grade,
    CASE 
        WHEN (passed_checks * 100.0 / total_checks) < 70 THEN 'Immediate attention required'
        WHEN (passed_checks * 100.0 / total_checks) < 85 THEN 'Improvement needed'
        ELSE 'Maintain current standards'
    END as recommendation
FROM quality_metrics
ORDER BY pass_rate ASC;

-- =====================================================================================
-- EXERCISE 4: Automated Quality Monitoring
-- Goal: Set up automated monitoring, alerting, and trend analysis
-- =====================================================================================

-- 4.1: Quality trend analysis
CREATE OR REPLACE VIEW QUALITY_TRENDS AS
WITH daily_quality AS (
    SELECT 
        check_timestamp::DATE as check_date,
        table_name,
        AVG(metric_value) as daily_avg_score,
        COUNT(CASE WHEN status = 'PASS' THEN 1 END) * 100.0 / COUNT(*) as daily_pass_rate
    FROM DATA_QUALITY_RESULTS
    WHERE check_timestamp >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY check_timestamp::DATE, table_name
),
trend_calculation AS (
    SELECT 
        *,
        LAG(daily_avg_score) OVER (PARTITION BY table_name ORDER BY check_date) as prev_avg_score,
        LAG(daily_pass_rate) OVER (PARTITION BY table_name ORDER BY check_date) as prev_pass_rate
    FROM daily_quality
)
SELECT 
    check_date,
    table_name,
    daily_avg_score,
    daily_pass_rate,
    CASE 
        WHEN prev_avg_score IS NULL THEN 'NO_TREND'
        WHEN daily_avg_score > prev_avg_score THEN 'IMPROVING'
        WHEN daily_avg_score < prev_avg_score THEN 'DECLINING'
        ELSE 'STABLE'
    END as score_trend,
    CASE 
        WHEN prev_pass_rate IS NULL THEN 'NO_TREND'
        WHEN daily_pass_rate > prev_pass_rate THEN 'IMPROVING'
        WHEN daily_pass_rate < prev_pass_rate THEN 'DECLINING'
        ELSE 'STABLE'
    END as pass_rate_trend,
    ROUND(daily_avg_score - COALESCE(prev_avg_score, daily_avg_score), 2) as score_change,
    ROUND(daily_pass_rate - COALESCE(prev_pass_rate, daily_pass_rate), 2) as pass_rate_change
FROM trend_calculation
ORDER BY check_date DESC, table_name;

-- 4.2: Alert generation system
CREATE OR REPLACE VIEW QUALITY_ALERTS AS
WITH current_issues AS (
    SELECT 
        result_id,
        table_name,
        check_name,
        status,
        metric_value,
        threshold_value,
        check_timestamp,
        business_impact,
        severity_level
    FROM DATA_QUALITY_RESULTS
    WHERE status = 'FAIL'
    AND check_timestamp >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
),
alert_prioritization AS (
    SELECT 
        *,
        CASE 
            WHEN severity_level = 'CRITICAL' THEN 1
            WHEN severity_level = 'HIGH' THEN 2
            WHEN severity_level = 'MEDIUM' THEN 3
            ELSE 4
        END as priority_order,
        CASE 
            WHEN metric_value < (threshold_value * 0.5) THEN 'CRITICAL'
            WHEN metric_value < (threshold_value * 0.8) THEN 'WARNING'
            ELSE 'INFO'
        END as alert_level
    FROM current_issues
)
SELECT 
    result_id,
    table_name,
    check_name,
    alert_level,
    severity_level,
    metric_value,
    threshold_value,
    business_impact,
    CONCAT(
        'ALERT: ', check_name, ' failed. ',
        'Current value: ', metric_value, ', ',
        'Threshold: ', threshold_value, '. ',
        'Impact: ', business_impact
    ) as alert_message,
    check_timestamp,
    CASE 
        WHEN alert_level = 'CRITICAL' THEN 'operations_manager@udx.com'
        WHEN alert_level = 'WARNING' THEN 'data_team@udx.com'
        ELSE 'analysts@udx.com'
    END as notification_target
FROM alert_prioritization
ORDER BY priority_order, check_timestamp DESC;

-- 4.3: Automated scheduling setup
CREATE OR REPLACE TASK daily_quality_assessment_task
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON 0 8 * * * UTC'  -- Every day at 8 AM UTC
AS
CALL run_comprehensive_quality_assessment();

-- Enable the task (commented out for safety)
-- ALTER TASK daily_quality_assessment_task RESUME;

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

-- =====================================================================================
-- EXERCISE 5: Test and Validation
-- Goal: Execute all quality checks and validate the framework
-- =====================================================================================

-- Execute the comprehensive quality assessment
CALL run_comprehensive_quality_assessment();

-- View the results
SELECT * FROM QUALITY_SCORECARD;
SELECT * FROM QUALITY_DASHBOARD_SUMMARY;
SELECT * FROM QUALITY_ALERTS;
SELECT * FROM QUALITY_TRENDS WHERE check_date >= CURRENT_DATE() - 7;

-- Specific validation checks
SELECT 'Email Format Issues' as check_type, COUNT(*) as issue_count
FROM email_format_validation 
WHERE email_format_status = 'INVALID'

UNION ALL

SELECT 'Age Validation Issues' as check_type, COUNT(*) as issue_count
FROM age_validation 
WHERE validation_status = 'FAIL'

UNION ALL

SELECT 'Capacity Violations' as check_type, COUNT(*) as issue_count
FROM ride_capacity_validation 
WHERE capacity_status = 'OVER_CAPACITY'

UNION ALL

SELECT 'Date Issues' as check_type, COUNT(*) as issue_count
FROM date_validation 
WHERE date_status IN ('FUTURE_DATE', 'TOO_OLD');

-- =====================================================================================
-- SUMMARY REPORT
-- =====================================================================================

-- Generate a comprehensive summary report
SELECT 
    'Data Quality Fundamentals Assessment Summary' as report_title,
    CURRENT_TIMESTAMP() as generated_at,
    (SELECT COUNT(*) FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE()) as total_checks_run,
    (SELECT COUNT(*) FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE() AND status = 'PASS') as checks_passed,
    (SELECT COUNT(*) FROM QUALITY_ALERTS) as active_alerts,
    (SELECT AVG(avg_quality_score) FROM QUALITY_DASHBOARD_SUMMARY WHERE table_name != 'OVERALL') as overall_quality_score;

-- =====================================================================================
-- END OF LAB 02 EXERCISES
-- Next: Continue to Lab 03 for Advanced Data Validation techniques
-- ===================================================================================== 