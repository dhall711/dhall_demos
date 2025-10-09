-- =====================================================
-- UDX Dynamic Pricing POC - Synthetic Data Generation
-- Snowflake SQL Script for ML/AI Proof of Concept
-- =====================================================

-- Set up database and schema for POC
CREATE OR REPLACE DATABASE UDX_PRICING_POC;
USE DATABASE UDX_PRICING_POC;
CREATE OR REPLACE SCHEMA PRICING_DATA;
USE SCHEMA PRICING_DATA;

-- =====================================================
-- DATA OVERVIEW AND SUMMARY
-- =====================================================
-- 
-- PURPOSE:
-- This script generates comprehensive synthetic data for UDX's Dynamic Pricing POC
-- to demonstrate Snowflake ML capabilities vs. current Databricks round-trip architecture.
-- Based on transcript requirements from Slalom-Snowflake-UDX partnership discussion.
--
-- BUSINESS CONTEXT:
-- - Current state: Manual pricing process taking 3-4 weeks
-- - Future state: Daily dynamic pricing with automated workflows
-- - Challenge: Eliminate data round-trip (Snowflake → Azure Synapse → Databricks → Email)
-- - Solution: Snowpark ML for unified platform approach
--
-- =====================================================
-- CORE DATA TABLES (5 primary sources mentioned in transcript):
-- =====================================================
--
-- 1. HISTORICAL_SALES (730 days × 4 parks × 6 ticket types × 6 channels × 6 segments)
--    - Purpose: Transaction volumes, revenue metrics, seasonal patterns
--    - Volume: ~40,000 records (2 years of sales data)
--    - Key Features: Seasonal demand patterns, day-of-week effects, weather correlation
--    - Business Logic: Peak seasons (Jun-Aug, Dec), shoulder seasons, local holidays
--    - ML Use Cases: Demand forecasting, price elasticity modeling, segment analysis
--
-- 2. HISTORICAL_PRICING (730 days × 4 parks × 6 ticket types)
--    - Purpose: Price points, elasticity measurements, competitive positioning  
--    - Volume: ~4,400 records (2 years of pricing decisions)
--    - Key Features: Base vs dynamic pricing, competitor intelligence, constraint flags
--    - Business Logic: Seasonal price adjustments, partner agreement compliance
--    - ML Use Cases: Price optimization, elasticity modeling, constraint enforcement
--
-- 3. WEATHER_DATA (1095 days × 4 parks)
--    - Purpose: Real-time and forecasted weather for immediate pricing adjustments
--    - Volume: ~4,400 records (3 years including forecasts)
--    - Key Features: Climate-appropriate patterns, severity scoring, forecast confidence
--    - Business Logic: Different climate zones (tropical, subtropical, temperate, mediterranean)
--    - ML Use Cases: Weather impact modeling, real-time price adjustments
--
-- 4. CAPACITY_DATA (180 days × 4 parks)
--    - Purpose: Static park capacity, dynamic utilization metrics
--    - Volume: ~720 records (6 months forward-looking)
--    - Key Features: Reserved vs available capacity, maintenance impacts, constraint levels
--    - Business Logic: Capacity allocation (walkup 15%, VIP 5%, groups 10%)
--    - ML Use Cases: Capacity-based pricing, utilization optimization
--
-- 5. FINANCIAL_FORECAST (18 months × 4 parks)
--    - Purpose: Accounting alignment data for revenue recognition
--    - Volume: ~72 records (monthly forecasts by park)
--    - Key Features: Revenue targets, margin requirements, pricing flexibility
--    - Business Logic: Seasonal revenue patterns, strategic priorities
--    - ML Use Cases: Target-based optimization, margin constraint modeling
--
-- =====================================================
-- SUPPORTING BUSINESS LOGIC TABLES:
-- =====================================================
--
-- 6. PRICING_CONSTRAINTS (8 sample constraints)
--    - Purpose: Partner agreements, marketing restrictions, competitive protocols
--    - Key Features: Price limits, advance notice requirements, penalty structures
--    - Business Context: Hotel partners (7-14 day notice), Travel agents (21 day notice)
--    - ML Use Cases: Constraint validation, automated compliance checking
--
-- 7. DEMAND_ELASTICITY_REFERENCE (12 elasticity profiles)
--    - Purpose: Historical elasticity measurements by segment and season
--    - Key Features: Elasticity ranges (-3.0 to -0.5), confidence levels, optimal price ranges
--    - Business Context: Family leisure most price-sensitive, VIP least sensitive
--    - ML Use Cases: Elasticity-based pricing models, demand prediction
--
-- =====================================================
-- PARK CODES AND LOCATIONS:
-- =====================================================
-- UDX_ORLANDO    - Universal Studios Orlando (Subtropical climate, 25k capacity)
-- UDX_HOLLYWOOD  - Universal Studios Hollywood (Mediterranean climate, 15k capacity)  
-- UDX_JAPAN      - Universal Studios Japan (Temperate climate, 20k capacity)
-- UDX_SINGAPORE  - Universal Studios Singapore (Tropical climate, 12k capacity)
--
-- =====================================================
-- TICKET TYPES AND PRICING RANGES:
-- =====================================================
-- SINGLE_DAY_GENERAL  - $99-149 (Base admission, highest volume)
-- SINGLE_DAY_EXPRESS  - $169-249 (Express pass included, premium option)
-- MULTI_DAY_2         - $189-229 (2-day park-to-park)
-- MULTI_DAY_3         - $249-299 (3-day park-to-park)
-- SEASON_PASS         - $399-499 (Annual pass, lowest daily volume)
-- VIP_EXPERIENCE      - $449-599 (Premium experience, lowest price sensitivity)
--
-- =====================================================
-- SEASONAL PATTERNS BUILT INTO DATA:
-- =====================================================
-- PEAK SEASONS:    Jun-Aug (Summer), Dec (Holidays) - 25-40% price premiums
-- SHOULDER SEASONS: Mar-May, Sep-Nov - Standard pricing with 5-15% variation
-- LOW SEASONS:     Jan-Feb, Oct (post-summer) - 5-20% discounts
-- 
-- DAY-OF-WEEK PATTERNS:
-- Monday-Tuesday:   Lowest demand (20-30% below average)
-- Wednesday-Thursday: Moderate demand (10% below to average)
-- Friday:           Above average (10-20% premium)
-- Saturday-Sunday:  Peak demand (30-50% premium)
--
-- =====================================================
-- ML FEATURE ENGINEERING:
-- =====================================================
-- 
-- ML_FEATURES_DAILY View combines all sources with derived features:
-- - Price premiums vs base pricing
-- - Revenue achievement vs targets  
-- - Competitive positioning indicators
-- - Advance booking patterns
-- - Weather impact correlations
-- - Capacity utilization relationships
--
-- Ready for Snowpark ML model training:
-- - Demand forecasting models
-- - Price elasticity estimation
-- - Constrained optimization algorithms
-- - Real-time pricing adjustments
--
-- =====================================================
-- POC DEMONSTRATION SCENARIOS:
-- =====================================================
-- 1. Weather Impact: Show price adjustments for weather severity > 7
-- 2. Capacity Constraints: Demonstrate pricing when utilization > 85%
-- 3. Partner Compliance: Validate pricing against hotel/OTA agreements
-- 4. Competitive Response: Model rapid price changes within 3-day notice
-- 5. Seasonal Optimization: Compare peak vs low season pricing strategies
-- 6. Real-time Processing: Demonstrate sub-hourly price adjustments
--
-- =====================================================
-- SNOWFLAKE ML CAPABILITIES TO DEMONSTRATE:
-- =====================================================
-- - Snowpark ML model training without data movement
-- - Real-time inference with stored procedures
-- - Automated constraint validation using SQL
-- - Integration with external APIs (weather, competitor pricing)
-- - Scalable processing for daily batch and real-time workloads
-- - Cost optimization vs Databricks round-trip architecture
--
-- =====================================================

-- =====================================================
-- 1. HISTORICAL SALES DATA
-- Transaction volumes, revenue metrics, seasonal patterns
-- =====================================================

CREATE OR REPLACE TABLE HISTORICAL_SALES (
    SALES_DATE DATE,
    PARK_CODE VARCHAR(20),
    TICKET_TYPE VARCHAR(50),
    ADMISSION_DATE DATE,
    TICKETS_SOLD INTEGER,
    TOTAL_REVENUE DECIMAL(12,2),
    AVERAGE_PRICE DECIMAL(8,2),
    CHANNEL VARCHAR(30),
    GUEST_SEGMENT VARCHAR(30),
    WEATHER_CONDITION VARCHAR(20),
    DAY_OF_WEEK INTEGER,
    IS_HOLIDAY BOOLEAN,
    IS_SCHOOL_BREAK BOOLEAN,
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Generate 2 years of historical sales data
INSERT INTO HISTORICAL_SALES
WITH date_spine AS (
    SELECT DATEADD(day, seq4(), '2022-01-01'::date) as sales_date
    FROM table(generator(rowcount => 730))
),
parks AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO', 'Universal Studios Orlando'),
    ('UDX_HOLLYWOOD', 'Universal Studios Hollywood'),
    ('UDX_JAPAN', 'Universal Studios Japan'),
    ('UDX_SINGAPORE', 'Universal Studios Singapore')
    AS t(park_code, park_name)
),
ticket_types AS (
    SELECT * FROM VALUES
    ('SINGLE_DAY_GENERAL', 'Single Day General Admission'),
    ('SINGLE_DAY_EXPRESS', 'Single Day with Express Pass'),
    ('MULTI_DAY_2', '2-Day Park-to-Park'),
    ('MULTI_DAY_3', '3-Day Park-to-Park'),
    ('SEASON_PASS', 'Annual Season Pass'),
    ('VIP_EXPERIENCE', 'VIP Experience Package')
    AS t(ticket_type, ticket_description)
),
channels AS (
    SELECT * FROM VALUES
    ('DIRECT_ONLINE', 'Direct Website Sales'),
    ('DIRECT_GATE', 'Gate Sales'),
    ('HOTEL_PARTNER', 'Hotel Partner Sales'),
    ('TRAVEL_AGENT', 'Travel Agent Sales'),
    ('OTA_PARTNER', 'Online Travel Agency'),
    ('CORPORATE', 'Corporate Group Sales')
    AS t(channel, channel_description)
),
segments AS (
    SELECT * FROM VALUES
    ('FAMILY_LEISURE', 'Family Leisure Travelers'),
    ('ADULT_COUPLE', 'Adult Couples'),
    ('INTERNATIONAL', 'International Tourists'),
    ('LOCAL_RESIDENT', 'Local Residents'),
    ('BUSINESS_TRAVELER', 'Business Travelers'),
    ('STUDENT_GROUP', 'Student Groups')
    AS t(guest_segment, segment_description)
)
SELECT 
    d.sales_date,
    p.park_code,
    t.ticket_type,
    DATEADD(day, FLOOR(UNIFORM(0, 90, RANDOM())), d.sales_date) as admission_date,
    -- Seasonal and day-of-week patterns for ticket sales
    FLOOR(
        CASE 
            WHEN MONTH(d.sales_date) IN (6,7,8,12) THEN UNIFORM(150, 800, RANDOM()) -- Peak seasons
            WHEN MONTH(d.sales_date) IN (1,2,9,10) THEN UNIFORM(50, 300, RANDOM()) -- Low seasons
            ELSE UNIFORM(80, 500, RANDOM()) -- Shoulder seasons
        END *
        CASE DAYOFWEEK(d.sales_date)
            WHEN 1 THEN 1.4  -- Sunday
            WHEN 2 THEN 0.7  -- Monday
            WHEN 3 THEN 0.8  -- Tuesday
            WHEN 4 THEN 0.9  -- Wednesday
            WHEN 5 THEN 1.0  -- Thursday
            WHEN 6 THEN 1.3  -- Friday
            WHEN 7 THEN 1.5  -- Saturday
        END *
        CASE t.ticket_type
            WHEN 'SINGLE_DAY_GENERAL' THEN 1.0
            WHEN 'SINGLE_DAY_EXPRESS' THEN 0.4
            WHEN 'MULTI_DAY_2' THEN 0.3
            WHEN 'MULTI_DAY_3' THEN 0.2
            WHEN 'SEASON_PASS' THEN 0.1
            WHEN 'VIP_EXPERIENCE' THEN 0.05
        END
    ) as tickets_sold,
    0 as total_revenue, -- Will calculate after insert
    -- Base pricing with seasonal adjustments
    CASE t.ticket_type
        WHEN 'SINGLE_DAY_GENERAL' THEN 
            CASE 
                WHEN MONTH(d.sales_date) IN (6,7,8,12) THEN UNIFORM(129, 149, RANDOM())
                WHEN MONTH(d.sales_date) IN (1,2,9,10) THEN UNIFORM(99, 119, RANDOM())
                ELSE UNIFORM(109, 129, RANDOM())
            END
        WHEN 'SINGLE_DAY_EXPRESS' THEN 
            CASE 
                WHEN MONTH(d.sales_date) IN (6,7,8,12) THEN UNIFORM(199, 249, RANDOM())
                ELSE UNIFORM(169, 199, RANDOM())
            END
        WHEN 'MULTI_DAY_2' THEN UNIFORM(189, 229, RANDOM())
        WHEN 'MULTI_DAY_3' THEN UNIFORM(249, 299, RANDOM())
        WHEN 'SEASON_PASS' THEN UNIFORM(399, 499, RANDOM())
        WHEN 'VIP_EXPERIENCE' THEN UNIFORM(449, 599, RANDOM())
    END as average_price,
    c.channel,
    s.guest_segment,
    CASE FLOOR(UNIFORM(1, 11, RANDOM()))
        WHEN 1 THEN 'SUNNY'
        WHEN 2 THEN 'PARTLY_CLOUDY'
        WHEN 3 THEN 'CLOUDY'
        WHEN 4 THEN 'LIGHT_RAIN'
        WHEN 5 THEN 'HEAVY_RAIN'
        WHEN 6 THEN 'SUNNY'
        WHEN 7 THEN 'SUNNY'
        WHEN 8 THEN 'PARTLY_CLOUDY'
        WHEN 9 THEN 'SUNNY'
        ELSE 'PARTLY_CLOUDY'
    END as weather_condition,
    DAYOFWEEK(d.sales_date) as day_of_week,
    CASE 
        WHEN d.sales_date IN ('2022-01-01', '2022-07-04', '2022-11-24', '2022-12-25', 
                              '2023-01-01', '2023-07-04', '2023-11-23', '2023-12-25') THEN TRUE
        ELSE FALSE
    END as is_holiday,
    CASE 
        WHEN MONTH(d.sales_date) IN (6,7,8) OR 
             (MONTH(d.sales_date) = 12 AND DAY(d.sales_date) > 15) OR
             (MONTH(d.sales_date) = 3 AND DAY(d.sales_date) BETWEEN 15 AND 25) THEN TRUE
        ELSE FALSE
    END as is_school_break,
    CURRENT_TIMESTAMP()
