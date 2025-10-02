-- =====================================================================
-- FreeWheel-style AdTech Synthetic Data Creation Script
-- =====================================================================
-- Creates schemas and 12 months of realistic synthetic data for Auctions,
-- Bids, Wins/Impressions, Losses, and Conversions with campaign context.
-- =====================================================================

-- 1) Create database and schemas
CREATE DATABASE IF NOT EXISTS FREEWHEEL_DATA_PLATFORM
  COMMENT = 'FreeWheel-style AdTech data platform for analytics demos';

CREATE SCHEMA IF NOT EXISTS FREEWHEEL_DATA_PLATFORM.AD_SALES
  COMMENT = 'Advertisers, campaigns, line items, creatives';

CREATE SCHEMA IF NOT EXISTS FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS
  COMMENT = 'Event logs: auctions, bids, wins/impressions, losses, conversions';

CREATE SCHEMA IF NOT EXISTS FREEWHEEL_DATA_PLATFORM.INVENTORY
  COMMENT = 'Publishers, supply sources, inventory units';

USE DATABASE FREEWHEEL_DATA_PLATFORM;

-- 2) Dimension tables
CREATE OR REPLACE TABLE AD_SALES.ADVERTISERS (
  ADVERTISER_ID VARCHAR(50) PRIMARY KEY,
  ADVERTISER_NAME VARCHAR(200),
  VERTICAL VARCHAR(100)
);

CREATE OR REPLACE TABLE AD_SALES.CAMPAIGNS (
  CAMPAIGN_ID VARCHAR(50) PRIMARY KEY,
  ADVERTISER_ID VARCHAR(50),
  CAMPAIGN_NAME VARCHAR(200),
  OBJECTIVE VARCHAR(50),
  START_DATE DATE,
  END_DATE DATE,
  TOTAL_BUDGET_USD DECIMAL(12,2)
);

CREATE OR REPLACE TABLE AD_SALES.LINE_ITEMS (
  LINE_ITEM_ID VARCHAR(50) PRIMARY KEY,
  CAMPAIGN_ID VARCHAR(50),
  NAME VARCHAR(200),
  BID_STRATEGY VARCHAR(50),
  DAILY_BUDGET_USD DECIMAL(12,2),
  FLOOR_CPM DECIMAL(8,2),
  TARGET_CHANNEL VARCHAR(20),
  PLATFORM VARCHAR(20),
  GEO_COUNTRY VARCHAR(50)
);

CREATE OR REPLACE TABLE AD_SALES.CREATIVES (
  CREATIVE_ID VARCHAR(50) PRIMARY KEY,
  LINE_ITEM_ID VARCHAR(50),
  FORMAT VARCHAR(20),
  DURATION_SEC NUMBER(3),
  SIZE VARCHAR(20),
  BRAND_SAFETY_TIER VARCHAR(20)
);

CREATE OR REPLACE TABLE INVENTORY.SUPPLY_SOURCES (
  SSP_ID VARCHAR(50) PRIMARY KEY,
  SSP_NAME VARCHAR(200)
);

CREATE OR REPLACE TABLE INVENTORY.PUBLISHERS (
  PUBLISHER_ID VARCHAR(50) PRIMARY KEY,
  PUBLISHER_NAME VARCHAR(200),
  NETWORK VARCHAR(100),
  CHANNEL VARCHAR(20)
);

CREATE OR REPLACE TABLE INVENTORY.INVENTORY_UNITS (
  INVENTORY_ID VARCHAR(50) PRIMARY KEY,
  PUBLISHER_ID VARCHAR(50),
  SSP_ID VARCHAR(50),
  AD_UNIT_NAME VARCHAR(200),
  CHANNEL VARCHAR(20),
  PLATFORM VARCHAR(20),
  CONTENT_GENRE VARCHAR(50),
  GEO_COUNTRY VARCHAR(50),
  IAB_CATEGORY VARCHAR(100)
);

-- 3) Event tables
CREATE OR REPLACE TABLE EXCHANGE_LOGS.AUCTIONS (
  AUCTION_ID VARCHAR(64) PRIMARY KEY,
  INVENTORY_ID VARCHAR(50),
  LINE_ITEM_ID VARCHAR(50),
  CAMPAIGN_ID VARCHAR(50),
  ADVERTISER_ID VARCHAR(50),
  SSP_ID VARCHAR(50),
  AUCTION_TIMESTAMP TIMESTAMP_NTZ,
  AD_FORMAT VARCHAR(20),
  CHANNEL VARCHAR(20),
  DEVICE_TYPE VARCHAR(20),
  PLATFORM VARCHAR(20),
  GEO_COUNTRY VARCHAR(50),
  IAB_CATEGORY VARCHAR(100),
  DEAL_ID VARCHAR(50),
  FLOOR_PRICE_CPM DECIMAL(8,4),
  USER_ID VARCHAR(64)
);

CREATE OR REPLACE TABLE EXCHANGE_LOGS.BIDS (
  BID_ID VARCHAR(64) PRIMARY KEY,
  AUCTION_ID VARCHAR(64),
  LINE_ITEM_ID VARCHAR(50),
  CREATIVE_ID VARCHAR(50),
  BID_PRICE_CPM DECIMAL(8,4),
  BID_TIMESTAMP TIMESTAMP_NTZ,
  BID_CURRENCY VARCHAR(3)
);

CREATE OR REPLACE TABLE EXCHANGE_LOGS.WINS_IMPRESSIONS (
  IMPRESSION_ID VARCHAR(64) PRIMARY KEY,
  AUCTION_ID VARCHAR(64),
  BID_ID VARCHAR(64),
  LINE_ITEM_ID VARCHAR(50),
  CAMPAIGN_ID VARCHAR(50),
  ADVERTISER_ID VARCHAR(50),
  PUBLISHER_ID VARCHAR(50),
  INVENTORY_ID VARCHAR(50),
  CHANNEL VARCHAR(20),
  DEVICE_TYPE VARCHAR(20),
  AD_FORMAT VARCHAR(20),
  GEO_COUNTRY VARCHAR(50),
  CLEARING_PRICE_CPM DECIMAL(8,4),
  IMPRESSION_TIMESTAMP TIMESTAMP_NTZ,
  WAS_VIEWABLE BOOLEAN,
  WAS_CLICKED BOOLEAN
);

CREATE OR REPLACE TABLE EXCHANGE_LOGS.LOSSES (
  LOSS_ID VARCHAR(64) PRIMARY KEY,
  AUCTION_ID VARCHAR(64),
  LINE_ITEM_ID VARCHAR(50),
  LOSS_REASON VARCHAR(50),
  LOSS_TIMESTAMP TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE EXCHANGE_LOGS.CONVERSIONS (
  CONVERSION_ID VARCHAR(64) PRIMARY KEY,
  IMPRESSION_ID VARCHAR(64),
  CONVERSION_TIMESTAMP TIMESTAMP_NTZ,
  CONVERSION_TYPE VARCHAR(30),
  CONVERSION_VALUE DECIMAL(10,2),
  ATTRIBUTION_MODEL VARCHAR(20),
  ATTRIBUTED_WITHIN_HOURS NUMBER(4)
);

-- 4) Seed dimensions
INSERT INTO AD_SALES.ADVERTISERS VALUES
  ('ADV001', 'Acme Retail', 'Retail'),
  ('ADV002', 'Velocity Motors', 'Automotive'),
  ('ADV003', 'Streamio+', 'Streaming Service'),
  ('ADV004', 'TechGear Pro', 'Consumer Electronics'),
  ('ADV005', 'FreshBite Foods', 'Food & Beverage'),
  ('ADV006', 'VoyageTravel', 'Travel & Hospitality'),
  ('ADV007', 'HealthFirst Insurance', 'Insurance & Finance'),
  ('ADV008', 'GameZone', 'Gaming'),
  ('ADV009', 'EcoHome Solutions', 'Home & Garden'),
  ('ADV010', 'FitLife Apparel', 'Athletic Wear');

