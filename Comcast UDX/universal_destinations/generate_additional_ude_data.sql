-- =====================================================================
-- Universal Destinations & Experiences - Additional Synthetic Data
-- =====================================================================
-- This script generates additional synthetic data to create a more
-- robust dataset for testing and demonstration purposes
-- =====================================================================

USE DATABASE UNIVERSAL_DATA_PLATFORM;

-- =====================================================================
-- GENERATE ADDITIONAL GUEST PROFILES (100 more guests)
-- =====================================================================

INSERT INTO GUEST_ANALYTICS.GUEST_PROFILES 
SELECT 
    'G' || LPAD(ROW_NUMBER() OVER (ORDER BY SEQ8()) + 10, 3, '0') as GUEST_ID,
    CASE (UNIFORM(1, 20, RANDOM()) % 20)
        WHEN 1 THEN 'Emma' WHEN 2 THEN 'Liam' WHEN 3 THEN 'Olivia' WHEN 4 THEN 'Noah'
        WHEN 5 THEN 'Ava' WHEN 6 THEN 'Oliver' WHEN 7 THEN 'Charlotte' WHEN 8 THEN 'Elijah'
        WHEN 9 THEN 'Amelia' WHEN 10 THEN 'William' WHEN 11 THEN 'Sophia' WHEN 12 THEN 'James'
        WHEN 13 THEN 'Isabella' WHEN 14 THEN 'Benjamin' WHEN 15 THEN 'Mia' WHEN 16 THEN 'Lucas'
        WHEN 17 THEN 'Harper' WHEN 18 THEN 'Henry' WHEN 19 THEN 'Evelyn' ELSE 'Alexander'
    END as FIRST_NAME,
    CASE (UNIFORM(1, 15, RANDOM()) % 15)
        WHEN 1 THEN 'Smith' WHEN 2 THEN 'Johnson' WHEN 3 THEN 'Williams' WHEN 4 THEN 'Brown'
        WHEN 5 THEN 'Jones' WHEN 6 THEN 'Garcia' WHEN 7 THEN 'Miller' WHEN 8 THEN 'Davis'
        WHEN 9 THEN 'Rodriguez' WHEN 10 THEN 'Martinez' WHEN 11 THEN 'Hernandez' 
        WHEN 12 THEN 'Lopez' WHEN 13 THEN 'Gonzalez' WHEN 14 THEN 'Wilson' ELSE 'Anderson'
    END as LAST_NAME,
    LOWER(FIRST_NAME || '.' || LAST_NAME || '@email.com') as EMAIL_ADDRESS,
    '555-' || LPAD(UNIFORM(1000, 9999, RANDOM()), 4, '0') as PHONE_NUMBER,
    DATEADD(year, -UNIFORM(18, 65, RANDOM()), CURRENT_DATE()) as DATE_OF_BIRTH,
    CASE (UNIFORM(1, 10, RANDOM()) % 10)
        WHEN 1 THEN '90210' WHEN 2 THEN '10001' WHEN 3 THEN '33101' WHEN 4 THEN '60601'
        WHEN 5 THEN '30301' WHEN 6 THEN '77001' WHEN 7 THEN '85001' WHEN 8 THEN '98101'
        WHEN 9 THEN '20001' ELSE '97201'
    END as ZIP_CODE,
    CASE (UNIFORM(1, 10, RANDOM()) % 10)
        WHEN 1 THEN 'California' WHEN 2 THEN 'New York' WHEN 3 THEN 'Florida' 
        WHEN 4 THEN 'Illinois' WHEN 5 THEN 'Georgia' WHEN 6 THEN 'Texas'
        WHEN 7 THEN 'Arizona' WHEN 8 THEN 'Washington' WHEN 9 THEN 'DC' ELSE 'Oregon'
    END as STATE,
    CASE (UNIFORM(1, 8, RANDOM()) % 8)
        WHEN 1 THEN 'USA' WHEN 2 THEN 'Canada' WHEN 3 THEN 'UK' WHEN 4 THEN 'Japan'
        WHEN 5 THEN 'China' WHEN 6 THEN 'Australia' WHEN 7 THEN 'Germany' ELSE 'France'
    END as COUNTRY,
    CASE (UNIFORM(1, 6, RANDOM()) % 6)
        WHEN 1 THEN 'English' WHEN 2 THEN 'Spanish' WHEN 3 THEN 'French'
        WHEN 4 THEN 'Japanese' WHEN 5 THEN 'Mandarin' ELSE 'German'
    END as PREFERRED_LANGUAGE,
    CASE (UNIFORM(1, 3, RANDOM()) % 3)
        WHEN 1 THEN 'Standard' WHEN 2 THEN 'Premier' ELSE 'Preferred'
    END as MEMBERSHIP_TIER,
    UNIFORM(1, 8, RANDOM()) as FAMILY_SIZE,
    CASE (UNIFORM(1, 5, RANDOM()) % 5)
        WHEN 1 THEN 'Universal Studios Hollywood' WHEN 2 THEN 'Universal Orlando Resort'
        WHEN 3 THEN 'Universal Studios Japan' WHEN 4 THEN 'Universal Beijing Resort'
        ELSE 'Universal Studios Singapore'
    END as PREFERRED_PARK,
    DATEADD(day, -UNIFORM(30, 1500, RANDOM()), CURRENT_TIMESTAMP()) as ACCOUNT_CREATED_DATE,
    DATEADD(day, -UNIFORM(1, 90, RANDOM()), CURRENT_TIMESTAMP()) as LAST_VISIT_DATE,
    UNIFORM(500, 5000, RANDOM()) + (UNIFORM(1, 99, RANDOM()) / 100.0) as TOTAL_SPEND_AMOUNT,
    CASE MEMBERSHIP_TIER 
        WHEN 'Standard' THEN 299.99 
        WHEN 'Premier' THEN 599.99 
        ELSE 899.99 
    END as MEMBERSHIP_VALUE,
    UNIFORM(70, 99, RANDOM()) / 10.0 as CURRENT_PERFORMANCE_RATING