FROM date_spine d
CROSS JOIN parks p
CROSS JOIN ticket_types t
CROSS JOIN channels c
CROSS JOIN segments s
WHERE UNIFORM(0, 1, RANDOM()) < 0.15; -- Sample roughly 15% of all combinations

-- Update total revenue based on tickets sold and average price
UPDATE HISTORICAL_SALES 
SET total_revenue = tickets_sold * average_price;

-- =====================================================
-- 2. HISTORICAL PRICING DATA
-- Historical price points, elasticity measurements, competitive positioning
-- =====================================================

CREATE OR REPLACE TABLE HISTORICAL_PRICING (
    PRICING_DATE DATE,
    PARK_CODE VARCHAR(20),
    TICKET_TYPE VARCHAR(50),
    ADMISSION_DATE_START DATE,
    ADMISSION_DATE_END DATE,
    BASE_PRICE DECIMAL(8,2),
    DYNAMIC_PRICE DECIMAL(8,2),
    PRICE_TIER VARCHAR(20),
    DEMAND_LEVEL VARCHAR(20),
    CAPACITY_UTILIZATION DECIMAL(5,2),
    PRICE_ELASTICITY DECIMAL(6,4),
    COMPETITOR_AVG_PRICE DECIMAL(8,2),
    MARKETING_CAMPAIGN_ACTIVE BOOLEAN,
    PARTNER_CONSTRAINTS_ACTIVE BOOLEAN,
    PRICE_CHANGE_REASON VARCHAR(100),
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO HISTORICAL_PRICING
WITH pricing_dates AS (
    SELECT DATEADD(day, seq4(), '2022-01-01'::date) as pricing_date
    FROM table(generator(rowcount => 730))
),
parks AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO', 'Universal Studios Orlando'),
    ('UDX_HOLLYWOOD', 'Universal Studios Hollywood'),
    ('UDX_JAPAN', 'Universal Studios Japan'),
    ('UDX_SINGAPORE', 'Universal Studios Singapore')
    AS t(park_code, park_name)
),
ticket_types AS (
    SELECT * FROM VALUES
    ('SINGLE_DAY_GENERAL', 109.00),
    ('SINGLE_DAY_EXPRESS', 179.00),
    ('MULTI_DAY_2', 199.00),
    ('MULTI_DAY_3', 259.00),
    ('SEASON_PASS', 449.00),
    ('VIP_EXPERIENCE', 499.00)
    AS t(ticket_type, base_price)
)
SELECT 
    p.pricing_date,
    pk.park_code,
    t.ticket_type,
    DATEADD(day, FLOOR(UNIFORM(1, 14, RANDOM())), p.pricing_date) as admission_date_start,
    DATEADD(day, FLOOR(UNIFORM(15, 90, RANDOM())), p.pricing_date) as admission_date_end,
    t.base_price,
    -- Dynamic pricing based on demand and seasonality
    t.base_price * (
        1 + 
        CASE 
            WHEN MONTH(p.pricing_date) IN (6,7,8,12) THEN UNIFORM(0.15, 0.35, RANDOM()) -- Peak season uplift
            WHEN MONTH(p.pricing_date) IN (1,2,9,10) THEN UNIFORM(-0.20, -0.05, RANDOM()) -- Low season discount
            ELSE UNIFORM(-0.05, 0.15, RANDOM()) -- Shoulder season variation
        END +
        CASE DAYOFWEEK(p.pricing_date)
            WHEN 1 THEN UNIFORM(0.05, 0.15, RANDOM())  -- Sunday premium
            WHEN 2 THEN UNIFORM(-0.15, -0.05, RANDOM())  -- Monday discount
            WHEN 3 THEN UNIFORM(-0.10, 0.00, RANDOM())   -- Tuesday slight discount
            WHEN 4 THEN UNIFORM(-0.05, 0.05, RANDOM())   -- Wednesday neutral
            WHEN 5 THEN UNIFORM(0.00, 0.10, RANDOM())    -- Thursday slight premium
            WHEN 6 THEN UNIFORM(0.10, 0.20, RANDOM())    -- Friday premium
            WHEN 7 THEN UNIFORM(0.15, 0.25, RANDOM())    -- Saturday highest premium
        END
    ) as dynamic_price,
    CASE 
        WHEN UNIFORM(0, 1, RANDOM()) < 0.2 THEN 'PREMIUM'
        WHEN UNIFORM(0, 1, RANDOM()) < 0.6 THEN 'STANDARD'
        ELSE 'VALUE'
    END as price_tier,
    CASE 
        WHEN MONTH(p.pricing_date) IN (6,7,8,12) THEN 
            CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.7 THEN 'HIGH' ELSE 'VERY_HIGH' END
        WHEN MONTH(p.pricing_date) IN (1,2,9,10) THEN 
            CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.6 THEN 'LOW' ELSE 'MEDIUM' END
        ELSE 
            CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.5 THEN 'MEDIUM' ELSE 'HIGH' END
    END as demand_level,
    UNIFORM(0.45, 0.95, RANDOM()) as capacity_utilization,
    UNIFORM(-2.5, -0.8, RANDOM()) as price_elasticity, -- Typical elasticity for leisure activities
    -- Competitor pricing (anonymized)
    t.base_price * UNIFORM(0.95, 1.15, RANDOM()) as competitor_avg_price,
    UNIFORM(0, 1, RANDOM()) < 0.3 as marketing_campaign_active,
    UNIFORM(0, 1, RANDOM()) < 0.25 as partner_constraints_active,
    CASE FLOOR(UNIFORM(1, 8, RANDOM()))
        WHEN 1 THEN 'Seasonal Demand Adjustment'
        WHEN 2 THEN 'Weather Impact Pricing'
        WHEN 3 THEN 'Capacity Optimization'
        WHEN 4 THEN 'Competitive Response'
        WHEN 5 THEN 'Marketing Campaign Support'
        WHEN 6 THEN 'Partner Agreement Compliance'
        ELSE 'Regular Optimization'
    END as price_change_reason,
    CURRENT_TIMESTAMP()
FROM pricing_dates p
CROSS JOIN parks pk
CROSS JOIN ticket_types t
WHERE UNIFORM(0, 1, RANDOM()) < 0.25; -- Sample 25% of combinations

-- =====================================================
-- 3. WEATHER DATA
-- Real-time and forecasted weather data for pricing adjustments
-- =====================================================

CREATE OR REPLACE TABLE WEATHER_DATA (
    WEATHER_DATE DATE,
    PARK_CODE VARCHAR(20),
    TEMPERATURE_HIGH INTEGER,
    TEMPERATURE_LOW INTEGER,
    PRECIPITATION_PROBABILITY INTEGER,
    PRECIPITATION_AMOUNT DECIMAL(4,2),
    WEATHER_CONDITION VARCHAR(30),
    WIND_SPEED INTEGER,
    HUMIDITY INTEGER,
    UV_INDEX INTEGER,
    WEATHER_SEVERITY_SCORE INTEGER, -- 1-10 scale for pricing impact
    IS_FORECAST BOOLEAN,
    FORECAST_CONFIDENCE DECIMAL(3,2),
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO WEATHER_DATA
WITH weather_dates AS (
    SELECT DATEADD(day, seq4(), '2022-01-01'::date) as weather_date
    FROM table(generator(rowcount => 1095)) -- 3 years including forecast
),
parks_weather AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO', 27.0, 85, 'Subtropical'),     -- Orlando climate
    ('UDX_HOLLYWOOD', 22.0, 65, 'Mediterranean'), -- LA climate  
    ('UDX_JAPAN', 15.0, 70, 'Temperate'),         -- Osaka climate
    ('UDX_SINGAPORE', 29.0, 90, 'Tropical')       -- Singapore climate
    AS t(park_code, avg_temp, avg_humidity, climate_type)
)
SELECT 
    w.weather_date,
    p.park_code,
    -- Temperature with seasonal variation
    FLOOR(p.avg_temp + 
        CASE 
            WHEN MONTH(w.weather_date) IN (12,1,2) THEN UNIFORM(-8, -2, RANDOM()) -- Winter
            WHEN MONTH(w.weather_date) IN (6,7,8) THEN UNIFORM(3, 8, RANDOM())   -- Summer
            ELSE UNIFORM(-3, 3, RANDOM()) -- Spring/Fall
        END * 
        CASE p.climate_type
            WHEN 'Tropical' THEN 0.5      -- Less temperature variation
            WHEN 'Subtropical' THEN 0.8
            WHEN 'Mediterranean' THEN 1.0
            WHEN 'Temperate' THEN 1.2     -- More temperature variation
        END
    ) * 9/5 + 32 as temperature_high, -- Convert to Fahrenheit
    
    FLOOR(p.avg_temp + 
        CASE 
            WHEN MONTH(w.weather_date) IN (12,1,2) THEN UNIFORM(-12, -6, RANDOM())
            WHEN MONTH(w.weather_date) IN (6,7,8) THEN UNIFORM(-2, 3, RANDOM())
            ELSE UNIFORM(-7, -2, RANDOM())
        END * 
        CASE p.climate_type
            WHEN 'Tropical' THEN 0.5
            WHEN 'Subtropical' THEN 0.8
            WHEN 'Mediterranean' THEN 1.0
            WHEN 'Temperate' THEN 1.2
        END
    ) * 9/5 + 32 as temperature_low,
    
    -- Precipitation probability based on season and climate
    FLOOR(
        CASE p.climate_type
            WHEN 'Tropical' THEN UNIFORM(20, 80, RANDOM())
            WHEN 'Subtropical' THEN 
                CASE WHEN MONTH(w.weather_date) IN (6,7,8,9) THEN UNIFORM(40, 90, RANDOM())
                     ELSE UNIFORM(10, 40, RANDOM()) END
            WHEN 'Mediterranean' THEN 
                CASE WHEN MONTH(w.weather_date) IN (12,1,2,3) THEN UNIFORM(30, 70, RANDOM())
                     ELSE UNIFORM(5, 25, RANDOM()) END
            WHEN 'Temperate' THEN UNIFORM(25, 65, RANDOM())
        END
    ) as precipitation_probability,
    
    CASE WHEN UNIFORM(0, 100, RANDOM()) < 
        CASE p.climate_type
            WHEN 'Tropical' THEN 45
            WHEN 'Subtropical' THEN 35
            WHEN 'Mediterranean' THEN 20
            WHEN 'Temperate' THEN 30
        END
    THEN UNIFORM(0.01, 2.5, RANDOM()) ELSE 0.00 END as precipitation_amount,
    
    CASE FLOOR(UNIFORM(1, 11, RANDOM()))
        WHEN 1 THEN 'Clear Skies'
        WHEN 2 THEN 'Partly Cloudy'
        WHEN 3 THEN 'Mostly Cloudy'
        WHEN 4 THEN 'Overcast'
        WHEN 5 THEN 'Light Rain'
        WHEN 6 THEN 'Moderate Rain'
        WHEN 7 THEN 'Heavy Rain'
        WHEN 8 THEN 'Thunderstorms'
        WHEN 9 THEN 'Clear Skies'
        ELSE 'Partly Cloudy'
    END as weather_condition,
    
    FLOOR(UNIFORM(3, 25, RANDOM())) as wind_speed,
    FLOOR(p.avg_humidity + UNIFORM(-20, 20, RANDOM())) as humidity,
    FLOOR(UNIFORM(1, 11, RANDOM())) as uv_index,
    
    -- Weather severity score (1=perfect, 10=severe impact on park operations)
    CASE 
        WHEN precipitation_amount > 1.5 THEN FLOOR(UNIFORM(7, 10, RANDOM()))
        WHEN precipitation_amount > 0.5 THEN FLOOR(UNIFORM(4, 7, RANDOM()))
        WHEN temperature_high > 95 OR temperature_high < 40 THEN FLOOR(UNIFORM(5, 8, RANDOM()))
        WHEN wind_speed > 20 THEN FLOOR(UNIFORM(4, 7, RANDOM()))
        ELSE FLOOR(UNIFORM(1, 4, RANDOM()))
    END as weather_severity_score,
    
    w.weather_date > CURRENT_DATE() as is_forecast,
    CASE WHEN w.weather_date > CURRENT_DATE() 
         THEN UNIFORM(0.60, 0.95, RANDOM()) 
         ELSE 1.00 END as forecast_confidence,
    CURRENT_TIMESTAMP()
