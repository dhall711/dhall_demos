-- =====================================================
-- UDX Data Quality Project: Sample Data Loading
-- =====================================================
-- This script creates realistic theme park operational data
-- with intentional data quality issues for learning purposes

USE DATABASE UDX_DATA_QUALITY_PROJECT;
USE SCHEMA THEME_PARK_OPS;
USE WAREHOUSE UDX_AI_WAREHOUSE;

-- =====================================================
-- 1. THEME PARKS MASTER DATA
-- =====================================================

CREATE OR REPLACE TABLE PARKS (
    park_id STRING,
    park_name STRING,
    location STRING,
    region STRING,
    opening_date DATE,
    total_capacity INTEGER,
    is_active BOOLEAN
);

INSERT INTO PARKS VALUES
    ('UDX-FL', 'Universal Studios Florida', 'Orlando, FL', 'Southeast', '1990-06-07', 35000, TRUE),
    ('UDX-CA', 'Universal Studios Hollywood', 'Los Angeles, CA', 'West', '1964-07-15', 28000, TRUE),
    ('UDX-JP', 'Universal Studios Japan', 'Osaka, Japan', 'Asia Pacific', '2001-03-31', 30000, TRUE),
    ('UDX-SG', 'Universal Studios Singapore', 'Singapore', 'Asia Pacific', '2010-03-18', 25000, TRUE),
    ('UDX-CN', 'Universal Beijing Resort', 'Beijing, China', 'Asia Pacific', '2021-09-20', 40000, TRUE),
    ('UDX-EP', 'Epic Universe Orlando', 'Orlando, FL', 'Southeast', '2025-01-01', 50000, FALSE); -- Future park

-- =====================================================
-- 2. RIDES AND ATTRACTIONS
-- =====================================================

CREATE OR REPLACE TABLE RIDES (
    ride_id STRING,
    park_id STRING,
    ride_name STRING,
    ride_type STRING, -- 'Roller Coaster', 'Dark Ride', 'Water Ride', 'Simulator', 'Family'
    thrill_level STRING, -- 'Family', 'Moderate', 'Intense', 'Extreme'
    hourly_capacity INTEGER,
    height_requirement INTEGER, -- in cm
    opened_date DATE,
    is_operational BOOLEAN,
    maintenance_frequency_days INTEGER
);