FROM TABLE(GENERATOR(ROWCOUNT => 100));

-- =====================================================================
-- GENERATE ADDITIONAL VISIT SESSIONS
-- =====================================================================

INSERT INTO GUEST_ANALYTICS.VISIT_SESSIONS
SELECT 
    'V' || LPAD(ROW_NUMBER() OVER (ORDER BY g.GUEST_ID, SEQ8()) + 10, 4, '0') as VISIT_ID,
    g.GUEST_ID,
    g.PREFERRED_PARK as PARK_LOCATION,
    DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) as VISIT_DATE,
    TIMESTAMP_FROM_PARTS(
        VISIT_DATE, 
        TIME_FROM_PARTS(UNIFORM(8, 11, RANDOM()), UNIFORM(0, 59, RANDOM()), 0)
    ) as ENTRY_TIME,
    TIMESTAMP_FROM_PARTS(
        VISIT_DATE, 
        TIME_FROM_PARTS(UNIFORM(18, 23, RANDOM()), UNIFORM(0, 59, RANDOM()), 0)
    ) as EXIT_TIME,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Single Day' WHEN 2 THEN 'Multi-Day' 
        WHEN 3 THEN 'Annual Pass' ELSE 'Special Event'
    END as TICKET_TYPE,
    CASE (UNIFORM(1, 5, RANDOM()) % 5)
        WHEN 1 THEN 'Sunny' WHEN 2 THEN 'Partly Cloudy' WHEN 3 THEN 'Cloudy'
        WHEN 4 THEN 'Rainy' ELSE 'Clear'
    END as WEATHER_CONDITIONS,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' WHEN 3 THEN 'High' ELSE 'Peak'
    END as CROWD_LEVEL,
    UNIFORM(50, 500, RANDOM()) + (UNIFORM(1, 99, RANDOM()) / 100.0) as SPEND_AMOUNT,
    'A' || LPAD(UNIFORM(1, 20, RANDOM()), 3, '0') as ATTRACTION_ID
