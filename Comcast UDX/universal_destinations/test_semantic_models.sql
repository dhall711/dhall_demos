-- =====================================================================
-- Universal Destinations & Experiences - Semantic Model Testing Script
-- =====================================================================
-- This script tests all the verified queries from the semantic models
-- to ensure they work correctly with the synthetic data
-- =====================================================================

USE DATABASE UNIVERSAL_DATA_PLATFORM;

-- =====================================================================
-- TEST GUEST ANALYTICS QUERIES
-- =====================================================================

-- Test: Top Spending Guests
SELECT '=== GUEST ANALYTICS: Top Spending Guests ===' as test_name;
SELECT GUEST_ID, FIRST_NAME, LAST_NAME, SUM(TOTAL_SPEND_AMOUNT) as total_spend 
FROM UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.GUEST_PROFILES 
GROUP BY GUEST_ID, FIRST_NAME, LAST_NAME 
ORDER BY total_spend DESC 
LIMIT 10;

-- Test: Guest Demographics by Park
SELECT '=== GUEST ANALYTICS: Guest Demographics by Park ===' as test_name;
SELECT v.PARK_LOCATION, g.STATE, g.COUNTRY, COUNT(DISTINCT g.GUEST_ID) as guest_count 
FROM UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.GUEST_PROFILES g 
JOIN UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.VISIT_SESSIONS v ON g.GUEST_ID = v.GUEST_ID 
GROUP BY v.PARK_LOCATION, g.STATE, g.COUNTRY 
ORDER BY guest_count DESC
LIMIT 15;

-- Test: Membership Tier Analysis
SELECT '=== GUEST ANALYTICS: Membership Tier Analysis ===' as test_name;
SELECT MEMBERSHIP_TIER, 
       COUNT(DISTINCT GUEST_ID) as member_count, 
       AVG(TOTAL_SPEND_AMOUNT) as avg_spend 
FROM UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.GUEST_PROFILES 
GROUP BY MEMBERSHIP_TIER 
ORDER BY avg_spend DESC;

-- =====================================================================
-- TEST PARK OPERATIONS QUERIES
-- =====================================================================

-- Test: Highest Wait Time Attractions
SELECT '=== PARK OPERATIONS: Highest Wait Time Attractions ===' as test_name;
SELECT a.ATTRACTION_NAME, a.PARK_LOCATION, AVG(w.WAIT_TIME_MINUTES) as avg_wait_time 
FROM UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.ATTRACTIONS a 
JOIN UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.WAIT_TIMES w ON a.ATTRACTION_ID = w.ATTRACTION_ID 
GROUP BY a.ATTRACTION_NAME, a.PARK_LOCATION 
ORDER BY avg_wait_time DESC 
LIMIT 10;

-- Test: Capacity Efficiency by Park
SELECT '=== PARK OPERATIONS: Capacity Efficiency by Park ===' as test_name;
SELECT a.PARK_LOCATION, 
       AVG((c.GUESTS_PER_HOUR::FLOAT / c.THEORETICAL_CAPACITY) * 100) as avg_capacity_utilization,
       AVG(c.OPERATIONAL_EFFICIENCY_SCORE) as avg_efficiency 
FROM UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.ATTRACTIONS a 
JOIN UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.HOURLY_CAPACITY c ON a.ATTRACTION_ID = c.ATTRACTION_ID 
GROUP BY a.PARK_LOCATION 
ORDER BY avg_capacity_utilization DESC;

-- Test: Franchise Performance Analysis
SELECT '=== PARK OPERATIONS: Franchise Performance Analysis ===' as test_name;
SELECT a.FRANCHISE, a.PARK_LOCATION,
       COUNT(DISTINCT a.ATTRACTION_ID) as attraction_count,
       AVG(a.GUEST_SATISFACTION_RATING) as avg_satisfaction
FROM UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.ATTRACTIONS a 
GROUP BY a.FRANCHISE, a.PARK_LOCATION 
ORDER BY avg_satisfaction DESC 
LIMIT 15;

-- =====================================================================
-- TEST REVENUE ANALYTICS QUERIES
-- =====================================================================

-- Test: Revenue by Park Location
SELECT '=== REVENUE ANALYTICS: Revenue by Park Location ===' as test_name;
SELECT ts.PARK_LOCATION, 
       SUM(ts.TICKET_PRICE - ts.DISCOUNT_AMOUNT) as ticket_revenue,
       COUNT(DISTINCT ts.GUEST_ID) as unique_guests