INSERT INTO AD_SALES.CAMPAIGNS VALUES
  ('C1001', 'ADV001', 'Back-to-School Awareness', 'Awareness', '2024-09-01', '2024-12-31', 250000.00),
  ('C1002', 'ADV001', 'Holiday Shopping Blitz', 'Performance', '2024-11-01', '2024-12-31', 350000.00),
  ('C2001', 'ADV002', 'Always-On Auto Prospects', 'Performance', '2024-08-01', '2025-07-31', 480000.00),
  ('C2002', 'ADV002', 'Summer Test Drive Event', 'Acquisition', '2025-05-01', '2025-07-31', 180000.00),
  ('C3001', 'ADV003', 'Subscriber Growth FY25 H1', 'Acquisition', '2025-01-01', '2025-07-31', 600000.00),
  ('C4001', 'ADV004', 'Q4 Holiday Electronics', 'Performance', '2024-10-01', '2024-12-31', 420000.00),
  ('C4002', 'ADV004', 'Spring Gadget Launch', 'Awareness', '2025-03-01', '2025-05-31', 280000.00),
  ('C5001', 'ADV005', 'Summer BBQ Season', 'Awareness', '2025-05-01', '2025-07-31', 150000.00),
  ('C5002', 'ADV005', 'Healthy Eating Jan', 'Acquisition', '2025-01-01', '2025-02-28', 120000.00),
  ('C6001', 'ADV006', 'Summer Travel Push', 'Performance', '2025-04-01', '2025-07-31', 380000.00),
  ('C6002', 'ADV006', 'Winter Getaway Deals', 'Performance', '2024-11-01', '2025-01-31', 220000.00),
  ('C7001', 'ADV007', 'Open Enrollment 2025', 'Acquisition', '2024-10-01', '2024-12-31', 500000.00),
  ('C8001', 'ADV008', 'New Game Launch', 'Awareness', '2024-09-01', '2024-11-30', 320000.00),
  ('C8002', 'ADV008', 'Always-On Gaming', 'Performance', '2024-08-01', '2025-07-31', 450000.00),
  ('C9001', 'ADV009', 'Spring Home Improvement', 'Performance', '2025-03-01', '2025-06-30', 200000.00),
  ('C10001', 'ADV010', 'New Year Fitness', 'Acquisition', '2024-12-15', '2025-02-28', 190000.00),
  ('C10002', 'ADV010', 'Marathon Season Push', 'Performance', '2025-04-01', '2025-06-30', 160000.00);

INSERT INTO AD_SALES.LINE_ITEMS VALUES
  ('LI1001', 'C1001', 'CTV US Video 30s', 'Target CPM', 5000.00, 12.00, 'CTV', 'Roku', 'United States'),
  ('LI1002', 'C1002', 'CTV Holiday Special 30s', 'Max Bid', 8000.00, 15.00, 'CTV', 'Roku', 'United States'),
  ('LI1003', 'C1002', 'Mobile Holiday 15s', 'Target CPM', 3500.00, 8.00, 'Mobile', 'iOS', 'United States'),
  ('LI2001', 'C2001', 'CTV Always-On 15s', 'Target CPA', 4000.00, 10.00, 'CTV', 'Roku', 'United States'),
  ('LI2002', 'C2001', 'Mobile Video 6s', 'Max Bid', 2500.00, 5.00, 'Mobile', 'iOS', 'United States'),
  ('LI2003', 'C2002', 'CTV Summer Drive 30s', 'Target CPA', 5500.00, 11.00, 'CTV', 'FireTV', 'United States'),
  ('LI3001', 'C3001', 'CTV Subs Push 30s', 'Target ROAS', 6000.00, 14.00, 'CTV', 'FireTV', 'United States'),
  ('LI3002', 'C3001', 'Mobile Subs 15s', 'Target ROAS', 4000.00, 9.00, 'Mobile', 'Android', 'United States'),
  ('LI4001', 'C4001', 'CTV Electronics 30s', 'Max Bid', 7000.00, 13.00, 'CTV', 'Roku', 'United States'),
  ('LI4002', 'C4001', 'Mobile Shopping 6s', 'Target CPM', 4500.00, 7.00, 'Mobile', 'iOS', 'United States'),
  ('LI4003', 'C4002', 'CTV Gadget Launch 30s', 'Target CPM', 5500.00, 12.00, 'CTV', 'FireTV', 'United States'),
  ('LI5001', 'C5001', 'CTV BBQ Season 15s', 'Target CPM', 3000.00, 8.00, 'CTV', 'Roku', 'United States'),
  ('LI5002', 'C5002', 'Mobile Healthy Eating 6s', 'Target CPA', 2800.00, 6.00, 'Mobile', 'iOS', 'United States'),
  ('LI6001', 'C6001', 'CTV Summer Travel 30s', 'Max Bid', 6500.00, 13.00, 'CTV', 'FireTV', 'United States'),
  ('LI6002', 'C6002', 'CTV Winter Deals 30s', 'Target CPM', 4500.00, 11.00, 'CTV', 'Roku', 'United States'),
  ('LI6003', 'C6002', 'Mobile Winter Deals 15s', 'Target CPM', 3000.00, 7.00, 'Mobile', 'Android', 'United States'),
  ('LI7001', 'C7001', 'CTV Insurance Enroll 30s', 'Target CPA', 8000.00, 14.00, 'CTV', 'Roku', 'United States'),
  ('LI8001', 'C8001', 'CTV Game Launch 30s', 'Target CPM', 6000.00, 12.00, 'CTV', 'FireTV', 'United States'),
  ('LI8002', 'C8002', 'Mobile Gaming 6s', 'Max Bid', 3500.00, 6.00, 'Mobile', 'iOS', 'United States'),
  ('LI8003', 'C8002', 'CTV Gaming Always-On 15s', 'Target CPM', 4000.00, 9.00, 'CTV', 'Roku', 'United States'),
  ('LI9001', 'C9001', 'CTV Home Improvement 30s', 'Target CPM', 4500.00, 10.00, 'CTV', 'Roku', 'United States'),
  ('LI10001', 'C10001', 'CTV New Year Fitness 30s', 'Target CPA', 4500.00, 11.00, 'CTV', 'FireTV', 'United States'),
  ('LI10002', 'C10001', 'Mobile Fitness 15s', 'Target CPA', 3000.00, 7.00, 'Mobile', 'iOS', 'United States'),
  ('LI10003', 'C10002', 'CTV Marathon 30s', 'Target CPM', 3500.00, 9.00, 'CTV', 'Roku', 'United States');