FROM weather_dates w
CROSS JOIN parks_weather p;

-- =====================================================
-- 4. CAPACITY AND INVENTORY DATA
-- Static park capacity data, dynamic utilization metrics
-- =====================================================

CREATE OR REPLACE TABLE CAPACITY_DATA (
    CAPACITY_DATE DATE,
    PARK_CODE VARCHAR(20),
    TOTAL_DAILY_CAPACITY INTEGER,
    RESERVED_CAPACITY INTEGER,
    AVAILABLE_CAPACITY INTEGER,
    CURRENT_RESERVATIONS INTEGER,
    WALKUP_CAPACITY INTEGER,
    VIP_CAPACITY INTEGER,
    GROUP_CAPACITY INTEGER,
    SPECIAL_EVENT_CAPACITY INTEGER,
    MAINTENANCE_IMPACT_CAPACITY INTEGER,
    WEATHER_ADJUSTED_CAPACITY INTEGER,
    CAPACITY_UTILIZATION_FORECAST DECIMAL(5,2),
    PRICING_CONSTRAINT_LEVEL VARCHAR(20),
    LAST_UPDATED TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO CAPACITY_DATA
WITH capacity_dates AS (
    SELECT DATEADD(day, seq4(), CURRENT_DATE()) as capacity_date
    FROM table(generator(rowcount => 180)) -- 6 months forward
),
park_capacities AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO', 25000, 'Large'),
    ('UDX_HOLLYWOOD', 15000, 'Medium'),
    ('UDX_JAPAN', 20000, 'Medium-Large'),
    ('UDX_SINGAPORE', 12000, 'Medium')
    AS t(park_code, base_capacity, size_category)
)
SELECT 
    c.capacity_date,
    p.park_code,
    p.base_capacity as total_daily_capacity,
    -- Reserved capacity varies by demand patterns
    FLOOR(p.base_capacity * 
        CASE 
            WHEN MONTH(c.capacity_date) IN (6,7,8,12) THEN UNIFORM(0.75, 0.95, RANDOM()) -- Peak seasons
            WHEN MONTH(c.capacity_date) IN (1,2,9,10) THEN UNIFORM(0.35, 0.65, RANDOM()) -- Low seasons
            ELSE UNIFORM(0.55, 0.80, RANDOM()) -- Shoulder seasons
        END *
        CASE DAYOFWEEK(c.capacity_date)
            WHEN 1 THEN 0.9   -- Sunday
            WHEN 2 THEN 0.5   -- Monday
            WHEN 3 THEN 0.6   -- Tuesday
            WHEN 4 THEN 0.7   -- Wednesday
            WHEN 5 THEN 0.8   -- Thursday
            WHEN 6 THEN 0.95  -- Friday
            WHEN 7 THEN 1.0   -- Saturday
        END
    ) as reserved_capacity,
    0 as available_capacity, -- Will calculate
    0 as current_reservations, -- Will calculate
    FLOOR(p.base_capacity * 0.15) as walkup_capacity, -- 15% held for walkups
    FLOOR(p.base_capacity * 0.05) as vip_capacity,    -- 5% for VIP
    FLOOR(p.base_capacity * 0.10) as group_capacity,  -- 10% for groups
    CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.1 
         THEN FLOOR(p.base_capacity * UNIFORM(0.05, 0.20, RANDOM())) 
         ELSE 0 END as special_event_capacity,
    -- Maintenance impact (random attractions down)
    CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.15 
         THEN FLOOR(p.base_capacity * UNIFORM(0.02, 0.08, RANDOM())) 
         ELSE 0 END as maintenance_impact_capacity,
    0 as weather_adjusted_capacity, -- Will calculate based on weather
    0 as capacity_utilization_forecast, -- Will calculate
    CASE 
        WHEN UNIFORM(0, 1, RANDOM()) < 0.1 THEN 'HIGH_CONSTRAINT'
        WHEN UNIFORM(0, 1, RANDOM()) < 0.3 THEN 'MEDIUM_CONSTRAINT'
        ELSE 'LOW_CONSTRAINT'
    END as pricing_constraint_level,
    CURRENT_TIMESTAMP()
FROM capacity_dates c
CROSS JOIN park_capacities p;

-- Update calculated fields
UPDATE CAPACITY_DATA c
SET 
    current_reservations = FLOOR(reserved_capacity * UNIFORM(0.7, 1.0, RANDOM())),
    weather_adjusted_capacity = CASE 
        WHEN (SELECT weather_severity_score FROM WEATHER_DATA w 
              WHERE w.weather_date = c.capacity_date AND w.park_code = c.park_code) > 7 
        THEN FLOOR(total_daily_capacity * 0.85) -- Severe weather reduces capacity
        WHEN (SELECT weather_severity_score FROM WEATHER_DATA w 
              WHERE w.weather_date = c.capacity_date AND w.park_code = c.park_code) > 4 
        THEN FLOOR(total_daily_capacity * 0.95) -- Moderate weather impact
        ELSE total_daily_capacity
    END;

UPDATE CAPACITY_DATA 
SET 
    available_capacity = total_daily_capacity - current_reservations - special_event_capacity - maintenance_impact_capacity,
    capacity_utilization_forecast = ROUND(
        (current_reservations::DECIMAL / NULLIF(total_daily_capacity, 0)) * 100, 2
    );

-- =====================================================
-- 5. FINANCIAL FORECAST DATA
-- Accounting alignment data for revenue recognition
-- =====================================================

CREATE OR REPLACE TABLE FINANCIAL_FORECAST (
    FORECAST_DATE DATE,
    PARK_CODE VARCHAR(20),
    FORECAST_PERIOD VARCHAR(20),
    REVENUE_TARGET DECIMAL(15,2),
    COST_OF_GOODS_SOLD DECIMAL(15,2),
    OPERATING_EXPENSES DECIMAL(15,2),
    MARKETING_BUDGET DECIMAL(12,2),
    PRICING_FLEXIBILITY_SCORE DECIMAL(3,2), -- 0-1 scale
    MARGIN_TARGET_PERCENT DECIMAL(5,2),
    VOLUME_TARGET INTEGER,
    STRATEGIC_PRIORITY VARCHAR(30),
    BUDGET_VARIANCE_TOLERANCE DECIMAL(5,2),
    COMPETITOR_PRICING_INTEL DECIMAL(8,2),
    ECONOMIC_INDICATOR_IMPACT VARCHAR(20),
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO FINANCIAL_FORECAST
WITH forecast_periods AS (
    SELECT DATEADD(month, seq4(), DATE_TRUNC('month', CURRENT_DATE())) as forecast_date
    FROM table(generator(rowcount => 18)) -- 18 months of forecasts
),
parks AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO', 450000000),    -- Annual revenue targets
    ('UDX_HOLLYWOOD', 280000000),
    ('UDX_JAPAN', 380000000),
    ('UDX_SINGAPORE', 220000000)
    AS t(park_code, annual_revenue_target)
)
SELECT 
    f.forecast_date,
    p.park_code,
    YEAR(f.forecast_date) || '-' || LPAD(MONTH(f.forecast_date), 2, '0') as forecast_period,
    -- Monthly revenue target with seasonal adjustment
    ROUND(p.annual_revenue_target / 12 * 
        CASE MONTH(f.forecast_date)
            WHEN 1 THEN 0.85   -- January - post holiday low
            WHEN 2 THEN 0.80   -- February - lowest month
            WHEN 3 THEN 1.05   -- March - spring break
            WHEN 4 THEN 1.00   -- April - moderate
            WHEN 5 THEN 0.95   -- May - shoulder
            WHEN 6 THEN 1.25   -- June - summer start
            WHEN 7 THEN 1.35   -- July - peak summer
            WHEN 8 THEN 1.30   -- August - peak summer
            WHEN 9 THEN 0.90   -- September - back to school
            WHEN 10 THEN 1.10  -- October - Halloween
            WHEN 11 THEN 1.05  -- November - Thanksgiving
            WHEN 12 THEN 1.40  -- December - holidays
        END * UNIFORM(0.95, 1.05, RANDOM()), 2
    ) as revenue_target,
    
    -- COGS typically 25-35% of revenue for theme parks
    ROUND(revenue_target * UNIFORM(0.25, 0.35, RANDOM()), 2) as cost_of_goods_sold,
    
    -- Operating expenses typically 40-50% of revenue
    ROUND(revenue_target * UNIFORM(0.40, 0.50, RANDOM()), 2) as operating_expenses,
    
    -- Marketing budget 8-12% of revenue
    ROUND(revenue_target * UNIFORM(0.08, 0.12, RANDOM()), 2) as marketing_budget,
    
    -- Pricing flexibility based on competitive position and demand
    CASE 
        WHEN MONTH(f.forecast_date) IN (6,7,8,12) THEN UNIFORM(0.85, 0.95, RANDOM()) -- Less flexibility in peak
        WHEN MONTH(f.forecast_date) IN (1,2,9,10) THEN UNIFORM(0.40, 0.70, RANDOM()) -- More flexibility in low season
        ELSE UNIFORM(0.60, 0.80, RANDOM()) -- Moderate flexibility
    END as pricing_flexibility_score,
    
    -- Target margin percentage
    ROUND(UNIFORM(15.0, 35.0, RANDOM()), 2) as margin_target_percent,
    
    -- Volume targets based on revenue and average ticket price
    FLOOR(revenue_target / 125) as volume_target, -- Assuming ~$125 average ticket
    
    CASE FLOOR(UNIFORM(1, 6, RANDOM()))
        WHEN 1 THEN 'REVENUE_GROWTH'
        WHEN 2 THEN 'MARKET_SHARE'
        WHEN 3 THEN 'MARGIN_OPTIMIZATION'
        WHEN 4 THEN 'CAPACITY_UTILIZATION'
        ELSE 'BALANCED_GROWTH'
    END as strategic_priority,
    
    ROUND(UNIFORM(5.0, 15.0, RANDOM()), 2) as budget_variance_tolerance,
    
    -- Competitor pricing intelligence (anonymized)
    ROUND(UNIFORM(95.0, 155.0, RANDOM()), 2) as competitor_pricing_intel,
    
    CASE FLOOR(UNIFORM(1, 6, RANDOM()))
        WHEN 1 THEN 'POSITIVE'
        WHEN 2 THEN 'NEGATIVE'
        WHEN 3 THEN 'NEUTRAL'
        WHEN 4 THEN 'MIXED'
        ELSE 'NEUTRAL'
    END as economic_indicator_impact,
    
    CURRENT_TIMESTAMP()
FROM forecast_periods f
CROSS JOIN parks p;

-- =====================================================
-- ADDITIONAL CONSTRAINT AND BUSINESS RULES TABLES
-- Partner agreements, marketing constraints, etc.
-- =====================================================

