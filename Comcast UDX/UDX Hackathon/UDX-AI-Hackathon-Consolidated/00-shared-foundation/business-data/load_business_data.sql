-- =====================================================
-- UDX NLP2SQL Hackathon: Business Analytics Data Loading
-- =====================================================
-- This script creates comprehensive business analytics data
-- optimized for natural language query translation

USE DATABASE UDX_NL2SQL;
USE SCHEMA BUSINESS_ANALYTICS;
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;

-- =====================================================
-- 1. PARKS MASTER DATA
-- =====================================================

CREATE OR REPLACE TABLE PARKS (
    park_id STRING,
    park_name STRING,
    park_region STRING,
    city STRING,
    state_country STRING,
    opening_date DATE,
    total_capacity INTEGER,
    annual_attendance_target INTEGER,
    is_active BOOLEAN,
    timezone STRING
);

INSERT INTO PARKS VALUES
    ('UDX-FL', 'Universal Studios Florida', 'Southeast', 'Orlando', 'Florida, USA', '1990-06-07', 35000, 12000000, TRUE, 'EST'),
    ('UDX-CA', 'Universal Studios Hollywood', 'West Coast', 'Los Angeles', 'California, USA', '1964-07-15', 28000, 9500000, TRUE, 'PST'),
    ('UDX-JP', 'Universal Studios Japan', 'Asia Pacific', 'Osaka', 'Japan', '2001-03-31', 30000, 14500000, TRUE, 'JST'),
    ('UDX-SG', 'Universal Studios Singapore', 'Asia Pacific', 'Singapore', 'Singapore', '2010-03-18', 25000, 8000000, TRUE, 'SGT'),
    ('UDX-CN', 'Universal Beijing Resort', 'Asia Pacific', 'Beijing', 'China', '2021-09-20', 40000, 15000000, TRUE, 'CST'),
    ('UDX-EP', 'Epic Universe Orlando', 'Southeast', 'Orlando', 'Florida, USA', '2025-01-01', 50000, 18000000, FALSE, 'EST');

-- =====================================================
-- 2. CUSTOMERS - Enhanced for Business Analytics
-- =====================================================

CREATE OR REPLACE TABLE CUSTOMERS (
    customer_id STRING,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone STRING,
    birth_date DATE,
    age_group STRING, -- '18-25', '26-35', '36-45', '46-55', '56-65', '65+'
    gender STRING,
    country STRING,
    region STRING,
    loyalty_tier STRING, -- 'Bronze', 'Silver', 'Gold', 'Platinum'
    loyalty_points INTEGER,
    total_lifetime_revenue DECIMAL(10,2),
    last_visit_date DATE,
    preferred_language STRING,
    marketing_opt_in BOOLEAN,
    customer_acquisition_channel STRING,
    registration_date DATE,
    is_vip BOOLEAN
);