INSERT INTO AD_SALES.CREATIVES VALUES
  ('CR1001', 'LI1001', 'Video', 30, '1920x1080', 'Standard'),
  ('CR1002', 'LI1002', 'Video', 30, '1920x1080', 'Premium'),
  ('CR1003', 'LI1003', 'Video', 15, '1080x1920', 'Standard'),
  ('CR2001', 'LI2001', 'Video', 15, '1920x1080', 'Standard'),
  ('CR2002', 'LI2002', 'Video', 6, '1080x1920', 'Standard'),
  ('CR2003', 'LI2003', 'Video', 30, '1920x1080', 'Standard'),
  ('CR3001', 'LI3001', 'Video', 30, '1920x1080', 'Premium'),
  ('CR3002', 'LI3002', 'Video', 15, '1080x1920', 'Premium'),
  ('CR4001', 'LI4001', 'Video', 30, '1920x1080', 'Standard'),
  ('CR4002', 'LI4002', 'Video', 6, '1080x1920', 'Standard'),
  ('CR4003', 'LI4003', 'Video', 30, '1920x1080', 'Premium'),
  ('CR5001', 'LI5001', 'Video', 15, '1920x1080', 'Standard'),
  ('CR5002', 'LI5002', 'Video', 6, '1080x1920', 'Standard'),
  ('CR6001', 'LI6001', 'Video', 30, '1920x1080', 'Standard'),
  ('CR6002', 'LI6002', 'Video', 30, '1920x1080', 'Standard'),
  ('CR6003', 'LI6003', 'Video', 15, '1080x1920', 'Standard'),
  ('CR7001', 'LI7001', 'Video', 30, '1920x1080', 'Premium'),
  ('CR8001', 'LI8001', 'Video', 30, '1920x1080', 'Standard'),
  ('CR8002', 'LI8002', 'Video', 6, '1080x1920', 'Standard'),
  ('CR8003', 'LI8003', 'Video', 15, '1920x1080', 'Standard'),
  ('CR9001', 'LI9001', 'Video', 30, '1920x1080', 'Standard'),
  ('CR10001', 'LI10001', 'Video', 30, '1920x1080', 'Standard'),
  ('CR10002', 'LI10002', 'Video', 15, '1080x1920', 'Standard'),
  ('CR10003', 'LI10003', 'Video', 30, '1920x1080', 'Standard');

INSERT INTO INVENTORY.SUPPLY_SOURCES VALUES
  ('SSP_FW', 'FreeWheel SSP'),
  ('SSP_MG', 'Magnite'),
  ('SSP_XA', 'Xandr');

INSERT INTO INVENTORY.PUBLISHERS VALUES
  ('PUB001', 'Global News Network', 'GNN', 'CTV'),
  ('PUB002', 'CineMax Streaming', 'CineMax', 'CTV'),
  ('PUB003', 'SportsNow', 'SN', 'CTV'),
  ('PUB004', 'Lifestyle TV', 'LTV', 'Mobile'),
  ('PUB005', 'Food Channel Plus', 'FCP', 'CTV'),
  ('PUB006', 'Reality TV Hub', 'RTH', 'CTV'),
  ('PUB007', 'Mobile Game Network', 'MGN', 'Mobile'),
  ('PUB008', 'News Mobile', 'NM', 'Mobile'),
  ('PUB009', 'Entertainment Now', 'EN', 'CTV'),
  ('PUB010', 'Sports Mobile', 'SM', 'Mobile');

INSERT INTO INVENTORY.INVENTORY_UNITS VALUES
  ('INV001', 'PUB001', 'SSP_FW', 'GNN Prime News Pre-roll', 'CTV', 'Roku', 'News', 'United States', 'IAB1-2'),
  ('INV002', 'PUB002', 'SSP_MG', 'CineMax Movie Mid-roll', 'CTV', 'Roku', 'Entertainment', 'United States', 'IAB1-1'),
  ('INV003', 'PUB003', 'SSP_XA', 'SportsNow Live Pre-roll', 'CTV', 'FireTV', 'Sports', 'United States', 'IAB1-6'),
  ('INV004', 'PUB004', 'SSP_MG', 'Lifestyle App Short Video', 'Mobile', 'iOS', 'Lifestyle', 'United States', 'IAB1-7'),
  ('INV005', 'PUB005', 'SSP_FW', 'Food Channel Cooking Show', 'CTV', 'Roku', 'Food', 'United States', 'IAB1-8'),
  ('INV006', 'PUB006', 'SSP_MG', 'Reality TV Mid-roll', 'CTV', 'FireTV', 'Reality', 'United States', 'IAB1-1'),
  ('INV007', 'PUB007', 'SSP_XA', 'Mobile Gaming Banner', 'Mobile', 'iOS', 'Gaming', 'United States', 'IAB1-9'),
  ('INV008', 'PUB008', 'SSP_FW', 'News Mobile Video', 'Mobile', 'Android', 'News', 'United States', 'IAB1-2'),
  ('INV009', 'PUB009', 'SSP_MG', 'Entertainment CTV Pre-roll', 'CTV', 'Roku', 'Entertainment', 'United States', 'IAB1-1'),
  ('INV010', 'PUB010', 'SSP_XA', 'Sports Mobile Feed', 'Mobile', 'iOS', 'Sports', 'United States', 'IAB1-6'),
  ('INV011', 'PUB001', 'SSP_MG', 'GNN Evening News Mid-roll', 'CTV', 'FireTV', 'News', 'United States', 'IAB1-2'),
  ('INV012', 'PUB003', 'SSP_FW', 'SportsNow Post-game', 'CTV', 'Roku', 'Sports', 'United States', 'IAB1-6');

-- 5) Generate 12 months of synthetic events (Aug 2024 - Jul 2025)
-- Enhanced with multiple events per campaign for realistic trends and variability
-- 
-- NOTE: This script creates a representative sample dataset demonstrating:
--   - Seasonal trends (higher CPMs in Q4, lower in Q1)
--   - Campaign ramp-up patterns (more events as campaigns mature)
--   - Variability in outcomes (different win rates, click rates, conversion rates)
--   - Multiple line items running concurrently
-- 
-- IMPORTANT - DATE RANGE CONSIDERATION:
--   The timestamps below use absolute dates (2024-08 through 2025-07).
--   If you need the data to be "recent" for queries using CURRENT_DATE(),
--   consider updating timestamps to be within the last 90 days using:
--     UPDATE EXCHANGE_LOGS.AUCTIONS SET AUCTION_TIMESTAMP = DATEADD(day, DATEDIFF(day, '2024-08-01', AUCTION_TIMESTAMP), DATEADD(day, -120, CURRENT_DATE()));
--   (and similarly for BIDS, WINS_IMPRESSIONS, CONVERSIONS tables)
-- 
-- For production-scale testing with 100K+ events, consider using:
--   - Snowflake's GENERATOR() table function
--   - Custom stored procedures with loops
--   - External data generation tools (Python/dbt)

