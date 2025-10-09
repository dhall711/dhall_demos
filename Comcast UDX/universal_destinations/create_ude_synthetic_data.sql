-- =====================================================================
-- Universal Destinations & Experiences - Synthetic Data Creation Script
-- =====================================================================
-- This script creates comprehensive synthetic test data for the UDE
-- Snowflake Intelligence semantic models
-- =====================================================================

-- 1. Create database and schemas
CREATE DATABASE IF NOT EXISTS UNIVERSAL_DATA_PLATFORM
  COMMENT = 'Universal Destinations & Experiences data platform for analytics';

CREATE SCHEMA IF NOT EXISTS UNIVERSAL_DATA_PLATFORM.GUEST_ANALYTICS
  COMMENT = 'Guest data, visits, and preferences analytics';

CREATE SCHEMA IF NOT EXISTS UNIVERSAL_DATA_PLATFORM.PARK_OPERATIONS
  COMMENT = 'Park operations, attractions, and capacity management';

CREATE SCHEMA IF NOT EXISTS UNIVERSAL_DATA_PLATFORM.REVENUE_ANALYTICS
  COMMENT = 'Revenue data across tickets, merchandise, and dining';

CREATE SCHEMA IF NOT EXISTS UNIVERSAL_DATA_PLATFORM.STAFF_MANAGEMENT
  COMMENT = 'Employee data, schedules, and training records';

CREATE SCHEMA IF NOT EXISTS UNIVERSAL_DATA_PLATFORM.HOTEL_ACCOMMODATION
  COMMENT = 'Hotel properties, reservations, and amenity usage analytics';

-- Set context
USE DATABASE UNIVERSAL_DATA_PLATFORM;

-- =====================================================================
-- 2. GUEST ANALYTICS TABLES
-- =====================================================================

-- Guest Profiles Table
CREATE OR REPLACE TABLE GUEST_ANALYTICS.GUEST_PROFILES (
    GUEST_ID VARCHAR(50) PRIMARY KEY,
    FIRST_NAME VARCHAR(100),
    LAST_NAME VARCHAR(100),
    EMAIL_ADDRESS VARCHAR(255),
    PHONE_NUMBER VARCHAR(20),
    DATE_OF_BIRTH DATE,
    ZIP_CODE VARCHAR(10),
    STATE VARCHAR(50),
    COUNTRY VARCHAR(50),
    PREFERRED_LANGUAGE VARCHAR(20),
    MEMBERSHIP_TIER VARCHAR(20),
    FAMILY_SIZE NUMBER(2),
    PREFERRED_PARK VARCHAR(50),
    ACCOUNT_CREATED_DATE TIMESTAMP_NTZ,
    LAST_VISIT_DATE TIMESTAMP_NTZ,
    TOTAL_SPEND_AMOUNT DECIMAL(10,2),
    MEMBERSHIP_VALUE DECIMAL(8,2),
    CURRENT_PERFORMANCE_RATING DECIMAL(4,2)
);

-- Visit Sessions Table
CREATE OR REPLACE TABLE GUEST_ANALYTICS.VISIT_SESSIONS (
    VISIT_ID VARCHAR(50) PRIMARY KEY,
    GUEST_ID VARCHAR(50),
    PARK_LOCATION VARCHAR(50),
    VISIT_DATE DATE,
    ENTRY_TIME TIMESTAMP_NTZ,
    EXIT_TIME TIMESTAMP_NTZ,
    TICKET_TYPE VARCHAR(30),
    WEATHER_CONDITIONS VARCHAR(20),
    CROWD_LEVEL VARCHAR(20),
    SPEND_AMOUNT DECIMAL(8,2),
    ATTRACTION_ID VARCHAR(50)
);

-- Guest Preferences Table
CREATE OR REPLACE TABLE GUEST_ANALYTICS.GUEST_PREFERENCES (
    PREFERENCE_ID VARCHAR(50) PRIMARY KEY,
    GUEST_ID VARCHAR(50),
    PREFERENCE_CATEGORY VARCHAR(50),
    PREFERENCE_VALUE VARCHAR(100),
    PREFERENCE_STRENGTH VARCHAR(20),
    PREFERENCE_SCORE NUMBER(2)
);

-- =====================================================================
-- 3. PARK OPERATIONS TABLES
-- =====================================================================

-- Attractions Table
CREATE OR REPLACE TABLE PARK_OPERATIONS.ATTRACTIONS (
    ATTRACTION_ID VARCHAR(50) PRIMARY KEY,
    ATTRACTION_NAME VARCHAR(200),
    PARK_LOCATION VARCHAR(50),
    THEMED_AREA VARCHAR(100),
    ATTRACTION_TYPE VARCHAR(50),
    FRANCHISE VARCHAR(50),
    HEIGHT_REQUIREMENT_INCHES NUMBER(3),
    THEORETICAL_HOURLY_CAPACITY NUMBER(5),
    RIDE_DURATION_MINUTES NUMBER(3),
    ACCESSIBILITY_FEATURES VARCHAR(500),
    OPERATIONAL_STATUS VARCHAR(20),
    OPENING_DATE DATE,
    LAST_MAJOR_MAINTENANCE_DATE DATE,
    DAILY_GUEST_COUNT NUMBER(6),
    WAIT_TIME_MINUTES NUMBER(4),
    ACTUAL_HOURLY_CAPACITY NUMBER(5),
    GUEST_SATISFACTION_RATING DECIMAL(4,2)
);

-- Wait Times Table
CREATE OR REPLACE TABLE PARK_OPERATIONS.WAIT_TIMES (
    WAIT_TIME_ID VARCHAR(50) PRIMARY KEY,
    ATTRACTION_ID VARCHAR(50),
    RECORDED_TIMESTAMP TIMESTAMP_NTZ,
    WAIT_TIME_MINUTES NUMBER(4),
    POSTED_WAIT_TIME_MINUTES NUMBER(4),
    WEATHER_CONDITION VARCHAR(20),
    SPECIAL_EVENT VARCHAR(100),
    CROWD_LEVEL VARCHAR(20)
);

-- Hourly Capacity Table
CREATE OR REPLACE TABLE PARK_OPERATIONS.HOURLY_CAPACITY (
    CAPACITY_RECORD_ID VARCHAR(50) PRIMARY KEY,
    ATTRACTION_ID VARCHAR(50),
    OPERATING_DATE DATE,
    OPERATING_HOUR NUMBER(2),
    GUESTS_PER_HOUR NUMBER(5),
    THEORETICAL_CAPACITY NUMBER(5),
    DOWNTIME_MINUTES NUMBER(3),
    WEATHER_IMPACT VARCHAR(20),
    STAFFING_LEVEL VARCHAR(20),
    OPERATIONAL_EFFICIENCY_SCORE DECIMAL(4,2)
);

-- =====================================================================
-- 4. REVENUE ANALYTICS TABLES
-- =====================================================================

-- Ticket Sales Table
CREATE OR REPLACE TABLE REVENUE_ANALYTICS.TICKET_SALES (
    TICKET_SALE_ID VARCHAR(50) PRIMARY KEY,
    GUEST_ID VARCHAR(50),
    PARK_LOCATION VARCHAR(50),
    TICKET_TYPE VARCHAR(50),
    TICKET_CATEGORY VARCHAR(20),
    PURCHASE_CHANNEL VARCHAR(30),
    PRICING_TIER VARCHAR(20),
    PROMOTIONAL_CODE VARCHAR(20),
    BUNDLE_PACKAGE VARCHAR(50),
    GUEST_SEGMENT VARCHAR(30),
    PURCHASE_TIMESTAMP TIMESTAMP_NTZ,
    VISIT_DATE DATE,
    TICKET_PRICE DECIMAL(8,2),
    DISCOUNT_AMOUNT DECIMAL(6,2)
);

