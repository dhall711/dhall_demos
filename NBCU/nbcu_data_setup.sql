-- ============================================================================
-- NBCUniversal Project Nexus - Competitive Analytics Data Setup
-- Database and Schema Creation with Synthetic Data Generation
-- ============================================================================

-- Database and Schema Creation
CREATE DATABASE IF NOT EXISTS STRATEGY_CLIENT;
USE DATABASE STRATEGY_CLIENT;

CREATE SCHEMA IF NOT EXISTS DEV;
USE SCHEMA DEV;

-- ============================================================================
-- 1. COMPETITOR_PROFILES Table
-- ============================================================================

CREATE OR REPLACE TABLE COMPETITOR_PROFILES (
    COMPETITOR_ID VARCHAR(20) PRIMARY KEY,
    COMPETITOR_NAME VARCHAR(100) NOT NULL,
    COMPANY_TYPE VARCHAR(50) NOT NULL,
    MARKET_SEGMENT VARCHAR(50) NOT NULL,
    PARENT_COMPANY VARCHAR(100),
    HEADQUARTERS_REGION VARCHAR(50) NOT NULL,
    MARKET_CAP_BILLIONS DECIMAL(10,2),
    EMPLOYEE_COUNT INTEGER,
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert Competitor Profiles Data
INSERT INTO COMPETITOR_PROFILES VALUES
('COMP_001', 'NBCUniversal', 'Broadcast & Cable', 'General Entertainment', 'Comcast Corporation', 'North America', 265.5, 35000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_002', 'Disney', 'Broadcast & Streaming', 'Family Entertainment', 'The Walt Disney Company', 'North America', 156.8, 220000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_003', 'Warner Bros Discovery', 'Cable & Streaming', 'General Entertainment', 'Warner Bros. Discovery Inc', 'North America', 24.3, 35000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_004', 'Fox Corporation', 'Broadcast', 'News & Sports', 'Fox Corporation', 'North America', 18.4, 9000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_005', 'Paramount Global', 'Broadcast & Streaming', 'General Entertainment', 'National Amusements', 'North America', 8.9, 24500, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_006', 'TelevisaUnivision', 'Broadcast & Cable', 'Hispanic Entertainment', 'TelevisaUnivision Holdings', 'North America', 12.1, 13000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_007', 'Netflix', 'Streaming', 'Global Streaming', 'Netflix Inc', 'North America', 191.4, 13000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_008', 'Amazon Prime Video', 'Streaming', 'Tech & Entertainment', 'Amazon Inc', 'North America', 1543.0, 1500000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_009', 'Hulu', 'Streaming', 'General Entertainment', 'The Walt Disney Company', 'North America', 27.5, 4500, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_010', 'YouTube TV', 'Streaming & Digital', 'Digital Platform', 'Alphabet Inc', 'North America', 1707.0, 174000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_011', 'Sony Pictures Television', 'Cable & Streaming', 'Global Entertainment', 'Sony Group Corporation', 'Asia Pacific', 108.3, 109000, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('COMP_012', 'A+E Networks', 'Cable', 'Lifestyle & Entertainment', 'Hearst Communications', 'North America', 15.2, 3500, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
-- Edge case: Private company with NULL market cap
('COMP_013', 'Vice Media Group', 'Digital', 'Youth Entertainment', 'Private Ownership', 'North America', NULL, 2800, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
-- Edge case: Small regional player
('COMP_014', 'Gray Television', 'Broadcast', 'Local News', 'Gray Television Inc', 'North America', 1.2, 8500, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- ============================================================================
-- 2. MI_MICROSTRATEGY_FACT Table (Main Advertising Revenue Table)
-- ============================================================================

CREATE OR REPLACE TABLE MI_MICROSTRATEGY_FACT (
    REVENUE_ID VARCHAR(50) PRIMARY KEY,
    COMPETITOR_ID VARCHAR(20) NOT NULL,
    REVENUE_QUARTER VARCHAR(2) NOT NULL,
    REVENUE_YEAR INTEGER NOT NULL,
    PLATFORM_TYPE VARCHAR(30) NOT NULL,
    AD_FORMAT VARCHAR(30) NOT NULL,
    AUDIENCE_DEMOGRAPHIC VARCHAR(30) NOT NULL,
    CONTENT_CATEGORY VARCHAR(30) NOT NULL,
    AD_REVENUE_MILLIONS DECIMAL(12,2) NOT NULL,
    QOQ_GROWTH_PERCENT DECIMAL(6,2),
    YOY_GROWTH_PERCENT DECIMAL(6,2),
    MARKET_SHARE_PERCENT DECIMAL(6,2),
    AVERAGE_CPM DECIMAL(8,2),
    IMPRESSION_MILLIONS DECIMAL(12,2),
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (COMPETITOR_ID) REFERENCES COMPETITOR_PROFILES(COMPETITOR_ID)
);

-- Generate Advertising Revenue Data for 5 quarters (Q3 2023 - Q3 2024)
-- This generates approximately 100+ records per quarter across all competitors

-- Q3 2023 Data
INSERT INTO MI_MICROSTRATEGY_FACT 
SELECT 
    'REV_' || COMPETITOR_ID || '_' || REVENUE_YEAR || '_' || REVENUE_QUARTER || '_' || 
    CASE PLATFORM_TYPE
        WHEN 'Broadcast TV' THEN 'BTV'
        WHEN 'Cable TV' THEN 'CTV'
        WHEN 'Streaming' THEN 'STR'
        WHEN 'Digital Display' THEN 'DIG'
        WHEN 'Connected TV' THEN 'CNC'
        WHEN 'Mobile Video' THEN 'MOB'
        WHEN 'Podcast' THEN 'POD'
        WHEN 'Social Media' THEN 'SOC'
        WHEN 'YouTube' THEN 'YTB'
        WHEN 'Hulu Ad Tier' THEN 'HLU'
        ELSE 'OTH'
    END || '_' || ROW_NUMBER() OVER (ORDER BY COMPETITOR_ID) as REVENUE_ID,
    COMPETITOR_ID,
    REVENUE_QUARTER,
    REVENUE_YEAR,
    PLATFORM_TYPE,
    AD_FORMAT,
    AUDIENCE_DEMOGRAPHIC,
    CONTENT_CATEGORY,
    AD_REVENUE_MILLIONS,
    QOQ_GROWTH_PERCENT,
    YOY_GROWTH_PERCENT,
    MARKET_SHARE_PERCENT,
    AVERAGE_CPM,
    IMPRESSION_MILLIONS,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as REVENUE_QUARTER, 2023 as REVENUE_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    platforms AS (
        SELECT 'Broadcast TV' as PLATFORM_TYPE, 'Video Commercial' as AD_FORMAT, 'Adults 25-54' as AUDIENCE_DEMOGRAPHIC, 'Prime Time Drama' as CONTENT_CATEGORY
        UNION ALL SELECT 'Cable TV', 'Video Commercial', 'Adults 18-49', 'News Programming'
        UNION ALL SELECT 'Streaming', 'Pre-Roll Video', 'Adults 18-34', 'Original Series'
        UNION ALL SELECT 'Digital Display', 'Banner Ad', 'Adults 25-54', 'Sports Content'
        UNION ALL SELECT 'Connected TV', 'Video Commercial', 'Adults 35-64', 'Reality TV'
        UNION ALL SELECT 'Mobile Video', 'Mobile Video Ad', 'Adults 18-34', 'Short Form Content'
        UNION ALL SELECT 'Podcast', 'Audio Commercial', 'Adults 25-54', 'News & Talk'
        UNION ALL SELECT 'Social Media', 'Video Ad', 'Adults 18-34', 'Entertainment News'
        UNION ALL SELECT 'YouTube', 'Pre-Roll Video', 'Adults 18-49', 'User Generated'
        UNION ALL SELECT 'Hulu Ad Tier', 'Video Commercial', 'Adults 25-54', 'Premium Drama'
    ),
    base_revenue AS (
        SELECT 
            c.COMPETITOR_ID,
            c.COMPETITOR_NAME,
            q.REVENUE_QUARTER,
            q.REVENUE_YEAR,
            p.PLATFORM_TYPE,
            p.AD_FORMAT,
            p.AUDIENCE_DEMOGRAPHIC,
            p.CONTENT_CATEGORY,
            CASE c.COMPETITOR_NAME
                WHEN 'NBCUniversal' THEN 
                    CASE p.PLATFORM_TYPE
                        WHEN 'Broadcast TV' THEN UNIFORM(850, 1200, RANDOM())
                        WHEN 'Cable TV' THEN UNIFORM(450, 650, RANDOM())
                        WHEN 'Streaming' THEN UNIFORM(180, 320, RANDOM())
                        WHEN 'Digital Display' THEN UNIFORM(120, 200, RANDOM())
                        WHEN 'Connected TV' THEN UNIFORM(95, 150, RANDOM())
                        ELSE UNIFORM(45, 85, RANDOM())
                    END
                WHEN 'Disney' THEN 
                    CASE p.PLATFORM_TYPE
                        WHEN 'Broadcast TV' THEN UNIFORM(750, 1100, RANDOM())
                        WHEN 'Streaming' THEN UNIFORM(380, 550, RANDOM())
                        WHEN 'Cable TV' THEN UNIFORM(320, 480, RANDOM())
                        WHEN 'Digital Display' THEN UNIFORM(180, 280, RANDOM())
                        WHEN 'Connected TV' THEN UNIFORM(140, 220, RANDOM())
                        ELSE UNIFORM(60, 110, RANDOM())
                    END
                WHEN 'Warner Bros Discovery' THEN 
                    CASE p.PLATFORM_TYPE
                        WHEN 'Cable TV' THEN UNIFORM(580, 780, RANDOM())
                        WHEN 'Streaming' THEN UNIFORM(280, 420, RANDOM())
                        WHEN 'Broadcast TV' THEN UNIFORM(180, 280, RANDOM())
                        WHEN 'Digital Display' THEN UNIFORM(95, 165, RANDOM())
                        WHEN 'Connected TV' THEN UNIFORM(85, 135, RANDOM())
                        ELSE UNIFORM(35, 75, RANDOM())
                    END
                WHEN 'Netflix' THEN 
                    CASE p.PLATFORM_TYPE
                        WHEN 'Streaming' THEN UNIFORM(420, 650, RANDOM())
                        WHEN 'Connected TV' THEN UNIFORM(180, 280, RANDOM())
                        WHEN 'Mobile Video' THEN UNIFORM(95, 155, RANDOM())
                        WHEN 'Digital Display' THEN UNIFORM(65, 125, RANDOM())
                        ELSE UNIFORM(25, 65, RANDOM())
                    END
                WHEN 'TelevisaUnivision' THEN 
                    CASE p.PLATFORM_TYPE
                        WHEN 'Broadcast TV' THEN UNIFORM(380, 520, RANDOM())
                        WHEN 'Cable TV' THEN UNIFORM(220, 340, RANDOM())
                        WHEN 'Streaming' THEN UNIFORM(85, 145, RANDOM())
                        WHEN 'Digital Display' THEN UNIFORM(45, 85, RANDOM())
                        ELSE UNIFORM(20, 50, RANDOM())
                    END
                ELSE UNIFORM(50, 200, RANDOM())
            END as BASE_REVENUE
        FROM COMPETITOR_PROFILES c
        CROSS JOIN quarters q
        CROSS JOIN platforms p
    )
    SELECT 
        COMPETITOR_ID,
        REVENUE_QUARTER,
        REVENUE_YEAR,
        PLATFORM_TYPE,
        AD_FORMAT,
        AUDIENCE_DEMOGRAPHIC,
        CONTENT_CATEGORY,
        ROUND(BASE_REVENUE * 
            CASE REVENUE_QUARTER
                WHEN 'Q4' THEN 1.15  -- Holiday boost
                WHEN 'Q1' THEN 0.85  -- Post-holiday dip
                WHEN 'Q2' THEN 1.05  -- Upfront season
                WHEN 'Q3' THEN 0.95  -- Summer slowdown
                ELSE 1.0
            END * 
            CASE REVENUE_YEAR
                WHEN 2024 THEN 1.08  -- YoY growth
                ELSE 1.0
            END, 2) as AD_REVENUE_MILLIONS,
        CASE 
            WHEN UNIFORM(0, 1, RANDOM()) < 0.05 THEN NULL  -- 5% NULL for edge case testing
            ELSE ROUND(UNIFORM(-25.5, 45.8, RANDOM()), 2) 
        END as QOQ_GROWTH_PERCENT,
        CASE 
            WHEN UNIFORM(0, 1, RANDOM()) < 0.03 THEN NULL  -- 3% NULL for edge case testing
            ELSE ROUND(UNIFORM(-35.2, 85.6, RANDOM()), 2) 
        END as YOY_GROWTH_PERCENT,
        ROUND(UNIFORM(0.8, 18.5, RANDOM()), 2) as MARKET_SHARE_PERCENT,
        ROUND(UNIFORM(2.50, 45.00, RANDOM()), 2) as AVERAGE_CPM,
        ROUND(BASE_REVENUE * UNIFORM(8.5, 25.3, RANDOM()), 2) as IMPRESSION_MILLIONS
    FROM base_revenue
);

-- ============================================================================
-- 3. MARKET_INTELLIGENCE Table
-- ============================================================================

CREATE OR REPLACE TABLE MARKET_INTELLIGENCE (
    INTELLIGENCE_ID VARCHAR(50) PRIMARY KEY,
    COMPETITOR_ID VARCHAR(20) NOT NULL,
    ANALYSIS_QUARTER VARCHAR(2) NOT NULL,
    ANALYSIS_YEAR INTEGER NOT NULL,
    DATA_SOURCE VARCHAR(50) NOT NULL,
    CONTENT_INVESTMENT_CATEGORY VARCHAR(50) NOT NULL,
    CONTENT_INVESTMENT_MILLIONS DECIMAL(12,2),
    SUBSCRIBER_COUNT_MILLIONS DECIMAL(10,2),
    STREAMING_HOURS_BILLIONS DECIMAL(8,2),
    AD_INVENTORY_AVAILABLE DECIMAL(15,0),
    PRICING_PREMIUM_INDEX DECIMAL(5,2),
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (COMPETITOR_ID) REFERENCES COMPETITOR_PROFILES(COMPETITOR_ID)
);

INSERT INTO MARKET_INTELLIGENCE 
SELECT 
    'INT_' || COMPETITOR_ID || '_' || ANALYSIS_YEAR || '_' || ANALYSIS_QUARTER || '_' || ROW_NUMBER() OVER (ORDER BY COMPETITOR_ID) as INTELLIGENCE_ID,
    COMPETITOR_ID,
    ANALYSIS_QUARTER,
    ANALYSIS_YEAR,
    DATA_SOURCE,
    CONTENT_INVESTMENT_CATEGORY,
    CONTENT_INVESTMENT_MILLIONS,
    SUBSCRIBER_COUNT_MILLIONS,
    STREAMING_HOURS_BILLIONS,
    AD_INVENTORY_AVAILABLE,
    PRICING_PREMIUM_INDEX,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as ANALYSIS_QUARTER, 2023 as ANALYSIS_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    sources AS (
        SELECT 'Nielsen' as DATA_SOURCE, 'Original Series' as CONTENT_INVESTMENT_CATEGORY
        UNION ALL SELECT 'ComScore', 'Live Sports'
        UNION ALL SELECT 'Kantar', 'Movies & Films'
        UNION ALL SELECT 'MoffettNathanson', 'News Programming'
        UNION ALL SELECT 'GroupM', 'Unscripted Reality'
        UNION ALL SELECT 'Magna Global', 'International Content'
    ),
    intelligence_data AS (
        SELECT 
            c.COMPETITOR_ID,
            c.COMPETITOR_NAME,
            q.ANALYSIS_QUARTER,
            q.ANALYSIS_YEAR,
            s.DATA_SOURCE,
            s.CONTENT_INVESTMENT_CATEGORY,
            CASE c.COMPETITOR_NAME
                WHEN 'NBCUniversal' THEN 
                    CASE s.CONTENT_INVESTMENT_CATEGORY
                        WHEN 'Original Series' THEN UNIFORM(450, 650, RANDOM())
                        WHEN 'Live Sports' THEN UNIFORM(380, 520, RANDOM())
                        WHEN 'Movies & Films' THEN UNIFORM(280, 420, RANDOM())
                        WHEN 'News Programming' THEN UNIFORM(180, 280, RANDOM())
                        WHEN 'Unscripted Reality' THEN UNIFORM(85, 145, RANDOM())
                        ELSE UNIFORM(65, 125, RANDOM())
                    END
                WHEN 'Disney' THEN 
                    CASE s.CONTENT_INVESTMENT_CATEGORY
                        WHEN 'Original Series' THEN UNIFORM(750, 950, RANDOM())
                        WHEN 'Movies & Films' THEN UNIFORM(580, 780, RANDOM())
                        WHEN 'Live Sports' THEN UNIFORM(480, 650, RANDOM())
                        WHEN 'International Content' THEN UNIFORM(280, 420, RANDOM())
                        WHEN 'Unscripted Reality' THEN UNIFORM(120, 200, RANDOM())
                        ELSE UNIFORM(85, 155, RANDOM())
                    END
                WHEN 'Netflix' THEN 
                    CASE s.CONTENT_INVESTMENT_CATEGORY
                        WHEN 'Original Series' THEN UNIFORM(1200, 1600, RANDOM())
                        WHEN 'International Content' THEN UNIFORM(650, 850, RANDOM())
                        WHEN 'Movies & Films' THEN UNIFORM(450, 650, RANDOM())
                        WHEN 'Unscripted Reality' THEN UNIFORM(180, 280, RANDOM())
                        ELSE UNIFORM(95, 165, RANDOM())
                    END
                ELSE UNIFORM(50, 300, RANDOM())
            END as BASE_INVESTMENT,
            CASE c.COMPETITOR_NAME
                WHEN 'NBCUniversal' THEN UNIFORM(25.5, 35.8, RANDOM())
                WHEN 'Disney' THEN UNIFORM(45.2, 58.9, RANDOM())
                WHEN 'Warner Bros Discovery' THEN UNIFORM(28.6, 38.4, RANDOM())
                WHEN 'Netflix' THEN UNIFORM(238.4, 268.7, RANDOM())
                WHEN 'Amazon Prime Video' THEN UNIFORM(165.8, 195.3, RANDOM())
                WHEN 'Hulu' THEN UNIFORM(42.8, 52.6, RANDOM())
                WHEN 'Paramount Global' THEN UNIFORM(32.5, 45.8, RANDOM())
                WHEN 'TelevisaUnivision' THEN UNIFORM(18.9, 26.7, RANDOM())
                ELSE UNIFORM(5.2, 25.8, RANDOM())
            END as BASE_SUBSCRIBERS
        FROM COMPETITOR_PROFILES c
        CROSS JOIN quarters q
        CROSS JOIN sources s
        WHERE NOT (c.COMPETITOR_NAME IN ('Fox Corporation', 'A+E Networks') AND s.CONTENT_INVESTMENT_CATEGORY = 'Live Sports')
    )
    SELECT 
        COMPETITOR_ID,
        ANALYSIS_QUARTER,
        ANALYSIS_YEAR,
        DATA_SOURCE,
        CONTENT_INVESTMENT_CATEGORY,
        ROUND(BASE_INVESTMENT * 
            CASE ANALYSIS_QUARTER
                WHEN 'Q4' THEN 1.25  -- Holiday content boost
                WHEN 'Q1' THEN 0.75  -- Lower spending
                WHEN 'Q2' THEN 1.10  -- Pilot season
                WHEN 'Q3' THEN 0.90  -- Summer content
                ELSE 1.0
            END, 2) as CONTENT_INVESTMENT_MILLIONS,
        ROUND(BASE_SUBSCRIBERS * 
            CASE ANALYSIS_YEAR
                WHEN 2024 THEN 1.06  -- Growth in 2024
                ELSE 1.0
            END, 2) as SUBSCRIBER_COUNT_MILLIONS,
        ROUND(BASE_SUBSCRIBERS * UNIFORM(8.5, 15.3, RANDOM()), 2) as STREAMING_HOURS_BILLIONS,
        ROUND(BASE_INVESTMENT * UNIFORM(125.5, 285.7, RANDOM()) * 1000000, 0) as AD_INVENTORY_AVAILABLE,
        ROUND(UNIFORM(0.85, 1.45, RANDOM()), 2) as PRICING_PREMIUM_INDEX
    FROM intelligence_data
);

-- ============================================================================
-- 4. PERFORMANCE_METRICS Table
-- ============================================================================

CREATE OR REPLACE TABLE PERFORMANCE_METRICS (
    METRIC_ID VARCHAR(50) PRIMARY KEY,
    COMPETITOR_ID VARCHAR(20) NOT NULL,
    METRIC_QUARTER VARCHAR(2) NOT NULL,
    METRIC_YEAR INTEGER NOT NULL,
    METRIC_CATEGORY VARCHAR(50) NOT NULL,
    MEASUREMENT_TYPE VARCHAR(50) NOT NULL,
    VIEWERSHIP_MILLIONS DECIMAL(10,2),
    ENGAGEMENT_RATE_PERCENT DECIMAL(5,2),
    RETENTION_RATE_PERCENT DECIMAL(5,2),
    BRAND_SENTIMENT_SCORE DECIMAL(4,2),
    SOCIAL_MEDIA_MENTIONS DECIMAL(12,0),
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (COMPETITOR_ID) REFERENCES COMPETITOR_PROFILES(COMPETITOR_ID)
);

INSERT INTO PERFORMANCE_METRICS 
SELECT 
    'MET_' || COMPETITOR_ID || '_' || METRIC_YEAR || '_' || METRIC_QUARTER || '_' || ROW_NUMBER() OVER (ORDER BY COMPETITOR_ID) as METRIC_ID,
    COMPETITOR_ID,
    METRIC_QUARTER,
    METRIC_YEAR,
    METRIC_CATEGORY,
    MEASUREMENT_TYPE,
    VIEWERSHIP_MILLIONS,
    ENGAGEMENT_RATE_PERCENT,
    RETENTION_RATE_PERCENT,
    BRAND_SENTIMENT_SCORE,
    SOCIAL_MEDIA_MENTIONS,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as METRIC_QUARTER, 2023 as METRIC_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    metrics AS (
        SELECT 'Audience Reach' as METRIC_CATEGORY, 'Total Viewership' as MEASUREMENT_TYPE
        UNION ALL SELECT 'Digital Engagement', 'Social Media Interaction'
        UNION ALL SELECT 'Brand Health', 'Consumer Sentiment'
        UNION ALL SELECT 'Content Performance', 'Series Retention'
        UNION ALL SELECT 'Advertising Effectiveness', 'Ad Recall Rate'
        UNION ALL SELECT 'Platform Performance', 'User Retention'
    ),
    performance_data AS (
        SELECT 
            c.COMPETITOR_ID,
            c.COMPETITOR_NAME,
            q.METRIC_QUARTER,
            q.METRIC_YEAR,
            m.METRIC_CATEGORY,
            m.MEASUREMENT_TYPE,
            CASE c.COMPETITOR_NAME
                WHEN 'NBCUniversal' THEN 
                    CASE m.METRIC_CATEGORY
                        WHEN 'Audience Reach' THEN UNIFORM(85.5, 125.8, RANDOM())
                        WHEN 'Digital Engagement' THEN UNIFORM(45.2, 68.9, RANDOM())
                        WHEN 'Content Performance' THEN UNIFORM(28.6, 42.3, RANDOM())
                        ELSE UNIFORM(15.8, 35.4, RANDOM())
                    END
                WHEN 'Disney' THEN 
                    CASE m.METRIC_CATEGORY
                        WHEN 'Audience Reach' THEN UNIFORM(95.8, 145.6, RANDOM())
                        WHEN 'Digital Engagement' THEN UNIFORM(75.4, 98.7, RANDOM())
                        WHEN 'Content Performance' THEN UNIFORM(52.8, 78.9, RANDOM())
                        ELSE UNIFORM(35.6, 58.4, RANDOM())
                    END
                WHEN 'Netflix' THEN 
                    CASE m.METRIC_CATEGORY
                        WHEN 'Audience Reach' THEN UNIFORM(185.6, 245.8, RANDOM())
                        WHEN 'Content Performance' THEN UNIFORM(128.9, 168.7, RANDOM())
                        WHEN 'Digital Engagement' THEN UNIFORM(95.6, 125.8, RANDOM())
                        ELSE UNIFORM(45.8, 78.9, RANDOM())
                    END
                ELSE UNIFORM(20.5, 80.8, RANDOM())
            END as BASE_VIEWERSHIP
        FROM COMPETITOR_PROFILES c
        CROSS JOIN quarters q
        CROSS JOIN metrics m
    )
    SELECT 
        COMPETITOR_ID,
        METRIC_QUARTER,
        METRIC_YEAR,
        METRIC_CATEGORY,
        MEASUREMENT_TYPE,
        ROUND(BASE_VIEWERSHIP, 2) as VIEWERSHIP_MILLIONS,
        ROUND(UNIFORM(2.5, 8.9, RANDOM()), 2) as ENGAGEMENT_RATE_PERCENT,
        ROUND(UNIFORM(72.5, 89.6, RANDOM()), 2) as RETENTION_RATE_PERCENT,
        ROUND(UNIFORM(6.2, 8.8, RANDOM()), 2) as BRAND_SENTIMENT_SCORE,
        ROUND(BASE_VIEWERSHIP * UNIFORM(1250, 3850, RANDOM()), 0) as SOCIAL_MEDIA_MENTIONS
    FROM performance_data
);

-- ============================================================================
-- EDGE CASE DATA INSERTION (Additional scenarios for robust testing)
-- ============================================================================

-- Insert some extreme scenarios for testing
INSERT INTO MI_MICROSTRATEGY_FACT VALUES
-- Extreme negative growth scenario (e.g., during economic downturn)
('REV_EXTREME_001', 'COMP_003', 'Q1', 2024, 'Cable TV', 'Video Commercial', 'Adults 25-54', 'News Programming', 150.25, -45.80, -68.30, 3.25, 8.50, 1250.75, CURRENT_TIMESTAMP()),
-- Zero revenue scenario (new platform launch)
('REV_EXTREME_002', 'COMP_013', 'Q3', 2023, 'Digital Display', 'Banner Ad', 'Adults 18-34', 'Youth Content', 0.00, NULL, NULL, 0.05, 2.50, 0.00, CURRENT_TIMESTAMP()),
-- Very high growth scenario (viral content)
('REV_EXTREME_003', 'COMP_007', 'Q4', 2023, 'Streaming', 'Pre-Roll Video', 'Adults 18-34', 'Original Series', 850.75, 185.50, 245.80, 15.25, 35.75, 24500.50, CURRENT_TIMESTAMP()),
-- Market share concentration (monopolistic scenario)
('REV_EXTREME_004', 'COMP_008', 'Q2', 2024, 'Connected TV', 'Video Commercial', 'Adults 25-54', 'Prime Time Drama', 1250.00, 25.50, 45.75, 85.25, 42.50, 30000.00, CURRENT_TIMESTAMP());

-- Insert NULL scenarios for content investment (testing data completeness)
INSERT INTO MARKET_INTELLIGENCE VALUES
('INT_NULL_001', 'COMP_013', 'Q3', 2023, 'Internal Estimates', 'Original Series', NULL, 2.5, 0.15, 5000000, 0.75, CURRENT_TIMESTAMP()),
('INT_NULL_002', 'COMP_014', 'Q1', 2024, 'Nielsen', 'Local Programming', 15.5, NULL, NULL, 2500000, 1.25, CURRENT_TIMESTAMP());

-- Insert performance metrics with edge cases
INSERT INTO PERFORMANCE_METRICS VALUES
-- Very low performance scenario
('MET_EDGE_001', 'COMP_013', 'Q1', 2024, 'Audience Reach', 'Total Viewership', 0.25, 0.15, 15.50, 3.20, 1500, CURRENT_TIMESTAMP()),
-- Exceptional performance scenario  
('MET_EDGE_002', 'COMP_007', 'Q4', 2023, 'Content Performance', 'Series Retention', 500.75, 25.80, 98.50, 9.85, 2500000, CURRENT_TIMESTAMP()),
-- NULL sentiment score (measurement unavailable)
('MET_EDGE_003', 'COMP_014', 'Q2', 2024, 'Brand Health', 'Consumer Sentiment', 8.50, 3.25, 78.90, NULL, 25000, CURRENT_TIMESTAMP());

-- ============================================================================
-- DATA VALIDATION QUERIES
-- ============================================================================

-- Query 1: Verify table record counts
SELECT 
    'COMPETITOR_PROFILES' as TABLE_NAME,
    COUNT(*) as RECORD_COUNT
FROM COMPETITOR_PROFILES
UNION ALL
SELECT 
    'MI_MICROSTRATEGY_FACT',
    COUNT(*)
FROM MI_MICROSTRATEGY_FACT
UNION ALL
SELECT 
    'MARKET_INTELLIGENCE',
    COUNT(*)
FROM MARKET_INTELLIGENCE
UNION ALL
SELECT 
    'PERFORMANCE_METRICS',
    COUNT(*)
FROM PERFORMANCE_METRICS;

-- Query 2: Verify data relationships
SELECT 
    'Revenue records with valid competitor IDs' as VALIDATION_CHECK,
    COUNT(*) as RECORD_COUNT
FROM MI_MICROSTRATEGY_FACT ar
JOIN COMPETITOR_PROFILES cp ON ar.COMPETITOR_ID = cp.COMPETITOR_ID
UNION ALL
SELECT 
    'Intelligence records with valid competitor IDs',
    COUNT(*)
FROM MARKET_INTELLIGENCE mi
JOIN COMPETITOR_PROFILES cp ON mi.COMPETITOR_ID = cp.COMPETITOR_ID
UNION ALL
SELECT 
    'Performance records with valid competitor IDs',
    COUNT(*)
FROM PERFORMANCE_METRICS pm
JOIN COMPETITOR_PROFILES cp ON pm.COMPETITOR_ID = cp.COMPETITOR_ID;

-- Query 3: Verify quarterly data completeness
SELECT 
    REVENUE_YEAR,
    REVENUE_QUARTER,
    COUNT(DISTINCT COMPETITOR_ID) as COMPETITORS_WITH_DATA,
    COUNT(*) as TOTAL_RECORDS
FROM MI_MICROSTRATEGY_FACT
GROUP BY REVENUE_YEAR, REVENUE_QUARTER
ORDER BY REVENUE_YEAR DESC, REVENUE_QUARTER;

-- Query 4: Sample data preview for each table
SELECT 'COMPETITOR_PROFILES Sample' as DATA_PREVIEW;
SELECT COMPETITOR_NAME, COMPANY_TYPE, MARKET_SEGMENT, MARKET_CAP_BILLIONS
FROM COMPETITOR_PROFILES
LIMIT 5;

SELECT 'MI_MICROSTRATEGY_FACT Sample' as DATA_PREVIEW;
SELECT 
    cp.COMPETITOR_NAME,
    ar.REVENUE_QUARTER,
    ar.REVENUE_YEAR,
    ar.PLATFORM_TYPE,
    ar.AD_REVENUE_MILLIONS,
    ar.MARKET_SHARE_PERCENT
FROM MI_MICROSTRATEGY_FACT ar
JOIN COMPETITOR_PROFILES cp ON ar.COMPETITOR_ID = cp.COMPETITOR_ID
LIMIT 5;

-- Query 5: Revenue totals by competitor and quarter
SELECT 
    cp.COMPETITOR_NAME,
    CONCAT(ar.REVENUE_YEAR, '-', ar.REVENUE_QUARTER) as QUARTER_YEAR,
    ROUND(SUM(ar.AD_REVENUE_MILLIONS), 2) as TOTAL_AD_REVENUE,
    ROUND(AVG(ar.MARKET_SHARE_PERCENT), 2) as AVG_MARKET_SHARE,
    COUNT(*) as PLATFORM_COUNT
FROM MI_MICROSTRATEGY_FACT ar
JOIN COMPETITOR_PROFILES cp ON ar.COMPETITOR_ID = cp.COMPETITOR_ID
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_YEAR, ar.REVENUE_QUARTER
ORDER BY ar.REVENUE_YEAR DESC, ar.REVENUE_QUARTER DESC, TOTAL_AD_REVENUE DESC
LIMIT 20;

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING THE SEMANTIC MODEL
-- ============================================================================

-- Test Query 1: Disney Q1 Performance (matches verified query in YAML)
SELECT 
    cp.COMPETITOR_NAME,
    ar.REVENUE_QUARTER,
    ar.REVENUE_YEAR,
    ROUND(SUM(ar.AD_REVENUE_MILLIONS), 2) as total_ad_revenue,
    ROUND(AVG(ar.MARKET_SHARE_PERCENT), 2) as avg_market_share,
    ROUND(AVG(ar.QOQ_GROWTH_PERCENT), 2) as qoq_growth,
    ROUND(AVG(ar.YOY_GROWTH_PERCENT), 2) as yoy_growth
FROM COMPETITOR_PROFILES cp
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID
WHERE cp.COMPETITOR_NAME = 'Disney' 
  AND ar.REVENUE_QUARTER = 'Q1'
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_QUARTER, ar.REVENUE_YEAR
ORDER BY ar.REVENUE_YEAR DESC;

-- Test Query 2: NBCU vs TelevisaUnivision 2023 Market Share
SELECT 
    cp.COMPETITOR_NAME,
    ar.REVENUE_YEAR,
    ROUND(AVG(ar.MARKET_SHARE_PERCENT), 2) as avg_market_share,
    ROUND(SUM(ar.AD_REVENUE_MILLIONS), 2) as total_revenue,
    ROUND(AVG(ar.YOY_GROWTH_PERCENT), 2) as yoy_growth
FROM COMPETITOR_PROFILES cp
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID
WHERE cp.COMPETITOR_NAME IN ('NBCUniversal', 'TelevisaUnivision')
  AND ar.REVENUE_YEAR = 2023
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_YEAR
ORDER BY avg_market_share DESC;

-- Test Query 3: 5 Quarter Revenue Growth Breakdown
SELECT 
    cp.COMPETITOR_NAME,
    CONCAT(ar.REVENUE_YEAR, '-', ar.REVENUE_QUARTER) as quarter_year,
    ROUND(SUM(ar.AD_REVENUE_MILLIONS), 2) as total_revenue,
    ROUND(AVG(ar.QOQ_GROWTH_PERCENT), 2) as qoq_growth,
    ROUND(AVG(ar.YOY_GROWTH_PERCENT), 2) as yoy_growth,
    ROUND(AVG(ar.MARKET_SHARE_PERCENT), 2) as market_share
FROM COMPETITOR_PROFILES cp
JOIN MI_MICROSTRATEGY_FACT ar ON cp.COMPETITOR_ID = ar.COMPETITOR_ID
WHERE (ar.REVENUE_YEAR = 2024 AND ar.REVENUE_QUARTER IN ('Q1', 'Q2', 'Q3'))
   OR (ar.REVENUE_YEAR = 2023 AND ar.REVENUE_QUARTER IN ('Q3', 'Q4'))
GROUP BY cp.COMPETITOR_NAME, ar.REVENUE_YEAR, ar.REVENUE_QUARTER
ORDER BY ar.REVENUE_YEAR DESC, ar.REVENUE_QUARTER DESC, total_revenue DESC;

-- ============================================================================
-- ENHANCED DATA QUALITY VALIDATION QUERIES
-- ============================================================================

-- Query 6: Edge Cases and Data Quality Validation
SELECT 
    'NULL Value Analysis' as VALIDATION_TYPE,
    'QOQ_GROWTH_PERCENT' as FIELD_NAME,
    COUNT(*) as NULL_COUNT,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM MI_MICROSTRATEGY_FACT)) as NULL_PERCENTAGE