CREATE OR REPLACE TABLE PRICING_CONSTRAINTS (
    CONSTRAINT_ID VARCHAR(50),
    PARK_CODE VARCHAR(20),
    CONSTRAINT_TYPE VARCHAR(30),
    PARTNER_NAME VARCHAR(100),
    TICKET_TYPE VARCHAR(50),
    MIN_PRICE DECIMAL(8,2),
    MAX_PRICE DECIMAL(8,2),
    DISCOUNT_LIMIT_PERCENT DECIMAL(5,2),
    ADVANCE_NOTICE_DAYS INTEGER,
    EFFECTIVE_DATE_START DATE,
    EFFECTIVE_DATE_END DATE,
    IS_ACTIVE BOOLEAN,
    CONSTRAINT_PRIORITY INTEGER, -- 1=highest, 5=lowest
    VIOLATION_PENALTY_AMOUNT DECIMAL(10,2),
    NOTES VARCHAR(500),
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO PRICING_CONSTRAINTS (
    CONSTRAINT_ID, PARK_CODE, CONSTRAINT_TYPE, PARTNER_NAME, TICKET_TYPE, 
    MIN_PRICE, MAX_PRICE, DISCOUNT_LIMIT_PERCENT, ADVANCE_NOTICE_DAYS, 
    EFFECTIVE_DATE_START, EFFECTIVE_DATE_END, IS_ACTIVE, CONSTRAINT_PRIORITY, 
    VIOLATION_PENALTY_AMOUNT, NOTES
) VALUES
('HOTEL_PARTNER_001', 'UDX_ORLANDO', 'HOTEL_AGREEMENT', 'Grand Resort Hotel', 'SINGLE_DAY_GENERAL', 95.00, 140.00, 15.00, 7, '2024-01-01', '2024-12-31', TRUE, 2, 5000.00, 'Cannot exceed 15% discount from base rate for hotel package guests'),
('HOTEL_PARTNER_002', 'UDX_ORLANDO', 'HOTEL_AGREEMENT', 'Universal Resort & Spa', 'MULTI_DAY_2', 170.00, 250.00, 20.00, 14, '2024-01-01', '2024-12-31', TRUE, 1, 10000.00, 'Preferred partner - maximum flexibility'),
('TRAVEL_AGENT_001', 'UDX_HOLLYWOOD', 'TRAVEL_AGENT', 'Vacation Specialists Inc', 'SINGLE_DAY_GENERAL', 90.00, 135.00, 12.00, 21, '2024-01-01', '2024-12-31', TRUE, 3, 2500.00, 'Requires 21-day advance notice for price changes'),
('OTA_PARTNER_001', 'UDX_JAPAN', 'OTA_AGREEMENT', 'TravelBooking.com', 'SINGLE_DAY_EXPRESS', 160.00, 220.00, 10.00, 5, '2024-01-01', '2024-12-31', TRUE, 2, 7500.00, 'Limited discount authority due to high volume'),
('MARKETING_CAMPAIGN_001', 'UDX_SINGAPORE', 'MARKETING_CONSTRAINT', 'Summer Family Fun Campaign', 'SINGLE_DAY_GENERAL', 99.00, 109.00, 0.00, 0, '2024-06-01', '2024-08-31', TRUE, 1, 0.00, 'Fixed pricing during marketing campaign period'),
('CORPORATE_GROUP_001', 'UDX_ORLANDO', 'GROUP_AGREEMENT', 'Enterprise Solutions Corp', 'SINGLE_DAY_GENERAL', 85.00, 115.00, 25.00, 30, '2024-01-01', '2024-12-31', TRUE, 4, 1000.00, 'Corporate volume discount program'),
('SEASONAL_PROMOTION_001', 'UDX_HOLLYWOOD', 'PROMOTIONAL_CONSTRAINT', 'Holiday Special Offer', 'MULTI_DAY_3', 199.00, 279.00, 30.00, 14, '2024-11-15', '2025-01-15', TRUE, 2, 0.00, 'Holiday season promotional pricing constraints'),
('COMPETITOR_RESPONSE_001', 'UDX_JAPAN', 'COMPETITIVE_CONSTRAINT', 'Market Response Protocol', 'SINGLE_DAY_GENERAL', 85.00, 145.00, 20.00, 3, '2024-01-01', '2024-12-31', TRUE, 1, 0.00, 'Rapid response pricing for competitive threats');

-- =====================================================
-- DEMAND PREDICTION AND ELASTICITY REFERENCE DATA
-- =====================================================

CREATE OR REPLACE TABLE DEMAND_ELASTICITY_REFERENCE (
    PARK_CODE VARCHAR(20),
    TICKET_TYPE VARCHAR(50),
    GUEST_SEGMENT VARCHAR(30),
    SEASON VARCHAR(20),
    BASE_ELASTICITY DECIMAL(6,4),
    ELASTICITY_RANGE_MIN DECIMAL(6,4),
    ELASTICITY_RANGE_MAX DECIMAL(6,4),
    DEMAND_SENSITIVITY_SCORE INTEGER, -- 1-10 scale
    OPTIMAL_PRICE_RANGE_MIN DECIMAL(8,2),
    OPTIMAL_PRICE_RANGE_MAX DECIMAL(8,2),
    LAST_UPDATED DATE,
    CONFIDENCE_LEVEL DECIMAL(3,2)
);

INSERT INTO DEMAND_ELASTICITY_REFERENCE VALUES
('UDX_ORLANDO', 'SINGLE_DAY_GENERAL', 'FAMILY_LEISURE', 'PEAK', -1.85, -2.20, -1.50, 7, 115.00, 135.00, CURRENT_DATE(), 0.85),
('UDX_ORLANDO', 'SINGLE_DAY_GENERAL', 'FAMILY_LEISURE', 'SHOULDER', -2.10, -2.45, -1.75, 8, 105.00, 125.00, CURRENT_DATE(), 0.82),
('UDX_ORLANDO', 'SINGLE_DAY_GENERAL', 'FAMILY_LEISURE', 'LOW', -2.65, -3.00, -2.30, 9, 95.00, 115.00, CURRENT_DATE(), 0.78),
('UDX_ORLANDO', 'SINGLE_DAY_EXPRESS', 'ADULT_COUPLE', 'PEAK', -1.25, -1.60, -0.90, 5, 185.00, 225.00, CURRENT_DATE(), 0.88),
('UDX_ORLANDO', 'SINGLE_DAY_EXPRESS', 'ADULT_COUPLE', 'SHOULDER', -1.45, -1.80, -1.10, 6, 165.00, 200.00, CURRENT_DATE(), 0.85),
('UDX_ORLANDO', 'SINGLE_DAY_EXPRESS', 'ADULT_COUPLE', 'LOW', -1.75, -2.10, -1.40, 7, 145.00, 180.00, CURRENT_DATE(), 0.80),
('UDX_ORLANDO', 'VIP_EXPERIENCE', 'INTERNATIONAL', 'PEAK', -0.85, -1.20, -0.50, 3, 450.00, 550.00, CURRENT_DATE(), 0.92),
('UDX_ORLANDO', 'VIP_EXPERIENCE', 'INTERNATIONAL', 'SHOULDER', -1.05, -1.40, -0.70, 4, 400.00, 500.00, CURRENT_DATE(), 0.89),
('UDX_ORLANDO', 'VIP_EXPERIENCE', 'INTERNATIONAL', 'LOW', -1.35, -1.70, -1.00, 5, 350.00, 450.00, CURRENT_DATE(), 0.85),
('UDX_HOLLYWOOD', 'SINGLE_DAY_GENERAL', 'LOCAL_RESIDENT', 'PEAK', -2.25, -2.60, -1.90, 8, 100.00, 120.00, CURRENT_DATE(), 0.83),
('UDX_HOLLYWOOD', 'SINGLE_DAY_GENERAL', 'LOCAL_RESIDENT', 'SHOULDER', -2.45, -2.80, -2.10, 9, 90.00, 110.00, CURRENT_DATE(), 0.80),
('UDX_HOLLYWOOD', 'SINGLE_DAY_GENERAL', 'LOCAL_RESIDENT', 'LOW', -2.85, -3.20, -2.50, 10, 80.00, 100.00, CURRENT_DATE(), 0.75);

-- =====================================================
-- REVENUE MANAGEMENT AND FORECASTING TABLES
-- =====================================================

-- =====================================================
-- BOOKING PACE AND ADVANCE PURCHASE PATTERNS
-- Critical for revenue forecasting and yield management
-- =====================================================

CREATE OR REPLACE TABLE BOOKING_PACE_ANALYSIS (
    BOOKING_DATE DATE,
    ADMISSION_DATE DATE,
    PARK_CODE VARCHAR(20),
    TICKET_TYPE VARCHAR(50),
    GUEST_SEGMENT VARCHAR(30),
    CHANNEL VARCHAR(30),
    ADVANCE_BOOKING_DAYS INTEGER,
    BOOKING_VOLUME INTEGER,
    BOOKING_REVENUE DECIMAL(12,2),
    AVERAGE_BOOKING_PRICE DECIMAL(8,2),
    CANCELLATION_RATE DECIMAL(5,4),
    NO_SHOW_RATE DECIMAL(5,4),
    BOOKING_CURVE_POSITION VARCHAR(20), -- EARLY, NORMAL, LATE, LAST_MINUTE
    REVENUE_IMPACT_SCORE DECIMAL(3,2), -- 0-1 scale
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO BOOKING_PACE_ANALYSIS
WITH booking_dates AS (
    SELECT DATEADD(day, seq4(), '2022-01-01'::date) as booking_date
    FROM table(generator(rowcount => 730))
),
admission_offsets AS (
    SELECT * FROM VALUES (1), (2), (3), (7), (14), (21), (30), (60), (90), (120) AS t(days_ahead)
),
parks AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO'), ('UDX_HOLLYWOOD'), ('UDX_JAPAN'), ('UDX_SINGAPORE')
    AS t(park_code)
),
ticket_types AS (
    SELECT * FROM VALUES
    ('SINGLE_DAY_GENERAL'), ('SINGLE_DAY_EXPRESS'), ('MULTI_DAY_2'), 
    ('MULTI_DAY_3'), ('SEASON_PASS'), ('VIP_EXPERIENCE')
    AS t(ticket_type)
),
segments AS (
    SELECT * FROM VALUES
    ('FAMILY_LEISURE'), ('ADULT_COUPLE'), ('INTERNATIONAL'), 
    ('LOCAL_RESIDENT'), ('BUSINESS_TRAVELER'), ('STUDENT_GROUP')
    AS t(guest_segment)
),
channels AS (
    SELECT * FROM VALUES
    ('DIRECT_ONLINE'), ('DIRECT_GATE'), ('HOTEL_PARTNER'), 
    ('TRAVEL_AGENT'), ('OTA_PARTNER'), ('CORPORATE')
    AS t(channel)
)
SELECT 
    b.booking_date,
    DATEADD(day, o.days_ahead, b.booking_date) as admission_date,
    p.park_code,
    t.ticket_type,
    s.guest_segment,
    c.channel,
    o.days_ahead as advance_booking_days,
    
    -- Booking volume varies by advance days and seasonality
    FLOOR(
        CASE o.days_ahead
            WHEN 1 THEN UNIFORM(5, 25, RANDOM())    -- Last minute bookings
            WHEN 2 THEN UNIFORM(8, 35, RANDOM())    -- 2 days ahead
            WHEN 3 THEN UNIFORM(12, 45, RANDOM())   -- 3 days ahead
            WHEN 7 THEN UNIFORM(25, 85, RANDOM())   -- 1 week ahead
            WHEN 14 THEN UNIFORM(35, 120, RANDOM()) -- 2 weeks ahead
            WHEN 21 THEN UNIFORM(45, 150, RANDOM()) -- 3 weeks ahead
            WHEN 30 THEN UNIFORM(55, 180, RANDOM()) -- 1 month ahead
            WHEN 60 THEN UNIFORM(35, 100, RANDOM()) -- 2 months ahead
            WHEN 90 THEN UNIFORM(20, 60, RANDOM())  -- 3 months ahead
            WHEN 120 THEN UNIFORM(10, 30, RANDOM()) -- 4 months ahead
        END *
        CASE 
            WHEN MONTH(DATEADD(day, o.days_ahead, b.booking_date)) IN (6,7,8,12) THEN UNIFORM(1.3, 1.8, RANDOM()) -- Peak season
            WHEN MONTH(DATEADD(day, o.days_ahead, b.booking_date)) IN (1,2,9,10) THEN UNIFORM(0.5, 0.8, RANDOM()) -- Low season
            ELSE UNIFORM(0.8, 1.2, RANDOM()) -- Shoulder season
        END *
        CASE t.ticket_type
            WHEN 'SINGLE_DAY_GENERAL' THEN 1.0
            WHEN 'SINGLE_DAY_EXPRESS' THEN 0.4
            WHEN 'MULTI_DAY_2' THEN 0.3
            WHEN 'MULTI_DAY_3' THEN 0.25
            WHEN 'SEASON_PASS' THEN 0.1
            WHEN 'VIP_EXPERIENCE' THEN 0.05
        END
    ) as booking_volume,
    
    0 as booking_revenue, -- Will calculate after
    
    -- Advance booking pricing (typically lower for early bookings)
    CASE t.ticket_type
        WHEN 'SINGLE_DAY_GENERAL' THEN 
            109.00 * (1 + 
                CASE o.days_ahead
                    WHEN 1 THEN UNIFORM(0.05, 0.15, RANDOM())    -- Last minute premium
                    WHEN 2 THEN UNIFORM(0.02, 0.08, RANDOM())    -- Short notice premium
                    WHEN 3 THEN UNIFORM(0.00, 0.05, RANDOM())    -- Slight premium
                    WHEN 7 THEN UNIFORM(-0.05, 0.02, RANDOM())   -- Standard pricing
                    WHEN 14 THEN UNIFORM(-0.10, -0.02, RANDOM()) -- Early bird discount
                    WHEN 21 THEN UNIFORM(-0.15, -0.05, RANDOM()) -- Advance purchase discount
                    WHEN 30 THEN UNIFORM(-0.20, -0.08, RANDOM()) -- Monthly advance discount
                    WHEN 60 THEN UNIFORM(-0.25, -0.10, RANDOM()) -- Deep advance discount
                    WHEN 90 THEN UNIFORM(-0.25, -0.10, RANDOM()) -- Maximum advance discount
                    WHEN 120 THEN UNIFORM(-0.25, -0.10, RANDOM()) -- Maximum advance discount
                END)
        WHEN 'SINGLE_DAY_EXPRESS' THEN 179.00 * (1 + UNIFORM(-0.15, 0.10, RANDOM()))
        WHEN 'MULTI_DAY_2' THEN 199.00 * (1 + UNIFORM(-0.20, 0.05, RANDOM()))
        WHEN 'MULTI_DAY_3' THEN 259.00 * (1 + UNIFORM(-0.25, 0.05, RANDOM()))
        WHEN 'SEASON_PASS' THEN 449.00 * (1 + UNIFORM(-0.15, 0.00, RANDOM()))
        WHEN 'VIP_EXPERIENCE' THEN 499.00 * (1 + UNIFORM(-0.10, 0.05, RANDOM()))
    END as average_booking_price,
    
    -- Cancellation rates vary by advance booking and ticket type
    CASE 
        WHEN o.days_ahead <= 3 THEN UNIFORM(0.02, 0.08, RANDOM()) -- Low cancellation for short advance
        WHEN o.days_ahead <= 14 THEN UNIFORM(0.05, 0.15, RANDOM()) -- Moderate cancellation
        WHEN o.days_ahead <= 60 THEN UNIFORM(0.08, 0.20, RANDOM()) -- Higher cancellation for advance bookings
        ELSE UNIFORM(0.12, 0.25, RANDOM()) -- Highest cancellation for very advance bookings
    END * 
    CASE t.ticket_type
        WHEN 'VIP_EXPERIENCE' THEN 0.5   -- Lower cancellation for premium tickets
        WHEN 'SEASON_PASS' THEN 0.3      -- Very low cancellation for annual passes
        WHEN 'SINGLE_DAY_EXPRESS' THEN 0.7 -- Moderate cancellation
        ELSE 1.0 -- Standard cancellation for general admission
    END as cancellation_rate,
    
    -- No-show rates (typically lower than cancellation)
    UNIFORM(0.01, 0.06, RANDOM()) * 
    CASE o.days_ahead
        WHEN 1 THEN 1.5  -- Higher no-show for last minute
        WHEN 2 THEN 1.2  -- Moderate no-show
        ELSE 1.0         -- Standard no-show
    END as no_show_rate,
    
    -- Booking curve position
    CASE o.days_ahead
        WHEN 1 THEN 'LAST_MINUTE'
        WHEN 2 THEN 'LAST_MINUTE'
        WHEN 3 THEN 'LAST_MINUTE'
        WHEN 7 THEN 'LATE'
        WHEN 14 THEN 'NORMAL'
        WHEN 21 THEN 'NORMAL'
        WHEN 30 THEN 'EARLY'
        ELSE 'VERY_EARLY'
    END as booking_curve_position,
    
    -- Revenue impact score (higher for reliable, high-value bookings)
    CASE 
        WHEN o.days_ahead BETWEEN 7 AND 30 AND t.ticket_type IN ('SINGLE_DAY_EXPRESS', 'VIP_EXPERIENCE') 
        THEN UNIFORM(0.85, 0.95, RANDOM())
        WHEN o.days_ahead BETWEEN 14 AND 60 AND t.ticket_type = 'SINGLE_DAY_GENERAL' 
        THEN UNIFORM(0.75, 0.85, RANDOM())
        WHEN o.days_ahead <= 3 
        THEN UNIFORM(0.60, 0.75, RANDOM()) -- Lower score for last minute uncertainty
        ELSE UNIFORM(0.65, 0.80, RANDOM())
    END as revenue_impact_score,
    
    CURRENT_TIMESTAMP()
FROM booking_dates b
CROSS JOIN admission_offsets o
CROSS JOIN parks p
CROSS JOIN ticket_types t
CROSS JOIN segments s
CROSS JOIN channels c
WHERE UNIFORM(0, 1, RANDOM()) < 0.08  -- Sample 8% to create realistic dataset size
AND DATEADD(day, o.days_ahead, b.booking_date) <= CURRENT_DATE() + 120; -- Don't project too far

-- Update booking revenue
UPDATE BOOKING_PACE_ANALYSIS 
SET booking_revenue = booking_volume * average_booking_price;

-- =====================================================
-- REVENUE PERFORMANCE TRACKING
-- Daily revenue tracking with variance analysis and KPIs
-- =====================================================

CREATE OR REPLACE TABLE REVENUE_PERFORMANCE (
    PERFORMANCE_DATE DATE,
    PARK_CODE VARCHAR(20),
    TICKET_TYPE VARCHAR(50),
    GUEST_SEGMENT VARCHAR(30),
    CHANNEL VARCHAR(30),
    ACTUAL_REVENUE DECIMAL(15,2),
    BUDGETED_REVENUE DECIMAL(15,2),
    FORECAST_REVENUE DECIMAL(15,2),
    PRIOR_YEAR_REVENUE DECIMAL(15,2),
    ACTUAL_VOLUME INTEGER,
    BUDGETED_VOLUME INTEGER,
    FORECAST_VOLUME INTEGER,
    PRIOR_YEAR_VOLUME INTEGER,
    AVERAGE_DAILY_RATE DECIMAL(8,2),
    REVENUE_PER_AVAILABLE_CAPACITY DECIMAL(8,2), -- RevPAC (like RevPAR for hotels)
    MARKET_SHARE_PERCENT DECIMAL(5,2),
    YIELD_PERCENTAGE DECIMAL(5,2),
    REVENUE_VARIANCE_PERCENT DECIMAL(6,2),
    VOLUME_VARIANCE_PERCENT DECIMAL(6,2),
    REVENUE_GROWTH_YOY_PERCENT DECIMAL(6,2),
    VOLUME_GROWTH_YOY_PERCENT DECIMAL(6,2),
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO REVENUE_PERFORMANCE
WITH performance_dates AS (
    SELECT DATEADD(day, seq4(), '2023-01-01'::date) as performance_date
    FROM table(generator(rowcount => 365)) -- 1 year of performance data
),
parks AS (
    SELECT * FROM VALUES 
    ('UDX_ORLANDO', 25000), ('UDX_HOLLYWOOD', 15000), 
    ('UDX_JAPAN', 20000), ('UDX_SINGAPORE', 12000)
    AS t(park_code, daily_capacity)
),
ticket_segments AS (
    SELECT t.ticket_type, s.guest_segment, c.channel, 
           t.base_revenue, s.segment_multiplier, c.channel_multiplier
    FROM (
        SELECT * FROM VALUES
        ('SINGLE_DAY_GENERAL', 25000), ('SINGLE_DAY_EXPRESS', 12000),
        ('MULTI_DAY_2', 8000), ('MULTI_DAY_3', 5000),
        ('SEASON_PASS', 2000), ('VIP_EXPERIENCE', 1500)
        AS t(ticket_type, base_revenue)
    ) t
    CROSS JOIN (
        SELECT * FROM VALUES
        ('FAMILY_LEISURE', 1.0), ('ADULT_COUPLE', 0.8), ('INTERNATIONAL', 1.2),
        ('LOCAL_RESIDENT', 0.6), ('BUSINESS_TRAVELER', 0.4), ('STUDENT_GROUP', 0.3)
        AS s(guest_segment, segment_multiplier)
    ) s
    CROSS JOIN (
        SELECT * FROM VALUES
        ('DIRECT_ONLINE', 1.0), ('DIRECT_GATE', 0.3), ('HOTEL_PARTNER', 0.7),
        ('TRAVEL_AGENT', 0.5), ('OTA_PARTNER', 0.6), ('CORPORATE', 0.2)
        AS c(channel, channel_multiplier)
    ) c
)
SELECT 
    pd.performance_date,
    p.park_code,
    ts.ticket_type,
    ts.guest_segment,
    ts.channel,
    
    -- Actual revenue with seasonal and random variation
    ROUND(ts.base_revenue * ts.segment_multiplier * ts.channel_multiplier *
        CASE 
            WHEN MONTH(pd.performance_date) IN (6,7,8,12) THEN UNIFORM(1.2, 1.6, RANDOM()) -- Peak season
            WHEN MONTH(pd.performance_date) IN (1,2,9,10) THEN UNIFORM(0.6, 0.9, RANDOM()) -- Low season
            ELSE UNIFORM(0.9, 1.2, RANDOM()) -- Shoulder season
        END *
        CASE DAYOFWEEK(pd.performance_date)
            WHEN 1 THEN 1.3  -- Sunday
            WHEN 2 THEN 0.6  -- Monday
            WHEN 3 THEN 0.7  -- Tuesday
            WHEN 4 THEN 0.8  -- Wednesday
            WHEN 5 THEN 0.9  -- Thursday
            WHEN 6 THEN 1.2  -- Friday
            WHEN 7 THEN 1.4  -- Saturday
        END * UNIFORM(0.85, 1.15, RANDOM()), 2) as actual_revenue,
    
    -- Budgeted revenue (typically more conservative)
    ROUND(ts.base_revenue * ts.segment_multiplier * ts.channel_multiplier *
        CASE 
            WHEN MONTH(pd.performance_date) IN (6,7,8,12) THEN 1.3
            WHEN MONTH(pd.performance_date) IN (1,2,9,10) THEN 0.75
            ELSE 1.0
        END *
        CASE DAYOFWEEK(pd.performance_date)
            WHEN 1 THEN 1.2
            WHEN 2 THEN 0.65
            WHEN 3 THEN 0.75
            WHEN 4 THEN 0.85
            WHEN 5 THEN 0.95
            WHEN 6 THEN 1.15
            WHEN 7 THEN 1.3
        END, 2) as budgeted_revenue,
    
    0 as forecast_revenue, -- Will calculate
    0 as prior_year_revenue, -- Will calculate
    0 as actual_volume, -- Will calculate
    0 as budgeted_volume, -- Will calculate
    0 as forecast_volume, -- Will calculate
    0 as prior_year_volume, -- Will calculate
    0 as average_daily_rate, -- Will calculate
    0 as revenue_per_available_capacity, -- Will calculate
    
    -- Market share varies by park and segment
    CASE p.park_code
        WHEN 'UDX_ORLANDO' THEN UNIFORM(25, 35, RANDOM())    -- Largest market share
        WHEN 'UDX_HOLLYWOOD' THEN UNIFORM(15, 25, RANDOM())  -- Medium market share
        WHEN 'UDX_JAPAN' THEN UNIFORM(20, 30, RANDOM())      -- Strong market share
        WHEN 'UDX_SINGAPORE' THEN UNIFORM(35, 45, RANDOM())  -- Dominant in smaller market
    END as market_share_percent,
    
    -- Yield percentage (revenue achieved vs optimal)
    UNIFORM(75, 95, RANDOM()) as yield_percentage,
    
    0 as revenue_variance_percent, -- Will calculate
    0 as volume_variance_percent, -- Will calculate
    0 as revenue_growth_yoy_percent, -- Will calculate
    0 as volume_growth_yoy_percent, -- Will calculate
    
    CURRENT_TIMESTAMP()
FROM performance_dates pd
CROSS JOIN parks p
CROSS JOIN ticket_segments ts
WHERE UNIFORM(0, 1, RANDOM()) < 0.25; -- Sample 25% for manageable dataset

-- Calculate derived fields
UPDATE REVENUE_PERFORMANCE rp
SET 
    forecast_revenue = actual_revenue * UNIFORM(0.95, 1.05, RANDOM()),
    prior_year_revenue = actual_revenue * UNIFORM(0.85, 1.20, RANDOM()),
    actual_volume = FLOOR(actual_revenue / 
        CASE ticket_type
            WHEN 'SINGLE_DAY_GENERAL' THEN 119
            WHEN 'SINGLE_DAY_EXPRESS' THEN 189
            WHEN 'MULTI_DAY_2' THEN 209
            WHEN 'MULTI_DAY_3' THEN 269
            WHEN 'SEASON_PASS' THEN 469
            WHEN 'VIP_EXPERIENCE' THEN 519
        END),
    budgeted_volume = FLOOR(budgeted_revenue / 
        CASE ticket_type
            WHEN 'SINGLE_DAY_GENERAL' THEN 119
            WHEN 'SINGLE_DAY_EXPRESS' THEN 189
            WHEN 'MULTI_DAY_2' THEN 209
            WHEN 'MULTI_DAY_3' THEN 269
            WHEN 'SEASON_PASS' THEN 469
            WHEN 'VIP_EXPERIENCE' THEN 519
        END);

UPDATE REVENUE_PERFORMANCE 
SET 
    forecast_volume = FLOOR(forecast_revenue / NULLIF(average_daily_rate, 0)),
    prior_year_volume = FLOOR(prior_year_revenue / NULLIF(average_daily_rate, 0)),
    average_daily_rate = CASE WHEN actual_volume > 0 THEN actual_revenue / actual_volume ELSE 0 END;

UPDATE REVENUE_PERFORMANCE 
SET 
    revenue_per_available_capacity = actual_revenue / 
        CASE park_code
            WHEN 'UDX_ORLANDO' THEN 25000
            WHEN 'UDX_HOLLYWOOD' THEN 15000
            WHEN 'UDX_JAPAN' THEN 20000
            WHEN 'UDX_SINGAPORE' THEN 12000
            ELSE 20000  -- Default capacity
        END,
    revenue_variance_percent = ROUND((actual_revenue - budgeted_revenue) / NULLIF(budgeted_revenue, 0) * 100, 2),
    volume_variance_percent = ROUND((actual_volume - budgeted_volume) / NULLIF(budgeted_volume, 0) * 100, 2),
    revenue_growth_yoy_percent = ROUND((actual_revenue - prior_year_revenue) / NULLIF(prior_year_revenue, 0) * 100, 2),
    volume_growth_yoy_percent = ROUND((actual_volume - prior_year_volume) / NULLIF(prior_year_volume, 0) * 100, 2);

-- =====================================================
-- COMPETITIVE REVENUE INTELLIGENCE
-- Market positioning and competitive benchmarking
-- =====================================================

CREATE OR REPLACE TABLE COMPETITIVE_REVENUE_INTEL (
    INTEL_DATE DATE,
    MARKET_REGION VARCHAR(30),
    COMPETITOR_TIER VARCHAR(20), -- TIER_1, TIER_2, LOCAL
    COMPETITOR_CODE VARCHAR(20), -- Anonymized competitor codes
    TICKET_CATEGORY VARCHAR(30),
    COMPETITOR_PRICE DECIMAL(8,2),
    COMPETITOR_VOLUME_INDEX INTEGER, -- Index vs UDX (100 = same volume)
    COMPETITOR_REVENUE_INDEX INTEGER, -- Index vs UDX (100 = same revenue)
    MARKET_POSITION_RANK INTEGER, -- 1 = market leader
    PRICING_STRATEGY VARCHAR(30),
    PROMOTIONAL_ACTIVITY VARCHAR(50),
    CAPACITY_UTILIZATION_EST DECIMAL(5,2),
    REVENUE_GROWTH_TREND VARCHAR(20), -- INCREASING, STABLE, DECLINING
    MARKET_SHARE_CHANGE_PERCENT DECIMAL(5,2),
    UDX_PRICE_ADVANTAGE_PERCENT DECIMAL(6,2), -- Positive = UDX premium, Negative = UDX discount
    STRATEGIC_THREAT_LEVEL VARCHAR(20), -- LOW, MEDIUM, HIGH, CRITICAL
    CREATED_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO COMPETITIVE_REVENUE_INTEL
WITH intel_dates AS (
    SELECT DATEADD(week, seq4(), '2023-01-01'::date) as intel_date -- Weekly competitive intelligence
    FROM table(generator(rowcount => 52))
),
market_competitors AS (
    SELECT * FROM VALUES
    ('ORLANDO_MARKET', 'TIER_1', 'COMP_A', 'Premium Theme Park'),
    ('ORLANDO_MARKET', 'TIER_2', 'COMP_B', 'Regional Attraction'),
    ('ORLANDO_MARKET', 'LOCAL', 'COMP_C', 'Local Entertainment'),
    ('HOLLYWOOD_MARKET', 'TIER_1', 'COMP_D', 'Major Studio Park'),
    ('HOLLYWOOD_MARKET', 'TIER_2', 'COMP_E', 'Entertainment Complex'),
    ('JAPAN_MARKET', 'TIER_1', 'COMP_F', 'Major Theme Park'),
    ('JAPAN_MARKET', 'TIER_2', 'COMP_G', 'Cultural Attraction'),
    ('SINGAPORE_MARKET', 'TIER_1', 'COMP_H', 'Integrated Resort'),
    ('SINGAPORE_MARKET', 'TIER_2', 'COMP_I', 'Regional Park')
    AS t(market_region, competitor_tier, competitor_code, competitor_type)
),
ticket_categories AS (
    SELECT * FROM VALUES
    ('GENERAL_ADMISSION'), ('EXPRESS_PREMIUM'), ('MULTI_DAY_PACKAGE'), ('VIP_EXPERIENCE')
    AS t(ticket_category)
)
SELECT 
    i.intel_date,
    mc.market_region,
    mc.competitor_tier,
    mc.competitor_code,
    tc.ticket_category,
    
    -- Competitor pricing based on tier and market
    CASE tc.ticket_category
        WHEN 'GENERAL_ADMISSION' THEN 
            CASE mc.competitor_tier
                WHEN 'TIER_1' THEN UNIFORM(105, 145, RANDOM())
                WHEN 'TIER_2' THEN UNIFORM(85, 125, RANDOM())
                WHEN 'LOCAL' THEN UNIFORM(65, 95, RANDOM())
            END
        WHEN 'EXPRESS_PREMIUM' THEN 
            CASE mc.competitor_tier
                WHEN 'TIER_1' THEN UNIFORM(175, 235, RANDOM())
                WHEN 'TIER_2' THEN UNIFORM(145, 195, RANDOM())
                WHEN 'LOCAL' THEN UNIFORM(95, 145, RANDOM())
            END
        WHEN 'MULTI_DAY_PACKAGE' THEN 
            CASE mc.competitor_tier
                WHEN 'TIER_1' THEN UNIFORM(195, 275, RANDOM())
                WHEN 'TIER_2' THEN UNIFORM(165, 225, RANDOM())
                WHEN 'LOCAL' THEN UNIFORM(125, 185, RANDOM())
            END
        WHEN 'VIP_EXPERIENCE' THEN 
            CASE mc.competitor_tier
                WHEN 'TIER_1' THEN UNIFORM(425, 575, RANDOM())
                WHEN 'TIER_2' THEN UNIFORM(325, 475, RANDOM())
                WHEN 'LOCAL' THEN UNIFORM(225, 375, RANDOM())
            END
    END as competitor_price,
    
    -- Volume and revenue indices
    CASE mc.competitor_tier
        WHEN 'TIER_1' THEN FLOOR(UNIFORM(80, 120, RANDOM()))  -- Similar scale to UDX
        WHEN 'TIER_2' THEN FLOOR(UNIFORM(40, 80, RANDOM()))   -- Smaller scale
        WHEN 'LOCAL' THEN FLOOR(UNIFORM(15, 40, RANDOM()))    -- Much smaller
    END as competitor_volume_index,
    
    CASE mc.competitor_tier
        WHEN 'TIER_1' THEN FLOOR(UNIFORM(85, 125, RANDOM()))
        WHEN 'TIER_2' THEN FLOOR(UNIFORM(45, 85, RANDOM()))
        WHEN 'LOCAL' THEN FLOOR(UNIFORM(20, 45, RANDOM()))
    END as competitor_revenue_index,
    
    -- Market position ranking
    CASE mc.competitor_tier
        WHEN 'TIER_1' THEN FLOOR(UNIFORM(1, 3, RANDOM()))
        WHEN 'TIER_2' THEN FLOOR(UNIFORM(3, 6, RANDOM()))
        WHEN 'LOCAL' THEN FLOOR(UNIFORM(6, 10, RANDOM()))
    END as market_position_rank,
    
    -- Pricing strategy
    CASE FLOOR(UNIFORM(1, 6, RANDOM()))
        WHEN 1 THEN 'PREMIUM_POSITIONING'
        WHEN 2 THEN 'VALUE_PRICING'
        WHEN 3 THEN 'DYNAMIC_PRICING'
        WHEN 4 THEN 'PENETRATION_PRICING'
        ELSE 'COMPETITIVE_MATCHING'
    END as pricing_strategy,
    
    -- Promotional activity
    CASE FLOOR(UNIFORM(1, 8, RANDOM()))
        WHEN 1 THEN 'SEASONAL_DISCOUNT'
        WHEN 2 THEN 'BUNDLE_PROMOTION'
        WHEN 3 THEN 'EARLY_BIRD_SPECIAL'
        WHEN 4 THEN 'LOCAL_RESIDENT_DEAL'
        WHEN 5 THEN 'GROUP_DISCOUNT'
        WHEN 6 THEN 'LOYALTY_PROGRAM'
        ELSE 'NO_ACTIVE_PROMOTION'
    END as promotional_activity,
    
    -- Capacity utilization estimate
    CASE mc.competitor_tier
        WHEN 'TIER_1' THEN UNIFORM(0.65, 0.85, RANDOM())
        WHEN 'TIER_2' THEN UNIFORM(0.55, 0.75, RANDOM())
        WHEN 'LOCAL' THEN UNIFORM(0.35, 0.65, RANDOM())
    END as capacity_utilization_est,
    
    -- Revenue growth trend
    CASE FLOOR(UNIFORM(1, 4, RANDOM()))
        WHEN 1 THEN 'INCREASING'
        WHEN 2 THEN 'STABLE'
        ELSE 'DECLINING'
    END as revenue_growth_trend,
    
    -- Market share change
    UNIFORM(-5.0, 8.0, RANDOM()) as market_share_change_percent,
    
    0 as udx_price_advantage_percent, -- Will calculate
    
    -- Strategic threat level
    CASE mc.competitor_tier
        WHEN 'TIER_1' THEN 
            CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.3 THEN 'HIGH' ELSE 'MEDIUM' END
        WHEN 'TIER_2' THEN 
            CASE WHEN UNIFORM(0, 1, RANDOM()) < 0.2 THEN 'MEDIUM' ELSE 'LOW' END
        WHEN 'LOCAL' THEN 'LOW'
    END as strategic_threat_level,
    
    CURRENT_TIMESTAMP()
FROM intel_dates i
CROSS JOIN market_competitors mc
CROSS JOIN ticket_categories tc
WHERE UNIFORM(0, 1, RANDOM()) < 0.8; -- Include 80% of combinations

-- Calculate UDX price advantage (will need UDX reference prices)
UPDATE COMPETITIVE_REVENUE_INTEL 
SET udx_price_advantage_percent = 
    CASE ticket_category
        WHEN 'GENERAL_ADMISSION' THEN ROUND((119.00 - competitor_price) / competitor_price * 100, 2)
        WHEN 'EXPRESS_PREMIUM' THEN ROUND((189.00 - competitor_price) / competitor_price * 100, 2)
        WHEN 'MULTI_DAY_PACKAGE' THEN ROUND((209.00 - competitor_price) / competitor_price * 100, 2)
        WHEN 'VIP_EXPERIENCE' THEN ROUND((519.00 - competitor_price) / competitor_price * 100, 2)
    END;

-- =====================================================
-- CREATE VIEWS FOR ML FEATURE ENGINEERING
-- =====================================================

CREATE OR REPLACE VIEW ML_FEATURES_DAILY AS
SELECT 
    h.sales_date,
    h.park_code,
    h.ticket_type,
    h.admission_date,
    -- Sales metrics
    h.tickets_sold,
    h.total_revenue,
    h.average_price,
    h.channel,
    h.guest_segment,
    h.day_of_week,
    h.is_holiday,
    h.is_school_break,
    
    -- Pricing data
    p.base_price,
    p.dynamic_price,
    p.price_tier,
    p.demand_level,
    p.capacity_utilization,
    p.price_elasticity,
    p.competitor_avg_price,
    p.marketing_campaign_active,
    p.partner_constraints_active,
    
    -- Weather features
    w.temperature_high,
    w.temperature_low,
    w.precipitation_probability,
    w.precipitation_amount,
    w.weather_condition,
    w.weather_severity_score,
    
    -- Capacity features
    c.total_daily_capacity,
    c.available_capacity,
    c.capacity_utilization_forecast,
    c.pricing_constraint_level,
    
    -- Financial context
    f.revenue_target,
    f.margin_target_percent,
    f.pricing_flexibility_score,
    f.strategic_priority,
    
    -- Derived features
    ROUND(h.total_revenue / NULLIF(f.revenue_target, 0) * 100, 2) as revenue_target_achievement_pct,
    ROUND((h.average_price - p.base_price) / NULLIF(p.base_price, 0) * 100, 2) as price_premium_pct,
    DATEDIFF(day, h.sales_date, h.admission_date) as advance_booking_days,
    CASE WHEN h.average_price > p.competitor_avg_price THEN 'PREMIUM' 
         WHEN h.average_price < p.competitor_avg_price THEN 'DISCOUNT' 
         ELSE 'COMPETITIVE' END as competitive_position
         
FROM HISTORICAL_SALES h
LEFT JOIN HISTORICAL_PRICING p ON h.sales_date = p.pricing_date 
    AND h.park_code = p.park_code 
    AND h.ticket_type = p.ticket_type
LEFT JOIN WEATHER_DATA w ON h.sales_date = w.weather_date 
    AND h.park_code = w.park_code
LEFT JOIN CAPACITY_DATA c ON h.admission_date = c.capacity_date 
    AND h.park_code = c.park_code
LEFT JOIN FINANCIAL_FORECAST f ON DATE_TRUNC('month', h.sales_date) = f.forecast_date 
    AND h.park_code = f.park_code;

-- =====================================================
-- SUMMARY STATISTICS AND DATA VALIDATION
-- =====================================================

-- Create summary view for data quality validation
CREATE OR REPLACE VIEW DATA_SUMMARY AS
SELECT 
    'HISTORICAL_SALES' as table_name,
    COUNT(*) as record_count,
    MIN(sales_date) as min_date,
    MAX(sales_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    COUNT(DISTINCT ticket_type) as distinct_ticket_types
FROM HISTORICAL_SALES
UNION ALL
SELECT 
    'HISTORICAL_PRICING' as table_name,
    COUNT(*) as record_count,
    MIN(pricing_date) as min_date,
    MAX(pricing_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    COUNT(DISTINCT ticket_type) as distinct_ticket_types
FROM HISTORICAL_PRICING
UNION ALL
SELECT 
    'WEATHER_DATA' as table_name,
    COUNT(*) as record_count,
    MIN(weather_date) as min_date,
    MAX(weather_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    NULL as distinct_ticket_types
FROM WEATHER_DATA
UNION ALL
SELECT 
    'CAPACITY_DATA' as table_name,
    COUNT(*) as record_count,
    MIN(capacity_date) as min_date,
    MAX(capacity_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    NULL as distinct_ticket_types
FROM CAPACITY_DATA
UNION ALL
SELECT 
    'FINANCIAL_FORECAST' as table_name,
    COUNT(*) as record_count,
    MIN(forecast_date) as min_date,
    MAX(forecast_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    NULL as distinct_ticket_types
FROM FINANCIAL_FORECAST
UNION ALL
SELECT 
    'BOOKING_PACE_ANALYSIS' as table_name,
    COUNT(*) as record_count,
    MIN(booking_date) as min_date,
    MAX(booking_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    COUNT(DISTINCT ticket_type) as distinct_ticket_types
FROM BOOKING_PACE_ANALYSIS
UNION ALL
SELECT 
    'REVENUE_PERFORMANCE' as table_name,
    COUNT(*) as record_count,
    MIN(performance_date) as min_date,
    MAX(performance_date) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    COUNT(DISTINCT ticket_type) as distinct_ticket_types
FROM REVENUE_PERFORMANCE
UNION ALL
SELECT 
    'COMPETITIVE_REVENUE_INTEL' as table_name,
    COUNT(*) as record_count,
    MIN(intel_date) as min_date,
    MAX(intel_date) as max_date,
    COUNT(DISTINCT CASE 
        WHEN market_region = 'ORLANDO_MARKET' THEN 'UDX_ORLANDO'
        WHEN market_region = 'HOLLYWOOD_MARKET' THEN 'UDX_HOLLYWOOD'
        WHEN market_region = 'JAPAN_MARKET' THEN 'UDX_JAPAN'
        WHEN market_region = 'SINGAPORE_MARKET' THEN 'UDX_SINGAPORE'
    END) as distinct_parks,
    COUNT(DISTINCT ticket_category) as distinct_ticket_types
FROM COMPETITIVE_REVENUE_INTEL
UNION ALL
SELECT 
    'PRICING_CONSTRAINTS' as table_name,
    COUNT(*) as record_count,
    MIN(effective_date_start) as min_date,
    MAX(effective_date_end) as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    COUNT(DISTINCT ticket_type) as distinct_ticket_types
FROM PRICING_CONSTRAINTS
UNION ALL
SELECT 
    'DEMAND_ELASTICITY_REFERENCE' as table_name,
    COUNT(*) as record_count,
    NULL as min_date,
    NULL as max_date,
    COUNT(DISTINCT park_code) as distinct_parks,
    COUNT(DISTINCT ticket_type) as distinct_ticket_types
FROM DEMAND_ELASTICITY_REFERENCE;

-- =====================================================
-- SAMPLE QUERIES FOR POC DEMONSTRATION
-- =====================================================

-- Query 1: Revenue and pricing analysis by season
SELECT 
    park_code,
    ticket_type,
    CASE 
        WHEN MONTH(sales_date) IN (6,7,8) THEN 'Summer'
        WHEN MONTH(sales_date) IN (12,1,2) THEN 'Winter'
        WHEN MONTH(sales_date) IN (3,4,5) THEN 'Spring'
        ELSE 'Fall'
    END as season,
    COUNT(*) as sales_transactions,
    SUM(tickets_sold) as total_tickets,
    SUM(total_revenue) as total_revenue,
    ROUND(AVG(average_price), 2) as avg_price,
    ROUND(AVG(CASE WHEN weather_severity_score <= 3 THEN tickets_sold END), 0) as avg_tickets_good_weather,
    ROUND(AVG(CASE WHEN weather_severity_score > 6 THEN tickets_sold END), 0) as avg_tickets_bad_weather
FROM ML_FEATURES_DAILY
GROUP BY park_code, ticket_type, season
ORDER BY park_code, ticket_type, season;

-- Query 2: Price elasticity analysis by segment
SELECT 
    park_code,
    guest_segment,
    CORR(average_price, tickets_sold) as price_demand_correlation,
    ROUND(AVG(price_elasticity), 4) as avg_elasticity,
    COUNT(*) as sample_size
FROM ML_FEATURES_DAILY
WHERE price_elasticity IS NOT NULL
GROUP BY park_code, guest_segment
HAVING COUNT(*) > 50
ORDER BY price_demand_correlation DESC;

-- Query 3: Capacity utilization and pricing opportunity analysis
SELECT 
    park_code,
    pricing_constraint_level,
    ROUND(AVG(capacity_utilization_forecast), 2) as avg_capacity_utilization,
    ROUND(AVG(pricing_flexibility_score), 2) as avg_pricing_flexibility,
    ROUND(AVG(price_premium_pct), 2) as avg_price_premium,
    COUNT(*) as days_analyzed
FROM ML_FEATURES_DAILY
WHERE capacity_utilization_forecast IS NOT NULL
GROUP BY park_code, pricing_constraint_level
ORDER BY park_code, avg_capacity_utilization DESC;

-- =====================================================
-- REVENUE FORECASTING AND OPTIMIZATION VIEWS
-- =====================================================

-- Forward Booking Curve Analysis for Revenue Forecasting
CREATE OR REPLACE VIEW FORWARD_BOOKING_CURVES AS
SELECT 
    bp.park_code,
    bp.ticket_type,
    bp.guest_segment,
    bp.admission_date,
    bp.advance_booking_days,
    bp.booking_curve_position,
    SUM(bp.booking_volume) as total_bookings,
    SUM(bp.booking_revenue) as total_booking_revenue,
    AVG(bp.average_booking_price) as avg_booking_price,
    AVG(bp.cancellation_rate) as avg_cancellation_rate,
    AVG(bp.no_show_rate) as avg_no_show_rate,
    AVG(bp.revenue_impact_score) as avg_revenue_impact,
    -- Calculate net expected revenue after cancellations and no-shows
    SUM(bp.booking_revenue * (1 - bp.cancellation_rate) * (1 - bp.no_show_rate)) as net_expected_revenue,
    -- Calculate forward booking momentum (simplified for GROUP BY compatibility)
    CASE 
        WHEN bp.advance_booking_days <= 7 AND SUM(bp.booking_volume) > 50 THEN 'ACCELERATING'
        WHEN bp.advance_booking_days > 60 AND SUM(bp.booking_volume) < 20 THEN 'DECELERATING'
        ELSE 'STABLE'
    END as booking_momentum,
    -- Revenue forecasting confidence based on booking patterns
    CASE 
        WHEN bp.advance_booking_days <= 7 THEN 0.95
        WHEN bp.advance_booking_days <= 30 THEN 0.85
        WHEN bp.advance_booking_days <= 60 THEN 0.75
        ELSE 0.65
    END as forecast_confidence
FROM BOOKING_PACE_ANALYSIS bp
WHERE bp.admission_date >= CURRENT_DATE()
GROUP BY bp.park_code, bp.ticket_type, bp.guest_segment, bp.admission_date, 
         bp.advance_booking_days, bp.booking_curve_position;

-- Revenue Performance Analytics with Forecasting
CREATE OR REPLACE VIEW REVENUE_ANALYTICS_DASHBOARD AS
SELECT 
    rp.performance_date,
    rp.park_code,
    rp.ticket_type,
    rp.guest_segment,
    rp.channel,
    rp.actual_revenue,
    rp.budgeted_revenue,
    rp.forecast_revenue,
    rp.prior_year_revenue,
    rp.actual_volume,
    rp.average_daily_rate,
    rp.revenue_per_available_capacity,
    rp.market_share_percent,
    rp.yield_percentage,
    rp.revenue_variance_percent,
    rp.volume_variance_percent,
    rp.revenue_growth_yoy_percent,
    
    -- Calculate rolling averages for trend analysis
    AVG(rp.actual_revenue) OVER (
        PARTITION BY rp.park_code, rp.ticket_type 
        ORDER BY rp.performance_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as revenue_7day_avg,
    
    AVG(rp.actual_revenue) OVER (
        PARTITION BY rp.park_code, rp.ticket_type 
        ORDER BY rp.performance_date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as revenue_30day_avg,
    
    -- Calculate revenue momentum indicators
    CASE 
        WHEN rp.actual_revenue > LAG(rp.actual_revenue, 7) OVER (
            PARTITION BY rp.park_code, rp.ticket_type 
            ORDER BY rp.performance_date
        ) THEN 'INCREASING'
        WHEN rp.actual_revenue < LAG(rp.actual_revenue, 7) OVER (
            PARTITION BY rp.park_code, rp.ticket_type 
            ORDER BY rp.performance_date
        ) THEN 'DECREASING'
        ELSE 'STABLE'
    END as revenue_trend_7day,
    
    -- Calculate optimal pricing opportunities
    CASE 
        WHEN rp.yield_percentage < 80 AND rp.revenue_variance_percent < -10 THEN 'PRICE_INCREASE_OPPORTUNITY'
        WHEN rp.yield_percentage > 95 AND rp.volume_variance_percent < -15 THEN 'PRICE_DECREASE_OPPORTUNITY'
        WHEN rp.market_share_percent < 20 AND rp.revenue_growth_yoy_percent < 0 THEN 'COMPETITIVE_RESPONSE_NEEDED'
        ELSE 'OPTIMAL_PRICING'
    END as pricing_recommendation,
    
    -- Revenue forecasting based on trends
    rp.actual_revenue * (1 + (rp.revenue_growth_yoy_percent / 100)) as next_period_forecast
    
FROM REVENUE_PERFORMANCE rp;

-- Competitive Position Analysis for Revenue Strategy
CREATE OR REPLACE VIEW COMPETITIVE_REVENUE_ANALYSIS AS
SELECT 
    cri.intel_date,
    cri.market_region,
    cri.competitor_tier,
    cri.ticket_category,
    AVG(cri.competitor_price) as avg_competitor_price,
    MIN(cri.competitor_price) as min_competitor_price,
    MAX(cri.competitor_price) as max_competitor_price,
    AVG(cri.competitor_volume_index) as avg_competitor_volume,
    AVG(cri.competitor_revenue_index) as avg_competitor_revenue,
    AVG(cri.capacity_utilization_est) as avg_competitor_utilization,
    AVG(cri.udx_price_advantage_percent) as avg_udx_price_advantage,
    
    -- Market opportunity scoring
    CASE 
        WHEN AVG(cri.udx_price_advantage_percent) < -10 AND AVG(cri.competitor_volume_index) > 90 
        THEN 'PRICE_INCREASE_OPPORTUNITY'
        WHEN AVG(cri.udx_price_advantage_percent) > 15 AND AVG(cri.competitor_volume_index) < 70 
        THEN 'MARKET_SHARE_OPPORTUNITY'
        WHEN COUNT(CASE WHEN cri.strategic_threat_level = 'HIGH' THEN 1 END) > 0 
        THEN 'DEFENSIVE_PRICING_NEEDED'
        ELSE 'COMPETITIVE_PARITY'
    END as market_opportunity,
    
    -- Revenue optimization recommendations
    CASE 
        WHEN AVG(cri.competitor_revenue_index) > 110 THEN 'REVENUE_OPTIMIZATION_CRITICAL'
        WHEN AVG(cri.competitor_revenue_index) > 105 THEN 'REVENUE_OPTIMIZATION_MODERATE'
        ELSE 'REVENUE_PERFORMANCE_STRONG'
    END as revenue_optimization_priority,
    
    COUNT(*) as competitor_sample_size
FROM COMPETITIVE_REVENUE_INTEL cri
GROUP BY cri.intel_date, cri.market_region, cri.competitor_tier, cri.ticket_category
HAVING COUNT(*) >= 2; -- Ensure sufficient sample size

-- =====================================================
-- REVENUE MANAGEMENT ML FEATURES VIEW
-- Comprehensive feature set for ML revenue forecasting and optimization
-- =====================================================

CREATE OR REPLACE VIEW ML_REVENUE_FEATURES AS
SELECT 
    -- Date and temporal features
    rp.performance_date,
    EXTRACT(YEAR FROM rp.performance_date) as year,
    EXTRACT(MONTH FROM rp.performance_date) as month,
    EXTRACT(DAYOFWEEK FROM rp.performance_date) as day_of_week,
    EXTRACT(DAYOFYEAR FROM rp.performance_date) as day_of_year,
    CASE 
        WHEN MONTH(rp.performance_date) IN (6,7,8) THEN 'SUMMER_PEAK'
        WHEN MONTH(rp.performance_date) = 12 THEN 'WINTER_HOLIDAY'
        WHEN MONTH(rp.performance_date) IN (1,2) THEN 'LOW_SEASON'
        WHEN MONTH(rp.performance_date) IN (3,4,5) THEN 'SPRING_SHOULDER'
        ELSE 'FALL_SHOULDER'
    END as season_category,
    
    -- Core revenue metrics
    rp.park_code,
    rp.ticket_type,
    rp.guest_segment,
    rp.channel,
    rp.actual_revenue,
    rp.budgeted_revenue,
    rp.forecast_revenue,
    rp.prior_year_revenue,
    rp.actual_volume,
    rp.average_daily_rate,
    rp.revenue_per_available_capacity,
    rp.market_share_percent,
    rp.yield_percentage,
    rp.revenue_variance_percent,
    rp.volume_variance_percent,
    rp.revenue_growth_yoy_percent,
    
    -- Booking pace features (from booking analysis)
    COALESCE(bp_agg.total_advance_bookings, 0) as total_advance_bookings,
    COALESCE(bp_agg.avg_advance_booking_days, 0) as avg_advance_booking_days,
    COALESCE(bp_agg.early_booking_revenue, 0) as early_booking_revenue,
    COALESCE(bp_agg.last_minute_revenue, 0) as last_minute_revenue,
    COALESCE(bp_agg.avg_cancellation_rate, 0.05) as avg_cancellation_rate,
    COALESCE(bp_agg.booking_momentum_score, 0.5) as booking_momentum_score,
    
    -- Competitive features
    COALESCE(comp_agg.competitor_price_index, 100) as competitor_price_index,
    COALESCE(comp_agg.market_position_score, 50) as market_position_score,
    COALESCE(comp_agg.competitive_pressure_score, 0.5) as competitive_pressure_score,
    
    -- Weather impact features
    COALESCE(w.weather_severity_score, 3) as weather_severity_score,
    COALESCE(w.temperature_high, 75) as temperature_high,
    COALESCE(w.precipitation_probability, 20) as precipitation_probability,
    
    -- Capacity and operational features
    COALESCE(c.capacity_utilization_forecast, 0.7) as capacity_utilization_forecast,
    COALESCE(c.pricing_constraint_level, 'LOW_CONSTRAINT') as pricing_constraint_level,
    COALESCE(c.available_capacity, 20000) as available_capacity,
    
    -- Financial context features
    COALESCE(f.revenue_target, rp.actual_revenue * 1.1) as revenue_target,
    COALESCE(f.margin_target_percent, 25) as margin_target_percent,
    COALESCE(f.pricing_flexibility_score, 0.7) as pricing_flexibility_score,
    COALESCE(f.strategic_priority, 'BALANCED_GROWTH') as strategic_priority,
    
    -- Derived ML features
    ROUND(rp.actual_revenue / NULLIF(rp.prior_year_revenue, 0), 4) as revenue_index_yoy,
    ROUND(rp.average_daily_rate / 
        CASE rp.ticket_type
            WHEN 'SINGLE_DAY_GENERAL' THEN 119.00
            WHEN 'SINGLE_DAY_EXPRESS' THEN 189.00
            WHEN 'MULTI_DAY_2' THEN 209.00
            WHEN 'MULTI_DAY_3' THEN 269.00
            WHEN 'SEASON_PASS' THEN 469.00
            WHEN 'VIP_EXPERIENCE' THEN 519.00
        END, 4) as price_index_vs_base,
    
    -- Optimization target variables
    CASE 
        WHEN rp.revenue_variance_percent > 10 THEN 'OVER_PERFORMING'
        WHEN rp.revenue_variance_percent < -10 THEN 'UNDER_PERFORMING'
        ELSE 'ON_TARGET'
    END as revenue_performance_category,
    
    CASE 
        WHEN rp.yield_percentage >= 90 THEN 'HIGH_YIELD'
        WHEN rp.yield_percentage >= 80 THEN 'MEDIUM_YIELD'
        ELSE 'LOW_YIELD'
    END as yield_category

FROM REVENUE_PERFORMANCE rp

-- Join booking pace aggregates
LEFT JOIN (
    SELECT 
        bp.admission_date,
        bp.park_code,
        bp.ticket_type,
        bp.guest_segment,
        SUM(bp.booking_volume) as total_advance_bookings,
        AVG(bp.advance_booking_days) as avg_advance_booking_days,
        SUM(CASE WHEN bp.booking_curve_position IN ('EARLY', 'VERY_EARLY') THEN bp.booking_revenue ELSE 0 END) as early_booking_revenue,
        SUM(CASE WHEN bp.booking_curve_position = 'LAST_MINUTE' THEN bp.booking_revenue ELSE 0 END) as last_minute_revenue,
        AVG(bp.cancellation_rate) as avg_cancellation_rate,
        AVG(bp.revenue_impact_score) as booking_momentum_score
    FROM BOOKING_PACE_ANALYSIS bp
    GROUP BY bp.admission_date, bp.park_code, bp.ticket_type, bp.guest_segment
) bp_agg ON rp.performance_date = bp_agg.admission_date 
    AND rp.park_code = bp_agg.park_code 
    AND rp.ticket_type = bp_agg.ticket_type 
    AND rp.guest_segment = bp_agg.guest_segment

-- Join competitive intelligence aggregates
LEFT JOIN (
    SELECT 
        cri.intel_date,
        CASE 
            WHEN cri.market_region = 'ORLANDO_MARKET' THEN 'UDX_ORLANDO'
            WHEN cri.market_region = 'HOLLYWOOD_MARKET' THEN 'UDX_HOLLYWOOD'
            WHEN cri.market_region = 'JAPAN_MARKET' THEN 'UDX_JAPAN'
            WHEN cri.market_region = 'SINGAPORE_MARKET' THEN 'UDX_SINGAPORE'
        END as park_code,
        AVG(cri.competitor_revenue_index) as competitor_price_index,
        AVG(cri.market_position_rank) as market_position_score,
        AVG(CASE 
            WHEN cri.strategic_threat_level = 'HIGH' THEN 0.9
            WHEN cri.strategic_threat_level = 'MEDIUM' THEN 0.6
            WHEN cri.strategic_threat_level = 'LOW' THEN 0.3
            ELSE 0.1
        END) as competitive_pressure_score
    FROM COMPETITIVE_REVENUE_INTEL cri
    GROUP BY cri.intel_date, park_code
) comp_agg ON DATE_TRUNC('week', rp.performance_date) = comp_agg.intel_date 
    AND rp.park_code = comp_agg.park_code

-- Join weather data
LEFT JOIN WEATHER_DATA w ON rp.performance_date = w.weather_date 
    AND rp.park_code = w.park_code

-- Join capacity data
LEFT JOIN CAPACITY_DATA c ON rp.performance_date = c.capacity_date 
    AND rp.park_code = c.park_code

-- Join financial forecasts
LEFT JOIN FINANCIAL_FORECAST f ON DATE_TRUNC('month', rp.performance_date) = f.forecast_date 
    AND rp.park_code = f.park_code;

-- =====================================================
-- REVENUE MANAGEMENT SAMPLE QUERIES FOR POC
-- =====================================================

-- Query 4: Revenue forecasting with booking pace analysis
SELECT 
    park_code,
    ticket_type,
    admission_date,
    total_bookings,
    total_booking_revenue,
    net_expected_revenue,
    booking_momentum,
    forecast_confidence,
    CASE 
        WHEN forecast_confidence > 0.8 AND booking_momentum = 'ACCELERATING' THEN 'STRONG_FORECAST'
        WHEN forecast_confidence > 0.7 AND booking_momentum IN ('STABLE', 'ACCELERATING') THEN 'MODERATE_FORECAST'
        ELSE 'WEAK_FORECAST'
    END as forecast_strength
FROM FORWARD_BOOKING_CURVES
WHERE admission_date BETWEEN CURRENT_DATE() AND CURRENT_DATE() + 60
ORDER BY park_code, admission_date, ticket_type;

-- Query 5: Revenue optimization opportunities
SELECT 
    park_code,
    ticket_type,
    guest_segment,
    pricing_recommendation,
    COUNT(*) as opportunity_days,
    AVG(yield_percentage) as avg_yield,
    AVG(revenue_variance_percent) as avg_variance,
    AVG(market_share_percent) as avg_market_share,
    SUM(actual_revenue) as total_revenue,
    SUM(next_period_forecast) as forecast_revenue
FROM REVENUE_ANALYTICS_DASHBOARD
WHERE performance_date >= CURRENT_DATE() - 90
GROUP BY park_code, ticket_type, guest_segment, pricing_recommendation
HAVING COUNT(*) >= 5  -- Only show significant patterns
ORDER BY total_revenue DESC;

-- Query 6: Competitive revenue positioning
SELECT 
    market_region,
    ticket_category,
    market_opportunity,
    revenue_optimization_priority,
    avg_udx_price_advantage,
    avg_competitor_price,
    avg_competitor_volume,
    competitor_sample_size
FROM COMPETITIVE_REVENUE_ANALYSIS
WHERE intel_date >= CURRENT_DATE() - 30
ORDER BY market_region, ticket_category;

-- Query 7: ML features summary for model training
SELECT 
    season_category,
    park_code,
    ticket_type,
    COUNT(*) as sample_size,
    AVG(actual_revenue) as avg_revenue,
    STDDEV(actual_revenue) as revenue_stddev,
    CORR(price_index_vs_base, yield_percentage) as price_yield_correlation
FROM ML_REVENUE_FEATURES
GROUP BY season_category, park_code, ticket_type
HAVING COUNT(*) >= 10  -- Ensures sufficient training data
ORDER BY avg_revenue DESC;

-- =====================================================
-- REVENUE MANAGEMENT AND FORECASTING CAPABILITIES SUMMARY
-- =====================================================
-- 
-- The following additional tables and views have been added to support
-- comprehensive revenue management and forecasting exercises:
--
-- NEW DATA TABLES:
-- ----------------
-- 8. BOOKING_PACE_ANALYSIS (~15,000 records)
--    - Advance booking patterns by days ahead (1-120 days)
--    - Cancellation and no-show rates by booking window
--    - Booking curve position analysis (EARLY, NORMAL, LATE, LAST_MINUTE)
--    - Revenue impact scoring for booking reliability
--    - Early bird vs last minute pricing differentials
--
-- 9. REVENUE_PERFORMANCE (~130,000 records)
--    - Daily revenue tracking with actual vs budget vs forecast
--    - Revenue Per Available Capacity (RevPAC) calculations
--    - Market share and yield percentage tracking
--    - Year-over-year growth analysis
--    - Revenue and volume variance reporting
--
-- 10. COMPETITIVE_REVENUE_INTEL (~1,400 records)
--     - Weekly competitive pricing intelligence by market
--     - Competitor revenue and volume indexing vs UDX
--     - Market position ranking and strategic threat levels
--     - Pricing strategy and promotional activity tracking
--     - UDX price advantage/disadvantage calculations
--
-- REVENUE MANAGEMENT VIEWS:
-- ------------------------
-- 11. FORWARD_BOOKING_CURVES
--     - Revenue forecasting based on booking pace analysis
--     - Net expected revenue after cancellations/no-shows
--     - Booking momentum indicators (ACCELERATING, STABLE, DECELERATING)
--     - Forecast confidence scoring by advance booking window
--
-- 12. REVENUE_ANALYTICS_DASHBOARD
--     - Revenue trend analysis with 7-day and 30-day rolling averages
--     - Pricing optimization recommendations (increase/decrease/competitive response)
--     - Revenue momentum indicators and next-period forecasting
--     - Performance categorization (over/under/on-target)
--
-- 13. COMPETITIVE_REVENUE_ANALYSIS
--     - Market opportunity identification (price increase, market share, defensive)
--     - Revenue optimization priority scoring (critical/moderate/strong)
--     - Competitive benchmarking with sufficient sample size validation
--
-- 14. ML_REVENUE_FEATURES
--     - Comprehensive feature engineering for ML model training
--     - 50+ features combining all data sources for revenue forecasting
--     - Temporal features, booking pace, competitive pressure, weather impact
--     - Target variables for optimization (revenue performance, yield categories)
--
-- REVENUE MANAGEMENT USE CASES SUPPORTED:
-- --------------------------------------
-- 1. DEMAND FORECASTING: Forward booking curves with confidence intervals
-- 2. YIELD MANAGEMENT: Revenue optimization opportunities identification
-- 3. COMPETITIVE PRICING: Market positioning and pricing strategy
-- 4. REVENUE FORECASTING: ML-ready features for predictive modeling
-- 5. BOOKING PACE ANALYSIS: Early vs late booking revenue patterns
-- 6. CONSTRAINT OPTIMIZATION: Partner agreement and operational constraint modeling
-- 7. MARKET INTELLIGENCE: Competitive benchmarking and threat assessment
-- 8. PERFORMANCE TRACKING: Variance analysis and KPI monitoring
-- 9. PRICE ELASTICITY: Demand response modeling by segment and season
-- 10. CAPACITY OPTIMIZATION: RevPAC and utilization-based pricing
--
-- REVENUE FORECASTING ML SCENARIOS:
-- ---------------------------------
-- A. SHORT-TERM FORECASTING (1-7 days):
--    - High confidence (0.95) using booking pace and weather data
--    - Last-minute booking adjustments and cancellation patterns
--    
-- B. MEDIUM-TERM FORECASTING (1-4 weeks):
--    - Moderate confidence (0.85) using booking curves and competitive intel
--    - Seasonal pattern recognition and marketing campaign impacts
--    
-- C. LONG-TERM FORECASTING (1-4 months):
--    - Lower confidence (0.65-0.75) using historical patterns and market trends
--    - Strategic pricing and capacity planning support
--
-- SNOWPARK ML OPTIMIZATION TARGETS:
-- ---------------------------------
-- - Revenue maximization subject to capacity constraints
-- - Yield percentage optimization across segments and channels
-- - Dynamic pricing based on real-time demand and competitive pressure
-- - Booking pace optimization for advance purchase vs walk-up revenue
-- - Market share protection while maintaining margin targets
--
-- =====================================================

-- Display summary for validation
SELECT 'Revenue Management Data Generation Complete!' as status, CURRENT_TIMESTAMP() as completion_time;
SELECT 'Total Tables Created: 10 core data tables + 4 revenue management views' as summary;
SELECT * FROM DATA_SUMMARY ORDER BY table_name; 

-- Revenue maximization with constraints
SELECT actual_revenue, yield_percentage, market_share_percent,
       margin_target_percent, pricing_constraint_level
FROM ML_REVENUE_FEATURES;

-- Booking volume prediction with advance booking patterns
SELECT total_advance_bookings, booking_momentum_score, weather_severity_score,
       capacity_utilization_forecast, actual_volume
FROM ML_REVENUE_FEATURES;

-- Features for price elasticity modeling
SELECT price_index_vs_base, yield_percentage, competitive_pressure_score,
       pricing_flexibility_score, revenue_performance_category
FROM ML_REVENUE_FEATURES;

-- Ready for ARIMA, Prophet, LSTM models
SELECT performance_date, actual_revenue, weather_severity_score, 
       capacity_utilization_forecast, season_category
FROM ML_REVENUE_FEATURES 
ORDER BY performance_date;

-- Example: Temporal split for time series validation
-- Training: 2022-2023 data 
-- Testing: 2024+ data
-- WHERE performance_date < '2024-01-01'  -- Training set
-- WHERE performance_date >= '2024-01-01' -- Test set