INSERT INTO RIDES VALUES
    -- Universal Studios Florida
    ('FL-001', 'UDX-FL', 'The Incredible Hulk Coaster', 'Roller Coaster', 'Extreme', 1920, 137, '1999-05-28', TRUE, 30),
    ('FL-002', 'UDX-FL', 'Harry Potter and the Escape from Gringotts', 'Dark Ride', 'Moderate', 1440, 107, '2014-07-08', TRUE, 14),
    ('FL-003', 'UDX-FL', 'Transformers: The Ride 3D', 'Simulator', 'Intense', 1200, 102, '2013-06-20', TRUE, 21),
    ('FL-004', 'UDX-FL', 'The Mummy Returns', 'Dark Ride', 'Intense', 1800, 122, '2004-05-21', TRUE, 28),
    ('FL-005', 'UDX-FL', 'Despicable Me Minion Mayhem', 'Simulator', 'Family', 2400, 0, '2012-07-02', TRUE, 14),
    ('FL-006', 'UDX-FL', 'Jurassic Park River Adventure', 'Water Ride', 'Moderate', 1800, 107, '1999-03-20', TRUE, 35),
    ('FL-007', 'UDX-FL', 'VelociCoaster', 'Roller Coaster', 'Extreme', 1440, 125, '2021-06-10', TRUE, 30),
    ('FL-008', 'UDX-FL', 'Hagrid''s Magical Creatures Motorbike Adventure', 'Family', 'Moderate', 1440, 122, '2019-06-13', TRUE, 21),
    
    -- Universal Studios Hollywood  
    ('CA-001', 'UDX-CA', 'The Wizarding World of Harry Potter', 'Dark Ride', 'Moderate', 1800, 107, '2016-04-07', TRUE, 14),
    ('CA-002', 'UDX-CA', 'Jurassic World - The Ride', 'Water Ride', 'Intense', 2000, 107, '2019-07-12', TRUE, 28),
    ('CA-003', 'UDX-CA', 'Transformers: The Ride 3D', 'Simulator', 'Intense', 1200, 102, '2012-05-25', TRUE, 21),
    ('CA-004', 'UDX-CA', 'The Mummy Returns', 'Dark Ride', 'Intense', 1800, 122, '2004-06-25', TRUE, 28),
    ('CA-005', 'UDX-CA', 'Super Nintendo World', 'Family', 'Family', 2000, 0, '2023-02-17', TRUE, 7),
    
    -- Universal Studios Japan
    ('JP-001', 'UDX-JP', 'The Flying Dinosaur', 'Roller Coaster', 'Extreme', 1000, 132, '2016-03-18', TRUE, 30),
    ('JP-002', 'UDX-JP', 'Harry Potter and the Forbidden Journey', 'Dark Ride', 'Moderate', 1800, 122, '2014-07-15', TRUE, 14),
    ('JP-003', 'UDX-JP', 'Mario Kart: Koopa''s Challenge', 'Dark Ride', 'Family', 1600, 107, '2021-03-18', TRUE, 14),
    ('JP-004', 'UDX-JP', 'Jaws', 'Water Ride', 'Moderate', 1440, 0, '2001-03-31', TRUE, 35),
    
    -- Universal Studios Singapore
    ('SG-001', 'UDX-SG', 'Battlestar Galactica: Human vs Cylon', 'Roller Coaster', 'Extreme', 1600, 125, '2010-03-18', TRUE, 30),
    ('SG-002', 'UDX-SG', 'Transformers: The Ride 3D', 'Simulator', 'Intense', 1200, 102, '2011-12-03', TRUE, 21),
    ('SG-003', 'UDX-SG', 'Jurassic Park Rapids Adventure', 'Water Ride', 'Moderate', 1800, 107, '2010-03-18', TRUE, 35),
    ('SG-004', 'UDX-SG', 'Revenge of the Mummy', 'Dark Ride', 'Intense', 1800, 122, '2010-03-18', TRUE, 28),
    
    -- Universal Beijing Resort
    ('CN-001', 'UDX-CN', 'Decepticoaster', 'Roller Coaster', 'Extreme', 1200, 132, '2021-09-20', TRUE, 30),
    ('CN-002', 'UDX-CN', 'Harry Potter and the Forbidden Journey', 'Dark Ride', 'Moderate', 1800, 122, '2021-09-20', TRUE, 14),
    ('CN-003', 'UDX-CN', 'Jurassic World Adventure', 'Water Ride', 'Intense', 2000, 107, '2021-09-20', TRUE, 28);

-- =====================================================
-- 3. GUEST DEMOGRAPHICS (with data quality issues)
-- =====================================================

CREATE OR REPLACE TABLE GUESTS (
    guest_id STRING,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone STRING,
    birth_date DATE,
    age INTEGER,
    gender STRING,
    country STRING,
    state_province STRING,
    zip_code STRING,
    preferred_language STRING,
    marketing_opt_in BOOLEAN,
    loyalty_tier STRING, -- 'Bronze', 'Silver', 'Gold', 'Platinum'
    registration_date DATE,
    last_visit_date DATE
);

-- Generate sample guest data (this would typically be much larger)
-- Note: Intentional data quality issues included for learning purposes