FROM (
    SELECT GUEST_ID, PREFERRED_PARK 
    FROM GUEST_ANALYTICS.GUEST_PROFILES 
    WHERE GUEST_ID LIKE 'G0%'
) g
CROSS JOIN TABLE(GENERATOR(ROWCOUNT => 3)) -- 3 visits per guest on average
WHERE UNIFORM(1, 100, RANDOM()) <= 75; -- 75% chance of generating a visit

-- =====================================================================
-- GENERATE ADDITIONAL ATTRACTIONS
-- =====================================================================

INSERT INTO PARK_OPERATIONS.ATTRACTIONS VALUES
('A011', 'The Simpsons Ride', 'Universal Studios Hollywood', 'Springfield', 'Family Ride', 'The Simpsons', 40, 2000, 6, 'Wheelchair accessible', 'Open', '2008-05-19', '2024-01-15', 14500, 30, 1850, 8.3),
('A012', 'Despicable Me Minion Mayhem', 'Universal Orlando Resort', 'Production Central', 'Family Ride', 'Illumination', 40, 2200, 5, 'Wheelchair accessible', 'Open', '2012-07-02', '2024-03-20', 16000, 35, 2050, 8.6),
('A013', 'Fast & Furious - Supercharged', 'Universal Studios Hollywood', 'Fast & Furious', 'Thrill Ride', 'Fast & Furious', 40, 1800, 4, 'Wheelchair accessible with transfer', 'Open', '2018-06-25', '2024-02-10', 12500, 25, 1700, 7.8),
('A014', 'E.T. Adventure', 'Universal Orlando Resort', 'Woody Woodpecker KidZone', 'Family Ride', 'Universal Studios', 34, 1600, 4, 'Wheelchair accessible', 'Open', '1990-06-07', '2024-04-08', 11000, 20, 1500, 8.1),
('A015', 'Jaws', 'Universal Studios Japan', 'Amity Village', 'Water Ride', 'Universal Studios', 36, 1500, 7, 'Wheelchair accessible with transfer', 'Open', '2001-03-31', '2024-01-25', 13000, 40, 1350, 8.4),
('A016', 'Men in Black Alien Attack', 'Universal Orlando Resort', 'World Expo', 'Interactive Ride', 'Men in Black', 42, 1800, 4, 'Wheelchair accessible', 'Open', '2000-08-15', '2024-05-18', 15500, 30, 1650, 8.7),
('A017', 'Revenge of the Mummy', 'Universal Studios Hollywood', 'Upper Lot', 'Thrill Ride', 'Universal Studios', 48, 1400, 3, 'Wheelchair accessible with transfer', 'Open', '2004-06-25', '2024-03-12', 12000, 55, 1250, 8.9),
('A018', 'KONG: Skull Island', 'Universal Orlando Resort', 'Skull Island', 'Thrill Ride', 'King Kong', 36, 1900, 6, 'Wheelchair accessible', 'Open', '2016-07-13', '2024-06-05', 14000, 45, 1750, 8.8),
('A019', 'Minion Park', 'Universal Studios Japan', 'Minion Park', 'Family Experience', 'Illumination', 0, 3000, 15, 'Fully wheelchair accessible', 'Open', '2017-04-21', '2024-04-30', 20000, 10, 2800, 9.0),
('A020', 'VelociCoaster', 'Universal Orlando Resort', 'Jurassic Park', 'Thrill Ride', 'Jurassic Park', 51, 1440, 2, 'Wheelchair accessible with transfer', 'Open', '2021-06-10', '2024-07-01', 17000, 75, 1300, 9.7);

-- =====================================================================
-- GENERATE ADDITIONAL WAIT TIMES DATA
-- =====================================================================

