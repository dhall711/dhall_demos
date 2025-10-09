-- ========================================
-- SNOWFLAKE CORTEX AI SETUP SCRIPT
-- ========================================
-- This script extends the sample database with Cortex AI functionality
-- Includes: AI Functions, Semantic Views, Cortex Search, and AI Agents

-- Prerequisites: Run sample_database.sql first
USE DATABASE STREAMLIT_DEMO;
USE SCHEMA SAMPLE_DATA;

-- ========================================
-- 1. ENABLE CORTEX AI FUNCTIONS
-- ========================================

-- Create a table for customer feedback and reviews
CREATE OR REPLACE TABLE CUSTOMER_FEEDBACK (
    FEEDBACK_ID INTEGER AUTOINCREMENT,
    CUSTOMER_ID INTEGER,
    PRODUCT_ID VARCHAR(10),
    RATING INTEGER,
    REVIEW_TEXT TEXT,
    FEEDBACK_DATE DATE,
    SUPPORT_TICKET_ID VARCHAR(20),
    FEEDBACK_CHANNEL VARCHAR(30),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample customer feedback data
INSERT INTO CUSTOMER_FEEDBACK (CUSTOMER_ID, PRODUCT_ID, RATING, REVIEW_TEXT, FEEDBACK_DATE, SUPPORT_TICKET_ID, FEEDBACK_CHANNEL)
VALUES
(1001, 'PROD-001', 5, 'Absolutely love this laptop! The performance is incredible and the battery life exceeds my expectations. Perfect for both work and gaming. Highly recommend to anyone looking for a premium device.', '2024-07-15', 'TKT-2024-001', 'Website Review'),
(1002, 'PROD-002', 4, 'Great wireless mouse with excellent tracking. The ergonomic design fits perfectly in my hand. Only minor complaint is that the click sound is a bit loud for office environments.', '2024-07-14', NULL, 'App Review'),
(1003, 'PROD-003', 5, 'This mechanical keyboard has transformed my typing experience. The tactile feedback is satisfying and the build quality is exceptional. Worth every penny for serious typists and programmers.', '2024-07-13', NULL, 'Website Review'),
(1004, 'PROD-001', 2, 'Disappointed with this purchase. The laptop runs very hot during normal use and the fan noise is excessive. Customer support was unhelpful when I reported these issues.', '2024-07-12', 'TKT-2024-002', 'Email'),
(1005, 'PROD-004', 4, 'Solid USB-C hub with good port selection. Works well with my MacBook and handles 4K video output without issues. Compact design is perfect for travel.', '2024-07-11', NULL, 'App Review'),
(1006, 'PROD-005', 3, 'Webcam quality is decent for the price point. Video is clear in good lighting but struggles in low light conditions. Audio quality could be better for professional calls.', '2024-07-10', NULL, 'Website Review'),
(1007, 'PROD-006', 5, 'Outstanding monitor with brilliant color reproduction. The 27-inch size is perfect for productivity and the stand adjustment options are comprehensive. Great value for money.', '2024-07-09', NULL, 'Website Review'),
(1008, 'PROD-007', 4, 'Impressive tablet with smooth performance and beautiful display. Battery life is excellent and the build quality feels premium. Only wish it had more storage options.', '2024-07-08', NULL, 'App Review'),
(1009, 'PROD-008', 1, 'Very poor experience with this smartphone. Battery drains quickly, camera quality is subpar, and the interface is laggy. Would not recommend to anyone.', '2024-07-07', 'TKT-2024-003', 'Phone Support'),
(1010, 'PROD-009', 5, 'These headphones deliver exceptional audio quality with deep bass and crystal clear highs. Comfort level is outstanding even during long listening sessions. Best purchase this year!', '2024-07-06', NULL, 'Website Review'),
(1011, 'PROD-010', 4, 'Smart watch with comprehensive health tracking features. The interface is intuitive and battery life is impressive. Sleep tracking accuracy could be improved but overall very satisfied.', '2024-07-05', NULL, 'App Review'),
(1012, 'PROD-001', 5, 'Fantastic laptop for professional work. Handles multiple applications smoothly and the display quality is stunning. Customer service was excellent when I had questions about setup.', '2024-07-04', NULL, 'Website Review'),
(1013, 'PROD-002', 3, 'Mouse works adequately but the wireless connection occasionally drops. For the price, I expected more reliability. Good for basic tasks but not ideal for gaming.', '2024-07-03', 'TKT-2024-004', 'Email'),
(1014, 'PROD-003', 5, 'Keyboard enthusiasts will love this product. The switches are responsive and the customizable backlight adds a professional touch. Excellent for both coding and writing.', '2024-07-02', NULL, 'Website Review'),
(1015, 'PROD-004', 2, 'Hub stopped working after two weeks of normal use. The build quality seems poor and customer support was slow to respond. Expected better durability for the price.', '2024-07-01', 'TKT-2024-005', 'Phone Support');

-- ========================================
-- 2. AI-ENHANCED VIEWS WITH CORTEX FUNCTIONS
-- ========================================

-- Sentiment Analysis View
CREATE OR REPLACE VIEW CUSTOMER_SENTIMENT_ANALYSIS AS
SELECT 
    cf.*,
    SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) as sentiment_score,
    CASE 
        WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) > 0.1 THEN 'Positive'
        WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) < -0.1 THEN 'Negative'
        ELSE 'Neutral'
    END as sentiment_category,
    SNOWFLAKE.CORTEX.SUMMARIZE(cf.REVIEW_TEXT::VARCHAR) as review_summary