INSERT INTO GUESTS 
WITH guest_base AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as guest_num
    FROM TABLE(GENERATOR(ROWCOUNT => 10000))
),
guest_details AS (
    SELECT 
        guest_num,
        'G' || LPAD(guest_num, 8, '0') as guest_id,
        CASE MOD(guest_num, 20)
            WHEN 0 THEN 'James' WHEN 1 THEN 'Mary' WHEN 2 THEN 'John' WHEN 3 THEN 'Patricia'
            WHEN 4 THEN 'Robert' WHEN 5 THEN 'Jennifer' WHEN 6 THEN 'Michael' WHEN 7 THEN 'Linda'
            WHEN 8 THEN 'William' WHEN 9 THEN 'Elizabeth' WHEN 10 THEN 'David' WHEN 11 THEN 'Barbara'
            WHEN 12 THEN 'Richard' WHEN 13 THEN 'Susan' WHEN 14 THEN 'Joseph' WHEN 15 THEN 'Jessica'
            WHEN 16 THEN 'Thomas' WHEN 17 THEN 'Sarah' WHEN 18 THEN 'Christopher' ELSE 'Karen'
        END as first_name,
        CASE MOD(guest_num, 15)
            WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Brown'
            WHEN 4 THEN 'Jones' WHEN 5 THEN 'Garcia' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Davis'
            WHEN 8 THEN 'Rodriguez' WHEN 9 THEN 'Martinez' WHEN 10 THEN 'Hernandez'
            WHEN 11 THEN 'Lopez' WHEN 12 THEN 'Gonzalez' WHEN 13 THEN 'Wilson' ELSE 'Anderson'
        END as last_name,
        -- Intentional data quality issue: Some missing emails (5% null rate)
        CASE WHEN MOD(guest_num, 20) = 0 THEN NULL 
             ELSE LOWER(
                CASE MOD(guest_num, 20)
                    WHEN 1 THEN 'james' WHEN 2 THEN 'mary' WHEN 3 THEN 'john' WHEN 4 THEN 'patricia'
                    WHEN 5 THEN 'robert' WHEN 6 THEN 'jennifer' WHEN 7 THEN 'michael' WHEN 8 THEN 'linda'
                    WHEN 9 THEN 'william' WHEN 10 THEN 'elizabeth' WHEN 11 THEN 'david' WHEN 12 THEN 'barbara'
                    WHEN 13 THEN 'richard' WHEN 14 THEN 'susan' WHEN 15 THEN 'joseph' WHEN 16 THEN 'jessica'
                    WHEN 17 THEN 'thomas' WHEN 18 THEN 'sarah' ELSE 'chris'
                END || '.' || 
                CASE MOD(guest_num, 15)
                    WHEN 0 THEN 'smith' WHEN 1 THEN 'johnson' WHEN 2 THEN 'williams' WHEN 3 THEN 'brown'
                    WHEN 4 THEN 'jones' WHEN 5 THEN 'garcia' WHEN 6 THEN 'miller' WHEN 7 THEN 'davis'
                    WHEN 8 THEN 'rodriguez' WHEN 9 THEN 'martinez' WHEN 10 THEN 'hernandez'
                    WHEN 11 THEN 'lopez' WHEN 12 THEN 'gonzalez' WHEN 13 THEN 'wilson' ELSE 'anderson'
                END || '@' ||
                CASE MOD(guest_num, 8)
                    WHEN 0 THEN 'gmail.com' WHEN 1 THEN 'yahoo.com' WHEN 2 THEN 'hotmail.com'
                    WHEN 3 THEN 'outlook.com' WHEN 4 THEN 'aol.com' WHEN 5 THEN 'icloud.com'
                    WHEN 6 THEN 'comcast.net' ELSE 'example.com'
                END
             )
        END as email,
        -- Phone numbers with some formatting inconsistencies
        CASE MOD(guest_num, 10)
            WHEN 0 THEN '+1-' || (555000000 + guest_num)::STRING
            WHEN 1 THEN '(' || SUBSTR((555000000 + guest_num)::STRING, 1, 3) || ') ' || 
                       SUBSTR((555000000 + guest_num)::STRING, 4, 3) || '-' || 
                       SUBSTR((555000000 + guest_num)::STRING, 7, 4)
            WHEN 2 THEN (555000000 + guest_num)::STRING
            ELSE SUBSTR((555000000 + guest_num)::STRING, 1, 3) || '-' || 
                 SUBSTR((555000000 + guest_num)::STRING, 4, 3) || '-' || 
                 SUBSTR((555000000 + guest_num)::STRING, 7, 4)
        END as phone,
        -- Birth dates with some outliers (data quality issue)
        CASE WHEN MOD(guest_num, 500) = 0 THEN DATE '1800-01-01'  -- Outlier: too old
             WHEN MOD(guest_num, 1000) = 0 THEN DATE '2030-01-01' -- Outlier: future date
             ELSE DATEADD(day, -UNIFORM(18*365, 80*365, RANDOM()), CURRENT_DATE())
        END as birth_date,
        -- Age calculation (some inconsistencies with birth_date - data quality issue)
        CASE WHEN MOD(guest_num, 500) = 0 THEN 250  -- Inconsistent with birth_date
             WHEN MOD(guest_num, 1000) = 0 THEN -5   -- Negative age
             ELSE UNIFORM(18, 80, RANDOM())
        END as age,
        CASE MOD(guest_num, 3) WHEN 0 THEN 'M' WHEN 1 THEN 'F' ELSE 'O' END as gender,
        CASE MOD(guest_num, 10)
            WHEN 0 THEN 'United States' WHEN 1 THEN 'Canada' WHEN 2 THEN 'United Kingdom'
            WHEN 3 THEN 'Japan' WHEN 4 THEN 'Germany' WHEN 5 THEN 'France'
            WHEN 6 THEN 'Australia' WHEN 7 THEN 'Brazil' WHEN 8 THEN 'China' ELSE 'Mexico'
        END as country,
        CASE MOD(guest_num, 50)
            WHEN 0 THEN 'California' WHEN 1 THEN 'Florida' WHEN 2 THEN 'New York' WHEN 3 THEN 'Texas'
            WHEN 4 THEN 'Ontario' WHEN 5 THEN 'London' WHEN 6 THEN 'Tokyo' WHEN 7 THEN 'Beijing'
            ELSE 'Other'
        END as state_province,
        -- Zip codes with some invalid formats (data quality issue)
        CASE WHEN MOD(guest_num, 100) = 0 THEN 'INVALID'  -- Invalid zip
             WHEN MOD(guest_num, 200) = 0 THEN '1234'      -- Too short
             ELSE LPAD((10000 + guest_num % 90000)::STRING, 5, '0')
        END as zip_code,
        CASE MOD(guest_num, 5)
            WHEN 0 THEN 'English' WHEN 1 THEN 'Spanish' WHEN 2 THEN 'French'
            WHEN 3 THEN 'Japanese' ELSE 'Mandarin'
        END as preferred_language,
        MOD(guest_num, 3) = 0 as marketing_opt_in,
        CASE MOD(guest_num, 4)
            WHEN 0 THEN 'Bronze' WHEN 1 THEN 'Silver' WHEN 2 THEN 'Gold' ELSE 'Platinum'
        END as loyalty_tier,
        DATEADD(day, -UNIFORM(1, 365*3, RANDOM()), CURRENT_DATE()) as registration_date,
        DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE()) as last_visit_date
    FROM guest_base
    WHERE guest_num <= 10000
)
SELECT * FROM guest_details;