-- Merchandise Sales Table
CREATE OR REPLACE TABLE REVENUE_ANALYTICS.MERCHANDISE_SALES (
    MERCHANDISE_SALE_ID VARCHAR(50) PRIMARY KEY,
    GUEST_ID VARCHAR(50),
    STORE_LOCATION_ID VARCHAR(50),
    STORE_TYPE VARCHAR(50),
    PRODUCT_CATEGORY VARCHAR(50),
    FRANCHISE VARCHAR(50),
    PRODUCT_NAME VARCHAR(200),
    PRICE_TIER VARCHAR(20),
    IS_SEASONAL_ITEM BOOLEAN,
    HAS_PERSONALIZATION BOOLEAN,
    PURCHASE_TIMESTAMP TIMESTAMP_NTZ,
    UNIT_PRICE DECIMAL(8,2),
    QUANTITY NUMBER(3),
    COST_OF_GOODS DECIMAL(8,2)
);

-- Food & Beverage Sales Table
CREATE OR REPLACE TABLE REVENUE_ANALYTICS.FOOD_BEVERAGE_SALES (
    FB_SALE_ID VARCHAR(50) PRIMARY KEY,
    GUEST_ID VARCHAR(50),
    RESTAURANT_ID VARCHAR(50),
    RESTAURANT_TYPE VARCHAR(50),
    THEMED_RESTAURANT VARCHAR(100),
    MEAL_PERIOD VARCHAR(20),
    ITEM_CATEGORY VARCHAR(30),
    DIETARY_PREFERENCE VARCHAR(30),
    FRANCHISE_THEMED VARCHAR(50),
    IS_SPECIAL_EVENT_MENU BOOLEAN,
    PURCHASE_TIMESTAMP TIMESTAMP_NTZ,
    ITEM_PRICE DECIMAL(6,2),
    QUANTITY NUMBER(2),
    ORDER_TOTAL DECIMAL(8,2),
    GUEST_RATING DECIMAL(4,2)
);

-- =====================================================================
-- 5. STAFF MANAGEMENT TABLES
-- =====================================================================

-- Employee Profiles Table
CREATE OR REPLACE TABLE STAFF_MANAGEMENT.EMPLOYEE_PROFILES (
    EMPLOYEE_ID VARCHAR(50) PRIMARY KEY,
    FIRST_NAME VARCHAR(100),
    LAST_NAME VARCHAR(100),
    EMPLOYEE_EMAIL VARCHAR(255),
    PHONE_NUMBER VARCHAR(20),
    PARK_LOCATION VARCHAR(50),
    DEPARTMENT VARCHAR(50),
    JOB_TITLE VARCHAR(100),
    EMPLOYMENT_TYPE VARCHAR(20),
    SHIFT_PREFERENCE VARCHAR(20),
    CERTIFICATION_LEVEL VARCHAR(20),
    LANGUAGE_SKILLS VARCHAR(200),
    EMERGENCY_CONTACT_NAME VARCHAR(100),
    EMERGENCY_CONTACT_PHONE VARCHAR(20),
    HIRE_DATE DATE,
    LAST_PROMOTION_DATE DATE,
    HOURLY_WAGE DECIMAL(6,2),
    ANNUAL_SALARY DECIMAL(10,2),
    CURRENT_PERFORMANCE_RATING DECIMAL(4,2)
);

-- Work Schedules Table
CREATE OR REPLACE TABLE STAFF_MANAGEMENT.WORK_SCHEDULES (
    SCHEDULE_ID VARCHAR(50) PRIMARY KEY,
    EMPLOYEE_ID VARCHAR(50),
    WORK_DATE DATE,
    SHIFT_TYPE VARCHAR(30),
    LOCATION_ASSIGNMENT VARCHAR(100),
    ROLE_ASSIGNMENT VARCHAR(100),
    SCHEDULE_STATUS VARCHAR(30),
    IS_OVERTIME_ELIGIBLE BOOLEAN,
    SPECIAL_EVENT VARCHAR(100),
    SHIFT_START_TIME TIMESTAMP_NTZ,
    SHIFT_END_TIME TIMESTAMP_NTZ,
    ACTUAL_CLOCK_IN_TIME TIMESTAMP_NTZ,
    ACTUAL_CLOCK_OUT_TIME TIMESTAMP_NTZ,
    HOURS_WORKED DECIMAL(4,2)
);

-- Training Records Table
CREATE OR REPLACE TABLE STAFF_MANAGEMENT.TRAINING_RECORDS (
    TRAINING_RECORD_ID VARCHAR(50) PRIMARY KEY,
    EMPLOYEE_ID VARCHAR(50),
    TRAINING_MODULE VARCHAR(200),
    TRAINING_CATEGORY VARCHAR(50),
    TRAINING_TYPE VARCHAR(30),
    IS_CERTIFICATION_REQUIRED BOOLEAN,
    TRAINER_NAME VARCHAR(100),
    TRAINING_STATUS VARCHAR(20),
    TRAINING_COMPLETION_DATE DATE,
    CERTIFICATION_EXPIRY_DATE DATE,
    TRAINING_SCORE NUMBER(3),
    TRAINING_DURATION_HOURS DECIMAL(4,2),
    ATTEMPT_NUMBER NUMBER(2)
);

-- =====================================================================
-- 5. HOTEL ACCOMMODATION TABLES
-- =====================================================================

-- Hotel Properties Table
CREATE OR REPLACE TABLE HOTEL_ACCOMMODATION.HOTEL_PROPERTIES (
    PROPERTY_ID VARCHAR(50) PRIMARY KEY,
    PROPERTY_NAME VARCHAR(200),
    PROPERTY_TYPE VARCHAR(50),
    PARK_LOCATION VARCHAR(50),
    THEME_LEVEL VARCHAR(50),
    STAR_RATING NUMBER(1),
    TOTAL_ROOMS NUMBER(4),
    AMENITIES_LEVEL VARCHAR(20),
    HAS_EARLY_PARK_ADMISSION BOOLEAN,
    INCLUDES_EXPRESS_PASS BOOLEAN,
    OPENING_DATE DATE,
    LAST_RENOVATION_DATE DATE,
    AVERAGE_DAILY_RATE DECIMAL(8,2),
    OCCUPANCY_RATE DECIMAL(5,2),
    GUEST_SATISFACTION_RATING DECIMAL(4,2)
);

-- Room Reservations Table
CREATE OR REPLACE TABLE HOTEL_ACCOMMODATION.ROOM_RESERVATIONS (
    RESERVATION_ID VARCHAR(50) PRIMARY KEY,
    GUEST_ID VARCHAR(50),
    PROPERTY_ID VARCHAR(50),
    ROOM_TYPE VARCHAR(30),
    ROOM_VIEW VARCHAR(30),
    BOOKING_CHANNEL VARCHAR(30),
    GUEST_TYPE VARCHAR(20),
    PACKAGE_TYPE VARCHAR(50),
    CANCELLATION_POLICY VARCHAR(20),
    SPECIAL_REQUESTS VARCHAR(500),
    BOOKING_TIMESTAMP TIMESTAMP_NTZ,
    CHECK_IN_DATE DATE,
    CHECK_OUT_DATE DATE,
    ACTUAL_CHECK_IN_TIME TIMESTAMP_NTZ,
    ACTUAL_CHECK_OUT_TIME TIMESTAMP_NTZ,
    ROOM_RATE DECIMAL(8,2),
    TOTAL_RESERVATION_AMOUNT DECIMAL(10,2),
    GUEST_SATISFACTION_RATING DECIMAL(4,2)
);

