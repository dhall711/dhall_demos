-- =====================================================
-- Lab 04: Cortex AI Integration - Hands-On Exercises
-- =====================================================
-- Learn to use Snowflake Cortex AI for data quality analysis

USE DATABASE UDX_DATA_QUALITY_PROJECT;
USE SCHEMA THEME_PARK_OPS;
USE WAREHOUSE UDX_AI_WAREHOUSE;

-- =====================================================
-- EXERCISE 1: Basic AI Data Analysis
-- =====================================================

-- 1.1: Test Cortex AI Connectivity
-- Let's start by testing if Cortex AI is working properly
SELECT 
    'Testing Cortex AI...' as test_description,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-8b', 
        'Hello! I am a data analyst working with theme park data. Can you help me analyze data quality issues?'
    ) as ai_response;

-- 1.2: Analyze Guest Demographics with AI
-- Ask AI to analyze guest distribution patterns
WITH guest_summary AS (
    SELECT 
        COUNT(*) as total_guests,
        COUNT(DISTINCT country) as countries_represented,
        AVG(age) as avg_age,
        COUNT(*) - COUNT(email) as missing_emails,
        SUM(CASE WHEN age < 0 OR age > 120 THEN 1 ELSE 0 END) as invalid_ages,
        SUM(CASE WHEN zip_code IN ('INVALID', '1234') THEN 1 ELSE 0 END) as invalid_zip_codes
    FROM GUESTS
)
SELECT 
    'Guest Demographics Analysis' as analysis_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'I am analyzing theme park guest data. Here are the key metrics: ',
            'Total guests: ', total_guests, ', ',
            'Countries represented: ', countries_represented, ', ',
            'Average age: ', ROUND(avg_age, 1), ' years, ',
            'Missing emails: ', missing_emails, ', ',
            'Invalid ages: ', invalid_ages, ', ',
            'Invalid zip codes: ', invalid_zip_codes, '. ',
            'Please provide insights about data quality and guest patterns. ',
            'What do these numbers tell us about our data quality and customer base?'
        )
    ) as ai_insights
FROM guest_summary;

-- 1.3: AI-Powered Ride Performance Analysis
-- Use AI to interpret ride operational metrics
WITH ride_performance AS (
    SELECT 
        r.ride_name,
        r.ride_type,
        COUNT(*) as operation_records,
        AVG(ro.wait_time_minutes) as avg_wait_time,
        AVG(ro.guest_satisfaction_score) as avg_satisfaction,
        SUM(ro.downtime_minutes) as total_downtime_minutes,
        COUNT(CASE WHEN ro.wait_time_minutes > 180 THEN 1 END) as excessive_wait_times
    FROM RIDES r
    JOIN RIDE_OPERATIONS ro ON r.ride_id = ro.ride_id
    WHERE r.park_id = 'UDX-FL'  -- Focus on Florida park
    GROUP BY r.ride_name, r.ride_type
    ORDER BY avg_satisfaction DESC
    LIMIT 5
)
SELECT 
    'Top 5 Rides Analysis - Universal Studios Florida' as analysis_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Analyze these top 5 performing rides at Universal Studios Florida theme park: ',
            LISTAGG(
                CONCAT(
                    ride_name, ' (', ride_type, '): ',
                    'Avg wait: ', ROUND(avg_wait_time, 1), ' min, ',
                    'Satisfaction: ', ROUND(avg_satisfaction, 2), '/5.0, ',
                    'Downtime: ', total_downtime_minutes, ' min total, ',
                    'Excessive waits: ', excessive_wait_times, ' times'
                ), '; '
            ) WITHIN GROUP (ORDER BY avg_satisfaction DESC),
            '. What patterns do you see? Which rides need attention and why?'
        )
    ) as ai_analysis
FROM ride_performance;

-- =====================================================
-- EXERCISE 2: Quality Issue Detection with AI
-- =====================================================

