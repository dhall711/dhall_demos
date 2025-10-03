-- ============================================================================
-- Comcast ISCO - Supply Chain Analytics Data Setup
-- Database and Schema Creation with Synthetic Data Generation
-- ============================================================================

-- Database and Schema Creation
CREATE DATABASE IF NOT EXISTS ISCO_ANALYTICS;
USE DATABASE ISCO_ANALYTICS;

CREATE SCHEMA IF NOT EXISTS PROD;
USE SCHEMA PROD;

-- ============================================================================
-- 1. SUPPLIER_PROFILES Table
-- ============================================================================

CREATE OR REPLACE TABLE SUPPLIER_PROFILES (
    SUPPLIER_ID VARCHAR(20) NOT NULL,
    SUPPLIER_NAME VARCHAR(100) NOT NULL,
    SUPPLIER_TYPE VARCHAR(50) NOT NULL,
    SUPPLIER_CATEGORY VARCHAR(100) NOT NULL,  -- Enhanced per guidelines
    GEOGRAPHIC_REGION VARCHAR(50) NOT NULL,
    TIER_LEVEL VARCHAR(10) NOT NULL,
    CONTRACT_STATUS VARCHAR(30) NOT NULL,
    IS_STRATEGIC_SUPPLIER BOOLEAN DEFAULT FALSE,  -- Boolean field per guidelines
    IS_ACTIVE BOOLEAN DEFAULT TRUE,  -- Boolean field per guidelines
    ANNUAL_SPEND_MILLIONS DECIMAL(10,2),
    SUPPLIER_SCORE DECIMAL(5,2),  -- Compliant with DECIMAL(4,2) minimum
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),  -- Proper for events per guidelines
    UPDATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert Supplier Profiles Data