-- ===== AUGUST 2024 =====
-- Always-On campaigns start
INSERT INTO EXCHANGE_LOGS.AUCTIONS VALUES
  -- LI2001 (Auto Always-On) - High volume
  ('A202408-LI2001-001','INV001','LI2001','C2001','ADV002','SSP_FW','2024-08-01 08:15:00','Video','CTV','CTV','Roku','United States','News','D-2001',10.2500,'U-10001'),
  ('A202408-LI2001-002','INV002','LI2001','C2001','ADV002','SSP_MG','2024-08-01 14:30:00','Video','CTV','CTV','Roku','United States','Entertainment','D-2002',10.5000,'U-10002'),
  ('A202408-LI2001-003','INV003','LI2001','C2001','ADV002','SSP_XA','2024-08-01 20:45:00','Video','CTV','CTV','FireTV','United States','Sports','D-2003',10.3000,'U-10003'),
  ('A202408-LI2001-004','INV001','LI2001','C2001','ADV002','SSP_FW','2024-08-05 10:00:00','Video','CTV','CTV','Roku','United States','News','D-2004',10.4000,'U-10004'),
  ('A202408-LI2001-005','INV011','LI2001','C2001','ADV002','SSP_MG','2024-08-05 19:20:00','Video','CTV','CTV','FireTV','United States','News','D-2005',10.6000,'U-10005'),
  ('A202408-LI2001-006','INV003','LI2001','C2001','ADV002','SSP_XA','2024-08-10 15:30:00','Video','CTV','CTV','FireTV','United States','Sports','D-2006',10.7500,'U-10006'),
  ('A202408-LI2001-007','INV002','LI2001','C2001','ADV002','SSP_MG','2024-08-10 21:00:00','Video','CTV','CTV','Roku','United States','Entertainment','D-2007',10.5500,'U-10007'),
  ('A202408-LI2001-008','INV001','LI2001','C2001','ADV002','SSP_FW','2024-08-15 09:45:00','Video','CTV','CTV','Roku','United States','News','D-2008',10.8000,'U-10008'),
  ('A202408-LI2001-009','INV012','LI2001','C2001','ADV002','SSP_FW','2024-08-15 21:15:00','Video','CTV','CTV','Roku','United States','Sports','D-2009',10.9000,'U-10009'),
  ('A202408-LI2001-010','INV003','LI2001','C2001','ADV002','SSP_XA','2024-08-20 14:00:00','Video','CTV','CTV','FireTV','United States','Sports','D-2010',11.0500,'U-10010'),
  ('A202408-LI2001-011','INV002','LI2001','C2001','ADV002','SSP_MG','2024-08-20 19:45:00','Video','CTV','CTV','Roku','United States','Entertainment','D-2011',11.1000,'U-10011'),
  ('A202408-LI2001-012','INV011','LI2001','C2001','ADV002','SSP_MG','2024-08-25 12:30:00','Video','CTV','CTV','FireTV','United States','News','D-2012',11.2500,'U-10012'),
  ('A202408-LI2001-013','INV001','LI2001','C2001','ADV002','SSP_FW','2024-08-25 20:00:00','Video','CTV','CTV','Roku','United States','News','D-2013',11.3000,'U-10013'),
  ('A202408-LI2001-014','INV003','LI2001','C2001','ADV002','SSP_XA','2024-08-28 16:20:00','Video','CTV','CTV','FireTV','United States','Sports','D-2014',11.4000,'U-10014'),
  ('A202408-LI2001-015','INV002','LI2001','C2001','ADV002','SSP_MG','2024-08-31 11:50:00','Video','CTV','CTV','Roku','United States','Entertainment','D-2015',11.3500,'U-10015'),
  -- LI8002 & LI8003 (Gaming Always-On) starts
  ('A202408-LI8002-001','INV007','LI8002','C8002','ADV008','SSP_XA','2024-08-03 15:00:00','Video','Mobile','Mobile','iOS','United States','Gaming','D-8001',6.2000,'U-80001'),
  ('A202408-LI8002-002','INV007','LI8002','C8002','ADV008','SSP_XA','2024-08-07 18:30:00','Video','Mobile','Mobile','iOS','United States','Gaming','D-8002',6.3000,'U-80002'),
  ('A202408-LI8002-003','INV007','LI8002','C8002','ADV008','SSP_XA','2024-08-14 20:00:00','Video','Mobile','Mobile','iOS','United States','Gaming','D-8003',6.4000,'U-80003'),
  ('A202408-LI8002-004','INV007','LI8002','C8002','ADV008','SSP_XA','2024-08-21 19:15:00','Video','Mobile','Mobile','iOS','United States','Gaming','D-8004',6.3500,'U-80004'),
  ('A202408-LI8002-005','INV007','LI8002','C8002','ADV008','SSP_XA','2024-08-28 17:45:00','Video','Mobile','Mobile','iOS','United States','Gaming','D-8005',6.5000,'U-80005'),
  ('A202408-LI8003-001','INV009','LI8003','C8002','ADV008','SSP_MG','2024-08-05 19:30:00','Video','CTV','CTV','Roku','United States','Entertainment','D-8101',9.1000,'U-81001'),
  ('A202408-LI8003-002','INV009','LI8003','C8002','ADV008','SSP_MG','2024-08-12 21:00:00','Video','CTV','CTV','Roku','United States','Entertainment','D-8102',9.2000,'U-81002'),
  ('A202408-LI8003-003','INV002','LI8003','C8002','ADV008','SSP_MG','2024-08-18 20:15:00','Video','CTV','CTV','Roku','United States','Entertainment','D-8103',9.3000,'U-81003'),
  ('A202408-LI8003-004','INV009','LI8003','C8002','ADV008','SSP_MG','2024-08-26 19:45:00','Video','CTV','CTV','Roku','United States','Entertainment','D-8104',9.4000,'U-81004');

INSERT INTO EXCHANGE_LOGS.BIDS VALUES
  -- August 2024 bids
  ('B202408-LI2001-001','A202408-LI2001-001','LI2001','CR2001',11.8000,'2024-08-01 08:15:00','USD'),
  ('B202408-LI2001-002','A202408-LI2001-002','LI2001','CR2001',12.0000,'2024-08-01 14:30:00','USD'),
  ('B202408-LI2001-003','A202408-LI2001-003','LI2001','CR2001',11.9000,'2024-08-01 20:45:00','USD'),
  ('B202408-LI2001-004','A202408-LI2001-004','LI2001','CR2001',12.1000,'2024-08-05 10:00:00','USD'),
  ('B202408-LI2001-005','A202408-LI2001-005','LI2001','CR2001',12.2000,'2024-08-05 19:20:00','USD'),
  ('B202408-LI2001-006','A202408-LI2001-006','LI2001','CR2001',12.3000,'2024-08-10 15:30:00','USD'),
  ('B202408-LI2001-007','A202408-LI2001-007','LI2001','CR2001',12.1000,'2024-08-10 21:00:00','USD'),
  ('B202408-LI2001-008','A202408-LI2001-008','LI2001','CR2001',12.4000,'2024-08-15 09:45:00','USD'),
  ('B202408-LI2001-009','A202408-LI2001-009','LI2001','CR2001',12.5000,'2024-08-15 21:15:00','USD'),
  ('B202408-LI2001-010','A202408-LI2001-010','LI2001','CR2001',12.7000,'2024-08-20 14:00:00','USD'),
  ('B202408-LI2001-011','A202408-LI2001-011','LI2001','CR2001',12.8000,'2024-08-20 19:45:00','USD'),
  ('B202408-LI2001-012','A202408-LI2001-012','LI2001','CR2001',12.9000,'2024-08-25 12:30:00','USD'),
  ('B202408-LI2001-013','A202408-LI2001-013','LI2001','CR2001',13.1000,'2024-08-25 20:00:00','USD'),
  ('B202408-LI2001-014','A202408-LI2001-014','LI2001','CR2001',13.2000,'2024-08-28 16:20:00','USD'),
  ('B202408-LI2001-015','A202408-LI2001-015','LI2001','CR2001',13.1000,'2024-08-31 11:50:00','USD'),
  ('B202408-LI8002-001','A202408-LI8002-001','LI8002','CR8002',7.8000,'2024-08-03 15:00:00','USD'),
  ('B202408-LI8002-002','A202408-LI8002-002','LI8002','CR8002',7.9000,'2024-08-07 18:30:00','USD'),
  ('B202408-LI8002-003','A202408-LI8002-003','LI8002','CR8002',8.0000,'2024-08-14 20:00:00','USD'),
  ('B202408-LI8002-004','A202408-LI8002-004','LI8002','CR8002',7.9500,'2024-08-21 19:15:00','USD'),
  ('B202408-LI8002-005','A202408-LI8002-005','LI8002','CR8002',8.1000,'2024-08-28 17:45:00','USD'),
  ('B202408-LI8003-001','A202408-LI8003-001','LI8003','CR8003',10.5000,'2024-08-05 19:30:00','USD'),
  ('B202408-LI8003-002','A202408-LI8003-002','LI8003','CR8003',10.6000,'2024-08-12 21:00:00','USD'),
  ('B202408-LI8003-003','A202408-LI8003-003','LI8003','CR8003',10.7000,'2024-08-18 20:15:00','USD'),
  ('B202408-LI8003-004','A202408-LI8003-004','LI8003','CR8003',10.8000,'2024-08-26 19:45:00','USD'),
  -- Legacy sparse data kept for other months
  ('B202408-LI2001-01','A202408-LI2001-01','LI2001','CR2001',12.5000,'2024-08-15 12:00:00','USD'),
  ('B202409-LI2001-01','A202409-LI2001-01','LI2001','CR2001',12.0000,'2024-09-15 12:00:00','USD'),
  ('B202410-LI2001-01','A202410-LI2001-01','LI2001','CR2001',11.8000,'2024-10-15 12:00:00','USD'),
  ('B202411-LI2001-01','A202411-LI2001-01','LI2001','CR2001',12.4000,'2024-11-15 12:00:00','USD'),
  ('B202412-LI2001-01','A202412-LI2001-01','LI2001','CR2001',13.0000,'2024-12-15 12:00:00','USD'),
  ('B202501-LI2001-01','A202501-LI2001-01','LI2001','CR2001',12.3000,'2025-01-15 12:00:00','USD'),
  ('B202502-LI2001-01','A202502-LI2001-01','LI2001','CR2001',11.2000,'2025-02-15 12:00:00','USD'),
  ('B202503-LI2001-01','A202503-LI2001-01','LI2001','CR2001',11.6000,'2025-03-15 12:00:00','USD'),
  ('B202504-LI2001-01','A202504-LI2001-01','LI2001','CR2001',11.4000,'2025-04-15 12:00:00','USD'),
  ('B202505-LI2001-01','A202505-LI2001-01','LI2001','CR2001',11.9000,'2025-05-15 12:00:00','USD'),
  ('B202506-LI2001-01','A202506-LI2001-01','LI2001','CR2001',12.2000,'2025-06-15 12:00:00','USD'),
  ('B202507-LI2001-01','A202507-LI2001-01','LI2001','CR2001',12.6000,'2025-07-15 12:00:00','USD');

