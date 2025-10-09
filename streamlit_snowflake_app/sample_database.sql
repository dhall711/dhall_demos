-- ========================================
-- ENHANCED STREAMLIT SAMPLE DATABASE SETUP SCRIPT WITH CORTEX AI SUPPORT
-- ========================================
-- This script creates a comprehensive sample database with realistic test data
-- Perfect for demonstrating Streamlit capabilities with Snowflake Cortex AI

-- Create Database and Schema
CREATE DATABASE IF NOT EXISTS STREAMLIT_DEMO;
USE DATABASE STREAMLIT_DEMO;

CREATE SCHEMA IF NOT EXISTS SAMPLE_DATA;
USE SCHEMA SAMPLE_DATA;

-- ========================================
-- 1. SALES DATA TABLE (Enhanced)
-- ========================================
CREATE OR REPLACE TABLE SALES_DATA (
    SALE_ID INTEGER AUTOINCREMENT,
    SALE_DATE DATE,
    CUSTOMER_ID INTEGER,
    PRODUCT_ID VARCHAR(10),
    PRODUCT_NAME VARCHAR(100),
    CATEGORY VARCHAR(50),
    REGION VARCHAR(20),
    SALES_REP VARCHAR(50),
    QUANTITY INTEGER,
    UNIT_PRICE DECIMAL(10,2),
    TOTAL_AMOUNT DECIMAL(12,2),
    PROFIT_MARGIN DECIMAL(5,2),
    PROFIT_AMOUNT DECIMAL(10,2),
    CHANNEL VARCHAR(30),
    PAYMENT_METHOD VARCHAR(20),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample sales data (step by step approach)
INSERT INTO SALES_DATA (
    SALE_DATE, 
    CUSTOMER_ID, 
    PRODUCT_ID, 
    PRODUCT_NAME, 
    CATEGORY, 
    REGION, 
    SALES_REP, 
    QUANTITY, 
    UNIT_PRICE, 
    TOTAL_AMOUNT, 
    PROFIT_MARGIN, 
    PROFIT_AMOUNT, 
    CHANNEL, 
    PAYMENT_METHOD
)
SELECT 
    DATEADD(day, row_number() OVER (ORDER BY seq4()) - 1, '2024-01-01') as SALE_DATE,
    UNIFORM(1000, 9999, RANDOM()) as CUSTOMER_ID,
    CASE UNIFORM(1, 10, RANDOM()) % 10 + 1
        WHEN 1 THEN 'PROD-001'
        WHEN 2 THEN 'PROD-002'
        WHEN 3 THEN 'PROD-003'
        WHEN 4 THEN 'PROD-004'
        WHEN 5 THEN 'PROD-005'
        WHEN 6 THEN 'PROD-006'
        WHEN 7 THEN 'PROD-007'
        WHEN 8 THEN 'PROD-008'
        WHEN 9 THEN 'PROD-009'
        ELSE 'PROD-010'
    END as PRODUCT_ID,
    CASE UNIFORM(1, 10, RANDOM()) % 10 + 1
        WHEN 1 THEN 'Laptop Pro 15'
        WHEN 2 THEN 'Wireless Mouse'
        WHEN 3 THEN 'Mechanical Keyboard'
        WHEN 4 THEN 'USB-C Hub'
        WHEN 5 THEN 'Webcam HD'
        WHEN 6 THEN 'Monitor 27 inch'
        WHEN 7 THEN 'Tablet 10 inch'
        WHEN 8 THEN 'Smartphone'
        WHEN 9 THEN 'Headphones'
        ELSE 'Smartwatch'
    END as PRODUCT_NAME,
    CASE UNIFORM(1, 4, RANDOM()) % 4 + 1
        WHEN 1 THEN 'Electronics'
        WHEN 2 THEN 'Accessories'
        WHEN 3 THEN 'Computing'
        ELSE 'Mobile'
    END as CATEGORY,
    CASE UNIFORM(1, 4, RANDOM()) % 4 + 1
        WHEN 1 THEN 'North'
        WHEN 2 THEN 'South'
        WHEN 3 THEN 'East'
        ELSE 'West'
    END as REGION,
    CASE UNIFORM(1, 8, RANDOM()) % 8 + 1
        WHEN 1 THEN 'Alice Johnson'
        WHEN 2 THEN 'Bob Smith'
        WHEN 3 THEN 'Carol Davis'
        WHEN 4 THEN 'David Wilson'
        WHEN 5 THEN 'Eva Brown'
        WHEN 6 THEN 'Frank Miller'
        WHEN 7 THEN 'Grace Lee'
        ELSE 'Henry Taylor'
    END as SALES_REP,
    UNIFORM(1, 10, RANDOM()) as QUANTITY,
    ROUND(UNIFORM(50, 1500, RANDOM()), 2) as UNIT_PRICE,
    0 as TOTAL_AMOUNT, -- Will be calculated in update
    ROUND(UNIFORM(15, 35, RANDOM()), 2) as PROFIT_MARGIN,
    0 as PROFIT_AMOUNT, -- Will be calculated in update
    CASE UNIFORM(1, 4, RANDOM()) % 4 + 1
        WHEN 1 THEN 'Online Store'
        WHEN 2 THEN 'Retail Store'
        WHEN 3 THEN 'Partner Channel'
        ELSE 'Direct Sales'
    END as CHANNEL,
    CASE UNIFORM(1, 5, RANDOM()) % 5 + 1
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'PayPal'
        WHEN 3 THEN 'Bank Transfer'
        WHEN 4 THEN 'Apple Pay'
        ELSE 'Google Pay'
    END as PAYMENT_METHOD
FROM table(generator(rowcount => 2500));

-- Update calculated amounts based on quantity and unit price
UPDATE SALES_DATA SET 
    TOTAL_AMOUNT = QUANTITY * UNIT_PRICE,
    PROFIT_AMOUNT = ROUND(QUANTITY * UNIT_PRICE * (PROFIT_MARGIN / 100), 2);

-- ========================================
-- 2. CUSTOMER DATA TABLE (Enhanced)
-- ========================================
CREATE OR REPLACE TABLE CUSTOMERS (
    CUSTOMER_ID INTEGER PRIMARY KEY,
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    EMAIL VARCHAR(100),
    PHONE VARCHAR(20),
    REGISTRATION_DATE DATE,
    CUSTOMER_SEGMENT VARCHAR(20),
    LIFETIME_VALUE DECIMAL(10,2),
    PREFERRED_REGION VARCHAR(20),
    AGE_GROUP VARCHAR(20),
    COMMUNICATION_PREFERENCE VARCHAR(30),
    PURCHASE_FREQUENCY VARCHAR(20),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert enhanced customer data
INSERT INTO CUSTOMERS (
    CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, PHONE, REGISTRATION_DATE, 
    CUSTOMER_SEGMENT, LIFETIME_VALUE, PREFERRED_REGION, AGE_GROUP, 
    COMMUNICATION_PREFERENCE, PURCHASE_FREQUENCY, IS_ACTIVE
)
WITH customer_base AS (
    SELECT UNIFORM(1000, 9999, RANDOM()) as customer_id
    FROM table(generator(rowcount => 1500))
)
SELECT DISTINCT
    customer_id,
    CASE UNIFORM(1, 20, RANDOM())
        WHEN 1 THEN 'John'
        WHEN 2 THEN 'Jane'
        WHEN 3 THEN 'Michael'
        WHEN 4 THEN 'Sarah'
        WHEN 5 THEN 'David'
        WHEN 6 THEN 'Lisa'
        WHEN 7 THEN 'Robert'
        WHEN 8 THEN 'Emily'
        WHEN 9 THEN 'William'
        WHEN 10 THEN 'Ashley'
        WHEN 11 THEN 'James'
        WHEN 12 THEN 'Jessica'
        WHEN 13 THEN 'Christopher'
        WHEN 14 THEN 'Amanda'
        WHEN 15 THEN 'Daniel'
        WHEN 16 THEN 'Stephanie'
        WHEN 17 THEN 'Matthew'
        WHEN 18 THEN 'Nicole'
        WHEN 19 THEN 'Andrew'
        ELSE 'Rachel'
    END as first_name,
    CASE UNIFORM(1, 15, RANDOM())
        WHEN 1 THEN 'Smith'
        WHEN 2 THEN 'Johnson'
        WHEN 3 THEN 'Williams'
        WHEN 4 THEN 'Brown'
        WHEN 5 THEN 'Jones'
        WHEN 6 THEN 'Garcia'
        WHEN 7 THEN 'Miller'
        WHEN 8 THEN 'Davis'
        WHEN 9 THEN 'Rodriguez'
        WHEN 10 THEN 'Martinez'
        WHEN 11 THEN 'Hernandez'
        WHEN 12 THEN 'Lopez'
        WHEN 13 THEN 'Gonzalez'
        WHEN 14 THEN 'Wilson'
        ELSE 'Anderson'
    END as last_name,
    LOWER(CONCAT(
        CASE UNIFORM(1, 20, RANDOM())
            WHEN 1 THEN 'john'
            WHEN 2 THEN 'jane'
            WHEN 3 THEN 'michael'
            WHEN 4 THEN 'sarah'
            WHEN 5 THEN 'david'
            WHEN 6 THEN 'lisa'
            WHEN 7 THEN 'robert'
            WHEN 8 THEN 'emily'
            WHEN 9 THEN 'william'
            WHEN 10 THEN 'ashley'
            WHEN 11 THEN 'james'
            WHEN 12 THEN 'jessica'
            WHEN 13 THEN 'christopher'
            WHEN 14 THEN 'amanda'
            WHEN 15 THEN 'daniel'
            WHEN 16 THEN 'stephanie'
            WHEN 17 THEN 'matthew'
            WHEN 18 THEN 'nicole'
            WHEN 19 THEN 'andrew'
            ELSE 'rachel'
        END,
        '.',
        CASE UNIFORM(1, 15, RANDOM())
            WHEN 1 THEN 'smith'
            WHEN 2 THEN 'johnson'
            WHEN 3 THEN 'williams'
            WHEN 4 THEN 'brown'
            WHEN 5 THEN 'jones'
            WHEN 6 THEN 'garcia'
            WHEN 7 THEN 'miller'
            WHEN 8 THEN 'davis'
            WHEN 9 THEN 'rodriguez'
            WHEN 10 THEN 'martinez'
            WHEN 11 THEN 'hernandez'
            WHEN 12 THEN 'lopez'
            WHEN 13 THEN 'gonzalez'
            WHEN 14 THEN 'wilson'
            ELSE 'anderson'
        END,
        '@email.com'
    )) as email,
    CONCAT(
        '(',
        LPAD(UNIFORM(200, 999, RANDOM()), 3, '0'),
        ') ',
        LPAD(UNIFORM(100, 999, RANDOM()), 3, '0'),
        '-',
        LPAD(UNIFORM(1000, 9999, RANDOM()), 4, '0')
    ) as phone,
    DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) as registration_date,
    CASE UNIFORM(1, 5, RANDOM())
        WHEN 1 THEN 'Premium'
        WHEN 2 THEN 'Standard'
        WHEN 3 THEN 'Basic'
        WHEN 4 THEN 'VIP'
        ELSE 'Enterprise'
    END as customer_segment,
    ROUND(UNIFORM(100, 8000, RANDOM()) + UNIFORM(0, 2000, RANDOM()), 2) as lifetime_value,
    CASE UNIFORM(1, 4, RANDOM())
        WHEN 1 THEN 'North'
        WHEN 2 THEN 'South'
        WHEN 3 THEN 'East'
        ELSE 'West'
    END as preferred_region,
    CASE UNIFORM(1, 5, RANDOM())
        WHEN 1 THEN '18-25'
        WHEN 2 THEN '26-35'
        WHEN 3 THEN '36-45'
        WHEN 4 THEN '46-55'
        ELSE '55+'
    END as age_group,
    CASE UNIFORM(1, 3, RANDOM())
        WHEN 1 THEN 'Email'
        WHEN 2 THEN 'SMS'
        ELSE 'Phone'
    END as communication_preference,
    CASE UNIFORM(1, 4, RANDOM())
        WHEN 1 THEN 'Weekly'
        WHEN 2 THEN 'Monthly'
        WHEN 3 THEN 'Quarterly'
        ELSE 'Yearly'
    END as purchase_frequency,
    CASE WHEN RANDOM() > 0.05 THEN TRUE ELSE FALSE END as is_active
FROM customer_base
LIMIT 1500;

-- ========================================
-- 3. PRODUCT CATALOG TABLE (Enhanced)
-- ========================================
CREATE OR REPLACE TABLE PRODUCTS (
    PRODUCT_ID VARCHAR(10) PRIMARY KEY,
    PRODUCT_NAME VARCHAR(100),
    CATEGORY VARCHAR(50),
    SUBCATEGORY VARCHAR(50),
    BRAND VARCHAR(50),
    PRICE DECIMAL(10,2),
    COST DECIMAL(10,2),
    INVENTORY_COUNT INTEGER,
    WEIGHT_KG DECIMAL(5,2),
    LAUNCH_DATE DATE,
    PRODUCT_DESCRIPTION TEXT,
    FEATURES TEXT,
    WARRANTY_MONTHS INTEGER,
    IS_DISCONTINUED BOOLEAN DEFAULT FALSE,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert enhanced product data
INSERT INTO PRODUCTS (
    PRODUCT_ID, PRODUCT_NAME, CATEGORY, SUBCATEGORY, BRAND, PRICE, COST, 
    INVENTORY_COUNT, WEIGHT_KG, LAUNCH_DATE, PRODUCT_DESCRIPTION, FEATURES, 
    WARRANTY_MONTHS, IS_DISCONTINUED
) VALUES
('PROD-001', 'Laptop Pro 15', 'Electronics', 'Computers', 'TechBrand', 1299.99, 800.00, 150, 2.1, '2023-03-15', 
 'High-performance laptop with 15-inch display, perfect for professional work and gaming. Features latest generation processor and dedicated graphics card.',
 'Intel i7 processor, 16GB RAM, 512GB SSD, NVIDIA GeForce RTX graphics, 15.6"" 4K display, backlit keyboard', 24, FALSE),
('PROD-002', 'Wireless Mouse', 'Accessories', 'Input Devices', 'MouseCorp', 29.99, 12.00, 500, 0.15, '2023-01-10',
 'Ergonomic wireless mouse with precision tracking and long battery life. Perfect for office and gaming use.',
 'Wireless connectivity, ergonomic design, precision optical sensor, 12-month battery life, programmable buttons', 12, FALSE),
('PROD-003', 'Mechanical Keyboard', 'Accessories', 'Input Devices', 'KeyMaster', 89.99, 35.00, 200, 1.2, '2023-02-20',
 'Premium mechanical keyboard with customizable RGB lighting and responsive switches for enhanced typing experience.',
 'Mechanical switches, RGB backlighting, programmable keys, USB-C connectivity, aluminum frame', 18, FALSE),
('PROD-004', 'USB-C Hub', 'Accessories', 'Connectivity', 'ConnectPro', 49.99, 20.00, 300, 0.3, '2023-04-05',
 'Multi-port USB-C hub with power delivery support. Expand your laptop connectivity with multiple ports.',
 'USB-C power delivery, 4x USB 3.0 ports, HDMI output, SD card reader, compact design', 12, FALSE),
('PROD-005', 'Webcam HD', 'Electronics', 'Video', 'VisionTech', 79.99, 30.00, 180, 0.4, '2023-01-25',
 'High-definition webcam with auto-focus and noise reduction microphone for professional video calls.',
 '1080p HD video, auto-focus, noise-canceling microphone, universal compatibility, privacy shutter', 12, FALSE),
('PROD-006', 'Monitor 27 inch', 'Electronics', 'Displays', 'ScreenMax', 299.99, 180.00, 75, 6.5, '2023-05-10',
 '27-inch professional monitor with 4K resolution and color accuracy perfect for creative professionals.',
 '27"" 4K UHD display, 99% sRGB color gamut, USB-C connectivity, height-adjustable stand, anti-glare coating', 36, FALSE),
('PROD-007', 'Tablet 10 inch', 'Electronics', 'Mobile', 'TabletCorp', 399.99, 250.00, 120, 0.8, '2023-06-15',
 'Versatile 10-inch tablet with stylus support and long battery life for work and entertainment.',
 '10.1"" touchscreen, stylus included, 12-hour battery life, WiFi + cellular options, lightweight design', 12, FALSE),
('PROD-008', 'Smartphone', 'Electronics', 'Mobile', 'PhoneMaker', 699.99, 400.00, 90, 0.2, '2023-07-01',
 'Latest smartphone with advanced camera system and 5G connectivity for modern mobile computing.',
 '6.7"" OLED display, triple camera system, 5G connectivity, wireless charging, 256GB storage', 24, FALSE),
('PROD-009', 'Headphones', 'Accessories', 'Audio', 'SoundBest', 199.99, 80.00, 250, 0.3, '2023-02-28',
 'Premium over-ear headphones with active noise cancellation and superior sound quality.',
 'Active noise cancellation, 30-hour battery life, wireless and wired modes, premium materials', 18, FALSE),
('PROD-010', 'Smartwatch', 'Electronics', 'Wearables', 'WristTech', 249.99, 120.00, 160, 0.1, '2023-08-20',
 'Advanced smartwatch with health monitoring and fitness tracking capabilities.',
 'Heart rate monitor, GPS tracking, water resistant, 7-day battery life, smartphone integration', 12, FALSE);

-- ========================================
-- 4. CUSTOMER FEEDBACK TABLE (For Cortex AI)
-- ========================================
CREATE OR REPLACE TABLE CUSTOMER_FEEDBACK (
    FEEDBACK_ID INTEGER AUTOINCREMENT,
    CUSTOMER_ID INTEGER,
    PRODUCT_ID VARCHAR(10),
    RATING INTEGER,
    REVIEW_TEXT TEXT,
    FEEDBACK_DATE DATE,
    SUPPORT_TICKET_ID VARCHAR(20),
    FEEDBACK_CHANNEL VARCHAR(30),
    SENTIMENT_SCORE DECIMAL(5,3),
    SENTIMENT_CATEGORY VARCHAR(10),
    AI_SUMMARY TEXT,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert comprehensive customer feedback for AI analysis
INSERT INTO CUSTOMER_FEEDBACK (CUSTOMER_ID, PRODUCT_ID, RATING, REVIEW_TEXT, FEEDBACK_DATE, SUPPORT_TICKET_ID, FEEDBACK_CHANNEL)
VALUES
(1001, 'PROD-001', 5, 'Absolutely love this laptop! The performance is incredible and the battery life exceeds my expectations. Perfect for both work and gaming. The 4K display is stunning and the build quality feels premium. Highly recommend to anyone looking for a high-end device.', '2024-07-15', 'TKT-2024-001', 'Website Review'),
(1002, 'PROD-002', 4, 'Great wireless mouse with excellent tracking precision. The ergonomic design fits perfectly in my hand and reduces strain during long work sessions. Only minor complaint is that the click sound is a bit loud for quiet office environments, but overall very satisfied.', '2024-07-14', NULL, 'App Review'),
(1003, 'PROD-003', 5, 'This mechanical keyboard has completely transformed my typing experience. The tactile feedback is incredibly satisfying and the RGB lighting looks fantastic. Build quality is exceptional with the aluminum frame feeling very solid. Worth every penny for serious typists and programmers.', '2024-07-13', NULL, 'Website Review'),
(1004, 'PROD-001', 2, 'Very disappointed with this laptop purchase. The device runs extremely hot during normal use and the fan noise is excessive and distracting. Customer support was unhelpful when I reported these thermal issues. Expected much better for this price point.', '2024-07-12', 'TKT-2024-002', 'Email'),
(1005, 'PROD-004', 4, 'Solid USB-C hub with good port selection and reliable connectivity. Works perfectly with my MacBook Pro and handles 4K video output without any issues. Compact design makes it perfect for travel. Power delivery works as advertised.', '2024-07-11', NULL, 'App Review'),
(1006, 'PROD-005', 3, 'Webcam video quality is decent for the price point. Image is clear and sharp in good lighting conditions but struggles significantly in low light situations. Audio quality from the built-in microphone could be better for professional video calls.', '2024-07-10', NULL, 'Website Review'),
(1007, 'PROD-006', 5, 'Outstanding monitor with brilliant color reproduction and sharp 4K resolution. The 27-inch size is perfect for productivity work and creative projects. Stand adjustment options are comprehensive and the build quality is excellent. Great value for professional use.', '2024-07-09', NULL, 'Website Review'),
(1008, 'PROD-007', 4, 'Impressive tablet with smooth performance and beautiful display quality. Battery life easily lasts a full day of heavy use and the included stylus works very well for drawing and note-taking. Only wish it had more internal storage options available.', '2024-07-08', NULL, 'App Review'),
(1009, 'PROD-008', 1, 'Extremely poor experience with this smartphone. Battery drains very quickly even with minimal usage, camera quality is significantly subpar compared to competitors, and the user interface is often laggy and unresponsive. Would not recommend to anyone.', '2024-07-07', 'TKT-2024-003', 'Phone Support'),
(1010, 'PROD-009', 5, 'These headphones deliver absolutely exceptional audio quality with deep, rich bass and crystal clear highs. The active noise cancellation works perfectly for blocking out distractions. Comfort level is outstanding even during very long listening sessions. Best audio purchase this year!', '2024-07-06', NULL, 'Website Review'),
(1011, 'PROD-010', 4, 'Smart watch with comprehensive health tracking features that work accurately. The interface is intuitive and easy to navigate, and battery life consistently lasts the full week as advertised. Sleep tracking accuracy could be improved but overall very satisfied with the purchase.', '2024-07-05', NULL, 'App Review'),
(1012, 'PROD-001', 5, 'Fantastic laptop perfectly suited for professional software development work. Handles multiple development environments and virtual machines smoothly. The display quality is absolutely stunning for both coding and design work. Customer service team was excellent when I had setup questions.', '2024-07-04', NULL, 'Website Review'),
(1013, 'PROD-002', 3, 'Mouse functions adequately for basic office tasks but the wireless connection occasionally drops during intensive use. For this price range, I expected much more reliability and consistent performance. Good enough for basic tasks but not ideal for gaming or precision work.', '2024-07-03', 'TKT-2024-004', 'Email'),
(1014, 'PROD-003', 5, 'Keyboard enthusiasts will absolutely love this product. The mechanical switches are highly responsive and provide excellent tactile feedback. The customizable RGB backlighting adds a professional touch to any workspace. Excellent investment for both coding and creative writing.', '2024-07-02', NULL, 'Website Review'),
(1015, 'PROD-004', 2, 'USB-C hub completely stopped working after just two weeks of normal daily use. The build quality seems quite poor for the price point and customer support response was very slow when I reported the issue. Expected much better durability and reliability.', '2024-07-01', 'TKT-2024-005', 'Phone Support'),
(1016, 'PROD-005', 4, 'Webcam provides good video quality for virtual meetings and streaming. Auto-focus feature works well and the privacy shutter is a nice security touch. Setup was very straightforward and it works with all major video conferencing platforms without issues.', '2024-06-30', NULL, 'Website Review'),
(1017, 'PROD-006', 5, 'Monitor is absolutely perfect for photo editing and graphic design work. Color accuracy is exceptional and the 4K resolution shows incredible detail. The adjustable stand allows for perfect positioning and the anti-glare coating reduces eye strain significantly.', '2024-06-29', NULL, 'App Review'),
(1018, 'PROD-007', 3, 'Tablet performance is generally good but the battery life doesn''t quite live up to the marketing claims. Screen quality is nice for media consumption but the speaker quality could be significantly better. Adequate for basic tasks but not exceptional.', '2024-06-28', NULL, 'Website Review'),
(1019, 'PROD-008', 4, 'Smartphone camera system is impressive with excellent photo quality in various lighting conditions. 5G connectivity is fast and reliable. Battery life is good for a full day of moderate to heavy usage. User interface is smooth and responsive.', '2024-06-27', NULL, 'App Review'),
(1020, 'PROD-009', 2, 'Headphones are uncomfortable for extended wearing periods and the noise cancellation feature doesn\'t work as effectively as advertised. Audio quality is mediocre at best for this price range. Expected much better performance and comfort from this brand.', '2024-06-26', 'TKT-2024-006', 'Email');

-- ========================================
-- 5. AI AGENT CONVERSATIONS TABLE
-- ========================================
CREATE OR REPLACE TABLE AI_AGENT_CONVERSATIONS (
    CONVERSATION_ID VARCHAR(50),
    CUSTOMER_ID INTEGER,
    AGENT_TYPE VARCHAR(30),
    MESSAGE_TYPE VARCHAR(20), -- 'user' or 'assistant'
    MESSAGE_TEXT TEXT,
    TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    INTENT_DETECTED VARCHAR(50),
    CONFIDENCE_SCORE DECIMAL(3,2),
    RESOLUTION_STATUS VARCHAR(20),
    SESSION_DURATION_MINUTES INTEGER
);

-- Insert sample AI agent conversations
INSERT INTO AI_AGENT_CONVERSATIONS VALUES
('CONV_001', 1001, 'Sales Assistant', 'user', 'I am looking for a high-performance laptop for both gaming and professional software development. What would you recommend from your current lineup?', '2024-07-20 10:30:00', 'product_recommendation', 0.95, 'active', 15),
('CONV_001', 1001, 'Sales Assistant', 'assistant', 'Based on your specific needs for gaming and development, I highly recommend the Laptop Pro 15. It features an Intel i7 processor, 16GB RAM, and NVIDIA GeForce RTX graphics, making it perfect for both intensive development work and modern gaming. Would you like to know more about its technical specifications or current pricing?', '2024-07-20 10:30:15', NULL, NULL, 'active', NULL),
('CONV_002', 1004, 'Support Agent', 'user', 'My laptop is running extremely hot and the fan noise is becoming unbearable during normal use. This is very frustrating as I just purchased it last month!', '2024-07-20 11:15:00', 'technical_support', 0.88, 'in_progress', 25),
('CONV_002', 1004, 'Support Agent', 'assistant', 'I completely understand your frustration with the overheating issue, and I apologize for this inconvenience. Thermal management is indeed very important for laptop performance. Let me help you troubleshoot this systematically. First, could you tell me what applications you typically run when this overheating occurs?', '2024-07-20 11:15:30', NULL, NULL, 'in_progress', NULL),
('CONV_003', 1007, 'Product Expert', 'user', 'Can you explain the differences between your monitor options? I need one specifically optimized for professional photo editing and color-critical work.', '2024-07-20 14:20:00', 'product_comparison', 0.92, 'resolved', 12),
('CONV_003', 1007, 'Product Expert', 'assistant', 'For professional photo editing, the Monitor 27 inch is absolutely perfect for your needs! It features exceptional color accuracy with 99% sRGB coverage, 4K UHD resolution for incredible detail, and professional-grade color calibration. The 27-inch size provides ample workspace for your editing tools and timeline.', '2024-07-20 14:20:45', NULL, NULL, 'resolved', NULL),
('CONV_004', 1010, 'Sales Assistant', 'user', 'I\'m interested in upgrading my audio setup for music production. What headphones would you recommend for studio work?', '2024-07-21 09:15:00', 'product_recommendation', 0.89, 'resolved', 8),
('CONV_004', 1010, 'Sales Assistant', 'assistant', 'For music production and studio work, our Headphones model offers exceptional audio fidelity with accurate frequency response across all ranges. They feature active noise cancellation to eliminate external interference and provide comfortable extended wearing for long studio sessions.', '2024-07-21 09:16:30', NULL, NULL, 'resolved', NULL);

-- ========================================
-- 6. AI INSIGHTS AND PREDICTIONS TABLE
-- ========================================
CREATE OR REPLACE TABLE AI_INSIGHTS (
    INSIGHT_ID INTEGER AUTOINCREMENT,
    INSIGHT_TYPE VARCHAR(50),
    SUBJECT_ID VARCHAR(50),
    SUBJECT_NAME VARCHAR(100),
    AI_SUMMARY TEXT,
    RECOMMENDATION TEXT,
    CONFIDENCE_SCORE DECIMAL(3,2),
    RISK_LEVEL VARCHAR(20),
    PREDICTED_IMPACT VARCHAR(20),
    INSIGHT_DATE DATE DEFAULT CURRENT_DATE(),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert AI-generated insights
INSERT INTO AI_INSIGHTS (INSIGHT_TYPE, SUBJECT_ID, SUBJECT_NAME, AI_SUMMARY, RECOMMENDATION, CONFIDENCE_SCORE, RISK_LEVEL, PREDICTED_IMPACT) VALUES
('product_performance', 'PROD-001', 'Laptop Pro 15', 'High-performing flagship product with excellent customer satisfaction metrics. Shows strong sales momentum in Q2 2024 with 94% positive sentiment analysis. Popular among professional users and gamers.', 'Increase inventory by 25% for Q3 and target premium customer segments with focused marketing campaigns', 0.94, 'Low', 'High'),
('product_performance', 'PROD-002', 'Wireless Mouse', 'Steady performer with moderate satisfaction scores. Some recurring complaints about connection reliability affecting overall ratings. Solid sales volume but room for improvement.', 'Address wireless connectivity issues in next product iteration and consider extended warranty program', 0.87, 'Medium', 'Medium'),
('customer_segment', 'Premium', 'Premium Customer Segment', 'High-value customers focused on quality over price. Demonstrate strong brand loyalty and prefer cutting-edge technology with premium support services. Average purchase value $1,200.', 'Offer exclusive early access to new products and dedicated premium support channels', 0.91, 'Low', 'High'),
('customer_segment', 'Standard', 'Standard Customer Segment', 'Price-conscious customers seeking reliable products with good value proposition. Highly value customer service quality and comprehensive product warranties. Average purchase value $350.', 'Focus on bundle deals and emphasize value propositions in marketing communications', 0.88, 'Medium', 'Medium'),
('market_trend', 'Electronics', 'Electronics Category', 'Strong growth trend in electronics category driven by remote work and digital transformation. Increasing demand for high-performance computing devices.', 'Expand electronics inventory and introduce new premium product lines', 0.89, 'Low', 'High'),
('anomaly_detection', 'SALES_SPIKE', 'Unusual Sales Pattern', 'Detected significant positive anomaly in sales volume during week of July 15th. 40% increase above normal patterns, likely due to promotional campaign effectiveness.', 'Analyze successful campaign elements for replication in future marketing initiatives', 0.93, 'Low', 'High');

-- ========================================
-- 7. ENHANCED WEB ANALYTICS TABLE
-- ========================================
CREATE OR REPLACE TABLE WEB_ANALYTICS (
    SESSION_ID VARCHAR(50),
    VISIT_DATE DATE,
    VISIT_TIME TIMESTAMP,
    USER_ID INTEGER,
    PAGE_VIEWS INTEGER,
    SESSION_DURATION_MINUTES INTEGER,
    BOUNCE_RATE DECIMAL(5,2),
    CONVERSION_FLAG BOOLEAN,
    TRAFFIC_SOURCE VARCHAR(50),
    DEVICE_TYPE VARCHAR(20),
    BROWSER VARCHAR(30),
    COUNTRY VARCHAR(50),
    PAGES_VISITED TEXT,
    USER_AGENT TEXT,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert enhanced web analytics data
INSERT INTO WEB_ANALYTICS (
    SESSION_ID, VISIT_DATE, VISIT_TIME, USER_ID, PAGE_VIEWS, SESSION_DURATION_MINUTES, 
    BOUNCE_RATE, CONVERSION_FLAG, TRAFFIC_SOURCE, DEVICE_TYPE, BROWSER, COUNTRY, 
    PAGES_VISITED, USER_AGENT
)
SELECT 
    CONCAT('SID_', LPAD(seq4(), 8, '0')) as session_id,
    DATEADD(day, UNIFORM(0, 365, RANDOM()), '2024-01-01'::date) as visit_date,
    DATEADD(hour, UNIFORM(0, 23, RANDOM()), 
            DATEADD(minute, UNIFORM(0, 59, RANDOM()), 
            DATEADD(day, UNIFORM(0, 365, RANDOM()), '2024-01-01'::date)::timestamp)) as visit_time,
    UNIFORM(1000, 9999, RANDOM()) as user_id,
    UNIFORM(1, 20, RANDOM()) as page_views,
    UNIFORM(1, 60, RANDOM()) as session_duration_minutes,
    ROUND(UNIFORM(0, 100, RANDOM()), 2) as bounce_rate,
    CASE WHEN UNIFORM(0, 1, RANDOM()) > 0.82 THEN TRUE ELSE FALSE END as conversion_flag,
    CASE UNIFORM(1, 7, RANDOM())
        WHEN 1 THEN 'Organic Search'
        WHEN 2 THEN 'Social Media'
        WHEN 3 THEN 'Direct'
        WHEN 4 THEN 'Email Campaign'
        WHEN 5 THEN 'Paid Ads'
        WHEN 6 THEN 'Referral'
        ELSE 'Affiliate'
    END as traffic_source,
    CASE UNIFORM(1, 4, RANDOM())
        WHEN 1 THEN 'Desktop'
        WHEN 2 THEN 'Mobile'
        WHEN 3 THEN 'Tablet'
        ELSE 'Smart TV'
    END as device_type,
    CASE UNIFORM(1, 6, RANDOM())
        WHEN 1 THEN 'Chrome'
        WHEN 2 THEN 'Safari'
        WHEN 3 THEN 'Firefox'
        WHEN 4 THEN 'Edge'
        WHEN 5 THEN 'Opera'
        ELSE 'Other'
    END as browser,
    CASE UNIFORM(1, 10, RANDOM())
        WHEN 1 THEN 'United States'
        WHEN 2 THEN 'Canada'
        WHEN 3 THEN 'United Kingdom'
        WHEN 4 THEN 'Germany'
        WHEN 5 THEN 'France'
        WHEN 6 THEN 'Australia'
        WHEN 7 THEN 'Japan'
        WHEN 8 THEN 'Brazil'
        WHEN 9 THEN 'India'
        ELSE 'Other'
    END as country,
    CONCAT('Homepage,Product-', UNIFORM(1,10,RANDOM()), ',Category-Electronics') as pages_visited,
    CONCAT('Mozilla/5.0 (', 
           CASE UNIFORM(1,3,RANDOM()) WHEN 1 THEN 'Windows NT 10.0' WHEN 2 THEN 'Macintosh' ELSE 'X11; Linux' END,
           ') Browser/Version') as user_agent
FROM table(generator(rowcount => 8000));

-- ========================================
-- 8. ENHANCED VIEWS FOR AI ANALYTICS
-- ========================================

-- Enhanced Daily Sales Summary with AI Insights
CREATE OR REPLACE VIEW DAILY_SALES_SUMMARY AS
SELECT 
    SALE_DATE,
    COUNT(*) as total_transactions,
    SUM(TOTAL_AMOUNT) as daily_revenue,
    SUM(PROFIT_AMOUNT) as daily_profit,
    AVG(TOTAL_AMOUNT) as avg_transaction_value,
    COUNT(DISTINCT CUSTOMER_ID) as unique_customers,
    COUNT(DISTINCT SALES_REP) as active_sales_reps,
    SUM(CASE WHEN CHANNEL = 'Online Store' THEN TOTAL_AMOUNT ELSE 0 END) as online_revenue,
    SUM(CASE WHEN CHANNEL = 'Retail Store' THEN TOTAL_AMOUNT ELSE 0 END) as retail_revenue
FROM SALES_DATA
GROUP BY SALE_DATE
ORDER BY SALE_DATE;

-- Enhanced Regional Performance with AI Metrics
CREATE OR REPLACE VIEW REGIONAL_PERFORMANCE AS
SELECT 
    REGION,
    COUNT(*) as total_sales,
    SUM(TOTAL_AMOUNT) as total_revenue,
    SUM(PROFIT_AMOUNT) as total_profit,
    AVG(PROFIT_MARGIN) as avg_profit_margin,
    COUNT(DISTINCT CUSTOMER_ID) as unique_customers,
    COUNT(DISTINCT SALES_REP) as sales_reps,
    AVG(TOTAL_AMOUNT) as avg_order_value,
    MAX(TOTAL_AMOUNT) as highest_sale,
    COUNT(DISTINCT CHANNEL) as channel_diversity
FROM SALES_DATA
GROUP BY REGION
ORDER BY total_revenue DESC;

-- Product Performance with Sentiment Analysis
CREATE OR REPLACE VIEW PRODUCT_PERFORMANCE_WITH_SENTIMENT AS
SELECT 
    s.PRODUCT_ID,
    s.PRODUCT_NAME,
    s.CATEGORY,
    p.BRAND,
    COUNT(s.SALE_ID) as units_sold,
    SUM(s.TOTAL_AMOUNT) as total_revenue,
    SUM(s.PROFIT_AMOUNT) as total_profit,
    AVG(s.PROFIT_MARGIN) as avg_profit_margin,
    p.INVENTORY_COUNT as current_inventory,
    COUNT(cf.FEEDBACK_ID) as review_count,
    AVG(cf.RATING) as avg_rating,
    AVG(cf.SENTIMENT_SCORE) as avg_sentiment,
    COUNT(CASE WHEN cf.SENTIMENT_CATEGORY = 'Positive' THEN 1 END) as positive_reviews,
    COUNT(CASE WHEN cf.SENTIMENT_CATEGORY = 'Negative' THEN 1 END) as negative_reviews
FROM SALES_DATA s
JOIN PRODUCTS p ON s.PRODUCT_ID = p.PRODUCT_ID
LEFT JOIN CUSTOMER_FEEDBACK cf ON s.PRODUCT_ID = cf.PRODUCT_ID
GROUP BY s.PRODUCT_ID, s.PRODUCT_NAME, s.CATEGORY, p.BRAND, p.INVENTORY_COUNT
ORDER BY total_revenue DESC;

-- Customer Intelligence with AI Insights
CREATE OR REPLACE VIEW CUSTOMER_INTELLIGENCE AS
SELECT 
    c.CUSTOMER_ID,
    CONCAT(c.FIRST_NAME, ' ', c.LAST_NAME) as customer_name,
    c.CUSTOMER_SEGMENT,
    c.AGE_GROUP,
    c.LIFETIME_VALUE,
    COUNT(s.SALE_ID) as total_purchases,
    SUM(s.TOTAL_AMOUNT) as total_spent,
    AVG(s.TOTAL_AMOUNT) as avg_order_value,
    MAX(s.SALE_DATE) as last_purchase_date,
    COUNT(cf.FEEDBACK_ID) as feedback_count,
    AVG(cf.RATING) as avg_rating,
    CASE 
        WHEN c.LIFETIME_VALUE < 500 AND COUNT(s.SALE_ID) < 2 THEN 'High Churn Risk'
        WHEN AVG(cf.SENTIMENT_SCORE) < -0.2 THEN 'Satisfaction Risk'
        WHEN c.LIFETIME_VALUE > 2000 THEN 'VIP Customer'
        ELSE 'Healthy'
    END as customer_risk_level
FROM CUSTOMERS c
LEFT JOIN SALES_DATA s ON c.CUSTOMER_ID = s.CUSTOMER_ID
LEFT JOIN CUSTOMER_FEEDBACK cf ON c.CUSTOMER_ID = cf.CUSTOMER_ID
WHERE c.IS_ACTIVE = TRUE
GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, c.CUSTOMER_SEGMENT, c.AGE_GROUP, c.LIFETIME_VALUE
ORDER BY total_spent DESC;

-- ========================================
-- 9. AI-ENHANCED STORED PROCEDURES
-- ========================================

-- Create a view instead of procedure for product insights (simpler approach)
CREATE OR REPLACE VIEW PRODUCT_AI_INSIGHTS AS
SELECT 
    p.PRODUCT_ID,
    p.PRODUCT_NAME,
    'Sales Performance' as INSIGHT_TYPE,
    CONCAT('Revenue: $', COALESCE(SUM(s.TOTAL_AMOUNT), 0)::VARCHAR, ' | Units: ', COALESCE(COUNT(s.SALE_ID), 0)::VARCHAR) as INSIGHT_VALUE,
    0.95 as CONFIDENCE_SCORE
FROM PRODUCTS p
LEFT JOIN SALES_DATA s ON p.PRODUCT_ID = s.PRODUCT_ID
GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME

UNION ALL

SELECT 
    p.PRODUCT_ID,
    p.PRODUCT_NAME,
    'Customer Sentiment' as INSIGHT_TYPE,
    CONCAT('Avg Rating: ', COALESCE(ROUND(AVG(cf.RATING), 1), 0)::VARCHAR, ' | Reviews: ', COALESCE(COUNT(cf.FEEDBACK_ID), 0)::VARCHAR) as INSIGHT_VALUE,
    0.88 as CONFIDENCE_SCORE
FROM PRODUCTS p
LEFT JOIN CUSTOMER_FEEDBACK cf ON p.PRODUCT_ID = cf.PRODUCT_ID
GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME;

-- ========================================
-- 10. VERIFICATION AND SAMPLE QUERIES
-- ========================================

-- Verify all tables have data
SELECT 'SALES_DATA' as table_name, COUNT(*) as record_count FROM SALES_DATA
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM CUSTOMERS
UNION ALL
SELECT 'PRODUCTS', COUNT(*) FROM PRODUCTS
UNION ALL
SELECT 'CUSTOMER_FEEDBACK', COUNT(*) FROM CUSTOMER_FEEDBACK
UNION ALL
SELECT 'AI_AGENT_CONVERSATIONS', COUNT(*) FROM AI_AGENT_CONVERSATIONS
UNION ALL
SELECT 'AI_INSIGHTS', COUNT(*) FROM AI_INSIGHTS
UNION ALL
SELECT 'WEB_ANALYTICS', COUNT(*) FROM WEB_ANALYTICS;

-- Sample AI-ready queries
SELECT 'Sample Product Performance with Sentiment' as info;
SELECT * FROM PRODUCT_PERFORMANCE_WITH_SENTIMENT LIMIT 5;

SELECT 'Sample Customer Intelligence' as info;
SELECT * FROM CUSTOMER_INTELLIGENCE LIMIT 5;

SELECT 'Sample AI Agent Conversations' as info;
SELECT CONVERSATION_ID, AGENT_TYPE, MESSAGE_TYPE, LEFT(MESSAGE_TEXT, 50) as PREVIEW, INTENT_DETECTED 
FROM AI_AGENT_CONVERSATIONS LIMIT 5;

-- ========================================
-- SCRIPT COMPLETE!
-- ========================================
-- Your enhanced sample database with Cortex AI support is ready!
-- 
-- New AI-Ready Features:
-- 1. Customer Feedback with Sentiment Analysis
-- 2. AI Agent Conversation Tracking
-- 3. AI Insights and Predictions Storage
-- 4. Enhanced Analytics Views
-- 5. Comprehensive Product Descriptions for AI Processing
-- 6. Customer Intelligence with Risk Assessment
-- 7. Advanced Web Analytics
-- 8. AI-Enhanced Stored Procedures
-- 
-- Next: Run cortex_ai_setup.sql to enable AI functions
-- Then: Use the enhanced app.py for full Cortex AI experience
-- ======================================== 