-- Hotel Amenities Usage Table
CREATE OR REPLACE TABLE HOTEL_ACCOMMODATION.AMENITIES_USAGE (
    USAGE_ID VARCHAR(50) PRIMARY KEY,
    RESERVATION_ID VARCHAR(50),
    AMENITY_TYPE VARCHAR(50),
    AMENITY_NAME VARCHAR(100),
    USAGE_CATEGORY VARCHAR(30),
    SERVICE_LOCATION VARCHAR(100),
    USAGE_TIMESTAMP TIMESTAMP_NTZ,
    USAGE_DURATION_HOURS DECIMAL(4,2),
    SERVICE_CHARGE DECIMAL(8,2),
    GUEST_RATING DECIMAL(4,2)
);

-- =====================================================================
-- 6. INSERT SYNTHETIC DATA
-- =====================================================================

-- Insert Guest Profiles Data
INSERT INTO GUEST_ANALYTICS.GUEST_PROFILES VALUES
('G001', 'Emma', 'Johnson', 'emma.johnson@email.com', '555-0101', '1985-03-15', '90210', 'California', 'USA', 'English', 'Premier', 4, 'Universal Studios Hollywood', '2020-01-15 10:30:00', '2024-07-20 14:00:00', 2850.75, 599.99, 9.2),
('G002', 'Michael', 'Chen', 'michael.chen@email.com', '555-0102', '1992-07-22', '10001', 'New York', 'USA', 'English', 'Standard', 2, 'Universal Orlando Resort', '2021-05-03 09:15:00', '2024-08-01 16:30:00', 1950.50, 299.99, 8.7),
('G003', 'Sofia', 'Rodriguez', 'sofia.rodriguez@email.com', '555-0103', '1978-11-08', '33101', 'Florida', 'USA', 'Spanish', 'Preferred', 3, 'Universal Orlando Resort', '2019-08-20 11:45:00', '2024-07-15 18:00:00', 4200.25, 899.99, 9.5),
('G004', 'James', 'Wilson', 'james.wilson@email.com', '555-0104', '1990-04-12', '60601', 'Illinois', 'USA', 'English', 'Standard', 1, 'Universal Studios Hollywood', '2022-02-14 13:20:00', '2024-06-30 15:45:00', 1200.00, 299.99, 7.8),
('G005', 'Yuki', 'Tanaka', 'yuki.tanaka@email.com', '555-0105', '1988-09-30', '100-0001', 'Tokyo', 'Japan', 'Japanese', 'Premier', 5, 'Universal Studios Japan', '2020-12-01 08:00:00', '2024-08-05 20:15:00', 3500.80, 599.99, 9.1),
('G006', 'Oliver', 'Smith', 'oliver.smith@email.com', '555-0106', '1995-01-25', 'SW1A 1AA', 'London', 'UK', 'English', 'Standard', 2, 'Universal Orlando Resort', '2023-06-10 12:00:00', '2024-07-25 17:30:00', 1650.30, 299.99, 8.4),
('G007', 'Isabella', 'Garcia', 'isabella.garcia@email.com', '555-0107', '1983-12-18', '28001', 'Madrid', 'Spain', 'Spanish', 'Preferred', 4, 'Universal Studios Hollywood', '2018-11-25 14:15:00', '2024-08-03 19:45:00', 3850.90, 899.99, 9.3),
('G008', 'Alexander', 'Brown', 'alex.brown@email.com', '555-0108', '1991-06-07', '75001', 'Texas', 'USA', 'English', 'Premier', 3, 'Universal Orlando Resort', '2021-09-12 10:45:00', '2024-07-28 16:00:00', 2750.65, 599.99, 8.9),
('G009', 'Li', 'Wang', 'li.wang@email.com', '555-0109', '1987-02-14', '100000', 'Beijing', 'China', 'Mandarin', 'Standard', 2, 'Universal Beijing Resort', '2022-04-08 09:30:00', '2024-08-02 14:20:00', 1800.45, 299.99, 8.6),
('G010', 'Priya', 'Patel', 'priya.patel@email.com', '555-0110', '1994-08-03', '400001', 'Mumbai', 'India', 'English', 'Premier', 6, 'Universal Studios Singapore', '2023-01-20 11:00:00', '2024-07-30 18:30:00', 2200.75, 599.99, 8.8);

-- Insert Visit Sessions Data
INSERT INTO GUEST_ANALYTICS.VISIT_SESSIONS VALUES
('V001', 'G001', 'Universal Studios Hollywood', '2024-07-20', '2024-07-20 09:00:00', '2024-07-20 21:00:00', 'Single Day', 'Sunny', 'High', 285.50, 'A001'),
('V002', 'G002', 'Universal Orlando Resort', '2024-08-01', '2024-08-01 10:00:00', '2024-08-01 20:00:00', 'Multi-Day', 'Partly Cloudy', 'Medium', 195.75, 'A002'),
('V003', 'G003', 'Universal Orlando Resort', '2024-07-15', '2024-07-15 08:30:00', '2024-07-15 22:00:00', 'Annual Pass', 'Sunny', 'Peak', 420.25, 'A003'),
('V004', 'G004', 'Universal Studios Hollywood', '2024-06-30', '2024-06-30 11:00:00', '2024-06-30 19:00:00', 'Single Day', 'Overcast', 'Low', 120.00, 'A004'),
('V005', 'G005', 'Universal Studios Japan', '2024-08-05', '2024-08-05 09:15:00', '2024-08-05 21:30:00', 'Annual Pass', 'Rainy', 'Medium', 350.80, 'A005'),
('V006', 'G006', 'Universal Orlando Resort', '2024-07-25', '2024-07-25 10:30:00', '2024-07-25 18:00:00', 'Multi-Day', 'Sunny', 'High', 165.30, 'A006'),
('V007', 'G007', 'Universal Studios Hollywood', '2024-08-03', '2024-08-03 08:00:00', '2024-08-03 23:00:00', 'Annual Pass', 'Clear', 'Peak', 385.90, 'A007'),
('V008', 'G008', 'Universal Orlando Resort', '2024-07-28', '2024-07-28 09:45:00', '2024-07-28 20:30:00', 'Special Event', 'Partly Cloudy', 'High', 275.65, 'A008'),
('V009', 'G009', 'Universal Beijing Resort', '2024-08-02', '2024-08-02 10:00:00', '2024-08-02 19:15:00', 'Single Day', 'Cloudy', 'Medium', 180.45, 'A009'),
('V010', 'G010', 'Universal Studios Singapore', '2024-07-30', '2024-07-30 11:30:00', '2024-07-30 21:00:00', 'Multi-Day', 'Humid', 'High', 220.75, 'A010');

-- Insert Guest Preferences Data
INSERT INTO GUEST_ANALYTICS.GUEST_PREFERENCES VALUES
('P001', 'G001', 'Attraction Type', 'Thrill Rides', 'Strong', 9),
('P002', 'G001', 'Franchise', 'Harry Potter', 'Strong', 10),
('P003', 'G002', 'Food', 'Quick Service', 'Moderate', 7),
('P004', 'G002', 'Merchandise', 'Collectibles', 'Strong', 8),
('P005', 'G003', 'Experience', 'VIP Tours', 'Strong', 9),
('P006', 'G003', 'Franchise', 'Jurassic Park', 'Moderate', 8),
('P007', 'G004', 'Attraction Type', 'Family Rides', 'Moderate', 6),
('P008', 'G005', 'Franchise', 'Nintendo', 'Strong', 10),
('P009', 'G005', 'Food', 'Themed Dining', 'Strong', 9),
('P010', 'G006', 'Merchandise', 'Apparel', 'Moderate', 7);