FROM CUSTOMER_FEEDBACK cf;

-- Product Review Summary with AI
CREATE OR REPLACE VIEW PRODUCT_AI_INSIGHTS AS
SELECT 
    p.PRODUCT_ID,
    p.PRODUCT_NAME,
    p.CATEGORY,
    COUNT(cf.FEEDBACK_ID) as total_reviews,
    AVG(cf.RATING) as avg_rating,
    AVG(SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR)) as avg_sentiment_score,
    SNOWFLAKE.CORTEX.SUMMARIZE(
        LISTAGG(cf.REVIEW_TEXT, ' | ') WITHIN GROUP (ORDER BY cf.FEEDBACK_DATE DESC)::VARCHAR
    ) as overall_feedback_summary,
    COUNT(CASE WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) > 0.1 THEN 1 END) as positive_reviews,
    COUNT(CASE WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) < -0.1 THEN 1 END) as negative_reviews
FROM PRODUCTS p
LEFT JOIN CUSTOMER_FEEDBACK cf ON p.PRODUCT_ID = cf.PRODUCT_ID
GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME, p.CATEGORY;

-- ========================================
-- 3. SEMANTIC LAYER SETUP
-- ========================================

-- Create semantic model for business intelligence
CREATE OR REPLACE VIEW SEMANTIC_SALES_MODEL AS
SELECT 
    sd.SALE_DATE,
    sd.CUSTOMER_ID,
    sd.PRODUCT_ID,
    sd.PRODUCT_NAME,
    sd.CATEGORY,
    sd.REGION,
    sd.SALES_REP,
    sd.QUANTITY,
    sd.UNIT_PRICE,
    sd.TOTAL_AMOUNT,
    sd.PROFIT_AMOUNT,
    sd.PROFIT_MARGIN,
    -- Customer attributes
    c.CUSTOMER_SEGMENT,
    c.LIFETIME_VALUE,
    -- Product attributes  
    p.BRAND,
    p.SUBCATEGORY,
    p.INVENTORY_COUNT,
    -- Time dimensions
    EXTRACT(YEAR FROM sd.SALE_DATE) as sale_year,
    EXTRACT(MONTH FROM sd.SALE_DATE) as sale_month,
    EXTRACT(DAY FROM sd.SALE_DATE) as sale_day,
    EXTRACT(QUARTER FROM sd.SALE_DATE) as sale_quarter,
    DAYNAME(sd.SALE_DATE) as sale_day_name,
    -- Calculated metrics
    CASE 
        WHEN sd.TOTAL_AMOUNT > 1000 THEN 'High Value'
        WHEN sd.TOTAL_AMOUNT > 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as transaction_value_tier,
    CASE
        WHEN sd.PROFIT_MARGIN > 25 THEN 'High Margin'
        WHEN sd.PROFIT_MARGIN > 15 THEN 'Medium Margin'
        ELSE 'Low Margin'
    END as profit_tier