FROM MI_MICROSTRATEGY_FACT 
WHERE QOQ_GROWTH_PERCENT IS NULL
UNION ALL
SELECT 
    'NULL Value Analysis',
    'YOY_GROWTH_PERCENT',
    COUNT(*),
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM MI_MICROSTRATEGY_FACT))
FROM MI_MICROSTRATEGY_FACT 
WHERE YOY_GROWTH_PERCENT IS NULL
UNION ALL
SELECT 
    'NULL Value Analysis',
    'MARKET_CAP_BILLIONS',
    COUNT(*),
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM COMPETITOR_PROFILES))
FROM COMPETITOR_PROFILES 
WHERE MARKET_CAP_BILLIONS IS NULL;

-- Query 7: Extreme Values Validation
SELECT 
    'Extreme Values Check' as VALIDATION_TYPE,
    'High Growth (>50%)' as SCENARIO,
    COUNT(*) as RECORD_COUNT
FROM MI_MICROSTRATEGY_FACT 
WHERE YOY_GROWTH_PERCENT > 50
UNION ALL
SELECT 
    'Extreme Values Check',
    'Negative Growth (<-20%)',
    COUNT(*)
FROM MI_MICROSTRATEGY_FACT 
WHERE YOY_GROWTH_PERCENT < -20
UNION ALL
SELECT 
    'Extreme Values Check',
    'Zero Revenue',
    COUNT(*)