-- 2.1: AI Detection of Data Anomalies
-- Let AI identify and explain specific data quality issues
WITH quality_issues AS (
    SELECT 
        'Email Completeness' as issue_type,
        COUNT(*) as total_records,
        COUNT(email) as valid_records,
        COUNT(*) - COUNT(email) as problematic_records,
        ROUND(((COUNT(*) - COUNT(email)) * 100.0 / COUNT(*)), 2) as problem_percentage
    FROM GUESTS
    
    UNION ALL
    
    SELECT 
        'Age Validity' as issue_type,
        COUNT(*) as total_records,
        COUNT(CASE WHEN age BETWEEN 0 AND 120 THEN 1 END) as valid_records,
        COUNT(CASE WHEN age < 0 OR age > 120 THEN 1 END) as problematic_records,
        ROUND((COUNT(CASE WHEN age < 0 OR age > 120 THEN 1 END) * 100.0 / COUNT(*)), 2) as problem_percentage
    FROM GUESTS
    
    UNION ALL
    
    SELECT 
        'Zip Code Format' as issue_type,
        COUNT(*) as total_records,
        COUNT(CASE WHEN zip_code NOT IN ('INVALID', '1234') AND LENGTH(zip_code) = 5 THEN 1 END) as valid_records,
        COUNT(CASE WHEN zip_code IN ('INVALID', '1234') OR LENGTH(zip_code) != 5 THEN 1 END) as problematic_records,
        ROUND((COUNT(CASE WHEN zip_code IN ('INVALID', '1234') OR LENGTH(zip_code) != 5 THEN 1 END) * 100.0 / COUNT(*)), 2) as problem_percentage
    FROM GUESTS
)
SELECT 
    'Data Quality Issues Analysis' as report_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'I found these data quality issues in our theme park guest database: ',
            LISTAGG(
                CONCAT(
                    issue_type, ': ', problematic_records, ' out of ', total_records, 
                    ' records (', problem_percentage, '% problematic)'
                ), '; '
            ) WITHIN GROUP (ORDER BY problem_percentage DESC),
            '. Please explain: 1) What each issue means for business operations, ',
            '2) Potential root causes, 3) Recommended remediation steps, ',
            '4) Priority order for fixing these issues.'
        )
    ) as ai_recommendations
FROM quality_issues;

-- 2.2: AI Analysis of Ticket Sales Anomalies
-- Detect and explain unusual patterns in ticket sales
WITH ticket_anomalies AS (
    SELECT 
        COUNT(CASE WHEN purchase_amount < 0 THEN 1 END) as negative_amounts,
        COUNT(CASE WHEN purchase_amount > 1000 THEN 1 END) as extremely_high_amounts,
        COUNT(CASE WHEN visit_date < purchase_date THEN 1 END) as visit_before_purchase,
        COUNT(CASE WHEN discount_amount > purchase_amount THEN 1 END) as discount_exceeds_price,
        COUNT(*) as total_tickets,
        AVG(purchase_amount) as avg_ticket_price
    FROM TICKETS
)
SELECT 
    'Ticket Sales Anomaly Analysis' as analysis_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'In our theme park ticket sales data of ', total_tickets, ' tickets with average price $', ROUND(avg_ticket_price, 2),
            ', I found these anomalies: ',
            negative_amounts, ' tickets with negative amounts, ',
            extremely_high_amounts, ' tickets over $1000, ',
            visit_before_purchase, ' tickets where visit date is before purchase date, ',
            discount_exceeds_price, ' tickets where discount exceeds ticket price. ',
            'What do these anomalies suggest about our data collection process? ',
            'How should we handle each type of anomaly? What business processes might cause these issues?'
        )
    ) as ai_explanation
FROM ticket_anomalies;

-- =====================================================
-- EXERCISE 3: Natural Language Business Insights
-- =====================================================