FROM SALES_DATA sd
LEFT JOIN CUSTOMERS c ON sd.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN PRODUCTS p ON sd.PRODUCT_ID = p.PRODUCT_ID;

-- ========================================
-- 4. CORTEX SEARCH SETUP
-- ========================================

-- Create a search service for product information
-- Note: This requires additional setup in Snowflake UI for full functionality
CREATE OR REPLACE TABLE PRODUCT_SEARCH_INDEX (
    PRODUCT_ID VARCHAR(10),
    SEARCH_CONTENT TEXT,
    CATEGORY VARCHAR(50),
    BRAND VARCHAR(50),
    KEYWORDS TEXT
);

-- Populate search index with enriched product data
INSERT INTO PRODUCT_SEARCH_INDEX
SELECT 
    p.PRODUCT_ID,
    CONCAT(
        p.PRODUCT_NAME, ' ',
        p.CATEGORY, ' ',
        p.SUBCATEGORY, ' ',
        p.BRAND, ' ',
        COALESCE(ai.overall_feedback_summary, ''),
        ' Price: $', p.PRICE,
        ' Inventory: ', p.INVENTORY_COUNT
    ) as search_content,
    p.CATEGORY,
    p.BRAND,
    CONCAT(
        p.PRODUCT_NAME, ',',
        p.CATEGORY, ',',
        p.SUBCATEGORY, ',',
        p.BRAND
    ) as keywords
FROM PRODUCTS p
LEFT JOIN PRODUCT_AI_INSIGHTS ai ON p.PRODUCT_ID = ai.PRODUCT_ID;

-- ========================================
-- 5. AI AGENT SIMULATION TABLES
-- ========================================

-- Customer Service Agent Conversations
CREATE OR REPLACE TABLE AI_AGENT_CONVERSATIONS (
    CONVERSATION_ID VARCHAR(50),
    CUSTOMER_ID INTEGER,
    AGENT_TYPE VARCHAR(30),
    MESSAGE_TYPE VARCHAR(20), -- 'user' or 'assistant'
    MESSAGE_TEXT TEXT,
    TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    INTENT_DETECTED VARCHAR(50),
    CONFIDENCE_SCORE DECIMAL(3,2),
    RESOLUTION_STATUS VARCHAR(20)
);

-- Sample AI agent conversations
INSERT INTO AI_AGENT_CONVERSATIONS VALUES
('CONV_001', 1001, 'Sales Assistant', 'user', 'I am looking for a laptop for gaming and work. What would you recommend?', '2024-07-20 10:30:00', 'product_recommendation', 0.95, 'active'),
('CONV_001', 1001, 'Sales Assistant', 'assistant', 'Based on your needs, I recommend the Laptop Pro 15. It offers excellent performance for both gaming and professional work, with outstanding battery life and display quality. Would you like to know more about its specifications?', '2024-07-20 10:30:15', NULL, NULL, 'active'),
('CONV_002', 1004, 'Support Agent', 'user', 'My laptop is overheating and making loud fan noises. This is very frustrating!', '2024-07-20 11:15:00', 'technical_support', 0.88, 'in_progress'),
('CONV_002', 1004, 'Support Agent', 'assistant', 'I understand your frustration with the overheating issue. This can indeed be concerning. Let me help you troubleshoot this. First, could you tell me what applications you typically run when this happens?', '2024-07-20 11:15:30', NULL, NULL, 'in_progress'),
('CONV_003', 1007, 'Product Expert', 'user', 'Can you explain the difference between your monitors? I need one for photo editing.', '2024-07-20 14:20:00', 'product_comparison', 0.92, 'resolved'),
('CONV_003', 1007, 'Product Expert', 'assistant', 'For photo editing, the Monitor 27 inch is perfect! It features exceptional color reproduction with 99% sRGB coverage, making it ideal for professional photo work. The 27-inch size provides ample workspace for editing tools.', '2024-07-20 14:20:45', NULL, NULL, 'resolved');