INSERT INTO PARK_OPERATIONS.WAIT_TIMES
SELECT 
    'WT' || LPAD(ROW_NUMBER() OVER (ORDER BY a.ATTRACTION_ID, dt.date_hour) + 10, 5, '0') as WAIT_TIME_ID,
    a.ATTRACTION_ID,
    dt.date_hour as RECORDED_TIMESTAMP,
    CASE 
        WHEN EXTRACT(HOUR FROM dt.date_hour) BETWEEN 11 AND 16 THEN UNIFORM(30, 90, RANDOM())
        WHEN EXTRACT(HOUR FROM dt.date_hour) BETWEEN 17 AND 21 THEN UNIFORM(45, 120, RANDOM())
        ELSE UNIFORM(10, 45, RANDOM())
    END as WAIT_TIME_MINUTES,
    WAIT_TIME_MINUTES + UNIFORM(-10, 15, RANDOM()) as POSTED_WAIT_TIME_MINUTES,
    CASE (UNIFORM(1, 5, RANDOM()) % 5)
        WHEN 1 THEN 'Sunny' WHEN 2 THEN 'Partly Cloudy' WHEN 3 THEN 'Cloudy'
        WHEN 4 THEN 'Rainy' ELSE 'Clear'
    END as WEATHER_CONDITION,
    CASE WHEN UNIFORM(1, 10, RANDOM()) = 1 THEN 'Halloween Horror Nights' ELSE NULL END as SPECIAL_EVENT,
    CASE 
        WHEN WAIT_TIME_MINUTES <= 30 THEN 'Low'
        WHEN WAIT_TIME_MINUTES <= 60 THEN 'Medium'
        WHEN WAIT_TIME_MINUTES <= 90 THEN 'High'
        ELSE 'Peak'
    END as CROWD_LEVEL
FROM PARK_OPERATIONS.ATTRACTIONS a
CROSS JOIN (
    SELECT DATEADD(hour, ROW_NUMBER() OVER (ORDER BY SEQ8()), 
                   DATEADD(day, -7, CURRENT_TIMESTAMP())) as date_hour
    FROM TABLE(GENERATOR(ROWCOUNT => 168)) -- 7 days * 24 hours
) dt
WHERE a.ATTRACTION_ID IN (SELECT ATTRACTION_ID FROM PARK_OPERATIONS.ATTRACTIONS LIMIT 20);

-- =====================================================================
-- GENERATE ADDITIONAL TICKET SALES
-- =====================================================================

INSERT INTO REVENUE_ANALYTICS.TICKET_SALES
SELECT 
    'TS' || LPAD(ROW_NUMBER() OVER (ORDER BY g.GUEST_ID, SEQ8()) + 10, 5, '0') as TICKET_SALE_ID,
    g.GUEST_ID,
    g.PREFERRED_PARK as PARK_LOCATION,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Single Day' WHEN 2 THEN 'Multi-Day' 
        WHEN 3 THEN 'Annual Pass' ELSE 'Special Event'
    END as TICKET_TYPE,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Adult' WHEN 2 THEN 'Child' WHEN 3 THEN 'Senior' ELSE 'Military'
    END as TICKET_CATEGORY,
    CASE (UNIFORM(1, 5, RANDOM()) % 5)
        WHEN 1 THEN 'Online' WHEN 2 THEN 'Mobile App' WHEN 3 THEN 'Gate'
        WHEN 4 THEN 'Hotel' ELSE 'Partner'
    END as PURCHASE_CHANNEL,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Value' WHEN 2 THEN 'Regular' WHEN 3 THEN 'Peak' ELSE 'Premium'
    END as PRICING_TIER,
    CASE WHEN UNIFORM(1, 5, RANDOM()) = 1 THEN 'SAVE' || UNIFORM(10, 25, RANDOM()) ELSE NULL END as PROMOTIONAL_CODE,
    CASE WHEN UNIFORM(1, 4, RANDOM()) = 1 THEN 'Express Pass' ELSE NULL END as BUNDLE_PACKAGE,
    CASE (UNIFORM(1, 3, RANDOM()) % 3)
        WHEN 1 THEN 'Local' WHEN 2 THEN 'Domestic Tourist' ELSE 'International'
    END as GUEST_SEGMENT,
    DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_TIMESTAMP()) as PURCHASE_TIMESTAMP,
    DATEADD(day, UNIFORM(0, 60, RANDOM()), PURCHASE_TIMESTAMP::DATE) as VISIT_DATE,
    CASE TICKET_TYPE
        WHEN 'Single Day' THEN UNIFORM(109, 149, RANDOM()) + 0.99
        WHEN 'Multi-Day' THEN UNIFORM(199, 299, RANDOM()) + 0.99
        WHEN 'Annual Pass' THEN UNIFORM(599, 899, RANDOM()) + 0.99
        ELSE UNIFORM(179, 229, RANDOM()) + 0.99
    END as TICKET_PRICE,
    CASE WHEN PROMOTIONAL_CODE IS NOT NULL THEN TICKET_PRICE * (UNIFORM(10, 25, RANDOM()) / 100.0) ELSE 0 END as DISCOUNT_AMOUNT