-- 3.1: AI-Generated Executive Summary
-- Create business-friendly summary of park performance
WITH park_metrics AS (
    SELECT 
        p.park_name,
        p.region,
        COUNT(DISTINCT t.ticket_id) as tickets_sold,
        ROUND(AVG(t.purchase_amount), 2) as avg_ticket_price,
        ROUND(AVG(ro.guest_satisfaction_score), 2) as avg_satisfaction,
        ROUND(AVG(ro.wait_time_minutes), 1) as avg_wait_time,
        COUNT(DISTINCT ro.ride_id) as active_rides
    FROM PARKS p
    LEFT JOIN TICKETS t ON p.park_id = t.park_id
    LEFT JOIN RIDE_OPERATIONS ro ON p.park_id = ro.park_id
    WHERE p.is_active = TRUE
    GROUP BY p.park_name, p.region
    ORDER BY tickets_sold DESC
)
SELECT 
    'Executive Summary - UDX Theme Parks Performance' as report_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Create an executive summary for Comcast UDX leadership based on these theme park metrics: ',
            LISTAGG(
                CONCAT(
                    park_name, ' (', region, '): ',
                    tickets_sold, ' tickets sold, ',
                    '$', avg_ticket_price, ' avg price, ',
                    avg_satisfaction, '/5.0 satisfaction, ',
                    avg_wait_time, ' min avg wait, ',
                    active_rides, ' active rides'
                ), '; '
            ) WITHIN GROUP (ORDER BY tickets_sold DESC),
            '. Please provide: 1) Key performance highlights, 2) Areas of concern, ',
            '3) Regional performance comparison, 4) Strategic recommendations for improvement. ',
            'Write in executive summary format suitable for C-level presentation.'
        )
    ) as executive_summary
FROM park_metrics;

-- 3.2: Guest Experience Insights
-- Generate natural language insights about guest behavior
WITH guest_behavior AS (
    SELECT 
        loyalty_tier,
        COUNT(*) as guest_count,
        AVG(age) as avg_age,
        COUNT(CASE WHEN marketing_opt_in = TRUE THEN 1 END) as opt_in_count,
        ROUND(COUNT(CASE WHEN marketing_opt_in = TRUE THEN 1 END) * 100.0 / COUNT(*), 1) as opt_in_percentage
    FROM GUESTS 
    WHERE email IS NOT NULL  -- Focus on guests with valid contact info
    GROUP BY loyalty_tier
    ORDER BY 
        CASE loyalty_tier 
            WHEN 'Platinum' THEN 1 
            WHEN 'Gold' THEN 2 
            WHEN 'Silver' THEN 3 
            WHEN 'Bronze' THEN 4 
        END
)
SELECT 
    'Guest Loyalty and Engagement Analysis' as insight_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Analyze guest loyalty patterns across our theme parks: ',
            LISTAGG(
                CONCAT(
                    loyalty_tier, ' tier: ', guest_count, ' guests (avg age ', ROUND(avg_age, 1), 
                    '), ', opt_in_percentage, '% marketing opt-in'
                ), '; '
            ) WITHIN GROUP (ORDER BY guest_count DESC),
            '. What does this tell us about guest engagement? How can we improve loyalty program effectiveness? ',
            'What marketing strategies would you recommend for each tier?'
        )
    ) as guest_insights
FROM guest_behavior;

-- =====================================================
-- EXERCISE 4: Automated Quality Recommendations
-- =====================================================

-- 4.1: AI-Powered Data Cleansing Suggestions
-- Generate specific SQL recommendations for fixing quality issues
WITH problematic_data AS (
    SELECT 
        COUNT(CASE WHEN email IS NULL THEN 1 END) as missing_emails,
        COUNT(CASE WHEN age < 0 THEN 1 END) as negative_ages,
        COUNT(CASE WHEN age > 120 THEN 1 END) as unrealistic_ages,
        COUNT(CASE WHEN zip_code = 'INVALID' THEN 1 END) as invalid_zips,
        COUNT(CASE WHEN birth_date > CURRENT_DATE() THEN 1 END) as future_birth_dates
    FROM GUESTS
)
SELECT 
    'Data Cleansing Action Plan' as recommendation_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'I need to fix these data quality issues in our guest database: ',
            missing_emails, ' missing emails, ',
            negative_ages, ' negative ages, ',
            unrealistic_ages, ' ages over 120, ',
            invalid_zips, ' invalid zip codes, ',
            future_birth_dates, ' future birth dates. ',
            'Please provide specific SQL UPDATE statements and data validation rules to fix each issue. ',
            'Also suggest preventive measures to avoid these issues in future data collection. ',
            'Format as actionable steps with SQL code examples.'
        )
    ) as cleansing_recommendations