-- AI Agent Performance Metrics
CREATE OR REPLACE TABLE AI_AGENT_METRICS (
    AGENT_TYPE VARCHAR(30),
    DATE DATE,
    TOTAL_CONVERSATIONS INTEGER,
    RESOLVED_CONVERSATIONS INTEGER,
    AVG_RESPONSE_TIME_SECONDS INTEGER,
    CUSTOMER_SATISFACTION_SCORE DECIMAL(3,2),
    COMMON_INTENTS TEXT
);

INSERT INTO AI_AGENT_METRICS VALUES
('Sales Assistant', '2024-07-20', 45, 38, 12, 4.2, 'product_recommendation,pricing_inquiry,feature_comparison'),
('Support Agent', '2024-07-20', 23, 18, 18, 3.8, 'technical_support,warranty_inquiry,troubleshooting'),
('Product Expert', '2024-07-20', 31, 29, 15, 4.5, 'product_comparison,specification_inquiry,compatibility_check');

-- ========================================
-- 6. ADVANCED AI ANALYTICS VIEWS
-- ========================================

-- AI-Powered Customer Intelligence View
CREATE OR REPLACE VIEW CUSTOMER_AI_INTELLIGENCE AS
SELECT 
    c.CUSTOMER_ID,
    c.FIRST_NAME,
    c.LAST_NAME,
    c.CUSTOMER_SEGMENT,
    c.LIFETIME_VALUE,
    -- Purchase behavior analysis
    COUNT(sd.SALE_ID) as total_purchases,
    AVG(sd.TOTAL_AMOUNT) as avg_order_value,
    SUM(sd.TOTAL_AMOUNT) as total_spent,
    -- Sentiment analysis from feedback
    AVG(CASE WHEN cf.REVIEW_TEXT IS NOT NULL 
        THEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) 
        ELSE NULL END) as avg_sentiment,
    -- AI-generated customer profile
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-8b'::VARCHAR,
        CONCAT(
            'Based on this customer data, create a brief customer profile: ',
            'Customer Segment: ', c.CUSTOMER_SEGMENT, ', ',
            'Total Purchases: ', COUNT(sd.SALE_ID), ', ',
            'Average Order Value: $', ROUND(AVG(sd.TOTAL_AMOUNT), 2), ', ',
            'Preferred Categories: ', LISTAGG(DISTINCT sd.CATEGORY, ', ')
        )::VARCHAR
    ) as ai_customer_profile,
    -- Risk assessment
    CASE 
        WHEN c.LIFETIME_VALUE < 500 AND COUNT(sd.SALE_ID) < 2 THEN 'High Churn Risk'
        WHEN AVG(CASE WHEN cf.REVIEW_TEXT IS NOT NULL 
                 THEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) 
                 ELSE NULL END) < -0.2 THEN 'Satisfaction Risk'
        ELSE 'Healthy'
    END as customer_risk_level
FROM CUSTOMERS c
LEFT JOIN SALES_DATA sd ON c.CUSTOMER_ID = sd.CUSTOMER_ID
LEFT JOIN CUSTOMER_FEEDBACK cf ON c.CUSTOMER_ID = cf.CUSTOMER_ID
WHERE c.IS_ACTIVE = TRUE
GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, c.CUSTOMER_SEGMENT, c.LIFETIME_VALUE;

-- Sales Forecasting with AI Insights
CREATE OR REPLACE VIEW AI_SALES_FORECAST AS
SELECT 
    DATE_TRUNC('MONTH', SALE_DATE) as month,
    REGION,
    CATEGORY,
    SUM(TOTAL_AMOUNT) as actual_revenue,
    COUNT(*) as transaction_count,
    -- AI-generated insights
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-8b'::VARCHAR,
        CONCAT(
            'Analyze this sales pattern and provide a brief forecast insight: ',
            'Month: ', DATE_TRUNC('MONTH', SALE_DATE), ', ',
            'Region: ', REGION, ', ',
            'Category: ', CATEGORY, ', ',
            'Revenue: $', SUM(TOTAL_AMOUNT), ', ',
            'Transactions: ', COUNT(*)
        )::VARCHAR
    ) as ai_forecast_insight
