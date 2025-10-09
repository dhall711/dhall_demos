-- =====================================================
-- UDX AI Hackathon: Unified Business Data Loader
-- =====================================================
-- This script loads comprehensive UDX theme park business data
-- supporting both NLP2SQL and Data Quality learning tracks

USE DATABASE UDX_AI_HACKATHON;
USE SCHEMA BUSINESS_ANALYTICS;
USE WAREHOUSE UDX_AI_WAREHOUSE;

-- =====================================================
-- 1. UNIVERSAL STUDIOS PARKS MASTER DATA
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
    timezone STRING,
    park_tier STRING               -- Premium, Standard, Regional
);

INSERT INTO PARKS VALUES
    ('UDX-FL', 'Universal Studios Florida', 'Southeast', 'Orlando', 'Florida, USA', '1990-06-07', 35000, 12000000, TRUE, 'EST', 'Premium'),
    ('UDX-IOA', 'Islands of Adventure', 'Southeast', 'Orlando', 'Florida, USA', '1999-05-28', 32000, 11000000, TRUE, 'EST', 'Premium'),
    ('UDX-CA', 'Universal Studios Hollywood', 'West Coast', 'Los Angeles', 'California, USA', '1964-07-15', 28000, 9500000, TRUE, 'PST', 'Premium'),
    ('UDX-JP', 'Universal Studios Japan', 'Asia Pacific', 'Osaka', 'Japan', '2001-03-31', 30000, 14500000, TRUE, 'JST', 'Premium'),
    ('UDX-SG', 'Universal Studios Singapore', 'Asia Pacific', 'Singapore', 'Singapore', '2010-03-18', 25000, 8000000, TRUE, 'SGT', 'Standard'),
    ('UDX-CN', 'Universal Beijing Resort', 'Asia Pacific', 'Beijing', 'China', '2021-09-20', 40000, 15000000, TRUE, 'CST', 'Premium');

-- =====================================================
-- 2. COMPREHENSIVE CUSTOMER DATA
-- =====================================================

CREATE OR REPLACE TABLE CUSTOMERS (
    customer_id STRING,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone STRING,
    birth_date DATE,
    age_group STRING,
    gender STRING,
    country STRING,
    region STRING,
    loyalty_tier STRING,
    loyalty_points INTEGER,
    total_lifetime_revenue DECIMAL(10,2),
    last_visit_date DATE,
    preferred_language STRING,
    marketing_opt_in BOOLEAN,
    customer_acquisition_channel STRING,
    registration_date DATE,
    is_vip BOOLEAN,
    data_quality_flag STRING      -- For Track B: CLEAN, SUSPECT, DUPLICATE, INCOMPLETE
);