-- Insert Attractions Data
INSERT INTO PARK_OPERATIONS.ATTRACTIONS VALUES
('A001', 'Harry Potter and the Forbidden Journey', 'Universal Studios Hollywood', 'Wizarding World of Harry Potter', 'Thrill Ride', 'Harry Potter', 48, 1800, 4, 'Wheelchair accessible with transfer', 'Open', '2016-04-07', '2024-03-15', 15000, 45, 1650, 9.2),
('A002', 'The Amazing Adventures of Spider-Man', 'Universal Orlando Resort', 'Marvel Super Hero Island', 'Thrill Ride', 'Marvel', 40, 2400, 5, 'Wheelchair accessible', 'Open', '1999-05-28', '2024-01-20', 18000, 25, 2200, 9.0),
('A003', 'Jurassic Park River Adventure', 'Universal Orlando Resort', 'Jurassic Park', 'Water Ride', 'Jurassic Park', 42, 2000, 6, 'Wheelchair accessible with transfer', 'Open', '1999-05-28', '2024-02-10', 16500, 35, 1850, 8.8),
('A004', 'Studio Tour', 'Universal Studios Hollywood', 'Studio Tour', 'Experience', 'Universal Studios', 0, 8000, 45, 'Fully wheelchair accessible', 'Open', '1964-07-15', '2024-04-05', 25000, 15, 7500, 8.5),
('A005', 'Super Nintendo World - Mario Kart', 'Universal Studios Japan', 'Super Nintendo World', 'Family Ride', 'Nintendo', 42, 1500, 5, 'Wheelchair accessible', 'Open', '2021-03-18', '2024-05-12', 12000, 60, 1350, 9.4),
('A006', 'The Mummy Returns', 'Universal Orlando Resort', 'New York', 'Thrill Ride', 'Universal Monsters', 48, 1900, 3, 'Wheelchair accessible with transfer', 'Open', '2004-05-21', '2024-06-01', 14000, 40, 1750, 8.7),
('A007', 'Transformers: The Ride-3D', 'Universal Studios Hollywood', 'Transformers', 'Thrill Ride', 'Transformers', 40, 1600, 4, 'Wheelchair accessible', 'Open', '2012-05-25', '2024-03-28', 13500, 50, 1480, 8.9),
('A008', 'Hagrid''s Magical Creatures Motorbike Adventure', 'Universal Orlando Resort', 'Wizarding World of Harry Potter', 'Family Ride', 'Harry Potter', 48, 1200, 3, 'Wheelchair accessible with transfer', 'Open', '2019-06-13', '2024-07-08', 11000, 90, 1100, 9.6),
('A009', 'Decepticoaster', 'Universal Beijing Resort', 'Transformers Metrobase', 'Thrill Ride', 'Transformers', 48, 1400, 2, 'Wheelchair accessible with transfer', 'Open', '2021-09-20', '2024-04-15', 10500, 55, 1260, 8.6),
('A010', 'Jurassic Park Rapids Adventure', 'Universal Studios Singapore', 'The Lost World', 'Water Ride', 'Jurassic Park', 42, 1800, 7, 'Wheelchair accessible', 'Open', '2010-03-18', '2024-02-28', 13000, 30, 1650, 8.4);

-- Insert Wait Times Data
INSERT INTO PARK_OPERATIONS.WAIT_TIMES VALUES
('WT001', 'A001', '2024-08-05 10:00:00', 45, 40, 'Sunny', NULL, 'High'),
('WT002', 'A002', '2024-08-05 11:00:00', 25, 30, 'Partly Cloudy', NULL, 'Medium'),
('WT003', 'A003', '2024-08-05 12:00:00', 35, 35, 'Sunny', NULL, 'High'),
('WT004', 'A004', '2024-08-05 13:00:00', 15, 20, 'Sunny', NULL, 'Medium'),
('WT005', 'A005', '2024-08-05 14:00:00', 60, 55, 'Clear', NULL, 'Peak'),
('WT006', 'A006', '2024-08-05 15:00:00', 40, 45, 'Partly Cloudy', NULL, 'High'),
('WT007', 'A007', '2024-08-05 16:00:00', 50, 45, 'Sunny', NULL, 'High'),
('WT008', 'A008', '2024-08-05 17:00:00', 90, 85, 'Sunny', NULL, 'Peak'),
('WT009', 'A009', '2024-08-05 18:00:00', 55, 60, 'Cloudy', NULL, 'High'),
('WT010', 'A010', '2024-08-05 19:00:00', 30, 35, 'Clear', NULL, 'Medium');

-- Insert Hourly Capacity Data
INSERT INTO PARK_OPERATIONS.HOURLY_CAPACITY VALUES
('HC001', 'A001', '2024-08-05', 10, 1650, 1800, 5, 'None', 'Full', 91.67),
('HC002', 'A002', '2024-08-05', 11, 2200, 2400, 0, 'None', 'Full', 91.67),
('HC003', 'A003', '2024-08-05', 12, 1850, 2000, 3, 'None', 'Full', 92.50),
('HC004', 'A004', '2024-08-05', 13, 7500, 8000, 0, 'None', 'Full', 93.75),
('HC005', 'A005', '2024-08-05', 14, 1350, 1500, 8, 'None', 'Full', 90.00),
('HC006', 'A006', '2024-08-05', 15, 1750, 1900, 2, 'None', 'Full', 92.11),
('HC007', 'A007', '2024-08-05', 16, 1480, 1600, 4, 'None', 'Full', 92.50),
('HC008', 'A008', '2024-08-05', 17, 1100, 1200, 10, 'None', 'Full', 91.67),
('HC009', 'A009', '2024-08-05', 18, 1260, 1400, 6, 'None', 'Full', 90.00),
('HC010', 'A010', '2024-08-05', 19, 1650, 1800, 1, 'None', 'Full', 91.67);

-- Insert Ticket Sales Data
INSERT INTO REVENUE_ANALYTICS.TICKET_SALES VALUES
('TS001', 'G001', 'Universal Studios Hollywood', 'Single Day', 'Adult', 'Online', 'Peak', NULL, 'Express Pass', 'Domestic Tourist', '2024-07-18 14:30:00', '2024-07-20', 139.99, 0.00),
('TS002', 'G002', 'Universal Orlando Resort', 'Multi-Day', 'Adult', 'Mobile App', 'Regular', 'SAVE15', NULL, 'Local', '2024-07-29 09:15:00', '2024-08-01', 199.99, 30.00),
('TS003', 'G003', 'Universal Orlando Resort', 'Annual Pass', 'Adult', 'Gate', 'Premium', NULL, 'VIP Experience', 'Domestic Tourist', '2024-07-13 16:45:00', '2024-07-15', 899.99, 0.00),
('TS004', 'G004', 'Universal Studios Hollywood', 'Single Day', 'Adult', 'Partner', 'Value', 'STUDENT10', NULL, 'Local', '2024-06-28 11:20:00', '2024-06-30', 109.99, 11.00),
('TS005', 'G005', 'Universal Studios Japan', 'Annual Pass', 'Adult', 'Online', 'Premium', NULL, 'Nintendo Package', 'International', '2024-08-03 08:00:00', '2024-08-05', 599.99, 0.00),
('TS006', 'G006', 'Universal Orlando Resort', 'Multi-Day', 'Adult', 'Hotel', 'Regular', NULL, 'Vacation Package', 'International', '2024-07-23 13:45:00', '2024-07-25', 249.99, 25.00),
('TS007', 'G007', 'Universal Studios Hollywood', 'Annual Pass', 'Adult', 'Online', 'Premium', NULL, 'Express Pass', 'International', '2024-08-01 10:30:00', '2024-08-03', 899.99, 0.00),
('TS008', 'G008', 'Universal Orlando Resort', 'Special Event', 'Adult', 'Mobile App', 'Peak', 'HHN2024', 'Halloween Package', 'Domestic Tourist', '2024-07-26 15:00:00', '2024-07-28', 179.99, 0.00),
('TS009', 'G009', 'Universal Beijing Resort', 'Single Day', 'Adult', 'Online', 'Regular', NULL, NULL, 'Local', '2024-07-31 12:15:00', '2024-08-02', 89.99, 9.00),
('TS010', 'G010', 'Universal Studios Singapore', 'Multi-Day', 'Adult', 'Partner', 'Peak', 'GROUP20', 'Universal Package', 'International', '2024-07-28 14:20:00', '2024-07-30', 159.99, 32.00);