-- =====================================================
-- 4. TICKET SALES DATA (with anomalies)
-- =====================================================

CREATE OR REPLACE TABLE TICKETS (
    ticket_id STRING,
    guest_id STRING,
    park_id STRING,
    ticket_type STRING, -- 'Single Day', 'Multi-Day', 'Annual Pass', 'VIP'
    purchase_date DATE,
    visit_date DATE,
    purchase_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    payment_method STRING,
    purchase_channel STRING, -- 'Online', 'Mobile App', 'Park Gate', 'Third Party'
    is_used BOOLEAN,
    guest_count INTEGER -- Number of guests on this ticket
);

-- Generate ticket data with intentional anomalies
INSERT INTO TICKETS
WITH ticket_base AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY RANDOM()) as ticket_num
    FROM TABLE(GENERATOR(ROWCOUNT => 50000))
),
ticket_details AS (
    SELECT 
        ticket_num,
        'T' || LPAD(ticket_num, 10, '0') as ticket_id,
        'G' || LPAD(UNIFORM(1, 10000, RANDOM()), 8, '0') as guest_id,
        CASE MOD(ticket_num, 6)
            WHEN 0 THEN 'UDX-FL' WHEN 1 THEN 'UDX-CA' WHEN 2 THEN 'UDX-JP'
            WHEN 3 THEN 'UDX-SG' WHEN 4 THEN 'UDX-CN' ELSE 'UDX-FL'
        END as park_id,
        CASE MOD(ticket_num, 4)
            WHEN 0 THEN 'Single Day' WHEN 1 THEN 'Multi-Day'
            WHEN 2 THEN 'Annual Pass' ELSE 'VIP'
        END as ticket_type,
        DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) as purchase_date,
        DATEADD(day, UNIFORM(0, 30, RANDOM()), 
                DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE())) as visit_date,
        -- Purchase amounts with some anomalies
        CASE WHEN MOD(ticket_num, 1000) = 0 THEN -50.00  -- Negative amount (refund issue)
             WHEN MOD(ticket_num, 2000) = 0 THEN 99999.99 -- Extremely high amount
             WHEN MOD(ticket_num, 4) = 0 THEN UNIFORM(89, 129, RANDOM()) -- Single Day: $89-129
             WHEN MOD(ticket_num, 4) = 1 THEN UNIFORM(179, 289, RANDOM()) -- Multi-Day: $179-289
             WHEN MOD(ticket_num, 4) = 2 THEN UNIFORM(399, 599, RANDOM()) -- Annual: $399-599
             ELSE UNIFORM(249, 349, RANDOM()) -- VIP: $249-349
        END as purchase_amount,
        UNIFORM(0, 50, RANDOM()) as discount_amount,
        CASE MOD(ticket_num, 5)
            WHEN 0 THEN 'Credit Card' WHEN 1 THEN 'Debit Card' WHEN 2 THEN 'PayPal'
            WHEN 3 THEN 'Apple Pay' ELSE 'Cash'
        END as payment_method,
        CASE MOD(ticket_num, 4)
            WHEN 0 THEN 'Online' WHEN 1 THEN 'Mobile App'
            WHEN 2 THEN 'Park Gate' ELSE 'Third Party'
        END as purchase_channel,
        ticket_num % 10 != 0 as is_used, -- 90% of tickets are used
        UNIFORM(1, 6, RANDOM()) as guest_count
    FROM ticket_base
    WHERE ticket_num <= 50000
)
SELECT * FROM ticket_details;