FROM SALES_DATA
WHERE SALE_DATE >= DATEADD(month, -6, CURRENT_DATE())
GROUP BY DATE_TRUNC('MONTH', SALE_DATE), REGION, CATEGORY
ORDER BY month DESC, actual_revenue DESC;

-- ========================================
-- 7. CORTEX ANALYST SEMANTIC MODEL
-- ========================================

-- Create a semantic model for natural language queries
CREATE OR REPLACE VIEW BUSINESS_SEMANTIC_MODEL AS
SELECT 
    -- Time dimensions
    sd.SALE_DATE as "Sale Date",
    EXTRACT(YEAR FROM sd.SALE_DATE) as "Year",
    EXTRACT(MONTH FROM sd.SALE_DATE) as "Month", 
    EXTRACT(QUARTER FROM sd.SALE_DATE) as "Quarter",
    MONTHNAME(sd.SALE_DATE) as "Month Name",
    
    -- Product dimensions
    sd.PRODUCT_NAME as "Product",
    sd.CATEGORY as "Category",
    p.BRAND as "Brand",
    p.SUBCATEGORY as "Subcategory",
    
    -- Customer dimensions
    c.CUSTOMER_SEGMENT as "Customer Segment",
    sd.REGION as "Region",
    sd.SALES_REP as "Sales Representative",
    
    -- Measures
    sd.QUANTITY as "Quantity Sold",
    sd.UNIT_PRICE as "Unit Price",
    sd.TOTAL_AMOUNT as "Revenue",
    sd.PROFIT_AMOUNT as "Profit",
    sd.PROFIT_MARGIN as "Profit Margin %",
    
    -- Customer metrics
    c.LIFETIME_VALUE as "Customer Lifetime Value",
    
    -- Product metrics
    p.INVENTORY_COUNT as "Current Inventory",
    p.PRICE as "List Price"
    
FROM SALES_DATA sd
LEFT JOIN CUSTOMERS c ON sd.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN PRODUCTS p ON sd.PRODUCT_ID = p.PRODUCT_ID;

-- ========================================
-- 8. AI ANOMALY DETECTION
-- ========================================

-- Create view for anomaly detection in sales
CREATE OR REPLACE VIEW SALES_ANOMALY_DETECTION AS
WITH daily_stats AS (
    SELECT 
        SALE_DATE,
        SUM(TOTAL_AMOUNT) as daily_revenue,
        COUNT(*) as daily_transactions,
        AVG(TOTAL_AMOUNT) as avg_transaction_value
    FROM SALES_DATA
    GROUP BY SALE_DATE
),
stats_with_moving_avg AS (
    SELECT *,
        AVG(daily_revenue) OVER (ORDER BY SALE_DATE ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) as moving_avg_revenue,
        STDDEV(daily_revenue) OVER (ORDER BY SALE_DATE ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) as moving_stddev_revenue
    FROM daily_stats
)
SELECT 
    SALE_DATE,
    daily_revenue,
    daily_transactions,
    avg_transaction_value,
    moving_avg_revenue,
    CASE 
        WHEN ABS(daily_revenue - moving_avg_revenue) > 2 * moving_stddev_revenue 
        THEN 'ANOMALY_DETECTED'
        ELSE 'NORMAL'
    END as anomaly_flag,
    -- AI explanation of anomaly
    CASE 
        WHEN ABS(daily_revenue - moving_avg_revenue) > 2 * moving_stddev_revenue 
        THEN SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b'::VARCHAR,
            CONCAT(
                'Explain this sales anomaly: Daily revenue was $', 
                ROUND(daily_revenue, 2), 
                ' vs 7-day average of $', 
                ROUND(moving_avg_revenue, 2),
                '. Transactions: ', daily_transactions
            )::VARCHAR
        )
        ELSE NULL
    END as ai_anomaly_explanation
FROM stats_with_moving_avg
WHERE moving_avg_revenue IS NOT NULL
ORDER BY SALE_DATE DESC;

-- ========================================
-- 9. STORED PROCEDURES FOR AI OPERATIONS
-- ========================================

