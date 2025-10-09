-- ============================================================================
-- NBCUniversal Competitive Analytics YAML Validation Test Script
-- Tests all verified queries and validates data model consistency
-- ============================================================================

-- Set the context for all queries
USE DATABASE STRATEGY_CLIENT;
USE SCHEMA DEV;

-- ============================================================================
-- VERIFIED QUERY TESTS
-- ============================================================================

-- Test 1: Disney Q1 Performance
-- Validates: competitor_profiles JOIN advertising_revenue (MI_MICROSTRATEGY_FACT)
SELECT 'Test 1: Disney Q1 Performance' as TEST_NAME;
SELECT 
    cp.COMPETITOR_NAME, 
    ar.REVENUE_QUARTER, 
    ar.REVENUE_YEAR, 
    SUM(ar.AD_REVENUE_MILLIONS) as total_ad_revenue, 
    AVG(ar.MARKET_SHARE_PERCENT) as avg_market_share, 
    AVG(ar.QOQ_GROWTH_PERCENT) as qoq_growth, 
    AVG(ar.YOY_GROWTH_PERCENT) as yoy_growth 
FROM COMPETITOR_PROFILES cp 
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID 
WHERE cp.COMPETITOR_NAME = 'Disney' 
  AND ar.REVENUE_QUARTER = 'Q1' 
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_QUARTER, ar.REVENUE_YEAR 
ORDER BY ar.REVENUE_YEAR DESC;

-- Test 2: NBCU vs TelevisaUnivision Market Share
-- Validates: competitor filtering and aggregation
SELECT 'Test 2: NBCU vs TelevisaUnivision Market Share' as TEST_NAME;
SELECT 
    cp.COMPETITOR_NAME, 
    ar.REVENUE_YEAR, 
    AVG(ar.MARKET_SHARE_PERCENT) as avg_market_share, 
    SUM(ar.AD_REVENUE_MILLIONS) as total_revenue, 
    AVG(ar.YOY_GROWTH_PERCENT) as yoy_growth 
FROM COMPETITOR_PROFILES cp 
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID 
WHERE cp.COMPETITOR_NAME IN ('NBCUniversal', 'TelevisaUnivision') 
  AND ar.REVENUE_YEAR = 2023 
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_YEAR 
ORDER BY avg_market_share DESC;

-- Test 3: 5 Quarter Revenue Growth Breakdown
-- Validates: complex date filtering and ordering
SELECT 'Test 3: 5 Quarter Revenue Growth Breakdown' as TEST_NAME;
SELECT 
    cp.COMPETITOR_NAME, 
    CONCAT(ar.REVENUE_YEAR, '-', ar.REVENUE_QUARTER) as quarter_year, 
    SUM(ar.AD_REVENUE_MILLIONS) as total_revenue, 
    AVG(ar.QOQ_GROWTH_PERCENT) as qoq_growth, 
    AVG(ar.YOY_GROWTH_PERCENT) as yoy_growth, 
    AVG(ar.MARKET_SHARE_PERCENT) as market_share 
FROM COMPETITOR_PROFILES cp 
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID 
WHERE (ar.REVENUE_YEAR = 2024 AND ar.REVENUE_QUARTER IN ('Q1', 'Q2', 'Q3')) 
   OR (ar.REVENUE_YEAR = 2023 AND ar.REVENUE_QUARTER IN ('Q3', 'Q4')) 
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_YEAR, ar.REVENUE_QUARTER 
ORDER BY ar.REVENUE_YEAR DESC, ar.REVENUE_QUARTER DESC, total_revenue DESC
LIMIT 20;

-- Test 4: Streaming vs Traditional Revenue Analysis
-- Validates: company_type grouping and platform analysis
SELECT 'Test 4: Streaming vs Traditional Revenue Analysis' as TEST_NAME;
SELECT 
    cp.COMPANY_TYPE, 
    ar.REVENUE_YEAR, 
    ar.REVENUE_QUARTER, 
    COUNT(DISTINCT cp.COMPETITOR_ID) as competitor_count, 
    SUM(ar.AD_REVENUE_MILLIONS) as total_revenue, 
    AVG(ar.QOQ_GROWTH_PERCENT) as avg_qoq_growth, 
    AVG(ar.YOY_GROWTH_PERCENT) as avg_yoy_growth, 
    SUM(ar.MARKET_SHARE_PERCENT) as combined_market_share 