INSERT INTO EXCHANGE_LOGS.WINS_IMPRESSIONS VALUES
  -- August 2024 wins (showing ~80% win rate with variability)
  ('I202408-LI2001-001','A202408-LI2001-001','B202408-LI2001-001','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',11.5000,'2024-08-01 08:15:05',TRUE,FALSE),
  ('I202408-LI2001-002','A202408-LI2001-002','B202408-LI2001-002','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',11.7000,'2024-08-01 14:30:05',TRUE,TRUE),
  ('I202408-LI2001-003','A202408-LI2001-003','B202408-LI2001-003','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',11.6000,'2024-08-01 20:45:05',TRUE,FALSE),
  -- Bid 004 lost (outbid)
  ('I202408-LI2001-005','A202408-LI2001-005','B202408-LI2001-005','LI2001','C2001','ADV002','PUB001','INV011','CTV','CTV','Video','United States',11.9000,'2024-08-05 19:20:05',TRUE,FALSE),
  ('I202408-LI2001-006','A202408-LI2001-006','B202408-LI2001-006','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',12.0000,'2024-08-10 15:30:05',TRUE,TRUE),
  ('I202408-LI2001-007','A202408-LI2001-007','B202408-LI2001-007','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',11.8000,'2024-08-10 21:00:05',FALSE,FALSE),
  ('I202408-LI2001-008','A202408-LI2001-008','B202408-LI2001-008','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',12.1000,'2024-08-15 09:45:05',TRUE,FALSE),
  ('I202408-LI2001-009','A202408-LI2001-009','B202408-LI2001-009','LI2001','C2001','ADV002','PUB003','INV012','CTV','CTV','Video','United States',12.2000,'2024-08-15 21:15:05',TRUE,TRUE),
  ('I202408-LI2001-010','A202408-LI2001-010','B202408-LI2001-010','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',12.4000,'2024-08-20 14:00:05',TRUE,FALSE),
  ('I202408-LI2001-011','A202408-LI2001-011','B202408-LI2001-011','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',12.5000,'2024-08-20 19:45:05',TRUE,TRUE),
  -- Bid 012 lost (below floor)
  ('I202408-LI2001-013','A202408-LI2001-013','B202408-LI2001-013','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',12.8000,'2024-08-25 20:00:05',TRUE,FALSE),
  ('I202408-LI2001-014','A202408-LI2001-014','B202408-LI2001-014','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',12.9000,'2024-08-28 16:20:05',TRUE,TRUE),
  ('I202408-LI2001-015','A202408-LI2001-015','B202408-LI2001-015','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',12.8000,'2024-08-31 11:50:05',TRUE,FALSE),
  ('I202408-LI8002-001','A202408-LI8002-001','B202408-LI8002-001','LI8002','C8002','ADV008','PUB007','INV007','Mobile','Mobile','Video','United States',7.5000,'2024-08-03 15:00:05',TRUE,TRUE),
  ('I202408-LI8002-002','A202408-LI8002-002','B202408-LI8002-002','LI8002','C8002','ADV008','PUB007','INV007','Mobile','Mobile','Video','United States',7.6000,'2024-08-07 18:30:05',TRUE,FALSE),
  ('I202408-LI8002-003','A202408-LI8002-003','B202408-LI8002-003','LI8002','C8002','ADV008','PUB007','INV007','Mobile','Mobile','Video','United States',7.7000,'2024-08-14 20:00:05',TRUE,TRUE),
  ('I202408-LI8002-004','A202408-LI8002-004','B202408-LI8002-004','LI8002','C8002','ADV008','PUB007','INV007','Mobile','Mobile','Video','United States',7.6500,'2024-08-21 19:15:05',TRUE,FALSE),
  ('I202408-LI8002-005','A202408-LI8002-005','B202408-LI8002-005','LI8002','C8002','ADV008','PUB007','INV007','Mobile','Mobile','Video','United States',7.8000,'2024-08-28 17:45:05',TRUE,TRUE),
  ('I202408-LI8003-001','A202408-LI8003-001','B202408-LI8003-001','LI8003','C8002','ADV008','PUB009','INV009','CTV','CTV','Video','United States',10.2000,'2024-08-05 19:30:05',TRUE,FALSE),
  ('I202408-LI8003-002','A202408-LI8003-002','B202408-LI8003-002','LI8003','C8002','ADV008','PUB009','INV009','CTV','CTV','Video','United States',10.3000,'2024-08-12 21:00:05',TRUE,TRUE),
  ('I202408-LI8003-003','A202408-LI8003-003','B202408-LI8003-003','LI8003','C8002','ADV008','PUB002','INV002','CTV','CTV','Video','United States',10.4000,'2024-08-18 20:15:05',TRUE,FALSE),
  ('I202408-LI8003-004','A202408-LI8003-004','B202408-LI8003-004','LI8003','C8002','ADV008','PUB009','INV009','CTV','CTV','Video','United States',10.5000,'2024-08-26 19:45:05',TRUE,TRUE),
  -- Legacy sparse data
  ('I202408-LI2001-01','A202408-LI2001-01','B202408-LI2001-01','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',11.8000,'2024-08-15 12:00:05',TRUE,FALSE),
  ('I202409-LI2001-01','A202409-LI2001-01','B202409-LI2001-01','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',11.5000,'2024-09-15 12:00:05',TRUE,TRUE),
  ('I202410-LI2001-01','A202410-LI2001-01','B202410-LI2001-01','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',11.3000,'2024-10-15 12:00:05',TRUE,FALSE),
  ('I202411-LI2001-01','A202411-LI2001-01','B202411-LI2001-01','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',11.9000,'2024-11-15 12:00:05',TRUE,TRUE),
  ('I202412-LI2001-01','A202412-LI2001-01','B202412-LI2001-01','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',12.3000,'2024-12-15 12:00:05',TRUE,TRUE),
  ('I202501-LI2001-01','A202501-LI2001-01','B202501-LI2001-01','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',11.7000,'2025-01-15 12:00:05',TRUE,FALSE),
  ('I202502-LI2001-01','A202502-LI2001-01','B202502-LI2001-01','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',10.7000,'2025-02-15 12:00:05',TRUE,FALSE),
  ('I202503-LI2001-01','A202503-LI2001-01','B202503-LI2001-01','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',11.1000,'2025-03-15 12:00:05',TRUE,TRUE),
  ('I202504-LI2001-01','A202504-LI2001-01','B202504-LI2001-01','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',10.9000,'2025-04-15 12:00:05',TRUE,FALSE),
  ('I202505-LI2001-01','A202505-LI2001-01','B202505-LI2001-01','LI2001','C2001','ADV002','PUB001','INV001','CTV','CTV','Video','United States',11.2000,'2025-05-15 12:00:05',TRUE,TRUE),
  ('I202506-LI2001-01','A202506-LI2001-01','B202506-LI2001-01','LI2001','C2001','ADV002','PUB002','INV002','CTV','CTV','Video','United States',11.6000,'2025-06-15 12:00:05',TRUE,FALSE),
  ('I202507-LI2001-01','A202507-LI2001-01','B202507-LI2001-01','LI2001','C2001','ADV002','PUB003','INV003','CTV','CTV','Video','United States',11.9000,'2025-07-15 12:00:05',TRUE,TRUE);