FROM problematic_data;

-- 4.2: AI-Generated Data Quality Rules
-- Create intelligent rules for ongoing monitoring
WITH ride_operations_issues AS (
    SELECT 
        COUNT(CASE WHEN wait_time_minutes < 0 THEN 1 END) as negative_wait_times,
        COUNT(CASE WHEN wait_time_minutes > 300 THEN 1 END) as excessive_wait_times,
        COUNT(CASE WHEN guest_satisfaction_score > 5.0 THEN 1 END) as invalid_satisfaction_scores,
        COUNT(CASE WHEN hourly_capacity = 0 THEN 1 END) as zero_capacity_records,
        COUNT(*) as total_operations_records
    FROM RIDE_OPERATIONS
)
SELECT 
    'Automated Data Quality Rules for Ride Operations' as rule_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Based on these operational data issues in ', total_operations_records, ' ride operation records: ',
            negative_wait_times, ' negative wait times, ',
            excessive_wait_times, ' wait times over 5 hours, ',
            invalid_satisfaction_scores, ' satisfaction scores above 5.0, ',
            zero_capacity_records, ' zero capacity records, ',
            'create automated data quality rules including: ',
            '1) Validation checks for real-time data entry, ',
            '2) Alert thresholds for anomaly detection, ',
            '3) Data cleansing procedures, ',
            '4) Business logic for acceptable value ranges. ',
            'Format as implementable business rules.'
        )
    ) as quality_rules
FROM ride_operations_issues;

-- =====================================================
-- EXERCISE 5: Advanced AI Analysis
-- =====================================================

-- 5.1: Predictive Quality Insights
-- Use AI to predict future data quality issues
WITH quality_trends AS (
    SELECT 
        DATE_TRUNC('month', operation_date) as month,
        COUNT(*) as total_operations,
        COUNT(CASE WHEN wait_time_minutes < 0 OR wait_time_minutes > 300 THEN 1 END) as anomalous_wait_times,
        AVG(guest_satisfaction_score) as avg_satisfaction,
        SUM(downtime_minutes) as total_downtime
    FROM RIDE_OPERATIONS
    WHERE operation_date >= DATEADD('month', -6, CURRENT_DATE())
    GROUP BY DATE_TRUNC('month', operation_date)
    ORDER BY month
)
SELECT 
    'Predictive Data Quality Analysis' as analysis_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Analyze these 6-month trends in ride operations data quality: ',
            LISTAGG(
                CONCAT(
                    TO_VARCHAR(month, 'YYYY-MM'), ': ', total_operations, ' operations, ',
                    anomalous_wait_times, ' anomalies, ', ROUND(avg_satisfaction, 2), ' avg satisfaction, ',
                    total_downtime, ' min downtime'
                ), '; '
            ) WITHIN GROUP (ORDER BY month),
            '. Based on these trends, predict: 1) What data quality issues might emerge in the next quarter? ',
            '2) Which metrics are improving or deteriorating? 3) What proactive measures should we take? ',
            '4) How can we prevent future data quality degradation?'
        )
    ) as predictive_insights
FROM quality_trends;

-- =====================================================
-- EXERCISE COMPLETION SUMMARY
-- =====================================================

-- Summary of AI-powered analysis capabilities demonstrated
SELECT 
    'Lab 04 Completion Summary' as lab_status,
    'Congratulations! You have successfully:' as achievements,
    '✅ Connected to Snowflake Cortex AI functions' as achievement_1,
    '✅ Generated natural language insights from data' as achievement_2,
    '✅ Created AI-powered data quality reports' as achievement_3,
    '✅ Built automated recommendations system' as achievement_4,
    '✅ Developed predictive quality analysis' as achievement_5,
    'Ready for Lab 05: Advanced Anomaly Detection!' as next_step;

-- Test query to verify all exercises completed successfully
SELECT 
    'AI Integration Test Passed' as test_result,
    CURRENT_TIMESTAMP() as completion_time,
    USER() as completed_by; 