-- Generate comprehensive customer analytics data (50,000 customers)
INSERT INTO CUSTOMERS
WITH customer_base AS (
    SELECT ROW_NUMBER() OVER (ORDER BY RANDOM()) as customer_num
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
        -- Email with intentional quality issues for Track B
        CASE 
            WHEN MOD(customer_num, 500) = 0 THEN NULL                              -- Missing emails (0.2%)
            WHEN MOD(customer_num, 750) = 0 THEN 'invalid-email'                   -- Invalid format (0.13%)
            ELSE LOWER(
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
                    WHEN 0 THEN 'gmail.com' WHEN 1 THEN 'yahoo.com' WHEN 2 THEN 'hotmail.com' 
                    WHEN 3 THEN 'outlook.com' WHEN 4 THEN 'icloud.com' ELSE 'email.com'
                END
            )
        END as email,
        -- Demographics with realistic distributions
        DATEADD('year', -FLOOR(18 + RANDOM() * 65), CURRENT_DATE()) as birth_date,
        CASE 
            WHEN DATEDIFF('year', DATEADD('year', -FLOOR(18 + RANDOM() * 65), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 18 AND 25 THEN '18-25'
            WHEN DATEDIFF('year', DATEADD('year', -FLOOR(18 + RANDOM() * 65), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 26 AND 35 THEN '26-35'
            WHEN DATEDIFF('year', DATEADD('year', -FLOOR(18 + RANDOM() * 65), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 36 AND 45 THEN '36-45'
            WHEN DATEDIFF('year', DATEADD('year', -FLOOR(18 + RANDOM() * 65), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 46 AND 55 THEN '46-55'
            WHEN DATEDIFF('year', DATEADD('year', -FLOOR(18 + RANDOM() * 65), CURRENT_DATE()), CURRENT_DATE()) BETWEEN 56 AND 65 THEN '56-65'
            ELSE '65+'
        END as age_group,
        CASE MOD(customer_num, 3) WHEN 0 THEN 'M' WHEN 1 THEN 'F' ELSE 'Other' END as gender,
        CASE MOD(customer_num, 10)
            WHEN 0 THEN 'USA' WHEN 1 THEN 'Canada' WHEN 2 THEN 'UK' WHEN 3 THEN 'Japan'
            WHEN 4 THEN 'Germany' WHEN 5 THEN 'France' WHEN 6 THEN 'Australia' 
            WHEN 7 THEN 'Singapore' WHEN 8 THEN 'China' ELSE 'Brazil'
        END as country,
        CASE MOD(customer_num, 6)
            WHEN 0 THEN 'North America' WHEN 1 THEN 'Europe' WHEN 2 THEN 'Asia Pacific'
            WHEN 3 THEN 'Latin America' WHEN 4 THEN 'North America' ELSE 'Asia Pacific'
        END as region,
        CASE MOD(customer_num, 4)
            WHEN 0 THEN 'Bronze' WHEN 1 THEN 'Silver' WHEN 2 THEN 'Gold' ELSE 'Platinum'
        END as loyalty_tier,
        FLOOR(RANDOM() * 10000) as loyalty_points,
        ROUND(50 + RANDOM() * 5000, 2) as total_lifetime_revenue,
        DATEADD('day', -FLOOR(RANDOM() * 365), CURRENT_DATE()) as last_visit_date,
        CASE MOD(customer_num, 5)
            WHEN 0 THEN 'English' WHEN 1 THEN 'Spanish' WHEN 2 THEN 'Japanese'
            WHEN 3 THEN 'Chinese' ELSE 'English'
        END as preferred_language,
        MOD(customer_num, 10) < 7 as marketing_opt_in,  -- 70% opt-in rate
        CASE MOD(customer_num, 6)
            WHEN 0 THEN 'Website' WHEN 1 THEN 'Social Media' WHEN 2 THEN 'Email'
            WHEN 3 THEN 'Partner' WHEN 4 THEN 'Referral' ELSE 'Advertising'
        END as customer_acquisition_channel,
        DATEADD('day', -FLOOR(RANDOM() * 1000), CURRENT_DATE()) as registration_date,
        MOD(customer_num, 20) = 0 as is_vip,  -- 5% VIP rate
        -- Data quality flags for Track B learning
        CASE 
            WHEN MOD(customer_num, 1000) = 0 THEN 'DUPLICATE'     -- 0.1% duplicates
            WHEN MOD(customer_num, 500) = 0 THEN 'INCOMPLETE'     -- 0.2% incomplete
            WHEN MOD(customer_num, 750) = 0 THEN 'SUSPECT'        -- 0.13% suspect data
            ELSE 'CLEAN'
        END as data_quality_flag
    FROM customer_base
)
SELECT 
    customer_id, first_name, last_name, email, 
    '+1-' || LPAD(FLOOR(RANDOM() * 9999999999), 10, '0') as phone,
    birth_date, age_group, gender, country, region,
    loyalty_tier, loyalty_points, total_lifetime_revenue,
    last_visit_date, preferred_language, marketing_opt_in,
    customer_acquisition_channel, registration_date, is_vip,
    data_quality_flag
FROM customer_analytics;

-- =====================================================
-- 3. COMPREHENSIVE SALES TRANSACTIONS
-- =====================================================

CREATE OR REPLACE TABLE SALES_TRANSACTIONS (
    transaction_id STRING,
    customer_id STRING,
    park_id STRING,
    transaction_date TIMESTAMP_NTZ,
    transaction_type STRING,
    product_category STRING,
    product_name STRING,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_revenue DECIMAL(10,2),
    discount_applied DECIMAL(10,2),
    payment_method STRING,
    staff_id STRING,
    transaction_source STRING,
    data_quality_score DECIMAL(3,2)    -- For Track B: 0.00-1.00 quality score
);

-- Generate 1M+ realistic transactions
INSERT INTO SALES_TRANSACTIONS
WITH transaction_base AS (
    SELECT ROW_NUMBER() OVER (ORDER BY RANDOM()) as txn_num
    FROM TABLE(GENERATOR(ROWCOUNT => 1000000))
),
park_customers AS (
    SELECT park_id FROM PARKS WHERE is_active = TRUE
),
active_customers AS (
    SELECT customer_id FROM CUSTOMERS TABLESAMPLE (70 ROWS)  -- Sample customers for transactions
)
SELECT 
    'TXN' || LPAD(txn_num, 10, '0') as transaction_id,
    (SELECT customer_id FROM active_customers ORDER BY RANDOM() LIMIT 1) as customer_id,
    (SELECT park_id FROM park_customers ORDER BY RANDOM() LIMIT 1) as park_id,
    DATEADD('minute', 
        FLOOR(RANDOM() * 525600),  -- Random minute in past year
        DATEADD('year', -1, CURRENT_TIMESTAMP())
    ) as transaction_date,
    CASE MOD(txn_num, 5)
        WHEN 0 THEN 'Ticket Purchase' WHEN 1 THEN 'Food & Beverage' 
        WHEN 2 THEN 'Merchandise' WHEN 3 THEN 'Photo Package' ELSE 'Express Pass'
    END as transaction_type,
    CASE MOD(txn_num, 7)
        WHEN 0 THEN 'Admission' WHEN 1 THEN 'Food' WHEN 2 THEN 'Beverage'
        WHEN 3 THEN 'Apparel' WHEN 4 THEN 'Souvenirs' WHEN 5 THEN 'Services' ELSE 'Experiences'
    END as product_category,
    CASE MOD(txn_num, 15)
        WHEN 0 THEN 'Single Day Ticket' WHEN 1 THEN 'Multi-Day Pass' WHEN 2 THEN 'Annual Pass'
        WHEN 3 THEN 'Butterbeer' WHEN 4 THEN 'Churros' WHEN 5 THEN 'Burger Meal'
        WHEN 6 THEN 'T-Shirt' WHEN 7 THEN 'Mug' WHEN 8 THEN 'Plush Toy'
        WHEN 9 THEN 'Express Pass' WHEN 10 THEN 'Photo Package' WHEN 11 THEN 'Parking'
        WHEN 12 THEN 'Locker Rental' WHEN 13 THEN 'Character Dining' ELSE 'Gift Card'
    END as product_name,
    CASE MOD(txn_num, 4) WHEN 0 THEN 1 WHEN 1 THEN 2 WHEN 2 THEN 1 ELSE 3 END as quantity,
    CASE MOD(txn_num, 15)
        WHEN 0 THEN 109.99 WHEN 1 THEN 289.99 WHEN 2 THEN 449.99  -- Tickets
        WHEN 3 THEN 15.99 WHEN 4 THEN 8.99 WHEN 5 THEN 19.99      -- Food
        WHEN 6 THEN 29.99 WHEN 7 THEN 24.99 WHEN 8 THEN 34.99     -- Merchandise
        WHEN 9 THEN 89.99 WHEN 10 THEN 39.99 WHEN 11 THEN 30.00   -- Services
        WHEN 12 THEN 12.00 WHEN 13 THEN 49.99 ELSE 25.00          -- Other
    END as unit_price,
    -- Total revenue with intentional calculation errors for Track B
    CASE 
        WHEN MOD(txn_num, 1000) = 0 THEN 0.00  -- Null revenue error (0.1%)
        WHEN MOD(txn_num, 2000) = 0 THEN -50.00  -- Negative revenue error (0.05%)
        ELSE (CASE MOD(txn_num, 4) WHEN 0 THEN 1 WHEN 1 THEN 2 WHEN 2 THEN 1 ELSE 3 END) * 
             (CASE MOD(txn_num, 15)
                WHEN 0 THEN 109.99 WHEN 1 THEN 289.99 WHEN 2 THEN 449.99  
                WHEN 3 THEN 15.99 WHEN 4 THEN 8.99 WHEN 5 THEN 19.99      
                WHEN 6 THEN 29.99 WHEN 7 THEN 24.99 WHEN 8 THEN 34.99     
                WHEN 9 THEN 89.99 WHEN 10 THEN 39.99 WHEN 11 THEN 30.00   
                WHEN 12 THEN 12.00 WHEN 13 THEN 49.99 ELSE 25.00          
             END)
    END as total_revenue,
    CASE WHEN MOD(txn_num, 10) = 0 THEN 5.00 ELSE 0.00 END as discount_applied,
    CASE MOD(txn_num, 4)
        WHEN 0 THEN 'Credit Card' WHEN 1 THEN 'Mobile Pay' 
        WHEN 2 THEN 'Cash' ELSE 'Gift Card'
    END as payment_method,
    'STAFF' || LPAD(MOD(txn_num, 500) + 1, 4, '0') as staff_id,
    CASE MOD(txn_num, 3)
        WHEN 0 THEN 'Point of Sale' WHEN 1 THEN 'Mobile App' ELSE 'Website'
    END as transaction_source,
    -- Data quality score for Track B
    CASE 
        WHEN MOD(txn_num, 1000) = 0 THEN 0.00   -- Severe quality issues
        WHEN MOD(txn_num, 500) = 0 THEN 0.65    -- Moderate quality issues
        WHEN MOD(txn_num, 100) = 0 THEN 0.85    -- Minor quality issues
        ELSE 0.95 + (RANDOM() * 0.05)           -- High quality
    END as data_quality_score
FROM transaction_base;

-- =====================================================
-- 4. PARK PERFORMANCE METRICS
-- =====================================================

CREATE OR REPLACE TABLE PARK_PERFORMANCE (
    performance_id STRING,
    park_id STRING,
    performance_date DATE,
    total_attendance INTEGER,
    capacity_utilization DECIMAL(5,4),
    guest_satisfaction_score DECIMAL(3,2),
    average_wait_time INTEGER,
    weather_condition STRING,
    temperature_f INTEGER,
    staff_count INTEGER,
    operational_incidents INTEGER,
    maintenance_issues INTEGER,
    data_completeness_score DECIMAL(3,2)   -- For Track B
);

-- Generate daily performance data for all parks
INSERT INTO PARK_PERFORMANCE
WITH date_range AS (
    SELECT DATEADD('day', ROW_NUMBER() OVER (ORDER BY 1) - 1, 
                   DATEADD('year', -2, CURRENT_DATE())) as perf_date
    FROM TABLE(GENERATOR(ROWCOUNT => 730))  -- 2 years of data
),
park_dates AS (
    SELECT p.park_id, d.perf_date
    FROM PARKS p
    CROSS JOIN date_range d
    WHERE p.is_active = TRUE
)
SELECT 
    park_id || '_' || TO_VARCHAR(perf_date, 'YYYYMMDD') as performance_id,
    park_id,
    perf_date as performance_date,
    FLOOR(1000 + RANDOM() * 25000) as total_attendance,
    0.45 + (RANDOM() * 0.50) as capacity_utilization,  -- 45-95% capacity
    6.5 + (RANDOM() * 3.5) as guest_satisfaction_score,  -- 6.5-10.0 satisfaction
    15 + FLOOR(RANDOM() * 45) as average_wait_time,     -- 15-60 minute waits
    CASE FLOOR(RANDOM() * 5)
        WHEN 0 THEN 'Sunny' WHEN 1 THEN 'Partly Cloudy' WHEN 2 THEN 'Cloudy'
        WHEN 3 THEN 'Rainy' ELSE 'Clear'
    END as weather_condition,
    45 + FLOOR(RANDOM() * 45) as temperature_f,         -- 45-90°F
    75 + FLOOR(RANDOM() * 50) as staff_count,           -- 75-125 staff
    FLOOR(RANDOM() * 5) as operational_incidents,       -- 0-4 incidents
    FLOOR(RANDOM() * 3) as maintenance_issues,          -- 0-2 issues
    -- Data completeness issues for Track B
    CASE 
        WHEN RANDOM() < 0.05 THEN 0.60     -- 5% incomplete days
        WHEN RANDOM() < 0.15 THEN 0.85     -- 10% partially complete
        ELSE 0.98 + (RANDOM() * 0.02)      -- 85% high completeness
    END as data_completeness_score
FROM park_dates;

-- =====================================================
-- 5. CREATE VIEWS FOR COMMON QUERIES
-- =====================================================

-- Executive summary view for Track A (NLP2SQL)
CREATE OR REPLACE VIEW EXECUTIVE_SUMMARY AS
SELECT 
    p.park_name,
    p.park_region,
    DATE_TRUNC('month', s.transaction_date) as month,
    SUM(s.total_revenue) as monthly_revenue,
    COUNT(DISTINCT s.customer_id) as unique_customers,
    COUNT(s.transaction_id) as total_transactions,
    AVG(pp.guest_satisfaction_score) as avg_satisfaction
FROM SALES_TRANSACTIONS s
JOIN PARKS p ON s.park_id = p.park_id
JOIN PARK_PERFORMANCE pp ON s.park_id = pp.park_id 
    AND DATE(s.transaction_date) = pp.performance_date
WHERE s.transaction_date >= DATEADD('year', -1, CURRENT_DATE())
GROUP BY p.park_name, p.park_region, DATE_TRUNC('month', s.transaction_date);

-- Data quality monitoring view for Track B
CREATE OR REPLACE VIEW DATA_QUALITY_DASHBOARD AS
SELECT 
    'CUSTOMERS' as table_name,
    COUNT(*) as total_records,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as null_emails,
    SUM(CASE WHEN data_quality_flag != 'CLEAN' THEN 1 ELSE 0 END) as quality_issues,
    ROUND(
        (COUNT(*) - SUM(CASE WHEN data_quality_flag != 'CLEAN' THEN 1 ELSE 0 END)) * 100.0 / COUNT(*), 
        2
    ) as quality_percentage
FROM CUSTOMERS

UNION ALL

SELECT 
    'SALES_TRANSACTIONS' as table_name,
    COUNT(*) as total_records,
    SUM(CASE WHEN total_revenue <= 0 THEN 1 ELSE 0 END) as invalid_revenue,
    SUM(CASE WHEN data_quality_score < 0.80 THEN 1 ELSE 0 END) as quality_issues,
    ROUND(AVG(data_quality_score) * 100, 2) as quality_percentage
FROM SALES_TRANSACTIONS;

-- =====================================================
-- 6. VALIDATION QUERIES
-- =====================================================

-- Verify data loading
SELECT 'Data Loading Complete!' as status;

SELECT 
    'PARKS' as table_name, 
    COUNT(*) as record_count 
FROM PARKS

UNION ALL

SELECT 
    'CUSTOMERS' as table_name, 
    COUNT(*) as record_count 
FROM CUSTOMERS

UNION ALL

SELECT 
    'SALES_TRANSACTIONS' as table_name, 
    COUNT(*) as record_count 
FROM SALES_TRANSACTIONS

UNION ALL

SELECT 
    'PARK_PERFORMANCE' as table_name, 
    COUNT(*) as record_count 
FROM PARK_PERFORMANCE;

-- Sample data quality issues for Track B
SELECT 
    'Data Quality Issues for Track B Learning:' as summary,
    COUNT(CASE WHEN c.data_quality_flag != 'CLEAN' THEN 1 END) as customer_issues,
    COUNT(CASE WHEN s.data_quality_score < 0.80 THEN 1 END) as transaction_issues,
    COUNT(CASE WHEN pp.data_completeness_score < 0.90 THEN 1 END) as performance_issues
FROM CUSTOMERS c
CROSS JOIN SALES_TRANSACTIONS s
CROSS JOIN PARK_PERFORMANCE pp
LIMIT 1;

-- =====================================================
-- 7. COMPLETION MESSAGE
-- =====================================================

SELECT 
    '🎢 UDX AI Hackathon Data Loading Complete! 🎢' as message,
    'Ready for both Track A (NLP2SQL) and Track B (Data Quality)' as status,
    'Choose your track and begin the labs!' as next_step; 