-- =====================================================
-- 5. RIDE OPERATIONS DATA (with quality issues)
-- =====================================================

CREATE OR REPLACE TABLE RIDE_OPERATIONS (
    operation_id STRING,
    ride_id STRING,
    park_id STRING,
    operation_date DATE,
    operation_hour INTEGER, -- 0-23
    guests_served INTEGER,
    wait_time_minutes INTEGER,
    downtime_minutes INTEGER,
    weather_condition STRING,
    staff_count INTEGER,
    hourly_capacity INTEGER, -- May differ from ride specification
    guest_satisfaction_score DECIMAL(3,2), -- 1.00 to 5.00
    maintenance_performed BOOLEAN
);

-- Generate operational data with realistic patterns and issues
INSERT INTO RIDE_OPERATIONS
WITH date_hours AS (
    SELECT 
        d.date_val,
        h.hour_val,
        ROW_NUMBER() OVER (ORDER BY d.date_val, h.hour_val, RANDOM()) as row_num
    FROM (
        SELECT DATEADD(day, SEQ4(), DATE '2024-01-01') as date_val
        FROM TABLE(GENERATOR(ROWCOUNT => 365))
    ) d
    CROSS JOIN (
        SELECT SEQ4() as hour_val
        FROM TABLE(GENERATOR(ROWCOUNT => 16))  -- Park hours: 8 AM to 11 PM
        WHERE SEQ4() BETWEEN 8 AND 23
    ) h
),
ride_ops AS (
    SELECT 
        dh.row_num,
        dh.date_val,
        dh.hour_val,
        r.ride_id,
        r.park_id,
        r.hourly_capacity as ride_capacity,
        -- Intentional data quality issues
        CASE 
            WHEN MOD(dh.row_num, 500) = 0 THEN 9999 -- Impossible wait time
            WHEN MOD(dh.row_num, 1000) = 0 THEN -10 -- Negative wait time
            WHEN r.ride_type = 'Roller Coaster' THEN UNIFORM(30, 120, RANDOM())
            WHEN r.ride_type = 'Dark Ride' THEN UNIFORM(15, 60, RANDOM())
            WHEN r.ride_type = 'Water Ride' THEN UNIFORM(20, 90, RANDOM())
            WHEN r.ride_type = 'Simulator' THEN UNIFORM(25, 75, RANDOM())
            ELSE UNIFORM(5, 30, RANDOM())
        END as wait_time_minutes,
        -- Downtime with some anomalies
        CASE 
            WHEN MOD(dh.row_num, 100) = 0 THEN UNIFORM(30, 120, RANDOM()) -- Scheduled maintenance
            WHEN MOD(dh.row_num, 2000) = 0 THEN 480 -- Major breakdown (8 hours)
            ELSE 0
        END as downtime_minutes,
        CASE MOD(dh.row_num, 10)
            WHEN 0 THEN 'Sunny' WHEN 1 THEN 'Partly Cloudy' WHEN 2 THEN 'Cloudy'
            WHEN 3 THEN 'Light Rain' WHEN 4 THEN 'Heavy Rain' WHEN 5 THEN 'Thunderstorm'
            WHEN 6 THEN 'Fog' WHEN 7 THEN 'Windy' WHEN 8 THEN 'Hot' ELSE 'Perfect'
        END as weather_condition,
        UNIFORM(2, 8, RANDOM()) as staff_count,
        -- Hourly capacity that may differ from ride specs (consistency issue)
        CASE 
            WHEN MOD(dh.row_num, 200) = 0 THEN r.hourly_capacity * 2 -- Impossible capacity
            WHEN MOD(dh.row_num, 300) = 0 THEN 0 -- Zero capacity
            ELSE UNIFORM(r.hourly_capacity * 0.7, r.hourly_capacity * 1.1, RANDOM())
        END as actual_capacity,
        -- Guest satisfaction with some anomalies
        CASE 
            WHEN MOD(dh.row_num, 1500) = 0 THEN 0.5 -- Extremely low satisfaction
            WHEN MOD(dh.row_num, 2000) = 0 THEN 6.0 -- Above maximum scale
            ELSE UNIFORM(3.5, 4.8, RANDOM()) / 1.0
        END as satisfaction_score
    FROM date_hours dh
    CROSS JOIN (SELECT * FROM RIDES WHERE is_operational = TRUE) r
    WHERE dh.row_num <= 100000
)
SELECT 
    'OP' || LPAD(row_num, 10, '0') as operation_id,
    ride_id,
    park_id,
    date_val as operation_date,
    hour_val as operation_hour,
    CASE 
        WHEN downtime_minutes > 0 THEN 0
        ELSE UNIFORM(actual_capacity * 0.3, actual_capacity * 0.9, RANDOM())
    END as guests_served,
    wait_time_minutes,
    downtime_minutes,
    weather_condition,
    staff_count,
    actual_capacity as hourly_capacity,
    satisfaction_score as guest_satisfaction_score,
    downtime_minutes > 0 as maintenance_performed