-- Insert Merchandise Sales Data
INSERT INTO REVENUE_ANALYTICS.MERCHANDISE_SALES VALUES
('MS001', 'G001', 'SL001', 'Themed Store', 'Apparel', 'Harry Potter', 'Hogwarts Robe - Adult', 'Premium', FALSE, TRUE, '2024-07-20 15:30:00', 129.99, 1, 45.00),
('MS002', 'G002', 'SL002', 'Cart', 'Collectibles', 'Marvel', 'Spider-Man Action Figure', 'Mid-Range', FALSE, FALSE, '2024-08-01 13:45:00', 34.99, 2, 12.50),
('MS003', 'G003', 'SL003', 'Universal CityWalk', 'Accessories', 'Jurassic Park', 'Dinosaur Backpack', 'Mid-Range', FALSE, FALSE, '2024-07-15 18:20:00', 79.99, 1, 28.00),
('MS004', 'G004', 'SL004', 'Themed Store', 'Toys', 'Universal Studios', 'Universal Logo T-Shirt', 'Budget', FALSE, FALSE, '2024-06-30 16:15:00', 24.99, 1, 8.50),
('MS005', 'G005', 'SL005', 'Themed Store', 'Collectibles', 'Nintendo', 'Mario Power-Up Potion', 'Premium', TRUE, FALSE, '2024-08-05 19:45:00', 89.99, 1, 30.00),
('MS006', 'G006', 'SL006', 'Cart', 'Apparel', 'Harry Potter', 'Gryffindor Scarf', 'Mid-Range', FALSE, FALSE, '2024-07-25 14:30:00', 49.99, 1, 18.00),
('MS007', 'G007', 'SL007', 'Themed Store', 'Accessories', 'Transformers', 'Autobot Keychain Set', 'Budget', FALSE, FALSE, '2024-08-03 20:00:00', 19.99, 3, 6.50),
('MS008', 'G008', 'SL008', 'Universal CityWalk', 'Collectibles', 'Universal Monsters', 'Horror Nights Pin Collection', 'Premium', TRUE, FALSE, '2024-07-28 17:30:00', 149.99, 1, 52.00),
('MS009', 'G009', 'SL009', 'Themed Store', 'Toys', 'Transformers', 'Optimus Prime Helmet', 'Luxury', FALSE, TRUE, '2024-08-02 16:45:00', 199.99, 1, 70.00),
('MS010', 'G010', 'SL010', 'Cart', 'Apparel', 'Jurassic Park', 'Raptor Squad Hoodie', 'Mid-Range', FALSE, FALSE, '2024-07-30 19:15:00', 64.99, 1, 22.50);

-- Insert Food & Beverage Sales Data
INSERT INTO REVENUE_ANALYTICS.FOOD_BEVERAGE_SALES VALUES
('FB001', 'G001', 'R001', 'Table Service', 'Three Broomsticks', 'Lunch', 'Entree', 'Regular', 'Harry Potter', FALSE, '2024-07-20 12:30:00', 18.99, 1, 45.50, 8.5),
('FB002', 'G002', 'R002', 'Quick Service', 'Comic Book Cafe', 'Snack', 'Beverage', 'Regular', 'Marvel', FALSE, '2024-08-01 15:15:00', 6.99, 2, 18.75, 7.8),
('FB003', 'G003', 'R003', 'Bar', 'Jurassic Cafe', 'Dinner', 'Alcohol', 'Regular', 'Jurassic Park', FALSE, '2024-07-15 19:45:00', 12.99, 3, 52.80, 9.1),
('FB004', 'G004', 'R004', 'Mobile Cart', 'Studio Snacks', 'Snack', 'Snack', 'Vegetarian', 'Universal Studios', FALSE, '2024-06-30 14:20:00', 8.99, 1, 12.50, 7.2),
('FB005', 'G005', 'R005', 'Table Service', 'Toadstool Cafe', 'Lunch', 'Entree', 'Allergy-Friendly', 'Nintendo', FALSE, '2024-08-05 13:00:00', 24.99, 1, 38.90, 9.3),
('FB006', 'G006', 'R006', 'Quick Service', 'Hogwarts Express Food Cart', 'Breakfast', 'Dessert', 'Regular', 'Harry Potter', FALSE, '2024-07-25 10:45:00', 9.99, 2, 25.30, 8.0),
('FB007', 'G007', 'R007', 'Bar', 'Transformers Energon Bar', 'Dinner', 'Alcohol', 'Regular', 'Transformers', TRUE, '2024-08-03 21:30:00', 15.99, 2, 42.70, 8.7),
('FB008', 'G008', 'R008', 'Table Service', 'Horror Nights Feast', 'Dinner', 'Entree', 'Regular', 'Universal Monsters', TRUE, '2024-07-28 18:00:00', 32.99, 1, 55.20, 9.0),
('FB009', 'G009', 'R009', 'Quick Service', 'Kung Fu Panda Noodle Shop', 'Lunch', 'Entree', 'Vegan', 'DreamWorks', FALSE, '2024-08-02 12:15:00', 16.99, 1, 22.85, 8.4),
('FB010', 'G010', 'R010', 'Mobile Cart', 'Minion Popcorn Cart', 'Snack', 'Snack', 'Gluten-Free', 'Illumination', FALSE, '2024-07-30 16:30:00', 11.99, 2, 28.40, 8.8);

-- Insert Employee Profiles Data
INSERT INTO STAFF_MANAGEMENT.EMPLOYEE_PROFILES VALUES
('E001', 'Sarah', 'Martinez', 'sarah.martinez@universalparks.com', '555-1001', 'Universal Studios Hollywood', 'Operations', 'Ride Operator', 'Full-Time', 'Mid-Day', 'Advanced', 'English, Spanish', 'Maria Martinez', '555-2001', '2020-03-15', '2023-03-15', 22.50, NULL, 8.9),
('E002', 'David', 'Kim', 'david.kim@universalparks.com', '555-1002', 'Universal Orlando Resort', 'Food Service', 'Restaurant Manager', 'Full-Time', 'Opening', 'Trainer', 'English, Korean', 'Jennifer Kim', '555-2002', '2018-06-01', '2022-06-01', 28.75, NULL, 9.2),
('E003', 'Ashley', 'Thompson', 'ashley.thompson@universalparks.com', '555-1003', 'Universal Studios Hollywood', 'Merchandise', 'Store Associate', 'Part-Time', 'Closing', 'Intermediate', 'English', 'Robert Thompson', '555-2003', '2022-01-10', NULL, 18.00, NULL, 8.1),
('E004', 'Carlos', 'Gonzalez', 'carlos.gonzalez@universalparks.com', '555-1004', 'Universal Orlando Resort', 'Entertainment', 'Character Performer', 'Seasonal', 'Mid-Day', 'Advanced', 'English, Spanish, Portuguese', 'Ana Gonzalez', '555-2004', '2021-05-20', '2024-05-20', 24.00, NULL, 9.5),
('E005', 'Takeshi', 'Yamamoto', 'takeshi.yamamoto@universalparks.com', '555-1005', 'Universal Studios Japan', 'Maintenance', 'Technical Specialist', 'Full-Time', 'Overnight', 'Trainer', 'Japanese, English', 'Yuki Yamamoto', '555-2005', '2017-09-12', '2021-09-12', 32.00, NULL, 9.0),
('E006', 'Emily', 'Davis', 'emily.davis@universalparks.com', '555-1006', 'Universal Orlando Resort', 'Operations', 'Attractions Supervisor', 'Full-Time', 'Opening', 'Trainer', 'English, French', 'Michael Davis', '555-2006', '2019-02-28', '2023-02-28', 26.50, NULL, 9.1),
('E007', 'Ahmed', 'Hassan', 'ahmed.hassan@universalparks.com', '555-1007', 'Universal Studios Singapore', 'Food Service', 'Chef', 'Full-Time', 'Mid-Day', 'Advanced', 'English, Arabic, Malay', 'Fatima Hassan', '555-2007', '2020-11-05', NULL, 25.75, NULL, 8.7),
('E008', 'Jessica', 'Miller', 'jessica.miller@universalparks.com', '555-1008', 'Universal Studios Hollywood', 'Operations', 'Guest Services Lead', 'Full-Time', 'Closing', 'Advanced', 'English, Mandarin', 'Mark Miller', '555-2008', '2021-04-14', '2024-04-14', 23.25, NULL, 8.8),
('E009', 'Liu', 'Chen', 'liu.chen@universalparks.com', '555-1009', 'Universal Beijing Resort', 'Merchandise', 'Inventory Coordinator', 'Full-Time', 'Opening', 'Intermediate', 'Mandarin, English', 'Wei Chen', '555-2009', '2021-08-30', NULL, 20.80, NULL, 8.4),
('E010', 'Marcus', 'Johnson', 'marcus.johnson@universalparks.com', '555-1010', 'Universal Orlando Resort', 'Entertainment', 'Show Director', 'Full-Time', 'Mid-Day', 'Trainer', 'English', 'Angela Johnson', '555-2010', '2016-12-03', '2020-12-03', 35.00, NULL, 9.4);