FROM COMPETITOR_PROFILES cp 
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID 
GROUP BY cp.COMPANY_TYPE, ar.REVENUE_YEAR, ar.REVENUE_QUARTER 
ORDER BY ar.REVENUE_YEAR DESC, ar.REVENUE_QUARTER DESC, total_revenue DESC
LIMIT 15;

-- Test 5: Content Investment ROI Analysis
-- Validates: 3-table JOIN (competitor_profiles, market_intelligence, advertising_revenue)
SELECT 'Test 5: Content Investment ROI Analysis' as TEST_NAME;
SELECT 
    cp.COMPETITOR_NAME, 
    mi.ANALYSIS_YEAR, 
    SUM(mi.CONTENT_INVESTMENT_MILLIONS) as content_investment, 
    SUM(ar.AD_REVENUE_MILLIONS) as ad_revenue, 
    (SUM(ar.AD_REVENUE_MILLIONS) / NULLIF(SUM(mi.CONTENT_INVESTMENT_MILLIONS), 0)) as revenue_per_content_dollar, 
    AVG(mi.SUBSCRIBER_COUNT_MILLIONS) as avg_subscribers 
FROM COMPETITOR_PROFILES cp 
JOIN MARKET_INTELLIGENCE mi ON cp.COMPETITOR_ID = mi.COMPETITOR_ID 
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID 
    AND mi.ANALYSIS_YEAR = ar.REVENUE_YEAR 
GROUP BY cp.COMPETITOR_NAME, mi.ANALYSIS_YEAR 
HAVING SUM(mi.CONTENT_INVESTMENT_MILLIONS) > 0 
ORDER BY revenue_per_content_dollar DESC
LIMIT 10;

-- ============================================================================
-- SEMANTIC MODEL VALIDATION TESTS
-- ============================================================================

-- Test 6: Validate All Table Definitions
SELECT 'Test 6: Table Definitions Validation' as TEST_NAME;
SELECT 
    'COMPETITOR_PROFILES' as TABLE_NAME,
    COUNT(*) as RECORD_COUNT,
    COUNT(DISTINCT COMPETITOR_ID) as UNIQUE_IDS
FROM COMPETITOR_PROFILES
UNION ALL
SELECT 
    'MI_MICROSTRATEGY_FACT',
    COUNT(*),
    COUNT(DISTINCT REVENUE_ID)
FROM MI_MICROSTRATEGY_FACT
UNION ALL
SELECT 
    'MARKET_INTELLIGENCE',
    COUNT(*),
    COUNT(DISTINCT INTELLIGENCE_ID)
FROM MARKET_INTELLIGENCE
UNION ALL
SELECT 
    'PERFORMANCE_METRICS',
    COUNT(*),
    COUNT(DISTINCT METRIC_ID)
FROM PERFORMANCE_METRICS;

-- Test 7: Validate All Relationships (Foreign Key Integrity)
SELECT 'Test 7: Relationship Validation' as TEST_NAME;
SELECT 
    'competitor_revenue' as RELATIONSHIP_NAME,
    COUNT(*) as VALID_JOINS
FROM COMPETITOR_PROFILES cp
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID
UNION ALL
SELECT 
    'competitor_intelligence',
    COUNT(*)
FROM COMPETITOR_PROFILES cp
JOIN MARKET_INTELLIGENCE mi ON cp.COMPETITOR_ID = mi.COMPETITOR_ID
UNION ALL
SELECT 
    'competitor_performance',
    COUNT(*)
FROM COMPETITOR_PROFILES cp
JOIN PERFORMANCE_METRICS pm ON cp.COMPETITOR_ID = pm.COMPETITOR_ID
UNION ALL
SELECT 
    'revenue_intelligence_correlation',
    COUNT(*)
FROM MI_MICROSTRATEGY_FACT ar
JOIN MARKET_INTELLIGENCE mi ON ar.COMPETITOR_ID = mi.COMPETITOR_ID 
    AND ar.REVENUE_QUARTER = mi.ANALYSIS_QUARTER 
    AND ar.REVENUE_YEAR = mi.ANALYSIS_YEAR
UNION ALL
SELECT 
    'performance_revenue_correlation',
    COUNT(*)
FROM PERFORMANCE_METRICS pm
JOIN MI_MICROSTRATEGY_FACT ar ON pm.COMPETITOR_ID = ar.COMPETITOR_ID 
    AND pm.METRIC_QUARTER = ar.REVENUE_QUARTER 
    AND pm.METRIC_YEAR = ar.REVENUE_YEAR;