FROM ride_ops;

-- =====================================================
-- 6. WEATHER DATA
-- =====================================================

CREATE OR REPLACE TABLE WEATHER (
    weather_id STRING,
    park_id STRING,
    date_recorded DATE,
    temperature_f INTEGER,
    humidity_percent INTEGER,
    precipitation_inches DECIMAL(4,2),
    wind_speed_mph INTEGER,
    weather_condition STRING,
    visibility_miles INTEGER
);

INSERT INTO WEATHER
WITH weather_data AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY date_val, park_id) as weather_num,
        date_val,
        park_id
    FROM (
        SELECT DATEADD(day, SEQ4(), DATE '2024-01-01') as date_val
        FROM TABLE(GENERATOR(ROWCOUNT => 365))
    ) d
    CROSS JOIN (
        SELECT DISTINCT park_id FROM PARKS WHERE is_active = TRUE
    ) p
)
SELECT 
    'W' || LPAD(weather_num, 8, '0') as weather_id,
    park_id,
    date_val as date_recorded,
    -- Temperature based on location
    CASE 
        WHEN park_id IN ('UDX-FL') THEN UNIFORM(65, 95, RANDOM())
        WHEN park_id IN ('UDX-CA') THEN UNIFORM(55, 85, RANDOM())
        WHEN park_id IN ('UDX-JP', 'UDX-CN') THEN UNIFORM(35, 85, RANDOM())
        WHEN park_id IN ('UDX-SG') THEN UNIFORM(75, 95, RANDOM())
        ELSE UNIFORM(50, 90, RANDOM())
    END as temperature_f,
    UNIFORM(30, 90, RANDOM()) as humidity_percent,
    -- Some extreme precipitation values (data quality issue)
    CASE 
        WHEN MOD(weather_num, 100) = 0 THEN 25.5  -- Extreme rainfall
        WHEN MOD(weather_num, 20) = 0 THEN UNIFORM(0.1, 2.0, RANDOM())
        ELSE 0.0
    END as precipitation_inches,
    UNIFORM(0, 35, RANDOM()) as wind_speed_mph,
    CASE MOD(weather_num, 10)
        WHEN 0 THEN 'Sunny' WHEN 1 THEN 'Partly Cloudy' WHEN 2 THEN 'Cloudy'
        WHEN 3 THEN 'Light Rain' WHEN 4 THEN 'Heavy Rain' WHEN 5 THEN 'Thunderstorm'
        WHEN 6 THEN 'Fog' WHEN 7 THEN 'Windy' WHEN 8 THEN 'Hot' ELSE 'Perfect'
    END as weather_condition,
    UNIFORM(1, 10, RANDOM()) as visibility_miles
FROM weather_data;

-- =====================================================
-- 7. DATA LOADING SUMMARY
-- =====================================================

SELECT 'Data loading completed!' as status,
       (SELECT COUNT(*) FROM PARKS) as parks_loaded,
       (SELECT COUNT(*) FROM RIDES) as rides_loaded,
       (SELECT COUNT(*) FROM GUESTS) as guests_loaded,
       (SELECT COUNT(*) FROM TICKETS) as tickets_loaded,
       (SELECT COUNT(*) FROM RIDE_OPERATIONS) as operations_loaded,
       (SELECT COUNT(*) FROM WEATHER) as weather_records_loaded;

-- Display intentional data quality issues for reference
SELECT 'Intentional Data Quality Issues Summary:' as note,
       '5% missing emails in GUESTS' as issue_1,
       'Age/birth_date inconsistencies in GUESTS' as issue_2,
       'Invalid zip codes in GUESTS' as issue_3,
       'Negative amounts in TICKETS' as issue_4,
       'Impossible wait times in RIDE_OPERATIONS' as issue_5,
       'Capacity inconsistencies in RIDE_OPERATIONS' as issue_6,
       'Extreme weather values in WEATHER' as issue_7; 