-- Insert Work Schedules Data
INSERT INTO STAFF_MANAGEMENT.WORK_SCHEDULES VALUES
('WS001', 'E001', '2024-08-05', 'Mid-Day', 'Harry Potter Area', 'Ride Operator', 'Confirmed', TRUE, NULL, '2024-08-05 12:00:00', '2024-08-05 20:00:00', '2024-08-05 11:55:00', '2024-08-05 20:15:00', 8.33),
('WS002', 'E002', '2024-08-05', 'Opening', 'Three Broomsticks', 'Restaurant Manager', 'Confirmed', FALSE, NULL, '2024-08-05 06:00:00', '2024-08-05 14:00:00', '2024-08-05 05:50:00', '2024-08-05 14:00:00', 8.17),
('WS003', 'E003', '2024-08-05', 'Closing', 'Universal Store', 'Store Associate', 'Confirmed', FALSE, NULL, '2024-08-05 16:00:00', '2024-08-05 23:00:00', '2024-08-05 16:05:00', '2024-08-05 23:10:00', 7.08),
('WS004', 'E004', '2024-08-05', 'Mid-Day', 'Character Meet Areas', 'Character Performer', 'Confirmed', FALSE, 'Summer Character Events', '2024-08-05 10:00:00', '2024-08-05 18:00:00', '2024-08-05 09:58:00', '2024-08-05 18:05:00', 8.12),
('WS005', 'E005', '2024-08-05', 'Overnight', 'Attraction Maintenance', 'Technical Specialist', 'Confirmed', TRUE, NULL, '2024-08-05 23:00:00', '2024-08-06 07:00:00', '2024-08-05 22:55:00', '2024-08-06 07:20:00', 8.42),
('WS006', 'E006', '2024-08-05', 'Opening', 'Islands of Adventure', 'Attractions Supervisor', 'Confirmed', FALSE, NULL, '2024-08-05 07:00:00', '2024-08-05 15:00:00', '2024-08-05 06:45:00', '2024-08-05 15:00:00', 8.25),
('WS007', 'E007', '2024-08-05', 'Mid-Day', 'Jurassic Cafe Kitchen', 'Chef', 'Confirmed', TRUE, NULL, '2024-08-05 11:00:00', '2024-08-05 20:00:00', '2024-08-05 10:55:00', '2024-08-05 20:30:00', 9.58),
('WS008', 'E008', '2024-08-05', 'Closing', 'Guest Services Desk', 'Guest Services Lead', 'Confirmed', FALSE, NULL, '2024-08-05 15:00:00', '2024-08-05 23:00:00', '2024-08-05 15:02:00', '2024-08-05 23:00:00', 7.97),
('WS009', 'E009', '2024-08-05', 'Opening', 'Merchandise Warehouse', 'Inventory Coordinator', 'Confirmed', FALSE, NULL, '2024-08-05 08:00:00', '2024-08-05 16:00:00', '2024-08-05 07:58:00', '2024-08-05 16:15:00', 8.28),
('WS010', 'E010', '2024-08-05', 'Mid-Day', 'Universal Theater', 'Show Director', 'Confirmed', TRUE, 'Special Summer Show', '2024-08-05 13:00:00', '2024-08-05 22:00:00', '2024-08-05 12:50:00', '2024-08-05 22:10:00', 9.33);

-- Insert Training Records Data
INSERT INTO STAFF_MANAGEMENT.TRAINING_RECORDS VALUES
('TR001', 'E001', 'Ride Safety Protocols', 'Safety', 'Classroom', TRUE, 'Mark Stevens', 'Completed', '2024-01-15', '2025-01-15', 95, 8.0, 1),
('TR002', 'E002', 'Food Service Management', 'Leadership', 'Online', FALSE, 'Lisa Rodriguez', 'Completed', '2024-02-20', NULL, 88, 12.0, 1),
('TR003', 'E003', 'Customer Service Excellence', 'Customer Service', 'Classroom', FALSE, 'Jennifer Park', 'Completed', '2024-03-10', NULL, 92, 6.0, 1),
('TR004', 'E004', 'Character Performance Standards', 'Technical', 'On-the-Job', TRUE, 'Michael Chang', 'Completed', '2024-01-25', '2025-01-25', 97, 16.0, 1),
('TR005', 'E005', 'Electrical Systems Maintenance', 'Technical', 'Simulation', TRUE, 'Robert Kim', 'Completed', '2024-04-05', '2025-04-05', 94, 24.0, 1),
('TR006', 'E006', 'Leadership Development Program', 'Leadership', 'Classroom', FALSE, 'Susan Wright', 'In Progress', NULL, NULL, NULL, 20.0, 1),
('TR007', 'E007', 'Food Safety Certification', 'Safety', 'Online', TRUE, 'Ahmed Ali', 'Completed', '2024-03-15', '2025-03-15', 96, 4.0, 1),
('TR008', 'E008', 'Guest Relations Advanced', 'Customer Service', 'Classroom', FALSE, 'Maria Garcia', 'Completed', '2024-02-28', NULL, 90, 8.0, 1),
('TR009', 'E009', 'Inventory Management Systems', 'Technical', 'Online', FALSE, 'David Lee', 'Completed', '2024-01-30', NULL, 85, 10.0, 2),
('TR010', 'E010', 'Entertainment Production', 'Technical', 'On-the-Job', FALSE, 'Rachel Green', 'Completed', '2024-04-20', NULL, 93, 32.0, 1);

