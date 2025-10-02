-- Comcast Promotion Reconciliation Demo - Data Setup
-- This script creates synthetic data representing Comcast services and promotions

-- Create database and schema
CREATE DATABASE IF NOT EXISTS COMCAST_DEMO;
USE DATABASE COMCAST_DEMO;
CREATE SCHEMA IF NOT EXISTS RECONCILIATION;
USE SCHEMA RECONCILIATION;

-- Create product catalog table
CREATE OR REPLACE TABLE PRODUCTS (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100),
    product_category VARCHAR(50),
    base_price DECIMAL(10,2),
    service_type VARCHAR(30)
);

-- Insert Comcast products
INSERT INTO PRODUCTS VALUES
('XFIN-INT-1G', 'Xfinity Internet 1 Gig', 'Internet', 89.99, 'Residential'),
('XFIN-INT-200', 'Xfinity Internet 200 Mbps', 'Internet', 54.99, 'Residential'),
('XFIN-TV-ULT', 'Xfinity TV Ultimate', 'Television', 79.99, 'Residential'),
('XFIN-TV-CHO', 'Xfinity TV Choice', 'Television', 49.99, 'Residential'),
('XFIN-MOB-UNL', 'Xfinity Mobile Unlimited', 'Mobile', 45.00, 'Mobile'),
('XFIN-MOB-BYG', 'Xfinity Mobile By the Gig', 'Mobile', 15.00, 'Mobile'),
('XFIN-HOME-SEC', 'Xfinity Home Security', 'Security', 39.99, 'Residential'),
('XFIN-BUS-INT', 'Business Internet Pro', 'Internet', 149.99, 'Business'),
('XFIN-BUS-VOICE', 'Business Voice', 'Voice', 29.99, 'Business'),
('XFIN-STREAM', 'Xfinity Stream', 'Streaming', 5.99, 'Residential');

-- Create promotion types table
CREATE OR REPLACE TABLE PROMOTION_TYPES (
    promo_code VARCHAR(20) PRIMARY KEY,
    promo_name VARCHAR(100),
    discount_type VARCHAR(20), -- 'PERCENTAGE', 'FIXED_AMOUNT', 'FREE_MONTHS'
    discount_value DECIMAL(10,2),
    duration_months INTEGER,
    applicable_products VARCHAR(500)
);

-- Insert promotion types
INSERT INTO PROMOTION_TYPES VALUES
('NEW-CUST-50', 'New Customer 50% Off', 'PERCENTAGE', 50.00, 12, 'XFIN-INT-1G,XFIN-INT-200'),
('TRIPLE-PLAY', 'Triple Play Bundle Discount', 'FIXED_AMOUNT', 30.00, 24, 'XFIN-INT-1G,XFIN-TV-ULT,XFIN-MOB-UNL'),
('LOYAL-DISC', 'Loyalty Discount', 'PERCENTAGE', 15.00, 6, 'ALL'),
('FIRST-RESP', 'First Responder Discount', 'PERCENTAGE', 25.00, 999, 'ALL'),
('STUDENT-20', 'Student Discount', 'PERCENTAGE', 20.00, 9, 'XFIN-INT-200,XFIN-STREAM'),
('MOBILE-FREE', 'Free Mobile for 3 Months', 'FREE_MONTHS', 3.00, 3, 'XFIN-MOB-UNL,XFIN-MOB-BYG'),
('BUS-STARTER', 'Business Starter Package', 'FIXED_AMOUNT', 75.00, 12, 'XFIN-BUS-INT,XFIN-BUS-VOICE'),
('STREAM-FREE', 'Free Streaming Trial', 'FREE_MONTHS', 6.00, 6, 'XFIN-STREAM'),
('SECURITY-50', 'Home Security 50% Off', 'PERCENTAGE', 50.00, 6, 'XFIN-HOME-SEC'),
('REFER-FRIEND', 'Refer a Friend Bonus', 'FIXED_AMOUNT', 100.00, 1, 'ALL');

-- Create order system data (source of truth for what was ordered)
CREATE OR REPLACE TABLE ORDER_SYSTEM_DATA (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(15),
    order_date DATE,
    product_id VARCHAR(20),
    promo_code VARCHAR(20),
    base_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    final_amount DECIMAL(10,2),
    order_status VARCHAR(20)
);

-- Create billing system data (what customers are actually charged)
CREATE OR REPLACE TABLE BILLING_SYSTEM_DATA (
    billing_id VARCHAR(25) PRIMARY KEY,
    customer_id VARCHAR(15),
    billing_date DATE,
    product_id VARCHAR(20),
    promo_code VARCHAR(20),
    base_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    final_amount DECIMAL(10,2),
    billing_cycle VARCHAR(10)
);

-- Generate synthetic order data
INSERT INTO ORDER_SYSTEM_DATA
SELECT 
    'ORD-' || LPAD(seq4(), 8, '0') as order_id,
    'CUST-' || LPAD(UNIFORM(100000, 999999, random()), 6, '0') as customer_id,
    DATEADD(day, -UNIFORM(1, 90, random()), CURRENT_DATE()) as order_date,
    p.product_id,
    CASE 
        WHEN UNIFORM(1, 100, random()) <= 70 THEN 
            (SELECT promo_code FROM PROMOTION_TYPES ORDER BY RANDOM() LIMIT 1)
        ELSE NULL 
    END as promo_code,
    p.base_price as base_amount,
    CASE 
        WHEN UNIFORM(1, 100, random()) <= 70 THEN
            ROUND(p.base_price * UNIFORM(10, 50, random()) / 100, 2)
        ELSE 0
    END as discount_amount,
    0 as final_amount,  -- Will calculate this
    'ACTIVE' as order_status