FROM GUEST_ANALYTICS.GUEST_PROFILES g
CROSS JOIN TABLE(GENERATOR(ROWCOUNT => 2)) -- 2 ticket purchases per guest on average
WHERE g.GUEST_ID LIKE 'G0%' AND UNIFORM(1, 100, RANDOM()) <= 80; -- 80% chance

-- =====================================================================
-- GENERATE ADDITIONAL MERCHANDISE SALES
-- =====================================================================

INSERT INTO REVENUE_ANALYTICS.MERCHANDISE_SALES
SELECT 
    'MS' || LPAD(ROW_NUMBER() OVER (ORDER BY g.GUEST_ID, SEQ8()) + 10, 5, '0') as MERCHANDISE_SALE_ID,
    g.GUEST_ID,
    'SL' || LPAD(UNIFORM(1, 20, RANDOM()), 3, '0') as STORE_LOCATION_ID,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Themed Store' WHEN 2 THEN 'Cart' 
        WHEN 3 THEN 'Universal CityWalk' ELSE 'Kiosk'
    END as STORE_TYPE,
    CASE (UNIFORM(1, 5, RANDOM()) % 5)
        WHEN 1 THEN 'Apparel' WHEN 2 THEN 'Collectibles' WHEN 3 THEN 'Toys'
        WHEN 4 THEN 'Accessories' ELSE 'Souvenirs'
    END as PRODUCT_CATEGORY,
    CASE (UNIFORM(1, 8, RANDOM()) % 8)
        WHEN 1 THEN 'Harry Potter' WHEN 2 THEN 'Nintendo' WHEN 3 THEN 'Jurassic Park'
        WHEN 4 THEN 'Marvel' WHEN 5 THEN 'Transformers' WHEN 6 THEN 'Universal Studios'
        WHEN 7 THEN 'Illumination' ELSE 'Universal Monsters'
    END as FRANCHISE,
    FRANCHISE || ' ' || PRODUCT_CATEGORY || ' Item' as PRODUCT_NAME,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Budget' WHEN 2 THEN 'Mid-Range' WHEN 3 THEN 'Premium' ELSE 'Luxury'
    END as PRICE_TIER,
    UNIFORM(1, 10, RANDOM()) = 1 as IS_SEASONAL_ITEM,
    UNIFORM(1, 8, RANDOM()) = 1 as HAS_PERSONALIZATION,
    DATEADD(minute, UNIFORM(60, 720, RANDOM()), 
            DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_TIMESTAMP())) as PURCHASE_TIMESTAMP,
    CASE PRICE_TIER
        WHEN 'Budget' THEN UNIFORM(15, 35, RANDOM()) + 0.99
        WHEN 'Mid-Range' THEN UNIFORM(35, 75, RANDOM()) + 0.99
        WHEN 'Premium' THEN UNIFORM(75, 150, RANDOM()) + 0.99
        ELSE UNIFORM(150, 300, RANDOM()) + 0.99
    END as UNIT_PRICE,
    UNIFORM(1, 3, RANDOM()) as QUANTITY,
    UNIT_PRICE * UNIFORM(25, 45, RANDOM()) / 100.0 as COST_OF_GOODS