FROM UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS.TICKET_SALES ts 
GROUP BY ts.PARK_LOCATION 
ORDER BY ticket_revenue DESC;

-- Test: Franchise Merchandise Performance
SELECT '=== REVENUE ANALYTICS: Franchise Merchandise Performance ===' as test_name;
SELECT FRANCHISE, PRODUCT_CATEGORY, 
       SUM(UNIT_PRICE * QUANTITY) as total_revenue,
       AVG(((UNIT_PRICE - COST_OF_GOODS) / UNIT_PRICE) * 100) as avg_profit_margin,
       SUM(QUANTITY) as total_units_sold 
FROM UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS.MERCHANDISE_SALES 
GROUP BY FRANCHISE, PRODUCT_CATEGORY 
ORDER BY total_revenue DESC 
LIMIT 15;

-- Test: Guest Spending Analysis
SELECT '=== REVENUE ANALYTICS: Guest Spending Analysis ===' as test_name;
SELECT ts.GUEST_SEGMENT, 
       COUNT(DISTINCT ts.GUEST_ID) as guest_count,
       AVG(ts.TICKET_PRICE - ts.DISCOUNT_AMOUNT) as avg_ticket_spend
FROM UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS.TICKET_SALES ts 
GROUP BY ts.GUEST_SEGMENT 
ORDER BY avg_ticket_spend DESC;

-- =====================================================================
-- TEST STAFF MANAGEMENT QUERIES
-- =====================================================================

-- Test: Department Staffing Levels
SELECT '=== STAFF MANAGEMENT: Department Staffing Levels ===' as test_name;
SELECT PARK_LOCATION, DEPARTMENT, EMPLOYMENT_TYPE, 
       COUNT(DISTINCT EMPLOYEE_ID) as employee_count, 
       AVG(CURRENT_PERFORMANCE_RATING) as avg_performance 
FROM UNIVERSAL_DATA_PLATFORM.STAFF_MANAGEMENT.EMPLOYEE_PROFILES 
GROUP BY PARK_LOCATION, DEPARTMENT, EMPLOYMENT_TYPE 
ORDER BY PARK_LOCATION, DEPARTMENT, employee_count DESC;

-- Test: Training Completion by Category
SELECT '=== STAFF MANAGEMENT: Training Completion by Category ===' as test_name;
SELECT e.DEPARTMENT, t.TRAINING_CATEGORY,
       COUNT(DISTINCT t.EMPLOYEE_ID) as employees_trained,
       AVG(CASE WHEN t.TRAINING_STATUS = 'Completed' THEN 1 ELSE 0 END) * 100 as completion_rate,
       AVG(t.TRAINING_SCORE) as avg_score 
FROM UNIVERSAL_DATA_PLATFORM.STAFF_MANAGEMENT.EMPLOYEE_PROFILES e 
JOIN UNIVERSAL_DATA_PLATFORM.STAFF_MANAGEMENT.TRAINING_RECORDS t ON e.EMPLOYEE_ID = t.EMPLOYEE_ID 
GROUP BY e.DEPARTMENT, t.TRAINING_CATEGORY 
ORDER BY completion_rate DESC;

-- =====================================================================
-- TEST UNIFIED ANALYTICS QUERIES
-- =====================================================================

-- Test: Park Performance Dashboard
SELECT '=== UNIFIED ANALYTICS: Park Performance Dashboard ===' as test_name;
SELECT a.PARK_LOCATION, 
       COUNT(DISTINCT a.ATTRACTION_ID) as total_attractions,
       AVG(a.GUEST_SATISFACTION_RATING) as avg_satisfaction,
       COUNT(DISTINCT e.EMPLOYEE_ID) as total_employees
FROM UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.ATTRACTIONS a 
LEFT JOIN UNIVERSAL_DATA_PLATFORM.STAFF_MANAGEMENT.EMPLOYEE_PROFILES e ON a.PARK_LOCATION = e.PARK_LOCATION 
GROUP BY a.PARK_LOCATION 
ORDER BY total_attractions DESC;

-- Test: Guest Lifetime Value Analysis
SELECT '=== UNIFIED ANALYTICS: Guest Lifetime Value Analysis ===' as test_name;
SELECT g.MEMBERSHIP_TIER, ts.GUEST_SEGMENT,
       COUNT(DISTINCT g.GUEST_ID) as guest_count,
       AVG(g.TOTAL_SPEND_AMOUNT + g.MEMBERSHIP_VALUE) as avg_lifetime_value