-- Insert Hotel Properties Data
INSERT INTO HOTEL_ACCOMMODATION.HOTEL_PROPERTIES VALUES
('HP001', 'Universal Aventura Hotel', 'Value Hotel', 'Universal Orlando Resort', 'Standard Themed', 4, 600, 'Standard', TRUE, FALSE, '2018-08-16', '2022-08-16', 189.99, 78.5, 8.4),
('HP002', 'Loews Sapphire Falls Resort', 'Resort Hotel', 'Universal Orlando Resort', 'Premium Themed', 5, 1000, 'Premium', TRUE, FALSE, '2016-07-14', '2023-07-14', 289.99, 82.3, 9.1),
('HP003', 'Universal Hard Rock Hotel', 'Resort Hotel', 'Universal Orlando Resort', 'Premium Themed', 5, 650, 'Luxury', TRUE, TRUE, '2001-01-02', '2021-01-02', 449.99, 85.7, 9.3),
('HP004', 'Loews Royal Pacific Resort', 'Resort Hotel', 'Universal Orlando Resort', 'Premium Themed', 5, 1000, 'Luxury', TRUE, TRUE, '2002-06-02', '2022-06-02', 419.99, 84.2, 9.2),
('HP005', 'Universal Beverly Hills Hotel', 'Resort Hotel', 'Universal Studios Hollywood', 'Premium Themed', 5, 400, 'Luxury', TRUE, TRUE, '2019-06-12', '2024-06-12', 529.99, 79.8, 9.0),
('HP006', 'Hotel Universal Port', 'Resort Hotel', 'Universal Studios Japan', 'Premium Themed', 5, 600, 'Premium', TRUE, FALSE, '2001-10-01', '2020-10-01', 299.99, 88.5, 8.9),
('HP007', 'NUO Hotel Beijing', 'Resort Hotel', 'Universal Beijing Resort', 'Premium Themed', 5, 400, 'Luxury', TRUE, TRUE, '2021-09-20', '2024-09-20', 259.99, 76.3, 8.7),
('HP008', 'Universal Studios Singapore Hotel', 'Resort Hotel', 'Universal Studios Singapore', 'Standard Themed', 4, 350, 'Standard', TRUE, FALSE, '2010-03-18', '2020-03-18', 199.99, 81.2, 8.5),
('HP009', 'Wizarding World Suites', 'Suites', 'Universal Orlando Resort', 'Premium Themed', 5, 200, 'Luxury', TRUE, TRUE, '2020-08-15', '2024-08-15', 599.99, 92.1, 9.6),
('HP010', 'Nintendo World Resort', 'Resort Hotel', 'Universal Studios Japan', 'Premium Themed', 5, 500, 'Premium', TRUE, TRUE, '2021-03-18', '2024-03-18', 399.99, 89.7, 9.4);

-- Insert Room Reservations Data
INSERT INTO HOTEL_ACCOMMODATION.ROOM_RESERVATIONS VALUES
('HR001', 'G001', 'HP003', 'Deluxe', 'Park View', 'Direct', 'Leisure', 'Park Package', 'Standard', 'Early check-in requested', '2024-07-18 14:30:00', '2024-07-20', '2024-07-22', '2024-07-20 14:00:00', '2024-07-22 11:00:00', 449.99, 1249.97, 9.2),
('HR002', 'G002', 'HP001', 'Standard', 'Pool View', 'Online', 'Leisure', 'Room Only', 'Flexible', NULL, '2024-07-29 09:15:00', '2024-08-01', '2024-08-03', '2024-08-01 15:30:00', '2024-08-03 11:15:00', 189.99, 419.98, 8.7),
('HR003', 'G003', 'HP002', 'Suite', 'Park View', 'Travel Agent', 'Leisure', 'Experience Package', 'Standard', 'Anniversary celebration', '2024-07-13 16:45:00', '2024-07-15', '2024-07-17', '2024-07-15 16:00:00', '2024-07-17 12:00:00', 389.99, 1169.97, 9.5),
('HR004', 'G004', 'HP001', 'Standard', 'City View', 'Phone', 'Leisure', 'Room Only', 'Strict', NULL, '2024-06-28 11:20:00', '2024-06-30', '2024-07-01', '2024-06-30 15:45:00', '2024-07-01 10:30:00', 189.99, 209.99, 7.8),
('HR005', 'G005', 'HP006', 'Deluxe', 'Park View', 'Direct', 'Leisure', 'Nintendo Package', 'Standard', 'Nintendo room theme requested', '2024-08-03 08:00:00', '2024-08-05', '2024-08-07', '2024-08-05 16:00:00', '2024-08-07 11:30:00', 299.99, 859.97, 9.1),
('HR006', 'G006', 'HP002', 'Standard', 'Pool View', 'Online', 'Leisure', 'Dining Package', 'Flexible', NULL, '2024-07-23 13:45:00', '2024-07-25', '2024-07-26', '2024-07-25 14:30:00', '2024-07-26 11:00:00', 289.99, 339.99, 8.4),
('HR007', 'G007', 'HP005', 'Suite', 'City View', 'Direct', 'VIP', 'Experience Package', 'Standard', 'VIP concierge services', '2024-08-01 10:30:00', '2024-08-03', '2024-08-05', '2024-08-03 15:00:00', '2024-08-05 12:00:00', 529.99, 1589.97, 9.3),
('HR008', 'G008', 'HP004', 'Deluxe', 'Park View', 'Travel Agent', 'Group', 'Halloween Package', 'Standard', 'Halloween Horror Nights access', '2024-07-26 15:00:00', '2024-07-28', '2024-07-30', '2024-07-28 16:30:00', '2024-07-30 11:45:00', 419.99, 1099.97, 8.9),
('HR009', 'G009', 'HP007', 'Standard', 'City View', 'Online', 'Business', 'Room Only', 'Flexible', 'Late checkout requested', '2024-07-31 12:15:00', '2024-08-02', '2024-08-03', '2024-08-02 14:20:00', '2024-08-03 13:00:00', 259.99, 279.99, 8.6),
('HR010', 'G010', 'HP008', 'Deluxe', 'Pool View', 'Travel Agent', 'Leisure', 'Universal Package', 'Standard', 'Family connecting rooms', '2024-07-28 14:20:00', '2024-07-30', '2024-08-01', '2024-07-30 15:15:00', '2024-08-01 11:30:00', 199.99, 459.98, 8.8);

-- Insert Hotel Amenities Usage Data
INSERT INTO HOTEL_ACCOMMODATION.AMENITIES_USAGE VALUES
('AU001', 'HR001', 'Pool', 'Hard Rock Pool Complex', 'Complimentary', 'Pool Deck', '2024-07-20 16:30:00', 3.5, 0.00, 9.0),
('AU002', 'HR001', 'Restaurant', 'The Kitchen', 'Premium', 'Hotel Restaurant', '2024-07-20 19:00:00', 2.0, 89.99, 8.8),
('AU003', 'HR002', 'Fitness', 'Fitness Center', 'Complimentary', 'Hotel Gym', '2024-08-01 07:00:00', 1.5, 0.00, 8.5),
('AU004', 'HR003', 'Spa', 'Mandara Spa', 'Premium', 'Spa Facility', '2024-07-16 14:00:00', 2.5, 199.99, 9.3),
('AU005', 'HR003', 'Concierge', 'VIP Concierge Service', 'Premium', 'Hotel Lobby', '2024-07-15 10:00:00', 0.5, 25.00, 9.1),
('AU006', 'HR005', 'Restaurant', 'Nintendo Character Dining', 'Premium', 'Themed Restaurant', '2024-08-05 18:30:00', 1.5, 65.99, 9.5),
('AU007', 'HR005', 'Pool', 'Nintendo Themed Pool', 'Complimentary', 'Pool Area', '2024-08-06 11:00:00', 4.0, 0.00, 9.2),
('AU008', 'HR007', 'Room Service', 'In-Room Dining', 'Premium', 'Guest Room', '2024-08-04 08:00:00', 0.5, 45.99, 8.7),
('AU009', 'HR008', 'Restaurant', 'Horror Nights Themed Dining', 'Premium', 'Special Event Restaurant', '2024-07-29 20:00:00', 2.5, 99.99, 9.0),
('AU010', 'HR010', 'Pool', 'Family Pool Complex', 'Complimentary', 'Pool Deck', '2024-07-31 15:00:00', 2.5, 0.00, 8.6);

-- =====================================================================
-- 7. CREATE VIEWS FOR SEMANTIC MODELS
-- =====================================================================