FROM GUEST_ANALYTICS.GUEST_PROFILES g
CROSS JOIN TABLE(GENERATOR(ROWCOUNT => 3)) -- 3 merchandise purchases per guest
WHERE g.GUEST_ID LIKE 'G0%' AND UNIFORM(1, 100, RANDOM()) <= 70; -- 70% chance

-- =====================================================================
-- GENERATE ADDITIONAL EMPLOYEE DATA
-- =====================================================================

INSERT INTO STAFF_MANAGEMENT.EMPLOYEE_PROFILES
SELECT 
    'E' || LPAD(ROW_NUMBER() OVER (ORDER BY SEQ8()) + 10, 3, '0') as EMPLOYEE_ID,
    CASE (UNIFORM(1, 20, RANDOM()) % 20)
        WHEN 1 THEN 'Alex' WHEN 2 THEN 'Jordan' WHEN 3 THEN 'Taylor' WHEN 4 THEN 'Casey'
        WHEN 5 THEN 'Morgan' WHEN 6 THEN 'Riley' WHEN 7 THEN 'Avery' WHEN 8 THEN 'Quinn'
        WHEN 9 THEN 'Sage' WHEN 10 THEN 'River' WHEN 11 THEN 'Dakota' WHEN 12 THEN 'Phoenix'
        WHEN 13 THEN 'Skyler' WHEN 14 THEN 'Cameron' WHEN 15 THEN 'Rowan' WHEN 16 THEN 'Peyton'
        WHEN 17 THEN 'Reese' WHEN 18 THEN 'Blake' WHEN 19 THEN 'Drew' ELSE 'Parker'
    END as FIRST_NAME,
    CASE (UNIFORM(1, 15, RANDOM()) % 15)
        WHEN 1 THEN 'Anderson' WHEN 2 THEN 'Thompson' WHEN 3 THEN 'Garcia' WHEN 4 THEN 'Martinez'
        WHEN 5 THEN 'Robinson' WHEN 6 THEN 'Clark' WHEN 7 THEN 'Rodriguez' WHEN 8 THEN 'Lewis'
        WHEN 9 THEN 'Lee' WHEN 10 THEN 'Walker' WHEN 11 THEN 'Hall' WHEN 12 THEN 'Allen'
        WHEN 13 THEN 'Young' WHEN 14 THEN 'King' ELSE 'Wright'
    END as LAST_NAME,
    LOWER(FIRST_NAME || '.' || LAST_NAME || '@universalparks.com') as EMPLOYEE_EMAIL,
    '555-' || LPAD(UNIFORM(1000, 9999, RANDOM()), 4, '0') as PHONE_NUMBER,
    CASE (UNIFORM(1, 5, RANDOM()) % 5)
        WHEN 1 THEN 'Universal Studios Hollywood' WHEN 2 THEN 'Universal Orlando Resort'
        WHEN 3 THEN 'Universal Studios Japan' WHEN 4 THEN 'Universal Beijing Resort'
        ELSE 'Universal Studios Singapore'
    END as PARK_LOCATION,
    CASE (UNIFORM(1, 6, RANDOM()) % 6)
        WHEN 1 THEN 'Operations' WHEN 2 THEN 'Food Service' WHEN 3 THEN 'Merchandise'
        WHEN 4 THEN 'Entertainment' WHEN 5 THEN 'Maintenance' ELSE 'Guest Services'
    END as DEPARTMENT,
    CASE DEPARTMENT
        WHEN 'Operations' THEN 'Ride Operator'
        WHEN 'Food Service' THEN 'Server'
        WHEN 'Merchandise' THEN 'Sales Associate'
        WHEN 'Entertainment' THEN 'Performer'
        WHEN 'Maintenance' THEN 'Technician'
        ELSE 'Guest Relations'
    END as JOB_TITLE,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Full-Time' WHEN 2 THEN 'Part-Time' WHEN 3 THEN 'Seasonal' ELSE 'Intern'
    END as EMPLOYMENT_TYPE,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Opening' WHEN 2 THEN 'Mid-Day' WHEN 3 THEN 'Closing' ELSE 'Overnight'
    END as SHIFT_PREFERENCE,
    CASE (UNIFORM(1, 4, RANDOM()) % 4)
        WHEN 1 THEN 'Entry' WHEN 2 THEN 'Intermediate' WHEN 3 THEN 'Advanced' ELSE 'Trainer'
    END as CERTIFICATION_LEVEL,
    'English' as LANGUAGE_SKILLS,
    FIRST_NAME || ' Emergency Contact' as EMERGENCY_CONTACT_NAME,
    '555-' || LPAD(UNIFORM(1000, 9999, RANDOM()), 4, '0') as EMERGENCY_CONTACT_PHONE,
    DATEADD(day, -UNIFORM(365, 2555, RANDOM()), CURRENT_DATE()) as HIRE_DATE,
    CASE WHEN UNIFORM(1, 3, RANDOM()) = 1 THEN DATEADD(year, UNIFORM(1, 3, RANDOM()), HIRE_DATE) ELSE NULL END as LAST_PROMOTION_DATE,
    CASE EMPLOYMENT_TYPE
        WHEN 'Full-Time' THEN UNIFORM(18, 35, RANDOM()) + (UNIFORM(0, 99, RANDOM()) / 100.0)
        WHEN 'Part-Time' THEN UNIFORM(15, 25, RANDOM()) + (UNIFORM(0, 99, RANDOM()) / 100.0)
        WHEN 'Seasonal' THEN UNIFORM(16, 22, RANDOM()) + (UNIFORM(0, 99, RANDOM()) / 100.0)
        ELSE UNIFORM(12, 18, RANDOM()) + (UNIFORM(0, 99, RANDOM()) / 100.0)
    END as HOURLY_WAGE,
    NULL as ANNUAL_SALARY,
    UNIFORM(60, 99, RANDOM()) / 10.0 as CURRENT_PERFORMANCE_RATING