-- Generate comprehensive customer analytics data
INSERT INTO CUSTOMERS
WITH customer_base AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as customer_num
    FROM TABLE(GENERATOR(ROWCOUNT => 50000))
),
customer_analytics AS (
    SELECT 
        customer_num,
        'CUST' || LPAD(customer_num, 8, '0') as customer_id,
        CASE MOD(customer_num, 25)
            WHEN 0 THEN 'James' WHEN 1 THEN 'Mary' WHEN 2 THEN 'John' WHEN 3 THEN 'Patricia' WHEN 4 THEN 'Robert'
            WHEN 5 THEN 'Jennifer' WHEN 6 THEN 'Michael' WHEN 7 THEN 'Linda' WHEN 8 THEN 'William' WHEN 9 THEN 'Elizabeth'
            WHEN 10 THEN 'David' WHEN 11 THEN 'Barbara' WHEN 12 THEN 'Richard' WHEN 13 THEN 'Susan' WHEN 14 THEN 'Joseph'
            WHEN 15 THEN 'Jessica' WHEN 16 THEN 'Thomas' WHEN 17 THEN 'Sarah' WHEN 18 THEN 'Christopher' WHEN 19 THEN 'Karen'
            WHEN 20 THEN 'Daniel' WHEN 21 THEN 'Nancy' WHEN 22 THEN 'Matthew' WHEN 23 THEN 'Lisa' ELSE 'Mark'
        END as first_name,
        CASE MOD(customer_num, 20)
            WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Brown' WHEN 4 THEN 'Jones'
            WHEN 5 THEN 'Garcia' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Davis' WHEN 8 THEN 'Rodriguez' WHEN 9 THEN 'Martinez'
            WHEN 10 THEN 'Hernandez' WHEN 11 THEN 'Lopez' WHEN 12 THEN 'Gonzalez' WHEN 13 THEN 'Wilson' WHEN 14 THEN 'Anderson'
            WHEN 15 THEN 'Thomas' WHEN 16 THEN 'Taylor' WHEN 17 THEN 'Moore' WHEN 18 THEN 'Jackson' ELSE 'Martin'
        END as last_name,
        LOWER(
            CASE MOD(customer_num, 25)
                WHEN 0 THEN 'james' WHEN 1 THEN 'mary' WHEN 2 THEN 'john' WHEN 3 THEN 'patricia' WHEN 4 THEN 'robert'
                WHEN 5 THEN 'jennifer' WHEN 6 THEN 'michael' WHEN 7 THEN 'linda' WHEN 8 THEN 'william' WHEN 9 THEN 'elizabeth'
                WHEN 10 THEN 'david' WHEN 11 THEN 'barbara' WHEN 12 THEN 'richard' WHEN 13 THEN 'susan' WHEN 14 THEN 'joseph'
                WHEN 15 THEN 'jessica' WHEN 16 THEN 'thomas' WHEN 17 THEN 'sarah' WHEN 18 THEN 'christopher' WHEN 19 THEN 'karen'
                WHEN 20 THEN 'daniel' WHEN 21 THEN 'nancy' WHEN 22 THEN 'matthew' WHEN 23 THEN 'lisa' ELSE 'mark'
            END || '.' || 
            CASE MOD(customer_num, 20)
                WHEN 0 THEN 'smith' WHEN 1 THEN 'johnson' WHEN 2 THEN 'williams' WHEN 3 THEN 'brown' WHEN 4 THEN 'jones'
                WHEN 5 THEN 'garcia' WHEN 6 THEN 'miller' WHEN 7 THEN 'davis' WHEN 8 THEN 'rodriguez' WHEN 9 THEN 'martinez'
                WHEN 10 THEN 'hernandez' WHEN 11 THEN 'lopez' WHEN 12 THEN 'gonzalez' WHEN 13 THEN 'wilson' WHEN 14 THEN 'anderson'
                WHEN 15 THEN 'thomas' WHEN 16 THEN 'taylor' WHEN 17 THEN 'moore' WHEN 18 THEN 'jackson' ELSE 'martin'
            END || '@' ||
            CASE MOD(customer_num, 10)
                WHEN 0 THEN 'gmail.com' WHEN 1 THEN 'yahoo.com' WHEN 2 THEN 'hotmail.com' WHEN 3 THEN 'outlook.com'
                WHEN 4 THEN 'aol.com' WHEN 5 THEN 'icloud.com' WHEN 6 THEN 'comcast.net' WHEN 7 THEN 'verizon.net'
                WHEN 8 THEN 'att.net' ELSE 'gmail.com'
            END
        ) as email,
        '+1-' || (4000000000 + customer_num)::STRING as phone,
        DATEADD(day, -UNIFORM(18*365, 75*365, RANDOM()), CURRENT_DATE()) as birth_date,
        -- Age groups for business analytics
        CASE 
            WHEN DATEDIFF(year, DATEADD(day, -UNIFORM(18*365, 75*365, RANDOM()), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 18 AND 25 THEN '18-25'
            WHEN DATEDIFF(year, DATEADD(day, -UNIFORM(18*365, 75*365, RANDOM()), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 26 AND 35 THEN '26-35'
            WHEN DATEDIFF(year, DATEADD(day, -UNIFORM(18*365, 75*365, RANDOM()), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 36 AND 45 THEN '36-45'
            WHEN DATEDIFF(year, DATEADD(day, -UNIFORM(18*365, 75*365, RANDOM()), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 46 AND 55 THEN '46-55'
            WHEN DATEDIFF(year, DATEADD(day, -UNIFORM(18*365, 75*365, RANDOM()), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 56 AND 65 THEN '56-65'
            ELSE '65+'
        END as age_group,
        CASE MOD(customer_num, 3) WHEN 0 THEN 'M' WHEN 1 THEN 'F' ELSE 'Other' END as gender,
        CASE MOD(customer_num, 15)
            WHEN 0 THEN 'United States' WHEN 1 THEN 'United Kingdom' WHEN 2 THEN 'Canada' WHEN 3 THEN 'Germany'
            WHEN 4 THEN 'France' WHEN 5 THEN 'Japan' WHEN 6 THEN 'Australia' WHEN 7 THEN 'Brazil' WHEN 8 THEN 'China'
            WHEN 9 THEN 'Mexico' WHEN 10 THEN 'India' WHEN 11 THEN 'South Korea' WHEN 12 THEN 'Spain' WHEN 13 THEN 'Italy'
            ELSE 'Netherlands'
        END as country,
        CASE MOD(customer_num, 5)
            WHEN 0 THEN 'North America' WHEN 1 THEN 'Europe' WHEN 2 THEN 'Asia Pacific'
            WHEN 3 THEN 'Latin America' ELSE 'Other'
        END as region,
        -- Weighted loyalty tiers (more Bronze, fewer Platinum)
        CASE 
            WHEN MOD(customer_num, 100) < 60 THEN 'Bronze'
            WHEN MOD(customer_num, 100) < 85 THEN 'Silver'
            WHEN MOD(customer_num, 100) < 95 THEN 'Gold'
            ELSE 'Platinum'
        END as loyalty_tier,
        -- Loyalty points correlated with tier
        CASE 
            WHEN MOD(customer_num, 100) < 60 THEN UNIFORM(0, 999, RANDOM())      -- Bronze
            WHEN MOD(customer_num, 100) < 85 THEN UNIFORM(1000, 4999, RANDOM())  -- Silver
            WHEN MOD(customer_num, 100) < 95 THEN UNIFORM(5000, 14999, RANDOM()) -- Gold
            ELSE UNIFORM(15000, 50000, RANDOM())                                 -- Platinum
        END as loyalty_points,
        -- Lifetime revenue correlated with loyalty tier
        CASE 
            WHEN MOD(customer_num, 100) < 60 THEN UNIFORM(100, 999, RANDOM())      -- Bronze
            WHEN MOD(customer_num, 100) < 85 THEN UNIFORM(1000, 4999, RANDOM())   -- Silver
            WHEN MOD(customer_num, 100) < 95 THEN UNIFORM(5000, 14999, RANDOM())  -- Gold
            ELSE UNIFORM(15000, 75000, RANDOM())                                  -- Platinum
        END as total_lifetime_revenue,
        DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) as last_visit_date,
        CASE MOD(customer_num, 8)
            WHEN 0 THEN 'English' WHEN 1 THEN 'Spanish' WHEN 2 THEN 'French' WHEN 3 THEN 'German'
            WHEN 4 THEN 'Japanese' WHEN 5 THEN 'Mandarin' WHEN 6 THEN 'Portuguese' ELSE 'English'
        END as preferred_language,
        MOD(customer_num, 4) != 0 as marketing_opt_in, -- 75% opt in rate
        CASE MOD(customer_num, 8)
            WHEN 0 THEN 'Online Search' WHEN 1 THEN 'Social Media' WHEN 2 THEN 'Email Marketing'
            WHEN 3 THEN 'Referral' WHEN 4 THEN 'TV Advertisement' WHEN 5 THEN 'Direct Visit'
            WHEN 6 THEN 'Travel Agent' ELSE 'Partner Promotion'
        END as customer_acquisition_channel,
        DATEADD(day, -UNIFORM(30, 1095, RANDOM()), CURRENT_DATE()) as registration_date,
        MOD(customer_num, 100) >= 95 as is_vip -- 5% VIP customers
    FROM customer_base
    WHERE customer_num <= 50000
)
SELECT * FROM customer_analytics;

-- =====================================================
-- 3. SALES TRANSACTIONS - Revenue Analytics Focus
-- =====================================================

CREATE OR REPLACE TABLE SALES_TRANSACTIONS (
    transaction_id STRING,
    customer_id STRING,
    park_id STRING,
    transaction_date DATE,
    transaction_time TIME,
    ticket_type STRING, -- 'Single Day', 'Multi-Day', 'Annual Pass', 'VIP Experience', 'Group Rate'
    ticket_quantity INTEGER,
    base_price DECIMAL(8,2),
    discount_amount DECIMAL(8,2),
    total_revenue DECIMAL(10,2),
    payment_method STRING,
    purchase_channel STRING, -- 'Online', 'Mobile App', 'Park Gate', 'Travel Agent', 'Corporate'
    promotion_code STRING,
    guest_count INTEGER,
    booking_lead_days INTEGER, -- Days between booking and visit
    is_refunded BOOLEAN
);

-- Generate comprehensive sales transaction data
INSERT INTO SALES_TRANSACTIONS
WITH transaction_base AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as trans_num
    FROM TABLE(GENERATOR(ROWCOUNT => 500000))
),
transaction_details AS (
    SELECT 
        trans_num,
        'TXN' || LPAD(trans_num, 10, '0') as transaction_id,
        'CUST' || LPAD(UNIFORM(1, 50000, RANDOM()), 8, '0') as customer_id,
        CASE MOD(trans_num, 6)
            WHEN 0 THEN 'UDX-FL' WHEN 1 THEN 'UDX-CA' WHEN 2 THEN 'UDX-JP'
            WHEN 3 THEN 'UDX-SG' WHEN 4 THEN 'UDX-CN' ELSE 'UDX-FL'
        END as park_id,
        -- Date distribution with seasonal patterns
        CASE 
            WHEN MOD(trans_num, 12) IN (5, 6, 7) THEN DATEADD(day, -UNIFORM(1, 90, RANDOM()), CURRENT_DATE()) -- Summer peak
            WHEN MOD(trans_num, 12) IN (11, 0) THEN DATEADD(day, -UNIFORM(1, 90, RANDOM()), CURRENT_DATE())  -- Holiday peak
            ELSE DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) -- Regular distribution
        END as transaction_date,
        TIME_FROM_PARTS(UNIFORM(6, 22, RANDOM()), UNIFORM(0, 59, RANDOM()), 0) as transaction_time,
        CASE MOD(trans_num, 10)
            WHEN 0 THEN 'Single Day' WHEN 1 THEN 'Single Day' WHEN 2 THEN 'Single Day' WHEN 3 THEN 'Single Day'
            WHEN 4 THEN 'Multi-Day' WHEN 5 THEN 'Multi-Day' WHEN 6 THEN 'Annual Pass'
            WHEN 7 THEN 'VIP Experience' WHEN 8 THEN 'Group Rate' ELSE 'Single Day'
        END as ticket_type,
        UNIFORM(1, 8, RANDOM()) as ticket_quantity,
        -- Base prices vary by ticket type and park
        CASE 
            WHEN MOD(trans_num, 10) IN (0,1,2,3) THEN UNIFORM(89, 139, RANDOM()) -- Single Day
            WHEN MOD(trans_num, 10) IN (4,5) THEN UNIFORM(169, 289, RANDOM())    -- Multi-Day
            WHEN MOD(trans_num, 10) = 6 THEN UNIFORM(399, 699, RANDOM())         -- Annual Pass
            WHEN MOD(trans_num, 10) = 7 THEN UNIFORM(249, 499, RANDOM())         -- VIP Experience
            ELSE UNIFORM(69, 119, RANDOM())                                      -- Group Rate
        END as base_price,
        UNIFORM(0, 75, RANDOM()) as discount_amount,
        CASE MOD(trans_num, 8)
            WHEN 0 THEN 'Credit Card' WHEN 1 THEN 'Debit Card' WHEN 2 THEN 'PayPal'
            WHEN 3 THEN 'Apple Pay' WHEN 4 THEN 'Google Pay' WHEN 5 THEN 'Cash'
            WHEN 6 THEN 'Corporate Card' ELSE 'Gift Card'
        END as payment_method,
        CASE MOD(trans_num, 6)
            WHEN 0 THEN 'Online' WHEN 1 THEN 'Mobile App' WHEN 2 THEN 'Park Gate'
            WHEN 3 THEN 'Travel Agent' WHEN 4 THEN 'Corporate' ELSE 'Online'
        END as purchase_channel,
        CASE MOD(trans_num, 20)
            WHEN 0 THEN 'SUMMER20' WHEN 1 THEN 'EARLY15' WHEN 2 THEN 'FAMILY25'
            WHEN 3 THEN 'VIP10' WHEN 4 THEN 'LOYALTY5' ELSE NULL
        END as promotion_code,
        UNIFORM(1, 12, RANDOM()) as guest_count,
        UNIFORM(0, 180, RANDOM()) as booking_lead_days,
        MOD(trans_num, 200) = 0 as is_refunded -- 0.5% refund rate
    FROM transaction_base
    WHERE trans_num <= 500000
)
SELECT 
    transaction_id, customer_id, park_id, transaction_date, transaction_time,
    ticket_type, ticket_quantity, base_price, discount_amount,
    ROUND((base_price - discount_amount) * ticket_quantity, 2) as total_revenue,
    payment_method, purchase_channel, promotion_code, guest_count, booking_lead_days, is_refunded
FROM transaction_details;

-- =====================================================
-- 4. PARK PERFORMANCE - Daily Operational Metrics
-- =====================================================

CREATE OR REPLACE TABLE PARK_PERFORMANCE (
    performance_id STRING,
    park_id STRING,
    performance_date DATE,
    daily_attendance INTEGER,
    daily_revenue DECIMAL(12,2),
    average_guest_satisfaction DECIMAL(3,2), -- 1.0 to 5.0
    weather_condition STRING,
    temperature_f INTEGER,
    operating_hours DECIMAL(4,2),
    staff_count INTEGER,
    maintenance_hours INTEGER,
    capacity_utilization_pct DECIMAL(5,2),
    fastpass_usage_pct DECIMAL(5,2),
    food_beverage_revenue DECIMAL(10,2),
    merchandise_revenue DECIMAL(10,2),
    parking_revenue DECIMAL(8,2)
);

-- Generate daily park performance data
INSERT INTO PARK_PERFORMANCE
WITH date_park_combinations AS (
    SELECT 
        d.date_val,
        p.park_id,
        ROW_NUMBER() OVER (ORDER BY d.date_val, p.park_id) as performance_num
    FROM (
        SELECT DATEADD(day, SEQ4(), DATEADD(year, -2, CURRENT_DATE())) as date_val
        FROM TABLE(GENERATOR(ROWCOUNT => 730)) -- 2 years of data
    ) d
    CROSS JOIN (
        SELECT park_id FROM PARKS WHERE is_active = TRUE
    ) p
)
SELECT 
    'PERF' || LPAD(performance_num, 8, '0') as performance_id,
    park_id,
    date_val as performance_date,
    -- Attendance varies by season, day of week, and park capacity
    CASE 
        WHEN EXTRACT(month FROM date_val) IN (6,7,8) THEN UNIFORM(15000, 35000, RANDOM()) -- Summer
        WHEN EXTRACT(month FROM date_val) IN (11,12) THEN UNIFORM(12000, 28000, RANDOM()) -- Holidays
        WHEN EXTRACT(dow FROM date_val) IN (6,0) THEN UNIFORM(10000, 25000, RANDOM()) -- Weekends
        ELSE UNIFORM(5000, 18000, RANDOM()) -- Regular days
    END as daily_attendance,
    -- Revenue correlation with attendance
    CASE 
        WHEN EXTRACT(month FROM date_val) IN (6,7,8) THEN UNIFORM(1500000, 3500000, RANDOM()) -- Summer
        WHEN EXTRACT(month FROM date_val) IN (11,12) THEN UNIFORM(1200000, 2800000, RANDOM()) -- Holidays
        WHEN EXTRACT(dow FROM date_val) IN (6,0) THEN UNIFORM(1000000, 2500000, RANDOM()) -- Weekends
        ELSE UNIFORM(500000, 1800000, RANDOM()) -- Regular days
    END as daily_revenue,
    UNIFORM(35, 48, RANDOM()) / 10.0 as average_guest_satisfaction,
    CASE MOD(performance_num, 12)
        WHEN 0 THEN 'Sunny' WHEN 1 THEN 'Partly Cloudy' WHEN 2 THEN 'Cloudy' WHEN 3 THEN 'Light Rain'
        WHEN 4 THEN 'Heavy Rain' WHEN 5 THEN 'Thunderstorm' WHEN 6 THEN 'Fog' WHEN 7 THEN 'Windy'
        WHEN 8 THEN 'Hot' WHEN 9 THEN 'Perfect' WHEN 10 THEN 'Cool' ELSE 'Warm'
    END as weather_condition,
    -- Temperature varies by park location
    CASE 
        WHEN park_id = 'UDX-FL' THEN UNIFORM(65, 95, RANDOM())
        WHEN park_id = 'UDX-CA' THEN UNIFORM(55, 85, RANDOM())
        WHEN park_id IN ('UDX-JP', 'UDX-CN') THEN UNIFORM(35, 85, RANDOM())
        WHEN park_id = 'UDX-SG' THEN UNIFORM(75, 95, RANDOM())
        ELSE UNIFORM(50, 90, RANDOM())
    END as temperature_f,
    UNIFORM(8, 16, RANDOM()) as operating_hours,
    UNIFORM(200, 800, RANDOM()) as staff_count,
    UNIFORM(0, 8, RANDOM()) as maintenance_hours,
    UNIFORM(45, 95, RANDOM()) as capacity_utilization_pct,
    UNIFORM(15, 75, RANDOM()) as fastpass_usage_pct,
    UNIFORM(200000, 800000, RANDOM()) as food_beverage_revenue,
    UNIFORM(100000, 500000, RANDOM()) as merchandise_revenue,
    UNIFORM(25000, 150000, RANDOM()) as parking_revenue
FROM date_park_combinations;

-- =====================================================
-- 5. ATTRACTION ANALYTICS - Ride Performance Data
-- =====================================================

CREATE OR REPLACE TABLE ATTRACTION_ANALYTICS (
    analytics_id STRING,
    park_id STRING,
    attraction_id STRING,
    attraction_name STRING,
    attraction_type STRING, -- 'Roller Coaster', 'Dark Ride', 'Water Ride', 'Simulator', 'Family', 'Show'
    date_recorded DATE,
    hour_of_day INTEGER,
    guests_served INTEGER,
    average_wait_time INTEGER,
    max_wait_time INTEGER,
    guest_satisfaction_score DECIMAL(3,2),
    throughput_per_hour INTEGER,
    downtime_minutes INTEGER,
    fastpass_percentage DECIMAL(5,2),
    guest_demographic_primary STRING -- '18-25', '26-35', '36-45', '46+', 'Family'
);

-- Create attraction master data first
CREATE OR REPLACE TEMPORARY TABLE temp_attractions AS
SELECT * FROM VALUES
    ('UDX-FL', 'FL-001', 'The Incredible Hulk Coaster', 'Roller Coaster'),
    ('UDX-FL', 'FL-002', 'Harry Potter Escape from Gringotts', 'Dark Ride'),
    ('UDX-FL', 'FL-003', 'Transformers: The Ride 3D', 'Simulator'),
    ('UDX-FL', 'FL-004', 'The Mummy Returns', 'Dark Ride'),
    ('UDX-FL', 'FL-005', 'Despicable Me Minion Mayhem', 'Simulator'),
    ('UDX-FL', 'FL-006', 'Jurassic Park River Adventure', 'Water Ride'),
    ('UDX-FL', 'FL-007', 'VelociCoaster', 'Roller Coaster'),
    ('UDX-FL', 'FL-008', 'Hagrids Motorbike Adventure', 'Family'),
    ('UDX-CA', 'CA-001', 'Harry Potter Forbidden Journey', 'Dark Ride'),
    ('UDX-CA', 'CA-002', 'Jurassic World The Ride', 'Water Ride'),
    ('UDX-CA', 'CA-003', 'Transformers 3D', 'Simulator'),
    ('UDX-CA', 'CA-004', 'The Mummy', 'Dark Ride'),
    ('UDX-CA', 'CA-005', 'Super Nintendo World', 'Family'),
    ('UDX-JP', 'JP-001', 'The Flying Dinosaur', 'Roller Coaster'),
    ('UDX-JP', 'JP-002', 'Harry Potter Forbidden Journey', 'Dark Ride'),
    ('UDX-JP', 'JP-003', 'Mario Kart Koopas Challenge', 'Dark Ride'),
    ('UDX-JP', 'JP-004', 'Jaws', 'Water Ride'),
    ('UDX-SG', 'SG-001', 'Battlestar Galactica', 'Roller Coaster'),
    ('UDX-SG', 'SG-002', 'Transformers 3D', 'Simulator'),
    ('UDX-SG', 'SG-003', 'Jurassic Park Rapids', 'Water Ride'),
    ('UDX-CN', 'CN-001', 'Decepticoaster', 'Roller Coaster'),
    ('UDX-CN', 'CN-002', 'Harry Potter Forbidden Journey', 'Dark Ride'),
    ('UDX-CN', 'CN-003', 'Jurassic World Adventure', 'Water Ride')
AS attractions(park_id, attraction_id, attraction_name, attraction_type);

-- Generate attraction analytics data
INSERT INTO ATTRACTION_ANALYTICS
WITH date_hour_attraction AS (
    SELECT 
        d.date_val,
        h.hour_val,
        a.park_id,
        a.attraction_id,
        a.attraction_name,
        a.attraction_type,
        ROW_NUMBER() OVER (ORDER BY d.date_val, h.hour_val, a.attraction_id) as analytics_num
    FROM (
        SELECT DATEADD(day, SEQ4(), DATEADD(month, -6, CURRENT_DATE())) as date_val
        FROM TABLE(GENERATOR(ROWCOUNT => 180)) -- 6 months of data
    ) d
    CROSS JOIN (
        SELECT SEQ4() as hour_val
        FROM TABLE(GENERATOR(ROWCOUNT => 14))  -- Park hours: 8 AM to 9 PM
        WHERE SEQ4() BETWEEN 8 AND 21
    ) h
    CROSS JOIN temp_attractions a
)
SELECT 
    'ATTR' || LPAD(analytics_num, 10, '0') as analytics_id,
    park_id,
    attraction_id,
    attraction_name,
    attraction_type,
    date_val as date_recorded,
    hour_val as hour_of_day,
    -- Guests served varies by attraction type and time
    CASE 
        WHEN attraction_type = 'Roller Coaster' THEN UNIFORM(800, 1200, RANDOM())
        WHEN attraction_type = 'Dark Ride' THEN UNIFORM(1000, 1800, RANDOM())
        WHEN attraction_type = 'Simulator' THEN UNIFORM(600, 1200, RANDOM())
        WHEN attraction_type = 'Water Ride' THEN UNIFORM(900, 1500, RANDOM())
        WHEN attraction_type = 'Family' THEN UNIFORM(1200, 2000, RANDOM())
        ELSE UNIFORM(500, 1000, RANDOM())
    END as guests_served,
    -- Wait times vary by popularity and time of day
    CASE 
        WHEN hour_val IN (11, 12, 13, 14, 15, 16) THEN UNIFORM(30, 120, RANDOM()) -- Peak hours
        WHEN hour_val IN (8, 9, 19, 20, 21) THEN UNIFORM(5, 45, RANDOM()) -- Off-peak
        ELSE UNIFORM(15, 75, RANDOM()) -- Regular
    END as average_wait_time,
    CASE 
        WHEN hour_val IN (11, 12, 13, 14, 15, 16) THEN UNIFORM(60, 180, RANDOM()) -- Peak hours
        WHEN hour_val IN (8, 9, 19, 20, 21) THEN UNIFORM(10, 60, RANDOM()) -- Off-peak
        ELSE UNIFORM(25, 90, RANDOM()) -- Regular
    END as max_wait_time,
    UNIFORM(35, 48, RANDOM()) / 10.0 as guest_satisfaction_score,
    CASE 
        WHEN attraction_type = 'Roller Coaster' THEN UNIFORM(800, 1200, RANDOM())
        WHEN attraction_type = 'Dark Ride' THEN UNIFORM(1000, 1800, RANDOM())
        WHEN attraction_type = 'Simulator' THEN UNIFORM(600, 1200, RANDOM())
        WHEN attraction_type = 'Water Ride' THEN UNIFORM(900, 1500, RANDOM())
        WHEN attraction_type = 'Family' THEN UNIFORM(1200, 2000, RANDOM())
        ELSE UNIFORM(500, 1000, RANDOM())
    END as throughput_per_hour,
    CASE 
        WHEN MOD(analytics_num, 50) = 0 THEN UNIFORM(30, 120, RANDOM()) -- Scheduled maintenance
        WHEN MOD(analytics_num, 500) = 0 THEN UNIFORM(120, 480, RANDOM()) -- Major downtime
        ELSE 0
    END as downtime_minutes,
    UNIFORM(20, 60, RANDOM()) as fastpass_percentage,
    CASE MOD(analytics_num, 5)
        WHEN 0 THEN '18-25' WHEN 1 THEN '26-35' WHEN 2 THEN '36-45'
        WHEN 3 THEN '46+' ELSE 'Family'
    END as guest_demographic_primary
FROM date_hour_attraction
WHERE analytics_num <= 100000;

-- =====================================================
-- 6. MARKETING CAMPAIGNS - Campaign Performance
-- =====================================================

CREATE OR REPLACE TABLE MARKETING_CAMPAIGNS (
    campaign_id STRING,
    campaign_name STRING,
    channel STRING, -- 'Social Media', 'Email', 'TV', 'Radio', 'Online Display', 'Search', 'Influencer'
    campaign_start_date DATE,
    campaign_end_date DATE,
    target_audience STRING,
    budget_allocated DECIMAL(10,2),
    budget_spent DECIMAL(10,2),
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    revenue_attributed DECIMAL(12,2),
    cost_per_acquisition DECIMAL(8,2),
    return_on_ad_spend DECIMAL(6,2),
    status STRING -- 'Active', 'Completed', 'Paused', 'Cancelled'
);

INSERT INTO MARKETING_CAMPAIGNS
WITH campaign_base AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as campaign_num
    FROM TABLE(GENERATOR(ROWCOUNT => 200))
)
SELECT 
    'CAMP' || LPAD(campaign_num, 6, '0') as campaign_id,
    CASE MOD(campaign_num, 20)
        WHEN 0 THEN 'Summer Spectacular 2024' WHEN 1 THEN 'Family Fun Festival' WHEN 2 THEN 'Holiday Magic'
        WHEN 3 THEN 'Spring Break Special' WHEN 4 THEN 'VIP Experience Launch' WHEN 5 THEN 'New Attraction Reveal'
        WHEN 6 THEN 'Annual Pass Promotion' WHEN 7 THEN 'Local Resident Discount' WHEN 8 THEN 'Corporate Group Sales'
        WHEN 9 THEN 'International Tourist Welcome' WHEN 10 THEN 'Student Discount Program' WHEN 11 THEN 'Senior Savings'
        WHEN 12 THEN 'Back to School Special' WHEN 13 THEN 'Halloween Horror Nights' WHEN 14 THEN 'Winter Wonderland'
        WHEN 15 THEN 'Valentines Romance Package' WHEN 16 THEN 'Graduation Celebration' WHEN 17 THEN 'Military Appreciation'
        WHEN 18 THEN 'Teacher Appreciation' ELSE 'Flash Sale Weekend'
    END as campaign_name,
    CASE MOD(campaign_num, 7)
        WHEN 0 THEN 'Social Media' WHEN 1 THEN 'Email' WHEN 2 THEN 'TV' WHEN 3 THEN 'Online Display'
        WHEN 4 THEN 'Search' WHEN 5 THEN 'Influencer' ELSE 'Radio'
    END as channel,
    DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) as campaign_start_date,
    DATEADD(day, UNIFORM(7, 90, RANDOM()), DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE())) as campaign_end_date,
    CASE MOD(campaign_num, 8)
        WHEN 0 THEN 'Families with Children' WHEN 1 THEN 'Young Adults 18-35' WHEN 2 THEN 'Local Residents'
        WHEN 3 THEN 'International Tourists' WHEN 4 THEN 'Corporate Groups' WHEN 5 THEN 'Students'
        WHEN 6 THEN 'Seniors 55+' ELSE 'General Audience'
    END as target_audience,
    UNIFORM(10000, 500000, RANDOM()) as budget_allocated,
    UNIFORM(8000, 450000, RANDOM()) as budget_spent,
    UNIFORM(100000, 5000000, RANDOM()) as impressions,
    UNIFORM(1000, 150000, RANDOM()) as clicks,
    UNIFORM(50, 5000, RANDOM()) as conversions,
    UNIFORM(25000, 2500000, RANDOM()) as revenue_attributed,
    UNIFORM(25, 250, RANDOM()) as cost_per_acquisition,
    UNIFORM(1.5, 12.0, RANDOM()) as return_on_ad_spend,
    CASE MOD(campaign_num, 4)
        WHEN 0 THEN 'Active' WHEN 1 THEN 'Completed' WHEN 2 THEN 'Paused' ELSE 'Completed'
    END as status
FROM campaign_base
WHERE campaign_num <= 200;

-- =====================================================
-- 7. FINANCIAL SUMMARY - Daily Financial Rollups
-- =====================================================

CREATE OR REPLACE TABLE FINANCIAL_SUMMARY (
    summary_id STRING,
    park_id STRING,
    summary_date DATE,
    ticket_revenue DECIMAL(12,2),
    food_beverage_revenue DECIMAL(10,2),
    merchandise_revenue DECIMAL(10,2),
    parking_revenue DECIMAL(8,2),
    total_revenue DECIMAL(12,2),
    operating_costs DECIMAL(10,2),
    gross_profit DECIMAL(12,2),
    guest_count INTEGER,
    revenue_per_guest DECIMAL(8,2),
    profit_margin_pct DECIMAL(5,2),
    year_over_year_growth_pct DECIMAL(6,2)
);

-- Generate financial summary data based on park performance
INSERT INTO FINANCIAL_SUMMARY
SELECT 
    'FIN' || LPAD(ROW_NUMBER() OVER (ORDER BY park_id, performance_date), 8, '0') as summary_id,
    park_id,
    performance_date as summary_date,
    daily_revenue as ticket_revenue,
    food_beverage_revenue,
    merchandise_revenue,
    parking_revenue,
    daily_revenue + food_beverage_revenue + merchandise_revenue + parking_revenue as total_revenue,
    ROUND(daily_revenue * UNIFORM(0.4, 0.7, RANDOM()), 2) as operating_costs,
    ROUND((daily_revenue + food_beverage_revenue + merchandise_revenue + parking_revenue) * UNIFORM(0.3, 0.6, RANDOM()), 2) as gross_profit,
    daily_attendance as guest_count,
    ROUND((daily_revenue + food_beverage_revenue + merchandise_revenue + parking_revenue) / daily_attendance, 2) as revenue_per_guest,
    UNIFORM(25, 60, RANDOM()) as profit_margin_pct,
    UNIFORM(-15, 25, RANDOM()) as year_over_year_growth_pct
FROM PARK_PERFORMANCE
WHERE daily_attendance > 0;

-- =====================================================
-- 8. DATA LOADING SUMMARY AND VALIDATION
-- =====================================================

-- Create data quality summary for validation
SELECT 'Business Analytics Data Loading Completed!' as status,
       (SELECT COUNT(*) FROM PARKS) as parks_loaded,
       (SELECT COUNT(*) FROM CUSTOMERS) as customers_loaded,
       (SELECT COUNT(*) FROM SALES_TRANSACTIONS) as transactions_loaded,
       (SELECT COUNT(*) FROM PARK_PERFORMANCE) as performance_records_loaded,
       (SELECT COUNT(*) FROM ATTRACTION_ANALYTICS) as attraction_analytics_loaded,
       (SELECT COUNT(*) FROM MARKETING_CAMPAIGNS) as campaigns_loaded,
       (SELECT COUNT(*) FROM FINANCIAL_SUMMARY) as financial_summaries_loaded;

-- Validate data relationships and business metrics
SELECT 'Business Metrics Validation' as validation_type,
       ROUND(SUM(total_revenue), 2) as total_revenue_all_transactions,
       ROUND(AVG(total_lifetime_revenue), 2) as avg_customer_lifetime_value,
       COUNT(DISTINCT customer_id) as unique_customers_with_transactions,
       COUNT(DISTINCT park_id) as active_parks_with_data,
       MIN(transaction_date) as earliest_transaction,
       MAX(transaction_date) as latest_transaction
FROM SALES_TRANSACTIONS;

-- Sample business query validation
SELECT 'Sample NL2SQL Query Test' as test_type,
       'Top 5 customers by revenue' as business_question,
       customer_id,
       total_lifetime_revenue
FROM CUSTOMERS
ORDER BY total_lifetime_revenue DESC
LIMIT 5; 