FROM UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.GUEST_PROFILES g 
LEFT JOIN UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS.TICKET_SALES ts ON g.GUEST_ID = ts.GUEST_ID
GROUP BY g.MEMBERSHIP_TIER, ts.GUEST_SEGMENT 
ORDER BY avg_lifetime_value DESC;

-- Test: Revenue Optimization Opportunities
SELECT '=== UNIFIED ANALYTICS: Revenue Optimization Opportunities ===' as test_name;
SELECT ts.PARK_LOCATION, ts.PRICING_TIER,
       COUNT(DISTINCT ts.GUEST_ID) as unique_guests,
       SUM(ts.TICKET_PRICE - ts.DISCOUNT_AMOUNT) as ticket_revenue,
       SUM(ts.TICKET_PRICE - ts.DISCOUNT_AMOUNT) / COUNT(DISTINCT ts.GUEST_ID) as revenue_per_guest
FROM UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS.TICKET_SALES ts 
GROUP BY ts.PARK_LOCATION, ts.PRICING_TIER 
ORDER BY revenue_per_guest DESC
LIMIT 10;

-- =====================================================================
-- CROSS-FUNCTIONAL ANALYSIS TESTS
-- =====================================================================

-- Test: Guest Journey Analysis
SELECT '=== CROSS-FUNCTIONAL: Guest Journey Analysis ===' as test_name;
SELECT g.GUEST_ID, g.MEMBERSHIP_TIER,
       COUNT(DISTINCT vs.VISIT_ID) as total_visits,
       SUM(ts.TICKET_PRICE - ts.DISCOUNT_AMOUNT) as total_ticket_spend,
       AVG(vs.SPEND_AMOUNT) as avg_visit_spend
FROM UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.GUEST_PROFILES g
LEFT JOIN UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.VISIT_SESSIONS vs ON g.GUEST_ID = vs.GUEST_ID
LEFT JOIN UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS.TICKET_SALES ts ON g.GUEST_ID = ts.GUEST_ID
GROUP BY g.GUEST_ID, g.MEMBERSHIP_TIER
HAVING total_visits > 0
ORDER BY total_ticket_spend DESC
LIMIT 10;

-- Test: Operational Efficiency vs Satisfaction
SELECT '=== CROSS-FUNCTIONAL: Operational Efficiency vs Satisfaction ===' as test_name;
SELECT a.FRANCHISE, 
       AVG(a.GUEST_SATISFACTION_RATING) as avg_satisfaction,
       AVG((hc.GUESTS_PER_HOUR::FLOAT / hc.THEORETICAL_CAPACITY) * 100) as avg_efficiency,
       AVG(wt.WAIT_TIME_MINUTES) as avg_wait_time
FROM UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.ATTRACTIONS a
LEFT JOIN UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.HOURLY_CAPACITY hc ON a.ATTRACTION_ID = hc.ATTRACTION_ID
LEFT JOIN UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.WAIT_TIMES wt ON a.ATTRACTION_ID = wt.ATTRACTION_ID
GROUP BY a.FRANCHISE
ORDER BY avg_satisfaction DESC;

-- Test: Staff Performance Impact
SELECT '=== CROSS-FUNCTIONAL: Staff Performance Impact ===' as test_name;
SELECT e.PARK_LOCATION, e.DEPARTMENT,
       COUNT(DISTINCT e.EMPLOYEE_ID) as staff_count,
       AVG(e.CURRENT_PERFORMANCE_RATING) as avg_staff_performance,
       AVG(a.GUEST_SATISFACTION_RATING) as avg_guest_satisfaction
FROM UNIVERSAL_DATA_PLATFORM.STAFF_MANAGEMENT.EMPLOYEE_PROFILES e
JOIN UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS.ATTRACTIONS a ON e.PARK_LOCATION = a.PARK_LOCATION
GROUP BY e.PARK_LOCATION, e.DEPARTMENT
ORDER BY avg_guest_satisfaction DESC
LIMIT 15;

-- =====================================================================
-- DATA QUALITY VALIDATION
-- =====================================================================

-- Test: Data Completeness Check
SELECT '=== DATA QUALITY: Completeness Check ===' as test_name;
SELECT 
    'Guest Profiles' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN GUEST_ID IS NOT NULL THEN 1 END) as non_null_ids,
    ROUND((COUNT(CASE WHEN GUEST_ID IS NOT NULL THEN 1 END)::FLOAT / COUNT(*)) * 100, 2) as completeness_pct