FROM TABLE(GENERATOR(ROWCOUNT => 50));

-- =====================================================================
-- CREATE SUMMARY STATISTICS VIEW
-- =====================================================================

CREATE OR REPLACE VIEW UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.DATA_SUMMARY AS
SELECT 
    'Total Guests' as metric,
    COUNT(DISTINCT GUEST_ID) as value,
    'guests' as unit
FROM GUEST_ANALYTICS.GUEST_PROFILES
UNION ALL
SELECT 
    'Total Visits' as metric,
    COUNT(DISTINCT VISIT_ID) as value,
    'visits' as unit
FROM GUEST_ANALYTICS.VISIT_SESSIONS
UNION ALL
SELECT 
    'Total Attractions' as metric,
    COUNT(DISTINCT ATTRACTION_ID) as value,
    'attractions' as unit
FROM PARK_OPERATIONS.ATTRACTIONS
UNION ALL
SELECT 
    'Total Employees' as metric,
    COUNT(DISTINCT EMPLOYEE_ID) as value,
    'employees' as unit
FROM STAFF_MANAGEMENT.EMPLOYEE_PROFILES
UNION ALL
SELECT 
    'Total Ticket Sales' as metric,
    COUNT(DISTINCT TICKET_SALE_ID) as value,
    'transactions' as unit
FROM REVENUE_ANALYTICS.TICKET_SALES
UNION ALL
SELECT 
    'Total Revenue' as metric,
    ROUND(SUM(TICKET_PRICE - DISCOUNT_AMOUNT), 2) as value,
    'USD' as unit
FROM REVENUE_ANALYTICS.TICKET_SALES;

-- =====================================================================
-- FINAL DATA VALIDATION
-- =====================================================================

SELECT 'Extended UDE synthetic data generation completed!' as status,
       CURRENT_TIMESTAMP() as completion_time;

-- Display summary of all data
SELECT * FROM UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS.DATA_SUMMARY
ORDER BY metric;