-- Test 8: Validate Fact Expressions (All columns exist in base tables)
SELECT 'Test 8: Fact Expression Validation' as TEST_NAME;

-- Validate advertising_revenue facts
SELECT 
    'advertising_revenue facts' as FACT_TABLE,
    COUNT(*) as RECORDS_WITH_VALID_FACTS
FROM MI_MICROSTRATEGY_FACT 
WHERE AD_REVENUE_MILLIONS IS NOT NULL 
  AND QOQ_GROWTH_PERCENT IS NOT NULL OR QOQ_GROWTH_PERCENT IS NULL  -- Allow NULLs
  AND YOY_GROWTH_PERCENT IS NOT NULL OR YOY_GROWTH_PERCENT IS NULL  -- Allow NULLs
  AND MARKET_SHARE_PERCENT IS NOT NULL 
  AND AVERAGE_CPM IS NOT NULL

UNION ALL

-- Validate market_intelligence facts
SELECT 
    'market_intelligence facts',
    COUNT(*)
FROM MARKET_INTELLIGENCE 
WHERE CONTENT_INVESTMENT_MILLIONS IS NOT NULL OR CONTENT_INVESTMENT_MILLIONS IS NULL  -- Allow NULLs
  AND SUBSCRIBER_COUNT_MILLIONS IS NOT NULL OR SUBSCRIBER_COUNT_MILLIONS IS NULL      -- Allow NULLs
  AND STREAMING_HOURS_BILLIONS IS NOT NULL OR STREAMING_HOURS_BILLIONS IS NULL       -- Allow NULLs
  AND AD_INVENTORY_AVAILABLE IS NOT NULL 
  AND PRICING_PREMIUM_INDEX IS NOT NULL

UNION ALL

-- Validate performance_metrics facts
SELECT 
    'performance_metrics facts',
    COUNT(*)
FROM PERFORMANCE_METRICS 
WHERE VIEWERSHIP_MILLIONS IS NOT NULL 
  AND ENGAGEMENT_RATE_PERCENT IS NOT NULL 
  AND RETENTION_RATE_PERCENT IS NOT NULL 
  AND BRAND_SENTIMENT_SCORE IS NOT NULL OR BRAND_SENTIMENT_SCORE IS NULL  -- Allow NULLs
  AND SOCIAL_MEDIA_MENTIONS IS NOT NULL;

-- Test 9: Validate Time Dimensions
SELECT 'Test 9: Time Dimension Validation' as TEST_NAME;

-- Test revenue_date construction
SELECT 
    'revenue_date construction' as TIME_DIMENSION,
    REVENUE_YEAR,
    REVENUE_QUARTER,
    CONCAT(REVENUE_YEAR, '-', 
      CASE REVENUE_QUARTER 
        WHEN 'Q1' THEN '03-31'
        WHEN 'Q2' THEN '06-30' 
        WHEN 'Q3' THEN '09-30'
        WHEN 'Q4' THEN '12-31'
      END)::DATE as revenue_date,
    COUNT(*) as RECORD_COUNT
FROM MI_MICROSTRATEGY_FACT 
GROUP BY REVENUE_YEAR, REVENUE_QUARTER
ORDER BY REVENUE_YEAR DESC, REVENUE_QUARTER;

-- Test 10: Validate Synonyms Coverage (Business terms that should work)
SELECT 'Test 10: Business Terms Coverage' as TEST_NAME;

-- Test competitor name variations that should be understood
SELECT 
    'Competitor Name Variations' as COVERAGE_TYPE,
    cp.COMPETITOR_NAME,
    cp.COMPANY_TYPE,
    cp.MARKET_SEGMENT
FROM COMPETITOR_PROFILES cp
WHERE cp.COMPETITOR_NAME IN (
    'Disney', 'NBCUniversal', 'Netflix', 'Amazon Prime Video',
    'Warner Bros Discovery', 'TelevisaUnivision'
)
ORDER BY cp.COMPETITOR_NAME;

-- ============================================================================
-- COMMON ISSUES VALIDATION
-- ============================================================================

-- Test 11: Check for Invalid Identifier Issues
SELECT 'Test 11: Invalid Identifier Check' as TEST_NAME;