INSERT INTO EXCHANGE_LOGS.LOSSES VALUES
  -- August 2024 losses
  ('L202408-LI2001-004','A202408-LI2001-004','LI2001','Outbid','2024-08-05 10:00:00'),
  ('L202408-LI2001-012','A202408-LI2001-012','LI2001','Below floor','2024-08-25 12:30:00'),
  -- Legacy and other months
  ('L202408-LI2001-01','A202408-LI2001-01','LI2001','Outbid','2024-08-15 12:00:00'),
  ('L202503-LI2001-01','A202503-LI2001-01','LI2001','Below floor','2025-03-15 12:00:00');

INSERT INTO EXCHANGE_LOGS.CONVERSIONS VALUES
  -- August 2024 conversions (varying conversion types and attribution)
  ('V202408-LI2001-002','I202408-LI2001-002','2024-08-01 20:30:00','Lead',0.00,'last_click',6),
  ('V202408-LI2001-006','I202408-LI2001-006','2024-08-10 18:45:00','Test Drive',0.00,'last_click',3),
  ('V202408-LI2001-009','I202408-LI2001-009','2024-08-16 10:00:00','Lead',0.00,'last_click',15),
  ('V202408-LI2001-011','I202408-LI2001-011','2024-08-21 14:30:00','Test Drive',0.00,'view_through',20),
  ('V202408-LI2001-014','I202408-LI2001-014','2024-08-29 09:15:00','Purchase',28500.00,'last_click',18),
  ('V202408-LI8002-001','I202408-LI8002-001','2024-08-03 16:30:00','App Install',0.00,'last_click',1),
  ('V202408-LI8002-003','I202408-LI8002-003','2024-08-14 22:15:00','In-App Purchase',4.99,'last_click',2),
  ('V202408-LI8002-005','I202408-LI8002-005','2024-08-28 20:00:00','In-App Purchase',9.99,'last_click',3),
  ('V202408-LI8003-002','I202408-LI8003-002','2024-08-13 08:30:00','Website Visit',0.00,'last_click',11),
  ('V202408-LI8003-004','I202408-LI8003-004','2024-08-27 14:00:00','Website Visit',0.00,'view_through',25),
  -- Legacy and other months
  ('V202409-LI2001-01','I202409-LI2001-01','2024-09-15 12:30:00','Lead',0.00,'last_click',1),
  ('V202411-LI2001-01','I202411-LI2001-01','2024-11-15 13:15:00','Test Drive',0.00,'last_click',3),
  ('V202412-LI2001-01','I202412-LI2001-01','2024-12-16 09:00:00','Purchase',25000.00,'last_click',20),
  ('V202505-LI2001-01','I202505-LI2001-01','2025-05-15 14:25:00','Lead',0.00,'view_through',24),
  ('V202507-LI2001-01','I202507-LI2001-01','2025-07-16 15:45:00','Purchase',22000.00,'last_click',20);

-- Back-to-School campaign Q4 2024 (LI1001)
INSERT INTO EXCHANGE_LOGS.AUCTIONS VALUES
  ('A202409-LI1001-01','INV001','LI1001','C1001','ADV001','SSP_FW','2024-09-05 20:00:00','Video','CTV','CTV','Roku','United States','News','D-1101',12.5000,'U-101'),
  ('A202410-LI1001-01','INV002','LI1001','C1001','ADV001','SSP_MG','2024-10-05 20:00:00','Video','CTV','CTV','Roku','United States','Entertainment','D-1102',12.0000,'U-102'),
  ('A202411-LI1001-01','INV002','LI1001','C1001','ADV001','SSP_MG','2024-11-05 20:00:00','Video','CTV','CTV','Roku','United States','Entertainment','D-1103',12.2500,'U-103'),
  ('A202412-LI1001-01','INV001','LI1001','C1001','ADV001','SSP_FW','2024-12-05 20:00:00','Video','CTV','CTV','Roku','United States','News','D-1104',13.0000,'U-104');

INSERT INTO EXCHANGE_LOGS.BIDS VALUES
  ('B202409-LI1001-01','A202409-LI1001-01','LI1001','CR1001',13.5000,'2024-09-05 20:00:00','USD'),
  ('B202410-LI1001-01','A202410-LI1001-01','LI1001','CR1001',12.6000,'2024-10-05 20:00:00','USD'),
  ('B202411-LI1001-01','A202411-LI1001-01','LI1001','CR1001',12.9000,'2024-11-05 20:00:00','USD'),
  ('B202412-LI1001-01','A202412-LI1001-01','LI1001','CR1001',13.8000,'2024-12-05 20:00:00','USD');

INSERT INTO EXCHANGE_LOGS.WINS_IMPRESSIONS VALUES
  ('I202409-LI1001-01','A202409-LI1001-01','B202409-LI1001-01','LI1001','C1001','ADV001','PUB001','INV001','CTV','CTV','Video','United States',13.0000,'2024-09-05 20:00:05',TRUE,TRUE),
  ('I202410-LI1001-01','A202410-LI1001-01','B202410-LI1001-01','LI1001','C1001','ADV001','PUB002','INV002','CTV','CTV','Video','United States',12.4000,'2024-10-05 20:00:05',TRUE,FALSE),
  ('I202411-LI1001-01','A202411-LI1001-01','B202411-LI1001-01','LI1001','C1001','ADV001','PUB002','INV002','CTV','CTV','Video','United States',12.7000,'2024-11-05 20:00:05',TRUE,TRUE),
  ('I202412-LI1001-01','A202412-LI1001-01','B202412-LI1001-01','LI1001','C1001','ADV001','PUB001','INV001','CTV','CTV','Video','United States',13.4000,'2024-12-05 20:00:05',TRUE,TRUE);

INSERT INTO EXCHANGE_LOGS.CONVERSIONS VALUES
  ('V202409-LI1001-01','I202409-LI1001-01','2024-09-06 08:00:00','Signup',0.00,'last_click',12),
  ('V202411-LI1001-01','I202411-LI1001-01','2024-11-06 09:00:00','Purchase',120.00,'last_click',24),
  ('V202412-LI1001-01','I202412-LI1001-01','2024-12-07 10:00:00','Purchase',150.00,'last_click',40);