FROM PRODUCTS p
CROSS JOIN (SELECT seq4() FROM TABLE(generator(rowcount => 1000))) t
WHERE seq4() <= 1000;

-- Update final amounts in order system
UPDATE ORDER_SYSTEM_DATA 
SET final_amount = base_amount - discount_amount;

-- Generate billing system data with intentional discrepancies
INSERT INTO BILLING_SYSTEM_DATA
SELECT 
    'BILL-' || order_id as billing_id,
    customer_id,
    DATEADD(day, UNIFORM(1, 15, random()), order_date) as billing_date,
    product_id,
    promo_code,
    base_amount,
    -- Introduce 15% error rate in discount amounts
    CASE 
        WHEN UNIFORM(1, 100, random()) <= 85 THEN discount_amount
        ELSE ROUND(discount_amount * UNIFORM(80, 120, random()) / 100, 2)
    END as discount_amount,
    0 as final_amount,  -- Will calculate this
    'MONTHLY' as billing_cycle
FROM ORDER_SYSTEM_DATA
WHERE UNIFORM(1, 100, random()) <= 95;  -- 5% missing billing records

-- Update final amounts in billing system
UPDATE BILLING_SYSTEM_DATA 
SET final_amount = base_amount - discount_amount;

-- Create reconciliation view
CREATE OR REPLACE VIEW PROMOTION_RECONCILIATION AS
SELECT 
    COALESCE(o.order_id, 'MISSING-' || b.billing_id) as record_id,
    COALESCE(o.customer_id, b.customer_id) as customer_id,
    COALESCE(o.order_date, b.billing_date) as transaction_date,
    COALESCE(o.product_id, b.product_id) as product_id,
    p.product_name,
    p.product_category,
    COALESCE(o.promo_code, b.promo_code) as promo_code,
    pt.promo_name,
    
    -- Order system amounts
    o.base_amount as order_base_amount,
    o.discount_amount as order_discount_amount,
    o.final_amount as order_final_amount,
    
    -- Billing system amounts  
    b.base_amount as billing_base_amount,
    b.discount_amount as billing_discount_amount,
    b.final_amount as billing_final_amount,
    
    -- Variance calculations
    COALESCE(o.discount_amount, 0) - COALESCE(b.discount_amount, 0) as discount_variance,
    COALESCE(o.final_amount, 0) - COALESCE(b.final_amount, 0) as final_amount_variance,
    
    -- Reconciliation status
    CASE 
        WHEN o.order_id IS NULL THEN 'BILLING_ONLY'
        WHEN b.billing_id IS NULL THEN 'ORDER_ONLY'
        WHEN ABS(COALESCE(o.discount_amount, 0) - COALESCE(b.discount_amount, 0)) > 0.01 THEN 'DISCOUNT_MISMATCH'
        WHEN ABS(COALESCE(o.final_amount, 0) - COALESCE(b.final_amount, 0)) > 0.01 THEN 'AMOUNT_MISMATCH'
        ELSE 'MATCHED'
    END as reconciliation_status,
    
    -- Risk scoring
    CASE 
        WHEN o.order_id IS NULL OR b.billing_id IS NULL THEN 'HIGH'
        WHEN ABS(COALESCE(o.discount_amount, 0) - COALESCE(b.discount_amount, 0)) > 20 THEN 'HIGH'
        WHEN ABS(COALESCE(o.discount_amount, 0) - COALESCE(b.discount_amount, 0)) > 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level
    
FROM ORDER_SYSTEM_DATA o
FULL OUTER JOIN BILLING_SYSTEM_DATA b 
    ON o.order_id = REPLACE(b.billing_id, 'BILL-', '')
LEFT JOIN PRODUCTS p 
    ON COALESCE(o.product_id, b.product_id) = p.product_id
LEFT JOIN PROMOTION_TYPES pt 
    ON COALESCE(o.promo_code, b.promo_code) = pt.promo_code;

-- Create summary statistics view
CREATE OR REPLACE VIEW RECONCILIATION_SUMMARY AS
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN reconciliation_status = 'MATCHED' THEN 1 ELSE 0 END) as matched_records,
    SUM(CASE WHEN reconciliation_status != 'MATCHED' THEN 1 ELSE 0 END) as exception_records,
    ROUND(SUM(CASE WHEN reconciliation_status = 'MATCHED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as match_rate_pct,
    SUM(ABS(discount_variance)) as total_discount_variance,
    SUM(ABS(final_amount_variance)) as total_amount_variance,
    COUNT(CASE WHEN risk_level = 'HIGH' THEN 1 END) as high_risk_count,
    COUNT(CASE WHEN risk_level = 'MEDIUM' THEN 1 END) as medium_risk_count,
    COUNT(CASE WHEN risk_level = 'LOW' THEN 1 END) as low_risk_count
FROM PROMOTION_RECONCILIATION;

-- Grant permissions for Streamlit app
GRANT USAGE ON DATABASE COMCAST_DEMO TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA COMCAST_DEMO.RECONCILIATION TO ROLE ACCOUNTADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA COMCAST_DEMO.RECONCILIATION TO ROLE ACCOUNTADMIN;
GRANT SELECT ON ALL VIEWS IN SCHEMA COMCAST_DEMO.RECONCILIATION TO ROLE ACCOUNTADMIN; 