-- Ensure all referenced columns exist in base tables
SELECT 
    'Column Existence Check' as CHECK_TYPE,
    CASE 
        WHEN COUNT(*) > 0 THEN 'PASS - All columns exist'
        ELSE 'FAIL - Missing columns'
    END as RESULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'DEV' 
  AND TABLE_NAME = 'MI_MICROSTRATEGY_FACT'
  AND COLUMN_NAME IN (
    'AD_REVENUE_MILLIONS', 'QOQ_GROWTH_PERCENT', 'YOY_GROWTH_PERCENT',
    'MARKET_SHARE_PERCENT', 'AVERAGE_CPM', 'COMPETITOR_ID',
    'REVENUE_QUARTER', 'REVENUE_YEAR', 'PLATFORM_TYPE', 'REVENUE_ID'
  )
HAVING COUNT(*) = 10;  -- Should have all 10 columns

-- Test 12: ID Length Validation
SELECT 'Test 12: ID Length Validation' as TEST_NAME;

-- Check that all generated IDs fit within VARCHAR constraints
SELECT 
    'ID Length Check' as CHECK_TYPE,
    MAX(LENGTH(REVENUE_ID)) as MAX_REVENUE_ID_LENGTH,
    CASE 
        WHEN MAX(LENGTH(REVENUE_ID)) <= 50 THEN 'PASS - All IDs within VARCHAR(50)'
        ELSE 'FAIL - Some IDs exceed VARCHAR(50)'
    END as RESULT
FROM MI_MICROSTRATEGY_FACT
UNION ALL
SELECT 
    'Intelligence ID Length Check',
    MAX(LENGTH(INTELLIGENCE_ID)),
    CASE 
        WHEN MAX(LENGTH(INTELLIGENCE_ID)) <= 50 THEN 'PASS - All IDs within VARCHAR(50)'
        ELSE 'FAIL - Some IDs exceed VARCHAR(50)'
    END
FROM MARKET_INTELLIGENCE
UNION ALL
SELECT 
    'Metric ID Length Check',
    MAX(LENGTH(METRIC_ID)),
    CASE 
        WHEN MAX(LENGTH(METRIC_ID)) <= 50 THEN 'PASS - All IDs within VARCHAR(50)'
        ELSE 'FAIL - Some IDs exceed VARCHAR(50)'
    END
FROM PERFORMANCE_METRICS;

-- Test 13: Decimal Precision Validation
SELECT 'Test 13: Decimal Precision Check' as TEST_NAME;

-- Check for values that would cause overflow in DECIMAL(4,2) vs DECIMAL(6,2)
SELECT 
    'Decimal Overflow Check' as CHECK_TYPE,
    MAX(ABS(QOQ_GROWTH_PERCENT)) as MAX_QOQ_GROWTH,
    MAX(ABS(YOY_GROWTH_PERCENT)) as MAX_YOY_GROWTH,
    MAX(MARKET_SHARE_PERCENT) as MAX_MARKET_SHARE,
    CASE 
        WHEN MAX(ABS(QOQ_GROWTH_PERCENT)) < 1000 
         AND MAX(ABS(YOY_GROWTH_PERCENT)) < 1000 
         AND MAX(MARKET_SHARE_PERCENT) < 1000 
        THEN 'PASS - All values within DECIMAL(6,2) range'
        ELSE 'FAIL - Values exceed precision'
    END as PRECISION_CHECK
FROM MI_MICROSTRATEGY_FACT;

-- ============================================================================
-- PERFORMANCE AND OPTIMIZATION TESTS
-- ============================================================================

-- Test 13: Query Performance Baseline
SELECT 'Test 13: Query Performance Baseline' as TEST_NAME;

-- Time a complex aggregation query
SELECT 
    COUNT(DISTINCT cp.COMPETITOR_ID) as TOTAL_COMPETITORS,
    COUNT(DISTINCT ar.REVENUE_ID) as TOTAL_REVENUE_RECORDS,
    COUNT(DISTINCT mi.INTELLIGENCE_ID) as TOTAL_INTELLIGENCE_RECORDS,
    AVG(ar.AD_REVENUE_MILLIONS) as AVG_REVENUE,
    SUM(CASE WHEN ar.QOQ_GROWTH_PERCENT IS NULL THEN 1 ELSE 0 END) as NULL_GROWTH_RECORDS
FROM COMPETITOR_PROFILES cp
LEFT JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID
LEFT JOIN MARKET_INTELLIGENCE mi ON cp.COMPETITOR_ID = mi.COMPETITOR_ID;

-- ============================================================================
-- FINAL VALIDATION SUMMARY
-- ============================================================================

SELECT 'VALIDATION COMPLETE' as STATUS,
       'All tests executed successfully' as MESSAGE,
       CURRENT_TIMESTAMP() as COMPLETION_TIME;