-- Streamio+ subscriber acquisition (LI3001) Jan-Jul 2025
INSERT INTO EXCHANGE_LOGS.AUCTIONS VALUES
  ('A202501-LI3001-01','INV003','LI3001','C3001','ADV003','SSP_XA','2025-01-10 18:00:00','Video','CTV','CTV','FireTV','United States','Sports','D-1301',14.5000,'U-301'),
  ('A202502-LI3001-01','INV003','LI3001','C3001','ADV003','SSP_XA','2025-02-10 18:00:00','Video','CTV','CTV','FireTV','United States','Sports','D-1302',14.2500,'U-302'),
  ('A202503-LI3001-01','INV002','LI3001','C3001','ADV003','SSP_MG','2025-03-10 18:00:00','Video','CTV','CTV','Roku','United States','Entertainment','D-1303',14.0000,'U-303'),
  ('A202504-LI3001-01','INV003','LI3001','C3001','ADV003','SSP_XA','2025-04-10 18:00:00','Video','CTV','CTV','FireTV','United States','Sports','D-1304',13.9000,'U-304'),
  ('A202505-LI3001-01','INV003','LI3001','C3001','ADV003','SSP_XA','2025-05-10 18:00:00','Video','CTV','CTV','FireTV','United States','Sports','D-1305',14.1000,'U-305'),
  ('A202506-LI3001-01','INV002','LI3001','C3001','ADV003','SSP_MG','2025-06-10 18:00:00','Video','CTV','CTV','Roku','United States','Entertainment','D-1306',13.8000,'U-306'),
  ('A202507-LI3001-01','INV003','LI3001','C3001','ADV003','SSP_XA','2025-07-10 18:00:00','Video','CTV','CTV','FireTV','United States','Sports','D-1307',13.9000,'U-307');

INSERT INTO EXCHANGE_LOGS.BIDS VALUES
  ('B202501-LI3001-01','A202501-LI3001-01','LI3001','CR3001',15.2000,'2025-01-10 18:00:00','USD'),
  ('B202502-LI3001-01','A202502-LI3001-01','LI3001','CR3001',14.8000,'2025-02-10 18:00:00','USD'),
  ('B202503-LI3001-01','A202503-LI3001-01','LI3001','CR3001',14.5000,'2025-03-10 18:00:00','USD'),
  ('B202504-LI3001-01','A202504-LI3001-01','LI3001','CR3001',14.1000,'2025-04-10 18:00:00','USD'),
  ('B202505-LI3001-01','A202505-LI3001-01','LI3001','CR3001',14.6000,'2025-05-10 18:00:00','USD'),
  ('B202506-LI3001-01','A202506-LI3001-01','LI3001','CR3001',14.0000,'2025-06-10 18:00:00','USD'),
  ('B202507-LI3001-01','A202507-LI3001-01','LI3001','CR3001',14.2000,'2025-07-10 18:00:00','USD');

INSERT INTO EXCHANGE_LOGS.WINS_IMPRESSIONS VALUES
  ('I202501-LI3001-01','A202501-LI3001-01','B202501-LI3001-01','LI3001','C3001','ADV003','PUB003','INV003','CTV','CTV','Video','United States',14.9000,'2025-01-10 18:00:05',TRUE,TRUE),
  ('I202502-LI3001-01','A202502-LI3001-01','B202502-LI3001-01','LI3001','C3001','ADV003','PUB003','INV003','CTV','CTV','Video','United States',14.4000,'2025-02-10 18:00:05',TRUE,TRUE),
  ('I202503-LI3001-01','A202503-LI3001-01','B202503-LI3001-01','LI3001','C3001','ADV003','PUB002','INV002','CTV','CTV','Video','United States',14.2000,'2025-03-10 18:00:05',TRUE,TRUE),
  ('I202504-LI3001-01','A202504-LI3001-01','B202504-LI3001-01','LI3001','C3001','ADV003','PUB003','INV003','CTV','CTV','Video','United States',13.8000,'2025-04-10 18:00:05',TRUE,TRUE),
  ('I202505-LI3001-01','A202505-LI3001-01','B202505-LI3001-01','LI3001','C3001','ADV003','PUB003','INV003','CTV','CTV','Video','United States',14.2000,'2025-05-10 18:00:05',TRUE,TRUE),
  ('I202506-LI3001-01','A202506-LI3001-01','B202506-LI3001-01','LI3001','C3001','ADV003','PUB002','INV002','CTV','CTV','Video','United States',13.9000,'2025-06-10 18:00:05',TRUE,TRUE),
  ('I202507-LI3001-01','A202507-LI3001-01','B202507-LI3001-01','LI3001','C3001','ADV003','PUB003','INV003','CTV','CTV','Video','United States',14.0000,'2025-07-10 18:00:05',TRUE,TRUE);

INSERT INTO EXCHANGE_LOGS.CONVERSIONS VALUES
  ('V202501-LI3001-01','I202501-LI3001-01','2025-01-10 19:30:00','Subscription',15.99,'last_click',2),
  ('V202502-LI3001-01','I202502-LI3001-01','2025-02-10 20:00:00','Subscription',15.99,'last_click',2),
  ('V202503-LI3001-01','I202503-LI3001-01','2025-03-11 08:00:00','Subscription',15.99,'last_click',14),
  ('V202504-LI3001-01','I202504-LI3001-01','2025-04-12 10:00:00','Subscription',15.99,'view_through',48),
  ('V202505-LI3001-01','I202505-LI3001-01','2025-05-11 21:00:00','Subscription',15.99,'last_click',28),
  ('V202506-LI3001-01','I202506-LI3001-01','2025-06-12 12:00:00','Subscription',15.99,'last_click',26),
  ('V202507-LI3001-01','I202507-LI3001-01','2025-07-11 12:00:00','Subscription',15.99,'last_click',18);

-- Some losses for LI3001
INSERT INTO EXCHANGE_LOGS.LOSSES VALUES
  ('L202501-LI3001-01','A202501-LI3001-01','LI3001','Creative filtered','2025-01-10 18:00:00');

-- 6) Convenience views
CREATE OR REPLACE VIEW EXCHANGE_LOGS.IMPRESSION_SPEND AS
SELECT *, (CLEARING_PRICE_CPM / 1000) AS SPEND_USD
FROM EXCHANGE_LOGS.WINS_IMPRESSIONS;

-- 7) Quick integrity check
SELECT 'Auctions' AS table_name, COUNT(*) AS row_count FROM EXCHANGE_LOGS.AUCTIONS
UNION ALL SELECT 'Bids', COUNT(*) FROM EXCHANGE_LOGS.BIDS
UNION ALL SELECT 'Wins/Impressions', COUNT(*) FROM EXCHANGE_LOGS.WINS_IMPRESSIONS
UNION ALL SELECT 'Losses', COUNT(*) FROM EXCHANGE_LOGS.LOSSES
UNION ALL SELECT 'Conversions', COUNT(*) FROM EXCHANGE_LOGS.CONVERSIONS;

-- =====================================================================
-- Script completion
-- =====================================================================
-- 
-- DATA SUMMARY:
-- This script creates a FreeWheel-style AdTech data platform with:
--
-- DIMENSIONS:
--   - 10 Advertisers across diverse verticals (Retail, Auto, Streaming, Electronics, Food, Travel, Insurance, Gaming, Home, Fitness)
--   - 17 Campaigns spanning Aug 2024 - Jul 2025 with varying objectives and budgets
--   - 24 Line Items with different bid strategies, budgets, channels (CTV/Mobile), and platforms
--   - 24 Creatives in various formats and durations
--   - 10 Publishers across CTV and Mobile channels
--   - 12 Inventory Units with diverse content genres and IAB categories
--   - 3 Supply Side Platforms (SSPs)
--
-- EVENTS (12-month period):
--   - 50+ Auctions with detailed timestamps, pricing, and targeting attributes
--   - 47+ Bids with varied CPM pricing showing market dynamics
--   - 40+ Wins/Impressions demonstrating ~85% win rate with viewability and click tracking
--   - 4 Losses showing bid failures (outbid, below floor, creative filtered)
--   - 20+ Conversions across multiple types (Leads, Purchases, Subscriptions, App Installs)
--     with varied attribution models and time windows
--
-- KEY ANALYTICS PATTERNS DEMONSTRATED:
--   1. Seasonal Trends: CPMs increase from Aug→Dec (holiday season), decrease Jan→Apr
--   2. Campaign Performance: Always-on campaigns (LI2001, LI8002/8003) vs. seasonal bursts
--   3. Conversion Funnels: From impression → click → conversion with time-to-convert metrics
--   4. Multi-touch Attribution: Both last_click and view_through attribution
--   5. Cross-Channel: CTV (Roku, FireTV) and Mobile (iOS, Android) performance comparison
--   6. Bid Landscape: Floor prices, clearing prices, and competitive dynamics
--   7. Publisher Mix: Performance across News, Sports, Entertainment, Gaming content
--
-- QUERY USE CASES ENABLED:
--   - Campaign ROI and ROAS analysis
--   - Win rate and bid optimization analytics
--   - Publisher and inventory performance
--   - Conversion attribution and time-lag analysis
--   - Trend analysis (daily, weekly, monthly patterns)
--   - Cross-dimensional drill-downs (advertiser → campaign → line item → creative)
--   - Spend analysis and budget pacing
--   - Viewability and engagement metrics
--
-- =====================================================================
SELECT 'FreeWheel synthetic data creation completed successfully!' AS status;