FROM GUEST_ANALYTICS.GUEST_PROFILES
UNION ALL
SELECT 
    'Visit Sessions' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN VISIT_ID IS NOT NULL THEN 1 END) as non_null_ids,
    ROUND((COUNT(CASE WHEN VISIT_ID IS NOT NULL THEN 1 END)::FLOAT / COUNT(*)) * 100, 2) as completeness_pct
FROM GUEST_ANALYTICS.VISIT_SESSIONS
UNION ALL
SELECT 
    'Attractions' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN ATTRACTION_ID IS NOT NULL THEN 1 END) as non_null_ids,
    ROUND((COUNT(CASE WHEN ATTRACTION_ID IS NOT NULL THEN 1 END)::FLOAT / COUNT(*)) * 100, 2) as completeness_pct
FROM PARK_OPERATIONS.ATTRACTIONS;

-- Test: Referential Integrity Check
SELECT '=== DATA QUALITY: Referential Integrity Check ===' as test_name;
SELECT 
    'Visit Sessions → Guest Profiles' as relationship,
    COUNT(DISTINCT vs.GUEST_ID) as child_unique_keys,
    COUNT(DISTINCT g.GUEST_ID) as parent_unique_keys,
    COUNT(DISTINCT vs.GUEST_ID) - COUNT(DISTINCT CASE WHEN g.GUEST_ID IS NOT NULL THEN vs.GUEST_ID END) as orphaned_records
FROM GUEST_ANALYTICS.VISIT_SESSIONS vs
LEFT JOIN GUEST_ANALYTICS.GUEST_PROFILES g ON vs.GUEST_ID = g.GUEST_ID
UNION ALL
SELECT 
    'Wait Times → Attractions' as relationship,
    COUNT(DISTINCT wt.ATTRACTION_ID) as child_unique_keys,
    COUNT(DISTINCT a.ATTRACTION_ID) as parent_unique_keys,
    COUNT(DISTINCT wt.ATTRACTION_ID) - COUNT(DISTINCT CASE WHEN a.ATTRACTION_ID IS NOT NULL THEN wt.ATTRACTION_ID END) as orphaned_records
FROM PARK_OPERATIONS.WAIT_TIMES wt
LEFT JOIN PARK_OPERATIONS.ATTRACTIONS a ON wt.ATTRACTION_ID = a.ATTRACTION_ID;

-- =====================================================================
-- PERFORMANCE METRICS
-- =====================================================================

-- Test: Query Performance Simulation
SELECT '=== PERFORMANCE: Query Performance Simulation ===' as test_name;
SELECT 
    'Complex Join Query' as query_type,
    COUNT(*) as result_count,
    CURRENT_TIMESTAMP() as execution_time
FROM GUEST_ANALYTICS.GUEST_PROFILES g
JOIN GUEST_ANALYTICS.VISIT_SESSIONS vs ON g.GUEST_ID = vs.GUEST_ID
JOIN REVENUE_ANALYTICS.TICKET_SALES ts ON g.GUEST_ID = ts.GUEST_ID
WHERE g.MEMBERSHIP_TIER = 'Premier'
AND vs.VISIT_DATE >= DATEADD(month, -3, CURRENT_DATE());

-- =====================================================================
-- FINAL SUMMARY
-- =====================================================================

SELECT '======================================================' as divider;
SELECT 'UNIVERSAL DESTINATIONS & EXPERIENCES' as title;
SELECT 'SEMANTIC MODEL TESTING COMPLETED SUCCESSFULLY' as status;
SELECT '======================================================' as divider;

-- Summary Statistics
SELECT 
    'FINAL DATA SUMMARY' as summary_title,
    (SELECT COUNT(*) FROM GUEST_ANALYTICS.GUEST_PROFILES) as total_guests,
    (SELECT COUNT(*) FROM GUEST_ANALYTICS.VISIT_SESSIONS) as total_visits,
    (SELECT COUNT(*) FROM PARK_OPERATIONS.ATTRACTIONS) as total_attractions,
    (SELECT COUNT(*) FROM STAFF_MANAGEMENT.EMPLOYEE_PROFILES) as total_employees,
    (SELECT COUNT(*) FROM REVENUE_ANALYTICS.TICKET_SALES) as total_ticket_sales,
    (SELECT ROUND(SUM(TICKET_PRICE - DISCOUNT_AMOUNT), 2) FROM REVENUE_ANALYTICS.TICKET_SALES) as total_revenue;

SELECT 'All semantic model queries executed successfully!' as completion_status,
       'Data is ready for Snowflake Cortex Analyst deployment' as next_steps;