-- Procedure to analyze customer sentiment
CREATE OR REPLACE PROCEDURE ANALYZE_CUSTOMER_SENTIMENT(PRODUCT_ID_PARAM VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    sentiment_summary VARCHAR;
BEGIN
    SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
        CONCAT(
            'Customer sentiment analysis for product ', :PRODUCT_ID_PARAM, ': ',
            'Average sentiment score: ', AVG(SNOWFLAKE.CORTEX.SENTIMENT(REVIEW_TEXT::VARCHAR))::VARCHAR, ', ',
            'Total reviews: ', COUNT(*)::VARCHAR, ', ',
            'Positive reviews: ', COUNT(CASE WHEN SNOWFLAKE.CORTEX.SENTIMENT(REVIEW_TEXT::VARCHAR) > 0.1 THEN 1 END)::VARCHAR, ', ',
            'Negative reviews: ', COUNT(CASE WHEN SNOWFLAKE.CORTEX.SENTIMENT(REVIEW_TEXT::VARCHAR) < -0.1 THEN 1 END)::VARCHAR
        )::VARCHAR
    ) INTO sentiment_summary
    FROM CUSTOMER_FEEDBACK
    WHERE PRODUCT_ID = :PRODUCT_ID_PARAM;
    
    RETURN sentiment_summary;
END;
$$;

-- Procedure for AI-powered recommendations
CREATE OR REPLACE PROCEDURE GET_AI_RECOMMENDATIONS(CUSTOMER_ID_PARAM INTEGER)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    recommendation VARCHAR;
BEGIN
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-8b'::VARCHAR,
        CONCAT(
            'Based on this customer purchase history, recommend products: ',
            'Customer Segment: ', c.CUSTOMER_SEGMENT, ', ',
            'Past Purchases: ', LISTAGG(DISTINCT sd.PRODUCT_NAME, ', '), ', ',
            'Preferred Categories: ', LISTAGG(DISTINCT sd.CATEGORY, ', '), ', ',
            'Average Order Value: $', AVG(sd.TOTAL_AMOUNT)::VARCHAR
        )::VARCHAR
    ) INTO recommendation
    FROM CUSTOMERS c
    LEFT JOIN SALES_DATA sd ON c.CUSTOMER_ID = sd.CUSTOMER_ID
    WHERE c.CUSTOMER_ID = :CUSTOMER_ID_PARAM
    GROUP BY c.CUSTOMER_SEGMENT;
    
    RETURN recommendation;
END;
$$;

-- ========================================
-- 10. VERIFICATION AND SAMPLE QUERIES
-- ========================================

-- Test Cortex AI functions
SELECT 'Testing Cortex AI Functions' as status;

-- Sample sentiment analysis
SELECT 
    p.PRODUCT_NAME,
    cf.REVIEW_TEXT,
    SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) as sentiment_score,
    SNOWFLAKE.CORTEX.SUMMARIZE(cf.REVIEW_TEXT::VARCHAR) as summary
FROM CUSTOMER_FEEDBACK cf
JOIN PRODUCTS p ON cf.PRODUCT_ID = p.PRODUCT_ID
LIMIT 3;

-- Sample AI insights
SELECT * FROM PRODUCT_AI_INSIGHTS LIMIT 5;

-- Sample customer intelligence
SELECT * FROM CUSTOMER_AI_INTELLIGENCE LIMIT 5;

-- Sample anomaly detection
SELECT * FROM SALES_ANOMALY_DETECTION 
WHERE anomaly_flag = 'ANOMALY_DETECTED' 
LIMIT 3;

-- ========================================
-- SCRIPT COMPLETE!
-- ========================================
-- Your Cortex AI setup is complete!
-- 
-- Available AI Features:
-- 1. Sentiment Analysis on Customer Reviews
-- 2. AI-Powered Product Insights
-- 3. Customer Intelligence with AI Profiles
-- 4. Sales Anomaly Detection with AI Explanations
-- 5. Natural Language Business Semantic Model
-- 6. AI Agent Conversation Tracking
-- 7. Predictive Analytics Views
-- 8. Stored Procedures for AI Operations
-- 
-- Next: Use cortex_ai_integration.py to connect these features to Streamlit
-- ======================================== 