FROM MI_MICROSTRATEGY_FACT 
WHERE AD_REVENUE_MILLIONS = 0
UNION ALL
SELECT 
    'Extreme Values Check',
    'High Market Share (>50%)',
    COUNT(*)
FROM MI_MICROSTRATEGY_FACT 
WHERE MARKET_SHARE_PERCENT > 50;

-- Query 8: Seasonal Pattern Validation
SELECT 
    REVENUE_QUARTER,
    ROUND(AVG(AD_REVENUE_MILLIONS), 2) as AVG_REVENUE,
    ROUND(STDDEV(AD_REVENUE_MILLIONS), 2) as REVENUE_STDDEV,
    COUNT(*) as RECORD_COUNT
FROM MI_MICROSTRATEGY_FACT
GROUP BY REVENUE_QUARTER
ORDER BY 
    CASE REVENUE_QUARTER 
        WHEN 'Q1' THEN 1 
        WHEN 'Q2' THEN 2 
        WHEN 'Q3' THEN 3 
        WHEN 'Q4' THEN 4 
    END;

-- Query 9: Data Type Precision Validation
SELECT 
    'Decimal Precision Check' as VALIDATION_TYPE,
    'Market Share >100%' as CHECK_DESCRIPTION,
    COUNT(*) as VIOLATION_COUNT
FROM MI_MICROSTRATEGY_FACT 
WHERE MARKET_SHARE_PERCENT > 100
UNION ALL
SELECT 
    'Decimal Precision Check',
    'Negative CPM Values',
    COUNT(*)
FROM MI_MICROSTRATEGY_FACT 
WHERE AVERAGE_CPM < 0
UNION ALL
SELECT 
    'Decimal Precision Check',
    'Brand Sentiment >10',
    COUNT(*)
FROM PERFORMANCE_METRICS 
WHERE BRAND_SENTIMENT_SCORE > 10;

-- ============================================================================
-- GRANTS AND PERMISSIONS (Optional - adjust as needed)
-- ============================================================================

-- Grant appropriate permissions to roles (adjust role names as needed)
-- GRANT SELECT ON ALL TABLES IN SCHEMA STRATEGY_CLIENT.DEV TO ROLE DATA_ANALYST;
-- GRANT SELECT ON ALL TABLES IN SCHEMA STRATEGY_CLIENT.DEV TO ROLE BUSINESS_USER;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================

SELECT 'NBCUniversal Project Nexus Data Setup Complete!' as STATUS,
       'All tables created with synthetic data for competitive analytics' as DESCRIPTION;