INSERT INTO SUPPLIER_PROFILES VALUES
-- Tier 1 OEM Suppliers (High-value strategic partners)
('SUP_001', 'Arris International', 'OEM', 'Cable Modems & DOCSIS Infrastructure', 'North America', 'Tier 1', 'Active', TRUE, TRUE, 285.5, 87.3, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_002', 'Technicolor Connected Home', 'OEM', 'Set-Top Boxes & Streaming Devices', 'Europe', 'Tier 1', 'Active', TRUE, TRUE, 195.2, 84.7, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_003', 'Cisco Systems', 'OEM', 'Network Equipment & Routers', 'North America', 'Tier 1', 'Active', TRUE, TRUE, 425.8, 91.2, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_004', 'Motorola Solutions', 'OEM', 'Cable Infrastructure & Amplifiers', 'North America', 'Tier 1', 'Active', TRUE, TRUE, 312.6, 88.9, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_005', 'Nokia Corporation', 'OEM', 'Fiber Optic Equipment & PON Systems', 'Europe', 'Tier 1', 'Active', TRUE, TRUE, 278.4, 86.5, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Tier 2 Component Suppliers (Mid-tier specialized suppliers)
('SUP_006', 'Amphenol Corporation', 'Component', 'Connectors & High-Performance Cables', 'North America', 'Tier 2', 'Active', FALSE, TRUE, 125.3, 82.1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_007', 'CommScope Technologies', 'Component', 'Infrastructure Hardware & Broadband', 'North America', 'Tier 2', 'Active', FALSE, TRUE, 98.7, 79.8, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_008', 'Corning Incorporated', 'Component', 'Fiber Optic Cables & Glass Technology', 'North America', 'Tier 2', 'Active', TRUE, TRUE, 167.9, 85.4, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_009', 'Hubbell Incorporated', 'Component', 'Power Equipment & Distribution', 'North America', 'Tier 2', 'Active', FALSE, TRUE, 89.4, 78.6, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Tier 3 Services & Support (Service providers and logistics partners)
('SUP_010', 'FedEx Supply Chain', 'Logistics', 'Transportation Services & Last Mile', 'North America', 'Tier 3', 'Active', TRUE, TRUE, 145.6, 83.2, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_011', 'UPS Supply Chain Solutions', 'Logistics', 'Warehousing & Distribution Networks', 'North America', 'Tier 3', 'Active', TRUE, TRUE, 132.8, 81.9, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_012', 'DHL Supply Chain', 'Logistics', 'Reverse Logistics & Refurbishment', 'Global', 'Tier 3', 'Active', TRUE, TRUE, 78.3, 80.4, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_013', 'Jabil Circuit', 'Manufacturing', 'Contract Manufacturing & Electronics', 'Asia Pacific', 'Tier 2', 'Active', FALSE, TRUE, 156.7, 84.1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_014', 'Flex (Flextronics)', 'Manufacturing', 'Electronics Manufacturing Services', 'Asia Pacific', 'Tier 2', 'Active', FALSE, TRUE, 203.5, 86.8, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Regional & Specialty Suppliers
('SUP_015', 'Optical Cable Corporation', 'Component', 'Specialty Cables & Custom Solutions', 'North America', 'Tier 2', 'Active', FALSE, TRUE, 45.9, 77.3, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_016', 'Preformed Line Products', 'Component', 'Hardware Accessories & Installation', 'North America', 'Tier 3', 'Active', FALSE, TRUE, 28.7, 75.8, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_017', 'C2G (Cables To Go)', 'Component', 'Consumer Cables & Connectivity', 'North America', 'Tier 3', 'Active', FALSE, TRUE, 35.2, 76.9, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Edge cases for testing (Enhanced per guidelines)
('SUP_018', 'Emerging Tech Solutions', 'Startup', 'IoT Devices & Smart Home Technology', 'North America', 'Tier 3', 'Pilot', FALSE, TRUE, 2.1, 65.5, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_019', 'Global Supply Partners', 'Distributor', 'Multi-Category Supply Distribution', 'Global', 'Tier 2', 'Under Review', FALSE, FALSE, NULL, 72.4, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_020', 'Regional Electronics Co', 'Regional', 'Local Components & Regional Support', 'North America', 'Tier 3', 'Active', FALSE, TRUE, 12.8, 68.7, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Additional edge cases per data quality guidelines
('SUP_021', 'Bankruptcy Test Corp', 'Component', 'Testing Supplier Bankruptcy Scenarios', 'North America', 'Tier 3', 'Terminated', FALSE, FALSE, 0.0, 0.0, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('SUP_022', 'Perfect Performance LLC', 'OEM', 'Testing Perfect Performance Scenarios', 'North America', 'Tier 1', 'Active', TRUE, TRUE, 150.0, 100.0, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- ============================================================================
-- 2. PRODUCT_CATALOG Table
-- Moved to standalone script: comcast_isco_product_catalog.sql
-- ============================================================================

-- ============================================================================
-- 3. INVENTORY_FACT Table (Main Inventory Management Table)
-- ============================================================================

CREATE OR REPLACE TABLE INVENTORY_FACT (
    INVENTORY_ID VARCHAR(50) NOT NULL,
    PRODUCT_SKU VARCHAR(30) NOT NULL,
    WAREHOUSE_LOCATION VARCHAR(50) NOT NULL,
    INVENTORY_QUARTER VARCHAR(2) NOT NULL,
    INVENTORY_YEAR INTEGER NOT NULL,
    PRODUCT_CATEGORY VARCHAR(30) NOT NULL,
    PRODUCT_TYPE VARCHAR(50) NOT NULL,
    STORAGE_TYPE VARCHAR(20) NOT NULL,
    UNITS_ON_HAND INTEGER NOT NULL,
    INVENTORY_VALUE_MILLIONS DECIMAL(12,2) NOT NULL,
    UNITS_SHIPPED INTEGER NOT NULL,
    INVENTORY_TURNOVER_RATIO DECIMAL(6,2),
    STOCKOUT_INCIDENTS INTEGER DEFAULT 0,
    EXCESS_INVENTORY_VALUE DECIMAL(10,2) DEFAULT 0.00,
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Generate Inventory Data for 5 quarters (Q3 2023 - Q3 2024)
INSERT INTO INVENTORY_FACT 
SELECT 
    'INV_' || WAREHOUSE_LOCATION || '_' || PRODUCT_SKU || '_' || INVENTORY_YEAR || '_' || INVENTORY_QUARTER || '_' || ROW_NUMBER() OVER (ORDER BY WAREHOUSE_LOCATION, PRODUCT_SKU) as INVENTORY_ID,
    PRODUCT_SKU,
    WAREHOUSE_LOCATION,
    INVENTORY_QUARTER,
    INVENTORY_YEAR,
    PRODUCT_CATEGORY,
    PRODUCT_TYPE,
    STORAGE_TYPE,
    UNITS_ON_HAND,
    INVENTORY_VALUE_MILLIONS,
    UNITS_SHIPPED,
    INVENTORY_TURNOVER_RATIO,
    STOCKOUT_INCIDENTS,
    EXCESS_INVENTORY_VALUE,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as INVENTORY_QUARTER, 2023 as INVENTORY_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    warehouses AS (
        SELECT 'Philadelphia DC' as WAREHOUSE_LOCATION, 'Northeast' as REGION
        UNION ALL SELECT 'Atlanta DC', 'Southeast'
        UNION ALL SELECT 'Denver DC', 'Central'
        UNION ALL SELECT 'Los Angeles DC', 'West'
        UNION ALL SELECT 'Chicago DC', 'Midwest'
        UNION ALL SELECT 'Phoenix DC', 'Southwest'
        UNION ALL SELECT 'Tampa Regional', 'Southeast'
        UNION ALL SELECT 'Portland Regional', 'Northwest'
    ),
    products AS (
        SELECT 'SKU_CM001' as PRODUCT_SKU, 'Cable Modems' as PRODUCT_CATEGORY, 'DOCSIS 3.1 Modem' as PRODUCT_TYPE, 'Regular' as STORAGE_TYPE
        UNION ALL SELECT 'SKU_CM002', 'Cable Modems', 'DOCSIS 3.0 Modem', 'Regular'
        UNION ALL SELECT 'SKU_STB001', 'Set-Top Boxes', 'X1 DVR Box', 'Regular'
        UNION ALL SELECT 'SKU_STB002', 'Set-Top Boxes', 'Xi6 Streaming Box', 'Regular'
        UNION ALL SELECT 'SKU_STB003', 'Set-Top Boxes', 'Flex Streaming Device', 'Regular'
        UNION ALL SELECT 'SKU_RTR001', 'Routers', 'xFi Gateway', 'Regular'
        UNION ALL SELECT 'SKU_RTR002', 'Routers', 'Advanced Gateway', 'Regular'
        UNION ALL SELECT 'SKU_CAB001', 'Cables', 'Coaxial Cable 25ft', 'Regular'
        UNION ALL SELECT 'SKU_CAB002', 'Cables', 'HDMI Cable 6ft', 'Regular'
        UNION ALL SELECT 'SKU_CAB003', 'Cables', 'Ethernet Cable 10ft', 'Regular'
        UNION ALL SELECT 'SKU_PWR001', 'Power Equipment', 'Power Supply 12V', 'Regular'
        UNION ALL SELECT 'SKU_PWR002', 'Power Equipment', 'UPS Battery Backup', 'Regular'
        UNION ALL SELECT 'SKU_INST001', 'Installation Kits', 'Self-Install Kit Basic', 'Regular'
        UNION ALL SELECT 'SKU_INST002', 'Installation Kits', 'Professional Install Kit', 'Regular'
        UNION ALL SELECT 'SKU_FBER001', 'Fiber Equipment', 'Fiber Modem', 'Regular'
        UNION ALL SELECT 'SKU_ACCS001', 'Accessories', 'Remote Control XR15', 'Regular'
        UNION ALL SELECT 'SKU_ACCS002', 'Accessories', 'Wall Mount Kit', 'Regular'
        UNION ALL SELECT 'SKU_VOICE001', 'Voice Equipment', 'Voice Modem', 'Regular'
        UNION ALL SELECT 'SKU_SEC001', 'Security Equipment', 'Security Camera', 'Regular'
        UNION ALL SELECT 'SKU_SEC002', 'Security Equipment', 'Motion Sensor', 'Regular'
    ),
    base_inventory AS (
        SELECT 
            w.WAREHOUSE_LOCATION,
            w.REGION,
            p.PRODUCT_SKU,
            p.PRODUCT_CATEGORY,
            p.PRODUCT_TYPE,
            p.STORAGE_TYPE,
            q.INVENTORY_QUARTER,
            q.INVENTORY_YEAR,
            CASE p.PRODUCT_CATEGORY
                WHEN 'Cable Modems' THEN UNIFORM(15000, 45000, RANDOM())
                WHEN 'Set-Top Boxes' THEN UNIFORM(12000, 35000, RANDOM())
                WHEN 'Routers' THEN UNIFORM(8000, 25000, RANDOM())
                WHEN 'Cables' THEN UNIFORM(25000, 75000, RANDOM())
                WHEN 'Power Equipment' THEN UNIFORM(5000, 18000, RANDOM())
                WHEN 'Installation Kits' THEN UNIFORM(10000, 30000, RANDOM())
                WHEN 'Fiber Equipment' THEN UNIFORM(3000, 12000, RANDOM())
                WHEN 'Accessories' THEN UNIFORM(20000, 60000, RANDOM())
                WHEN 'Voice Equipment' THEN UNIFORM(4000, 15000, RANDOM())
                WHEN 'Security Equipment' THEN UNIFORM(2000, 8000, RANDOM())
                ELSE UNIFORM(5000, 20000, RANDOM())
            END as BASE_INVENTORY_UNITS,
            CASE p.PRODUCT_CATEGORY
                WHEN 'Cable Modems' THEN UNIFORM(85, 125, RANDOM())
                WHEN 'Set-Top Boxes' THEN UNIFORM(150, 250, RANDOM())
                WHEN 'Routers' THEN UNIFORM(120, 180, RANDOM())
                WHEN 'Cables' THEN UNIFORM(5, 25, RANDOM())
                WHEN 'Power Equipment' THEN UNIFORM(35, 85, RANDOM())
                WHEN 'Installation Kits' THEN UNIFORM(25, 45, RANDOM())
                WHEN 'Fiber Equipment' THEN UNIFORM(200, 350, RANDOM())
                WHEN 'Accessories' THEN UNIFORM(15, 35, RANDOM())
                WHEN 'Voice Equipment' THEN UNIFORM(95, 145, RANDOM())
                WHEN 'Security Equipment' THEN UNIFORM(75, 125, RANDOM())
                ELSE UNIFORM(50, 100, RANDOM())
            END as UNIT_VALUE
        FROM warehouses w
        CROSS JOIN products p
        CROSS JOIN quarters q
    )
    SELECT 
        PRODUCT_SKU,
        WAREHOUSE_LOCATION,
        INVENTORY_QUARTER,
        INVENTORY_YEAR,
        PRODUCT_CATEGORY,
        PRODUCT_TYPE,
        STORAGE_TYPE,
        ROUND(BASE_INVENTORY_UNITS * 
            CASE INVENTORY_QUARTER
                WHEN 'Q4' THEN 1.25  -- Holiday inventory build-up
                WHEN 'Q1' THEN 0.75  -- Post-holiday reduction
                WHEN 'Q2' THEN 1.10  -- Spring installation season
                WHEN 'Q3' THEN 0.90  -- Summer maintenance
                ELSE 1.0
            END * 
            CASE INVENTORY_YEAR
                WHEN 2024 THEN 1.12  -- Growth in 2024
                ELSE 1.0
            END, 0) as UNITS_ON_HAND,
        ROUND(BASE_INVENTORY_UNITS * UNIT_VALUE * 
            CASE INVENTORY_QUARTER
                WHEN 'Q4' THEN 1.25
                WHEN 'Q1' THEN 0.75
                WHEN 'Q2' THEN 1.10
                WHEN 'Q3' THEN 0.90
                ELSE 1.0
            END * 
            CASE INVENTORY_YEAR
                WHEN 2024 THEN 1.12
                ELSE 1.0
            END / 1000000, 2) as INVENTORY_VALUE_MILLIONS,
        ROUND(BASE_INVENTORY_UNITS * UNIFORM(0.15, 0.45, RANDOM()), 0) as UNITS_SHIPPED,
        ROUND(UNIFORM(2.5, 8.9, RANDOM()), 2) as INVENTORY_TURNOVER_RATIO,
        CASE 
            WHEN UNIFORM(0, 1, RANDOM()) < 0.08 THEN ROUND(UNIFORM(1, 5, RANDOM()), 0)
            ELSE 0
        END as STOCKOUT_INCIDENTS,
        CASE 
            WHEN UNIFORM(0, 1, RANDOM()) < 0.12 THEN ROUND(BASE_INVENTORY_UNITS * UNIT_VALUE * 0.05 / 1000000, 2)
            ELSE 0.00
        END as EXCESS_INVENTORY_VALUE
    FROM base_inventory
);

-- ============================================================================
-- 3. LOGISTICS_METRICS Table
-- ============================================================================

CREATE OR REPLACE TABLE LOGISTICS_METRICS (
    LOGISTICS_ID VARCHAR(50) NOT NULL,
    SHIPMENT_QUARTER VARCHAR(2) NOT NULL,
    SHIPMENT_YEAR INTEGER NOT NULL,
    TRANSPORT_MODE VARCHAR(50) NOT NULL,  -- Enhanced per guidelines
    SERVICE_REGION VARCHAR(50) NOT NULL,
    SHIPMENT_TYPE VARCHAR(20) NOT NULL,
    DELIVERY_PRIORITY VARCHAR(15) NOT NULL,
    TOTAL_SHIPMENTS INTEGER NOT NULL,
    SHIPPING_COST_MILLIONS DECIMAL(10,2) NOT NULL,
    ON_TIME_DELIVERY_RATE DECIMAL(5,2),
    AVERAGE_TRANSIT_DAYS DECIMAL(4,2),
    COST_PER_SHIPMENT DECIMAL(8,2),
    DAMAGE_INCIDENTS INTEGER DEFAULT 0,
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO LOGISTICS_METRICS 
SELECT 
    'LOG_' || TRANSPORT_MODE || '_' || SERVICE_REGION || '_' || SHIPMENT_YEAR || '_' || SHIPMENT_QUARTER || '_' || ROW_NUMBER() OVER (ORDER BY TRANSPORT_MODE, SERVICE_REGION) as LOGISTICS_ID,
    SHIPMENT_QUARTER,
    SHIPMENT_YEAR,
    TRANSPORT_MODE,
    SERVICE_REGION,
    SHIPMENT_TYPE,
    DELIVERY_PRIORITY,
    TOTAL_SHIPMENTS,
    SHIPPING_COST_MILLIONS,
    ON_TIME_DELIVERY_RATE,
    AVERAGE_TRANSIT_DAYS,
    COST_PER_SHIPMENT,
    DAMAGE_INCIDENTS,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as SHIPMENT_QUARTER, 2023 as SHIPMENT_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    transport_modes AS (
        SELECT 'Ground Standard' as TRANSPORT_MODE, 'Forward' as SHIPMENT_TYPE, 'Standard' as DELIVERY_PRIORITY
        UNION ALL SELECT 'Ground Express', 'Forward', 'Express'
        UNION ALL SELECT 'Air Express', 'Forward', 'Critical'
        UNION ALL SELECT 'LTL Freight', 'Forward', 'Standard'
        UNION ALL SELECT 'FTL Truck', 'Forward', 'Standard'
        UNION ALL SELECT 'Last Mile Delivery', 'Forward', 'Express'
        UNION ALL SELECT 'Ground Standard', 'Reverse', 'Standard'
        UNION ALL SELECT 'Ground Express', 'Reverse', 'Express'
        UNION ALL SELECT 'LTL Freight', 'Reverse', 'Standard'
        UNION ALL SELECT 'Regional Carrier', 'Forward', 'Standard'
        UNION ALL SELECT 'White Glove', 'Forward', 'Critical'
        UNION ALL SELECT 'Same Day', 'Forward', 'Critical'
    ),
    regions AS (
        SELECT 'Northeast' as SERVICE_REGION
        UNION ALL SELECT 'Southeast'
        UNION ALL SELECT 'Central'
        UNION ALL SELECT 'West'
        UNION ALL SELECT 'Midwest'
        UNION ALL SELECT 'Southwest'
        UNION ALL SELECT 'Northwest'
        UNION ALL SELECT 'Mid-Atlantic'
    ),
    logistics_data AS (
        SELECT 
            q.SHIPMENT_QUARTER,
            q.SHIPMENT_YEAR,
            t.TRANSPORT_MODE,
            r.SERVICE_REGION,
            t.SHIPMENT_TYPE,
            t.DELIVERY_PRIORITY,
            CASE t.TRANSPORT_MODE
                WHEN 'Ground Standard' THEN UNIFORM(8500, 15000, RANDOM())
                WHEN 'Ground Express' THEN UNIFORM(3500, 7500, RANDOM())
                WHEN 'Air Express' THEN UNIFORM(450, 1200, RANDOM())
                WHEN 'LTL Freight' THEN UNIFORM(2500, 5500, RANDOM())
                WHEN 'FTL Truck' THEN UNIFORM(850, 1800, RANDOM())
                WHEN 'Last Mile Delivery' THEN UNIFORM(5500, 12000, RANDOM())
                WHEN 'Regional Carrier' THEN UNIFORM(1200, 3500, RANDOM())
                WHEN 'White Glove' THEN UNIFORM(250, 650, RANDOM())
                WHEN 'Same Day' THEN UNIFORM(150, 450, RANDOM())
                ELSE UNIFORM(1000, 5000, RANDOM())
            END as BASE_SHIPMENTS,
            CASE t.TRANSPORT_MODE
                WHEN 'Ground Standard' THEN UNIFORM(25, 45, RANDOM())
                WHEN 'Ground Express' THEN UNIFORM(45, 75, RANDOM())
                WHEN 'Air Express' THEN UNIFORM(85, 135, RANDOM())
                WHEN 'LTL Freight' THEN UNIFORM(35, 65, RANDOM())
                WHEN 'FTL Truck' THEN UNIFORM(450, 750, RANDOM())
                WHEN 'Last Mile Delivery' THEN UNIFORM(35, 65, RANDOM())
                WHEN 'Regional Carrier' THEN UNIFORM(28, 48, RANDOM())
                WHEN 'White Glove' THEN UNIFORM(125, 225, RANDOM())
                WHEN 'Same Day' THEN UNIFORM(85, 155, RANDOM())
                ELSE UNIFORM(40, 80, RANDOM())
            END as BASE_COST_PER_SHIPMENT
        FROM quarters q
        CROSS JOIN transport_modes t
        CROSS JOIN regions r
    )
    SELECT 
        SHIPMENT_QUARTER,
        SHIPMENT_YEAR,
        TRANSPORT_MODE,
        SERVICE_REGION,
        SHIPMENT_TYPE,
        DELIVERY_PRIORITY,
        ROUND(BASE_SHIPMENTS * 
            CASE SHIPMENT_QUARTER
                WHEN 'Q4' THEN 1.35  -- Holiday shipping surge
                WHEN 'Q1' THEN 0.75  -- Post-holiday decline
                WHEN 'Q2' THEN 1.15  -- Spring installations
                WHEN 'Q3' THEN 0.95  -- Summer maintenance
                ELSE 1.0
            END * 
            CASE SHIPMENT_YEAR
                WHEN 2024 THEN 1.08  -- Growth in 2024
                ELSE 1.0
            END, 0) as TOTAL_SHIPMENTS,
        ROUND(BASE_SHIPMENTS * BASE_COST_PER_SHIPMENT * 
            CASE SHIPMENT_QUARTER
                WHEN 'Q4' THEN 1.35
                WHEN 'Q1' THEN 0.75
                WHEN 'Q2' THEN 1.15
                WHEN 'Q3' THEN 0.95
                ELSE 1.0
            END * 
            CASE SHIPMENT_YEAR
                WHEN 2024 THEN 1.08
                ELSE 1.0
            END / 1000000, 2) as SHIPPING_COST_MILLIONS,
        CASE TRANSPORT_MODE
            WHEN 'Ground Standard' THEN ROUND(UNIFORM(92.5, 96.8, RANDOM()), 2)
            WHEN 'Ground Express' THEN ROUND(UNIFORM(94.2, 97.5, RANDOM()), 2)
            WHEN 'Air Express' THEN ROUND(UNIFORM(96.8, 98.9, RANDOM()), 2)
            WHEN 'LTL Freight' THEN ROUND(UNIFORM(88.5, 93.2, RANDOM()), 2)
            WHEN 'FTL Truck' THEN ROUND(UNIFORM(94.5, 97.8, RANDOM()), 2)
            WHEN 'Last Mile Delivery' THEN ROUND(UNIFORM(89.2, 94.5, RANDOM()), 2)
            WHEN 'Regional Carrier' THEN ROUND(UNIFORM(86.8, 91.5, RANDOM()), 2)
            WHEN 'White Glove' THEN ROUND(UNIFORM(95.5, 98.2, RANDOM()), 2)
            WHEN 'Same Day' THEN ROUND(UNIFORM(97.2, 99.1, RANDOM()), 2)
            ELSE ROUND(UNIFORM(85.0, 95.0, RANDOM()), 2)
        END as ON_TIME_DELIVERY_RATE,
        CASE TRANSPORT_MODE
            WHEN 'Ground Standard' THEN ROUND(UNIFORM(3.5, 7.2, RANDOM()), 2)
            WHEN 'Ground Express' THEN ROUND(UNIFORM(1.8, 3.5, RANDOM()), 2)
            WHEN 'Air Express' THEN ROUND(UNIFORM(0.8, 1.5, RANDOM()), 2)
            WHEN 'LTL Freight' THEN ROUND(UNIFORM(4.5, 8.5, RANDOM()), 2)
            WHEN 'FTL Truck' THEN ROUND(UNIFORM(2.2, 4.8, RANDOM()), 2)
            WHEN 'Last Mile Delivery' THEN ROUND(UNIFORM(0.5, 1.2, RANDOM()), 2)
            WHEN 'Regional Carrier' THEN ROUND(UNIFORM(2.8, 5.5, RANDOM()), 2)
            WHEN 'White Glove' THEN ROUND(UNIFORM(0.8, 2.2, RANDOM()), 2)
            WHEN 'Same Day' THEN ROUND(UNIFORM(0.1, 0.5, RANDOM()), 2)
            ELSE ROUND(UNIFORM(2.0, 6.0, RANDOM()), 2)
        END as AVERAGE_TRANSIT_DAYS,
        ROUND(BASE_COST_PER_SHIPMENT, 2) as COST_PER_SHIPMENT,
        CASE 
            WHEN UNIFORM(0, 1, RANDOM()) < 0.03 THEN ROUND(BASE_SHIPMENTS * 0.002, 0)
            ELSE 0
        END as DAMAGE_INCIDENTS
    FROM logistics_data
);

-- ============================================================================
-- 4. DEMAND_FORECAST Table
-- ============================================================================

CREATE OR REPLACE TABLE DEMAND_FORECAST (
    FORECAST_ID VARCHAR(50) NOT NULL,
    PRODUCT_SKU VARCHAR(30) NOT NULL,
    FORECAST_QUARTER VARCHAR(2) NOT NULL,
    FORECAST_YEAR INTEGER NOT NULL,
    FORECAST_METHOD VARCHAR(100) NOT NULL,  -- Enhanced per guidelines
    MARKET_SEGMENT VARCHAR(30) NOT NULL,
    DEMAND_DRIVER VARCHAR(50) NOT NULL,
    FORECASTED_DEMAND_UNITS INTEGER NOT NULL,
    ACTUAL_DEMAND_UNITS INTEGER,
    FORECAST_ACCURACY_PERCENT DECIMAL(5,2),
    DEMAND_VARIANCE_PERCENT DECIMAL(6,2),
    SAFETY_STOCK_DAYS DECIMAL(4,1),
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO DEMAND_FORECAST 
SELECT 
    'FCST_' || PRODUCT_SKU || '_' || FORECAST_YEAR || '_' || FORECAST_QUARTER || '_' || ROW_NUMBER() OVER (ORDER BY PRODUCT_SKU) as FORECAST_ID,
    PRODUCT_SKU,
    FORECAST_QUARTER,
    FORECAST_YEAR,
    FORECAST_METHOD,
    MARKET_SEGMENT,
    DEMAND_DRIVER,
    FORECASTED_DEMAND_UNITS,
    ACTUAL_DEMAND_UNITS,
    FORECAST_ACCURACY_PERCENT,
    DEMAND_VARIANCE_PERCENT,
    SAFETY_STOCK_DAYS,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as FORECAST_QUARTER, 2023 as FORECAST_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    forecast_methods AS (
        SELECT 'Time Series ARIMA' as FORECAST_METHOD, 'Residential' as MARKET_SEGMENT, 'Seasonal Patterns' as DEMAND_DRIVER
        UNION ALL SELECT 'Machine Learning', 'Business', 'New Product Launch'
        UNION ALL SELECT 'Statistical Regression', 'Residential', 'Market Growth'
        UNION ALL SELECT 'Collaborative Planning', 'Business', 'Customer Demand'
        UNION ALL SELECT 'Moving Average', 'Residential', 'Historical Trends'
        UNION ALL SELECT 'Exponential Smoothing', 'SMB', 'Seasonal Patterns'
        UNION ALL SELECT 'Neural Networks', 'Enterprise', 'Technology Upgrade'
        UNION ALL SELECT 'Ensemble Methods', 'Residential', 'Economic Indicators'
    ),
    products AS (
        SELECT 'SKU_CM001' as PRODUCT_SKU, 'Cable Modems' as CATEGORY
        UNION ALL SELECT 'SKU_CM002', 'Cable Modems'
        UNION ALL SELECT 'SKU_STB001', 'Set-Top Boxes'
        UNION ALL SELECT 'SKU_STB002', 'Set-Top Boxes'
        UNION ALL SELECT 'SKU_STB003', 'Set-Top Boxes'
        UNION ALL SELECT 'SKU_RTR001', 'Routers'
        UNION ALL SELECT 'SKU_RTR002', 'Routers'
        UNION ALL SELECT 'SKU_CAB001', 'Cables'
        UNION ALL SELECT 'SKU_CAB002', 'Cables'
        UNION ALL SELECT 'SKU_INST001', 'Installation Kits'
        UNION ALL SELECT 'SKU_FBER001', 'Fiber Equipment'
        UNION ALL SELECT 'SKU_VOICE001', 'Voice Equipment'
    ),
    forecast_data AS (
        SELECT 
            p.PRODUCT_SKU,
            p.CATEGORY,
            q.FORECAST_QUARTER,
            q.FORECAST_YEAR,
            fm.FORECAST_METHOD,
            fm.MARKET_SEGMENT,
            fm.DEMAND_DRIVER,
            CASE p.CATEGORY
                WHEN 'Cable Modems' THEN UNIFORM(85000, 125000, RANDOM())
                WHEN 'Set-Top Boxes' THEN UNIFORM(65000, 95000, RANDOM())
                WHEN 'Routers' THEN UNIFORM(45000, 75000, RANDOM())
                WHEN 'Cables' THEN UNIFORM(150000, 250000, RANDOM())
                WHEN 'Installation Kits' THEN UNIFORM(55000, 85000, RANDOM())
                WHEN 'Fiber Equipment' THEN UNIFORM(25000, 45000, RANDOM())
                WHEN 'Voice Equipment' THEN UNIFORM(20000, 35000, RANDOM())
                ELSE UNIFORM(30000, 60000, RANDOM())
            END as BASE_FORECAST
        FROM products p
        CROSS JOIN quarters q
        CROSS JOIN forecast_methods fm
        WHERE NOT (p.CATEGORY = 'Voice Equipment' AND fm.MARKET_SEGMENT = 'Enterprise')
    )
    SELECT 
        PRODUCT_SKU,
        FORECAST_QUARTER,
        FORECAST_YEAR,
        FORECAST_METHOD,
        MARKET_SEGMENT,
        DEMAND_DRIVER,
        ROUND(BASE_FORECAST * 
            CASE FORECAST_QUARTER
                WHEN 'Q4' THEN 1.25  -- Holiday demand spike
                WHEN 'Q1' THEN 0.80  -- Post-holiday lull
                WHEN 'Q2' THEN 1.15  -- Spring installations
                WHEN 'Q3' THEN 0.95  -- Summer steady
                ELSE 1.0
            END * 
            CASE FORECAST_YEAR
                WHEN 2024 THEN 1.12  -- Growth trend
                ELSE 1.0
            END, 0) as FORECASTED_DEMAND_UNITS,
        CASE 
            WHEN FORECAST_YEAR = 2024 AND FORECAST_QUARTER = 'Q3' THEN NULL  -- Future data not available
            ELSE ROUND(BASE_FORECAST * 
                CASE FORECAST_QUARTER
                    WHEN 'Q4' THEN 1.25
                    WHEN 'Q1' THEN 0.80
                    WHEN 'Q2' THEN 1.15
                    WHEN 'Q3' THEN 0.95
                    ELSE 1.0
                END * 
                CASE FORECAST_YEAR
                    WHEN 2024 THEN 1.12
                    ELSE 1.0
                END * UNIFORM(0.85, 1.15, RANDOM()), 0)  -- Actual variance
        END as ACTUAL_DEMAND_UNITS,
        CASE 
            WHEN FORECAST_YEAR = 2024 AND FORECAST_QUARTER = 'Q3' THEN NULL
            ELSE ROUND(UNIFORM(75.5, 96.8, RANDOM()), 2)
        END as FORECAST_ACCURACY_PERCENT,
        CASE 
            WHEN FORECAST_YEAR = 2024 AND FORECAST_QUARTER = 'Q3' THEN NULL
            ELSE ROUND(UNIFORM(-25.5, 35.8, RANDOM()), 2)
        END as DEMAND_VARIANCE_PERCENT,
        ROUND(UNIFORM(7.5, 21.5, RANDOM()), 1) as SAFETY_STOCK_DAYS
    FROM forecast_data
);

-- ============================================================================
-- 5. VENDOR_SCORECARD Table
-- ============================================================================

CREATE OR REPLACE TABLE VENDOR_SCORECARD (
    SCORECARD_ID VARCHAR(50) NOT NULL,
    SUPPLIER_ID VARCHAR(20) NOT NULL,
    EVALUATION_QUARTER VARCHAR(2) NOT NULL,
    EVALUATION_YEAR INTEGER NOT NULL,
    PERFORMANCE_CATEGORY VARCHAR(30) NOT NULL,
    METRIC_TYPE VARCHAR(30) NOT NULL,
    QUALITY_SCORE DECIMAL(5,2),
    DELIVERY_PERFORMANCE_SCORE DECIMAL(5,2),
    COST_COMPETITIVENESS_SCORE DECIMAL(5,2),
    DEFECT_RATE_PERCENT DECIMAL(5,3),
    ON_TIME_DELIVERY_PERCENT DECIMAL(5,2),
    COST_SAVINGS_MILLIONS DECIMAL(8,2),
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO VENDOR_SCORECARD 
SELECT 
    'VSC_' || SUPPLIER_ID || '_' || EVALUATION_YEAR || '_' || EVALUATION_QUARTER || '_' || ROW_NUMBER() OVER (ORDER BY SUPPLIER_ID) as SCORECARD_ID,
    SUPPLIER_ID,
    EVALUATION_QUARTER,
    EVALUATION_YEAR,
    PERFORMANCE_CATEGORY,
    METRIC_TYPE,
    QUALITY_SCORE,
    DELIVERY_PERFORMANCE_SCORE,
    COST_COMPETITIVENESS_SCORE,
    DEFECT_RATE_PERCENT,
    ON_TIME_DELIVERY_PERCENT,
    COST_SAVINGS_MILLIONS,
    CURRENT_TIMESTAMP()
FROM (
    WITH quarters AS (
        SELECT 'Q3' as EVALUATION_QUARTER, 2023 as EVALUATION_YEAR
        UNION ALL SELECT 'Q4', 2023
        UNION ALL SELECT 'Q1', 2024
        UNION ALL SELECT 'Q2', 2024
        UNION ALL SELECT 'Q3', 2024
    ),
    performance_categories AS (
        SELECT 'Quality Management' as PERFORMANCE_CATEGORY, 'Defect Rate' as METRIC_TYPE
        UNION ALL SELECT 'Delivery Performance', 'On-Time Delivery'
        UNION ALL SELECT 'Cost Management', 'Cost Reduction'
        UNION ALL SELECT 'Innovation', 'New Product Development'
        UNION ALL SELECT 'Sustainability', 'Environmental Impact'
        UNION ALL SELECT 'Risk Management', 'Supply Continuity'
    ),
    scorecard_data AS (
        SELECT 
            sp.SUPPLIER_ID,
            sp.SUPPLIER_NAME,
            sp.TIER_LEVEL,
            sp.SUPPLIER_SCORE as BASE_SCORE,
            q.EVALUATION_QUARTER,
            q.EVALUATION_YEAR,
            pc.PERFORMANCE_CATEGORY,
            pc.METRIC_TYPE
        FROM SUPPLIER_PROFILES sp
        CROSS JOIN quarters q
        CROSS JOIN performance_categories pc
        WHERE sp.CONTRACT_STATUS = 'Active'
    )
    SELECT 
        SUPPLIER_ID,
        EVALUATION_QUARTER,
        EVALUATION_YEAR,
        PERFORMANCE_CATEGORY,
        METRIC_TYPE,
        ROUND(BASE_SCORE + UNIFORM(-5.0, 8.5, RANDOM()), 2) as QUALITY_SCORE,
        ROUND(BASE_SCORE + UNIFORM(-3.5, 6.8, RANDOM()), 2) as DELIVERY_PERFORMANCE_SCORE,
        ROUND(BASE_SCORE + UNIFORM(-4.2, 7.3, RANDOM()), 2) as COST_COMPETITIVENESS_SCORE,
        CASE TIER_LEVEL
            WHEN 'Tier 1' THEN ROUND(UNIFORM(0.05, 0.25, RANDOM()), 3)
            WHEN 'Tier 2' THEN ROUND(UNIFORM(0.15, 0.45, RANDOM()), 3)
            WHEN 'Tier 3' THEN ROUND(UNIFORM(0.25, 0.75, RANDOM()), 3)
            ELSE ROUND(UNIFORM(0.35, 1.25, RANDOM()), 3)
        END as DEFECT_RATE_PERCENT,
        CASE TIER_LEVEL
            WHEN 'Tier 1' THEN ROUND(UNIFORM(94.5, 98.2, RANDOM()), 2)
            WHEN 'Tier 2' THEN ROUND(UNIFORM(92.3, 96.8, RANDOM()), 2)
            WHEN 'Tier 3' THEN ROUND(UNIFORM(88.5, 94.2, RANDOM()), 2)
            ELSE ROUND(UNIFORM(85.2, 91.5, RANDOM()), 2)
        END as ON_TIME_DELIVERY_PERCENT,
        CASE PERFORMANCE_CATEGORY
            WHEN 'Cost Management' THEN ROUND(UNIFORM(0.5, 8.5, RANDOM()), 2)
            WHEN 'Innovation' THEN ROUND(UNIFORM(0.2, 3.5, RANDOM()), 2)
            ELSE ROUND(UNIFORM(0.1, 2.2, RANDOM()), 2)
        END as COST_SAVINGS_MILLIONS
    FROM scorecard_data
);

-- ============================================================================
-- EDGE CASE DATA INSERTION (Additional scenarios for robust testing)
-- ============================================================================

-- Insert extreme scenarios for testing
INSERT INTO INVENTORY_FACT VALUES
-- Stockout scenario (zero inventory)
('INV_EXTREME_001', 'SKU_STB001', 'Denver DC', 'Q1', 2024, 'Set-Top Boxes', 'X1 DVR Box', 'Regular', 0, 0.00, 15000, 0.00, 3, 0.00, CURRENT_TIMESTAMP()),
-- Excess inventory scenario
('INV_EXTREME_002', 'SKU_CAB001', 'Los Angeles DC', 'Q2', 2024, 'Cables', 'Coaxial Cable 25ft', 'Regular', 150000, 3.75, 8500, 1.2, 0, 1.25, CURRENT_TIMESTAMP()),
-- High-value inventory
('INV_EXTREME_003', 'SKU_FBER001', 'Philadelphia DC', 'Q3', 2024, 'Fiber Equipment', 'Fiber Modem', 'Regular', 5000, 1.75, 2800, 12.5, 0, 0.00, CURRENT_TIMESTAMP());

-- Insert logistics edge cases
INSERT INTO LOGISTICS_METRICS VALUES
-- Emergency shipping scenario (high cost, fast delivery)
('LOG_EXTREME_001', 'Q2', 2024, 'Emergency Air', 'Northeast', 'Forward', 'Critical', 125, 0.85, 99.2, 0.3, 6800.00, 0, CURRENT_TIMESTAMP()),
-- Service failure scenario (low performance)
('LOG_EXTREME_002', 'Q1', 2024, 'Regional Carrier', 'Southwest', 'Forward', 'Standard', 850, 0.12, 65.5, 8.5, 140.00, 15, CURRENT_TIMESTAMP());

-- Insert vendor performance edge cases  
INSERT INTO VENDOR_SCORECARD VALUES
-- Poor performing supplier (Enhanced edge case per guidelines)
('VSC_EDGE_001', 'SUP_018', 'Q2', 2024, 'Quality Management', 'Defect Rate', 45.5, 42.8, 38.2, 2.850, 78.5, -0.25, CURRENT_TIMESTAMP()),
-- Exceptional performer (Perfect performance scenario per guidelines)
('VSC_EDGE_002', 'SUP_022', 'Q3', 2024, 'Cost Management', 'Cost Reduction', 100.0, 100.0, 100.0, 0.000, 100.0, 25.50, CURRENT_TIMESTAMP()),
-- Supplier bankruptcy scenario (Enhanced edge case per guidelines) 
('VSC_EDGE_003', 'SUP_021', 'Q1', 2024, 'Risk Management', 'Supply Continuity', 0.0, 0.0, 0.0, 15.000, 45.2, -5.75, CURRENT_TIMESTAMP()),
-- International shipping delays (Enhanced edge case per guidelines)
('VSC_EDGE_004', 'SUP_013', 'Q2', 2024, 'Delivery Performance', 'International Logistics', 78.5, 55.2, 82.1, 0.750, 72.8, 1.25, CURRENT_TIMESTAMP());

-- ============================================================================
-- DATA VALIDATION QUERIES
-- ============================================================================

-- Query 1: Verify table record counts
SELECT 
    'SUPPLIER_PROFILES' as TABLE_NAME,
    COUNT(*) as RECORD_COUNT
FROM SUPPLIER_PROFILES
UNION ALL
SELECT 
    'INVENTORY_FACT',
    COUNT(*)
FROM INVENTORY_FACT
UNION ALL
SELECT 
    'LOGISTICS_METRICS',
    COUNT(*)
FROM LOGISTICS_METRICS
UNION ALL
SELECT 
    'DEMAND_FORECAST',
    COUNT(*)
FROM DEMAND_FORECAST
UNION ALL
SELECT 
    'VENDOR_SCORECARD',
    COUNT(*)
FROM VENDOR_SCORECARD;

-- Query 2: Verify data relationships
SELECT 
    'Vendor scorecard records with valid supplier IDs' as VALIDATION_CHECK,
    COUNT(*) as RECORD_COUNT
FROM VENDOR_SCORECARD vs
JOIN SUPPLIER_PROFILES sp ON vs.SUPPLIER_ID = sp.SUPPLIER_ID
UNION ALL
SELECT 
    'Inventory records with product SKUs in demand forecast',
    COUNT(DISTINCT il.PRODUCT_SKU)
FROM INVENTORY_FACT il
JOIN DEMAND_FORECAST df ON il.PRODUCT_SKU = df.PRODUCT_SKU;

-- Query 3: Verify quarterly data completeness
SELECT 
    INVENTORY_YEAR,
    INVENTORY_QUARTER,
    COUNT(DISTINCT PRODUCT_SKU) as PRODUCTS_WITH_DATA,
    COUNT(DISTINCT WAREHOUSE_LOCATION) as WAREHOUSES_WITH_DATA,
    COUNT(*) as TOTAL_RECORDS
FROM INVENTORY_FACT
GROUP BY INVENTORY_YEAR, INVENTORY_QUARTER
ORDER BY INVENTORY_YEAR DESC, INVENTORY_QUARTER;

-- Query 4: Sample data preview for each table
SELECT 'SUPPLIER_PROFILES Sample' as DATA_PREVIEW;
SELECT SUPPLIER_NAME, SUPPLIER_TYPE, TIER_LEVEL, ANNUAL_SPEND_MILLIONS, SUPPLIER_SCORE
FROM SUPPLIER_PROFILES
LIMIT 5;

SELECT 'INVENTORY_FACT Sample' as DATA_PREVIEW;
SELECT 
    PRODUCT_SKU,
    WAREHOUSE_LOCATION,
    INVENTORY_QUARTER,
    INVENTORY_YEAR,
    PRODUCT_CATEGORY,
    UNITS_ON_HAND,
    INVENTORY_VALUE_MILLIONS
FROM INVENTORY_FACT
LIMIT 5;

-- Query 5: Inventory value by category and quarter
SELECT 
    PRODUCT_CATEGORY,
    CONCAT(INVENTORY_YEAR, '-', INVENTORY_QUARTER) as QUARTER_YEAR,
    ROUND(SUM(INVENTORY_VALUE_MILLIONS), 2) as TOTAL_INVENTORY_VALUE,
    ROUND(AVG(INVENTORY_TURNOVER_RATIO), 2) as AVG_TURNOVER_RATIO,
    SUM(STOCKOUT_INCIDENTS) as TOTAL_STOCKOUTS,
    COUNT(DISTINCT WAREHOUSE_LOCATION) as WAREHOUSE_COUNT
FROM INVENTORY_FACT
GROUP BY PRODUCT_CATEGORY, INVENTORY_YEAR, INVENTORY_QUARTER
ORDER BY INVENTORY_YEAR DESC, INVENTORY_QUARTER DESC, TOTAL_INVENTORY_VALUE DESC
LIMIT 20;

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING THE SEMANTIC MODEL
-- ============================================================================

-- Test Query 1: Q1 Inventory Turnover Analysis (matches verified query in YAML)
SELECT 
    il.PRODUCT_CATEGORY,
    il.INVENTORY_QUARTER,
    il.INVENTORY_YEAR,
    ROUND(AVG(il.INVENTORY_TURNOVER_RATIO), 2) as avg_turnover_ratio,
    ROUND(SUM(il.INVENTORY_VALUE_MILLIONS), 2) as total_inventory_value,
    SUM(il.STOCKOUT_INCIDENTS) as total_stockouts,
    ROUND(SUM(il.EXCESS_INVENTORY_VALUE), 2) as excess_inventory
FROM INVENTORY_FACT il
WHERE il.INVENTORY_QUARTER = 'Q1'
GROUP BY il.PRODUCT_CATEGORY, il.INVENTORY_QUARTER, il.INVENTORY_YEAR
ORDER BY il.INVENTORY_YEAR DESC, avg_turnover_ratio DESC;

-- Test Query 2: Top Suppliers Cost Performance
SELECT 
    sp.SUPPLIER_NAME,
    sp.SUPPLIER_TYPE,
    sp.TIER_LEVEL,
    ROUND(AVG(vp.COST_COMPETITIVENESS_SCORE), 2) as avg_cost_score,
    ROUND(AVG(vp.QUALITY_SCORE), 2) as avg_quality_score,
    ROUND(AVG(vp.DELIVERY_PERFORMANCE_SCORE), 2) as delivery_score,
    ROUND(SUM(vp.COST_SAVINGS_MILLIONS), 2) as total_savings
FROM SUPPLIER_PROFILES sp
JOIN VENDOR_SCORECARD vp ON sp.SUPPLIER_ID = vp.SUPPLIER_ID
GROUP BY sp.SUPPLIER_NAME, sp.SUPPLIER_TYPE, sp.TIER_LEVEL
ORDER BY avg_cost_score DESC, avg_quality_score DESC;

-- Test Query 3: Logistics Cost Optimization Opportunities
SELECT 
    lp.TRANSPORT_MODE,
    lp.SERVICE_REGION,
    lp.SHIPMENT_YEAR,
    SUM(lp.TOTAL_SHIPMENTS) as total_shipments,
    ROUND(SUM(lp.SHIPPING_COST_MILLIONS), 2) as total_cost,
    ROUND(AVG(lp.COST_PER_SHIPMENT), 2) as avg_cost_per_shipment,
    ROUND(AVG(lp.ON_TIME_DELIVERY_RATE), 2) as avg_otd_rate,
    SUM(lp.DAMAGE_INCIDENTS) as total_damage
FROM LOGISTICS_METRICS lp
GROUP BY lp.TRANSPORT_MODE, lp.SERVICE_REGION, lp.SHIPMENT_YEAR
ORDER BY total_cost DESC, avg_cost_per_shipment DESC;

-- Test Query 4: Demand Forecast Accuracy Trends
SELECT 
    df.FORECAST_METHOD,
    df.MARKET_SEGMENT,
    df.FORECAST_YEAR,
    df.FORECAST_QUARTER,
    ROUND(AVG(df.FORECAST_ACCURACY_PERCENT), 2) as avg_accuracy,
    SUM(df.FORECASTED_DEMAND_UNITS) as total_forecasted,
    SUM(df.ACTUAL_DEMAND_UNITS) as total_actual,
    ROUND(AVG(df.DEMAND_VARIANCE_PERCENT), 2) as avg_variance
FROM DEMAND_FORECAST df
WHERE df.ACTUAL_DEMAND_UNITS IS NOT NULL
GROUP BY df.FORECAST_METHOD, df.MARKET_SEGMENT, df.FORECAST_YEAR, df.FORECAST_QUARTER
ORDER BY df.FORECAST_YEAR DESC, df.FORECAST_QUARTER DESC, avg_accuracy DESC;

-- ============================================================================
-- ENHANCED DATA QUALITY VALIDATION QUERIES
-- ============================================================================

-- Query 6: Edge Cases and Data Quality Validation
SELECT 
    'NULL Value Analysis' as VALIDATION_TYPE,
    'FORECAST_ACCURACY_PERCENT' as FIELD_NAME,
    COUNT(*) as NULL_COUNT,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM DEMAND_FORECAST)) as NULL_PERCENTAGE
FROM DEMAND_FORECAST 
WHERE FORECAST_ACCURACY_PERCENT IS NULL
UNION ALL
SELECT 
    'NULL Value Analysis',
    'ANNUAL_SPEND_MILLIONS',
    COUNT(*),
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM SUPPLIER_PROFILES))
FROM SUPPLIER_PROFILES 
WHERE ANNUAL_SPEND_MILLIONS IS NULL;

-- Query 7: Extreme Values Validation
SELECT 
    'Extreme Values Check' as VALIDATION_TYPE,
    'High Inventory Value (>$5M)' as SCENARIO,
    COUNT(*) as RECORD_COUNT
FROM INVENTORY_FACT 
WHERE INVENTORY_VALUE_MILLIONS > 5
UNION ALL
SELECT 
    'Extreme Values Check',
    'Zero Inventory Units',
    COUNT(*)
FROM INVENTORY_FACT 
WHERE UNITS_ON_HAND = 0
UNION ALL
SELECT 
    'Extreme Values Check',
    'High Defect Rate (>1%)',
    COUNT(*)
FROM VENDOR_SCORECARD 
WHERE DEFECT_RATE_PERCENT > 1.0;

-- Query 8: Seasonal Pattern Validation
SELECT 
    INVENTORY_QUARTER,
    ROUND(AVG(INVENTORY_VALUE_MILLIONS), 2) as AVG_INVENTORY_VALUE,
    ROUND(AVG(INVENTORY_TURNOVER_RATIO), 2) as AVG_TURNOVER,
    COUNT(*) as RECORD_COUNT
FROM INVENTORY_FACT
GROUP BY INVENTORY_QUARTER
ORDER BY 
    CASE INVENTORY_QUARTER 
        WHEN 'Q1' THEN 1 
        WHEN 'Q2' THEN 2 
        WHEN 'Q3' THEN 3 
        WHEN 'Q4' THEN 4 
    END;

-- Query 9: Supply Chain KPI Summary
SELECT 
    'Inventory Performance' as KPI_CATEGORY,
    ROUND(AVG(INVENTORY_TURNOVER_RATIO), 2) as METRIC_VALUE,
    'Turnover Ratio' as METRIC_UNIT
FROM INVENTORY_FACT 
WHERE INVENTORY_QUARTER = 'Q3' AND INVENTORY_YEAR = 2024
UNION ALL
SELECT 
    'Logistics Performance',
    ROUND(AVG(ON_TIME_DELIVERY_RATE), 2),
    'Percent OTD'
FROM LOGISTICS_METRICS 
WHERE SHIPMENT_QUARTER = 'Q3' AND SHIPMENT_YEAR = 2024
UNION ALL
SELECT 
    'Supplier Performance',
    ROUND(AVG(QUALITY_SCORE), 2),
    'Quality Score'
FROM VENDOR_SCORECARD 
WHERE EVALUATION_QUARTER = 'Q3' AND EVALUATION_YEAR = 2024
UNION ALL
SELECT 
    'Forecast Accuracy',
    ROUND(AVG(FORECAST_ACCURACY_PERCENT), 2),
    'Percent Accurate'
FROM DEMAND_FORECAST 
WHERE FORECAST_QUARTER = 'Q3' AND FORECAST_YEAR = 2024 AND FORECAST_ACCURACY_PERCENT IS NOT NULL;

-- ============================================================================
-- GRANTS AND PERMISSIONS (Optional - adjust as needed)
-- ============================================================================

-- Grant appropriate permissions to roles (adjust role names as needed)
-- GRANT SELECT ON ALL TABLES IN SCHEMA ISCO_ANALYTICS.PROD TO ROLE SUPPLY_CHAIN_ANALYST;
-- GRANT SELECT ON ALL TABLES IN SCHEMA ISCO_ANALYTICS.PROD TO ROLE BUSINESS_USER;
-- GRANT SELECT ON ALL TABLES IN SCHEMA ISCO_ANALYTICS.PROD TO ROLE OPERATIONS_MANAGER;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================

SELECT 'Comcast ISCO Supply Chain Analytics Data Setup Complete!' as STATUS,
       'All tables created with synthetic data for supply chain operations' as DESCRIPTION;