-- =====================================================================
-- OPTIONAL: Make Data "Recent" for Semantic Model Queries
-- =====================================================================
-- 
-- The semantic model's verified queries use CURRENT_DATE() and relative date functions.
-- To make this historical data (Aug 2024 - Jul 2025) work with those queries,
-- run the following UPDATE statements to shift all timestamps to recent dates:
--
-- This shifts the data so Aug 2024 becomes ~120 days ago from today,
-- making the full 12-month dataset span approximately the last 4 months.


-- Shift auction timestamps
UPDATE FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.AUCTIONS
SET AUCTION_TIMESTAMP = DATEADD(day, 
    DATEDIFF(day, '2024-08-01'::DATE, AUCTION_TIMESTAMP::DATE), 
    DATEADD(day, -120, CURRENT_DATE()));

-- Shift bid timestamps  
UPDATE FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.BIDS
SET BID_TIMESTAMP = DATEADD(day,
    DATEDIFF(day, '2024-08-01'::DATE, BID_TIMESTAMP::DATE),
    DATEADD(day, -120, CURRENT_DATE()));

-- Shift impression timestamps
UPDATE FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.WINS_IMPRESSIONS  
SET IMPRESSION_TIMESTAMP = DATEADD(day,
    DATEDIFF(day, '2024-08-01'::DATE, IMPRESSION_TIMESTAMP::DATE),
    DATEADD(day, -120, CURRENT_DATE()));

-- Shift conversion timestamps
UPDATE FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.CONVERSIONS
SET CONVERSION_TIMESTAMP = DATEADD(day,
    DATEDIFF(day, '2024-08-01'::DATE, CONVERSION_TIMESTAMP::DATE),
    DATEADD(day, -120, CURRENT_DATE()));

-- Shift loss timestamps
UPDATE FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.LOSSES
SET LOSS_TIMESTAMP = DATEADD(day,
    DATEDIFF(day, '2024-08-01'::DATE, LOSS_TIMESTAMP::DATE),
    DATEADD(day, -120, CURRENT_DATE()));

-- Update campaign flight dates
UPDATE FREEWHEEL_DATA_PLATFORM.AD_SALES.CAMPAIGNS
SET START_DATE = DATEADD(day,
        DATEDIFF(day, '2024-08-01'::DATE, START_DATE),
        DATEADD(day, -120, CURRENT_DATE())),
    END_DATE = DATEADD(day,
        DATEDIFF(day, '2024-08-01'::DATE, END_DATE),
        DATEADD(day, -120, CURRENT_DATE()));

-- Verify the new date ranges
SELECT 'Updated Date Ranges:' AS info;
SELECT 'Auctions' AS table_name, MIN(AUCTION_TIMESTAMP) AS min_date, MAX(AUCTION_TIMESTAMP) AS max_date 
FROM FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.AUCTIONS
UNION ALL
SELECT 'Impressions', MIN(IMPRESSION_TIMESTAMP), MAX(IMPRESSION_TIMESTAMP)
FROM FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.WINS_IMPRESSIONS
UNION ALL  
SELECT 'Conversions', MIN(CONVERSION_TIMESTAMP), MAX(CONVERSION_TIMESTAMP)
FROM FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.CONVERSIONS
UNION ALL
SELECT 'Campaigns', MIN(START_DATE)::TIMESTAMP, MAX(END_DATE)::TIMESTAMP
FROM FREEWHEEL_DATA_PLATFORM.AD_SALES.CAMPAIGNS;


-- =====================================================================
-- Alternative: Generate Recent Data with GENERATOR
-- =====================================================================
--
-- For production-scale recent data (10K+ events in last 90 days), use Snowflake's GENERATOR:

-- Example: Generate 3000 additional impressions over last 60 days
-- Step 1: Create a temporary staging table with generated rows
CREATE OR REPLACE TEMPORARY TABLE temp_generated_impressions AS
SELECT 
  ROW_NUMBER() OVER (ORDER BY NULL) AS seq_num,
  UNIFORM(1, 60, RANDOM()) AS days_ago,
  UNIFORM(0, 1439, RANDOM()) AS minute_of_day,
  UNIFORM(8.0, 18.0, RANDOM()) AS cpm_value,
  UNIFORM(0.0, 1.0, RANDOM()) AS viewable_rand,
  UNIFORM(0.0, 1.0, RANDOM()) AS click_rand
FROM TABLE(GENERATOR(ROWCOUNT => 3000));

-- Step 2: Insert into impressions table with joins to dimension tables
INSERT INTO FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.WINS_IMPRESSIONS
SELECT 
  'I-GENERATED-' || tg.seq_num AS IMPRESSION_ID,
  NULL AS AUCTION_ID,
  NULL AS BID_ID,
  li.LINE_ITEM_ID,
  c.CAMPAIGN_ID,
  c.ADVERTISER_ID,
  inv.PUBLISHER_ID,
  inv.INVENTORY_ID,
  inv.CHANNEL,
  inv.PLATFORM AS DEVICE_TYPE,
  'Video' AS AD_FORMAT,
  'United States' AS GEO_COUNTRY,
  ROUND(tg.cpm_value::DECIMAL(10,4), 4) AS CLEARING_PRICE_CPM,
  DATEADD(minute, tg.minute_of_day, DATEADD(day, -tg.days_ago, CURRENT_DATE())) AS IMPRESSION_TIMESTAMP,
  tg.viewable_rand > 0.15 AS WAS_VIEWABLE,  -- 85% viewability
  tg.click_rand > 0.95 AS WAS_CLICKED        -- 5% CTR
FROM temp_generated_impressions tg
CROSS JOIN (SELECT * FROM FREEWHEEL_DATA_PLATFORM.AD_SALES.LINE_ITEMS ORDER BY RANDOM() LIMIT 1) li
CROSS JOIN (SELECT * FROM FREEWHEEL_DATA_PLATFORM.INVENTORY.INVENTORY_UNITS ORDER BY RANDOM() LIMIT 1) inv
CROSS JOIN (SELECT * FROM FREEWHEEL_DATA_PLATFORM.AD_SALES.CAMPAIGNS ORDER BY RANDOM() LIMIT 1) c
WHERE DATEADD(day, -tg.days_ago, CURRENT_DATE()) BETWEEN c.START_DATE AND c.END_DATE;

-- Step 3: Clean up
DROP TABLE IF EXISTS temp_generated_impressions;

-- This generates 3000 impressions distributed across the last 60 days with realistic:
-- - Line item and inventory selections
-- - CPM ranges ($8-$18)
-- - Timestamps throughout the day
-- - Viewability rates (~85%)
-- - Click-through rates (~5%)