-- Guest Analytics Views
CREATE OR REPLACE VIEW GUEST_ANALYTICS.GUEST_VISIT_SUMMARY AS
SELECT 
    gp.*,
    COUNT(DISTINCT vs.VISIT_ID) as TOTAL_VISITS,
    AVG(vs.SPEND_AMOUNT) as AVERAGE_SPEND_PER_VISIT
FROM GUEST_ANALYTICS.GUEST_PROFILES gp
LEFT JOIN GUEST_ANALYTICS.VISIT_SESSIONS vs ON gp.GUEST_ID = vs.GUEST_ID
GROUP BY gp.GUEST_ID, gp.FIRST_NAME, gp.LAST_NAME, gp.EMAIL_ADDRESS, 
         gp.PHONE_NUMBER, gp.DATE_OF_BIRTH, gp.ZIP_CODE, gp.STATE, 
         gp.COUNTRY, gp.PREFERRED_LANGUAGE, gp.MEMBERSHIP_TIER, 
         gp.FAMILY_SIZE, gp.PREFERRED_PARK, gp.ACCOUNT_CREATED_DATE, 
         gp.LAST_VISIT_DATE, gp.TOTAL_SPEND_AMOUNT, gp.MEMBERSHIP_VALUE, 
         gp.CURRENT_PERFORMANCE_RATING;

-- Park Operations Views
CREATE OR REPLACE VIEW PARK_OPERATIONS.ATTRACTION_PERFORMANCE AS
SELECT 
    a.*,
    AVG(wt.WAIT_TIME_MINUTES) as AVERAGE_WAIT_TIME,
    AVG(hc.OPERATIONAL_EFFICIENCY_SCORE) as AVERAGE_EFFICIENCY
FROM PARK_OPERATIONS.ATTRACTIONS a
LEFT JOIN PARK_OPERATIONS.WAIT_TIMES wt ON a.ATTRACTION_ID = wt.ATTRACTION_ID
LEFT JOIN PARK_OPERATIONS.HOURLY_CAPACITY hc ON a.ATTRACTION_ID = hc.ATTRACTION_ID
GROUP BY a.ATTRACTION_ID, a.ATTRACTION_NAME, a.PARK_LOCATION, a.THEMED_AREA,
         a.ATTRACTION_TYPE, a.FRANCHISE, a.HEIGHT_REQUIREMENT_INCHES,
         a.THEORETICAL_HOURLY_CAPACITY, a.RIDE_DURATION_MINUTES,
         a.ACCESSIBILITY_FEATURES, a.OPERATIONAL_STATUS, a.OPENING_DATE,
         a.LAST_MAJOR_MAINTENANCE_DATE, a.DAILY_GUEST_COUNT,
         a.WAIT_TIME_MINUTES, a.ACTUAL_HOURLY_CAPACITY, a.GUEST_SATISFACTION_RATING;

-- Staff Management Views
CREATE OR REPLACE VIEW STAFF_MANAGEMENT.EMPLOYEE_PERFORMANCE AS
SELECT 
    ep.*,
    AVG(ws.HOURS_WORKED) as AVERAGE_HOURS_PER_SHIFT,
    AVG(tr.TRAINING_SCORE) as AVERAGE_TRAINING_SCORE
FROM STAFF_MANAGEMENT.EMPLOYEE_PROFILES ep
LEFT JOIN STAFF_MANAGEMENT.WORK_SCHEDULES ws ON ep.EMPLOYEE_ID = ws.EMPLOYEE_ID
LEFT JOIN STAFF_MANAGEMENT.TRAINING_RECORDS tr ON ep.EMPLOYEE_ID = tr.EMPLOYEE_ID
GROUP BY ep.EMPLOYEE_ID, ep.FIRST_NAME, ep.LAST_NAME, ep.EMPLOYEE_EMAIL,
         ep.PHONE_NUMBER, ep.PARK_LOCATION, ep.DEPARTMENT, ep.JOB_TITLE,
         ep.EMPLOYMENT_TYPE, ep.SHIFT_PREFERENCE, ep.CERTIFICATION_LEVEL,
         ep.LANGUAGE_SKILLS, ep.EMERGENCY_CONTACT_NAME, ep.EMERGENCY_CONTACT_PHONE,
         ep.HIRE_DATE, ep.LAST_PROMOTION_DATE, ep.HOURLY_WAGE,
         ep.ANNUAL_SALARY, ep.CURRENT_PERFORMANCE_RATING;

-- =====================================================================
-- 8. GRANT PERMISSIONS
-- =====================================================================

-- Grant SELECT permissions to appropriate roles
-- GRANT SELECT ON ALL TABLES IN SCHEMA GUEST_ANALYTICS TO ROLE ANALYTICS_ROLE;
-- GRANT SELECT ON ALL TABLES IN SCHEMA PARK_OPERATIONS TO ROLE OPERATIONS_ROLE;
-- GRANT SELECT ON ALL TABLES IN SCHEMA REVENUE_ANALYTICS TO ROLE FINANCE_ROLE;
-- GRANT SELECT ON ALL TABLES IN SCHEMA STAFF_MANAGEMENT TO ROLE HR_ROLE;

-- =====================================================================
-- 9. DATA VALIDATION QUERIES
-- =====================================================================

-- Validate data integrity
SELECT 'Guest Profiles' as table_name, COUNT(*) as record_count FROM GUEST_ANALYTICS.GUEST_PROFILES
UNION ALL
SELECT 'Visit Sessions' as table_name, COUNT(*) as record_count FROM GUEST_ANALYTICS.VISIT_SESSIONS
UNION ALL
SELECT 'Guest Preferences' as table_name, COUNT(*) as record_count FROM GUEST_ANALYTICS.GUEST_PREFERENCES
UNION ALL
SELECT 'Attractions' as table_name, COUNT(*) as record_count FROM PARK_OPERATIONS.ATTRACTIONS
UNION ALL
SELECT 'Wait Times' as table_name, COUNT(*) as record_count FROM PARK_OPERATIONS.WAIT_TIMES
UNION ALL
SELECT 'Hourly Capacity' as table_name, COUNT(*) as record_count FROM PARK_OPERATIONS.HOURLY_CAPACITY
UNION ALL
SELECT 'Ticket Sales' as table_name, COUNT(*) as record_count FROM REVENUE_ANALYTICS.TICKET_SALES
UNION ALL
SELECT 'Merchandise Sales' as table_name, COUNT(*) as record_count FROM REVENUE_ANALYTICS.MERCHANDISE_SALES
UNION ALL
SELECT 'Food Beverage Sales' as table_name, COUNT(*) as record_count FROM REVENUE_ANALYTICS.FOOD_BEVERAGE_SALES
UNION ALL
SELECT 'Employee Profiles' as table_name, COUNT(*) as record_count FROM STAFF_MANAGEMENT.EMPLOYEE_PROFILES
UNION ALL
SELECT 'Work Schedules' as table_name, COUNT(*) as record_count FROM STAFF_MANAGEMENT.WORK_SCHEDULES
UNION ALL
SELECT 'Training Records' as table_name, COUNT(*) as record_count FROM STAFF_MANAGEMENT.TRAINING_RECORDS
UNION ALL
SELECT 'Hotel Properties' as table_name, COUNT(*) as record_count FROM HOTEL_ACCOMMODATION.HOTEL_PROPERTIES
UNION ALL
SELECT 'Room Reservations' as table_name, COUNT(*) as record_count FROM HOTEL_ACCOMMODATION.ROOM_RESERVATIONS
UNION ALL
SELECT 'Amenities Usage' as table_name, COUNT(*) as record_count FROM HOTEL_ACCOMMODATION.AMENITIES_USAGE;

-- =====================================================================
-- SCRIPT COMPLETION
-- =====================================================================

SELECT 'Universal Destinations & Experiences synthetic data creation completed successfully!' as status;