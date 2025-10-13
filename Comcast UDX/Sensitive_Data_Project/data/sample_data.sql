-- =====================================================================
-- Enhanced Snowflake Sensitive Data Discovery & Masking
-- Sample Data Creation Script
-- =====================================================================
-- This script creates comprehensive test data for validating the
-- sensitive data detection and masking application
-- =====================================================================

-- 1. Create a dedicated test database and schema
CREATE DATABASE IF NOT EXISTS TEST_SENSITIVE_DATA
  COMMENT = 'Test database for Sensitive Data Discovery & Masking Application';

CREATE SCHEMA IF NOT EXISTS TEST_SENSITIVE_DATA.DEMO_SCHEMA
  COMMENT = 'Demo schema containing tables with various sensitive data types';

-- Set context
USE DATABASE TEST_SENSITIVE_DATA;
USE SCHEMA DEMO_SCHEMA;

-- =====================================================================
-- 2. Create comprehensive customer profiles table
-- =====================================================================
CREATE OR REPLACE TABLE CUSTOMER_PROFILES (
    CUSTOMER_ID INT AUTOINCREMENT,
    FIRST_NAME VARCHAR(255) COMMENT 'Customer first name, potentially PII',
    LAST_NAME VARCHAR(255) COMMENT 'Customer last name, potentially PII',
    EMAIL_ADDRESS VARCHAR(255) COMMENT 'Customer email address, PII',
    PHONE_NUMBER VARCHAR(20) COMMENT 'Customer phone number, PII',
    SOCIAL_SECURITY_NUMBER VARCHAR(11) COMMENT 'Customer Social Security Number (SSN), highly sensitive PII',
    DATE_OF_BIRTH DATE COMMENT 'Customer date of birth, PII',
    CREDIT_CARD_NUMBER VARCHAR(16) COMMENT 'Customer credit card number, PCI data',
    STREET_ADDRESS VARCHAR(500) COMMENT 'Customer street address, PII',
    CITY VARCHAR(255),
    STATE VARCHAR(255),
    ZIP_CODE VARCHAR(10),
    ACCOUNT_BALANCE DECIMAL(18, 2),
    LAST_LOGIN_DATE TIMESTAMP_NTZ,
    CUSTOMER_NOTES VARCHAR(1000) COMMENT 'General customer notes, might contain sensitive info'
);

-- =====================================================================
-- 3. Create employee records table with different sensitive patterns
-- =====================================================================
CREATE OR REPLACE TABLE EMPLOYEE_RECORDS (
    EMP_ID INT AUTOINCREMENT,
    EMPLOYEE_SSN VARCHAR(11) COMMENT 'Employee Social Security Number',
    FULL_NAME VARCHAR(500) COMMENT 'Employee full name',
    WORK_EMAIL VARCHAR(255) COMMENT 'Corporate email address',
    PERSONAL_EMAIL VARCHAR(255) COMMENT 'Personal email, private information',
    HOME_PHONE VARCHAR(15) COMMENT 'Home phone number',
    MOBILE_PHONE VARCHAR(15) COMMENT 'Mobile phone number',
    HOME_ADDRESS VARCHAR(1000) COMMENT 'Home address, personal information',
    EMERGENCY_CONTACT_NAME VARCHAR(255) COMMENT 'Emergency contact name',
    EMERGENCY_CONTACT_PHONE VARCHAR(15) COMMENT 'Emergency contact phone',
    SALARY DECIMAL(12, 2) COMMENT 'Employee salary, confidential',
    HIRE_DATE DATE,
    DEPARTMENT VARCHAR(100),
    MANAGER_ID INT,
    PERFORMANCE_NOTES TEXT COMMENT 'Performance notes, may contain sensitive information'
);

-- =====================================================================
-- 4. Create financial transactions table
-- =====================================================================
CREATE OR REPLACE TABLE FINANCIAL_TRANSACTIONS (
    TRANSACTION_ID STRING DEFAULT UUID_STRING(),
    CUSTOMER_SSN VARCHAR(11) COMMENT 'Customer SSN for transaction',
    CREDIT_CARD_NUM VARCHAR(19) COMMENT 'Credit card number used',
    ACCOUNT_NUMBER VARCHAR(20) COMMENT 'Bank account number',
    ROUTING_NUMBER VARCHAR(9) COMMENT 'Bank routing number',
    TRANSACTION_AMOUNT DECIMAL(15, 2),
    TRANSACTION_DATE TIMESTAMP_NTZ,
    MERCHANT_NAME VARCHAR(255),
    TRANSACTION_TYPE VARCHAR(50),
    CUSTOMER_EMAIL VARCHAR(255) COMMENT 'Customer email for receipt',
    BILLING_ADDRESS VARCHAR(1000) COMMENT 'Billing address, PII'
);

-- =====================================================================
-- 5. Create medical records table (healthcare data)
-- =====================================================================
CREATE OR REPLACE TABLE PATIENT_RECORDS (
    PATIENT_ID STRING DEFAULT UUID_STRING(),
    PATIENT_SSN VARCHAR(11) COMMENT 'Patient Social Security Number, HIPAA protected',
    PATIENT_NAME VARCHAR(255) COMMENT 'Patient full name, PHI',
    DATE_OF_BIRTH DATE COMMENT 'Patient DOB, PHI',
    PATIENT_EMAIL VARCHAR(255) COMMENT 'Patient email, PHI',
    PATIENT_PHONE VARCHAR(15) COMMENT 'Patient contact phone, PHI',
    PATIENT_ADDRESS VARCHAR(1000) COMMENT 'Patient address, PHI',
    INSURANCE_ID VARCHAR(50) COMMENT 'Insurance member ID, sensitive',
    MEDICAL_RECORD_NUMBER VARCHAR(20) COMMENT 'Medical record number, PHI',
    DIAGNOSIS_CODES VARCHAR(500) COMMENT 'ICD-10 diagnosis codes',
    TREATMENT_NOTES TEXT COMMENT 'Clinical notes, highly sensitive PHI',
    DOCTOR_NAME VARCHAR(255),
    HOSPITAL_NAME VARCHAR(255),
    ADMISSION_DATE DATE,
    DISCHARGE_DATE DATE
);

-- =====================================================================
-- 6. Create educational records table
-- =====================================================================
CREATE OR REPLACE TABLE STUDENT_RECORDS (
    STUDENT_ID INT AUTOINCREMENT,
    STUDENT_SSN VARCHAR(11) COMMENT 'Student Social Security Number',
    FIRST_NAME VARCHAR(255) COMMENT 'Student first name',
    LAST_NAME VARCHAR(255) COMMENT 'Student last name',
    EMAIL_ADDRESS VARCHAR(255) COMMENT 'Student email address',
    PHONE_NUMBER VARCHAR(15) COMMENT 'Student phone number',
    PARENT_EMAIL VARCHAR(255) COMMENT 'Parent/guardian email',
    HOME_ADDRESS VARCHAR(1000) COMMENT 'Student home address',
    EMERGENCY_CONTACT VARCHAR(255) COMMENT 'Emergency contact information',
    GPA DECIMAL(3, 2),
    GRADUATION_YEAR INT,
    MAJOR VARCHAR(100),
    FINANCIAL_AID_AMOUNT DECIMAL(10, 2) COMMENT 'Financial aid amount, confidential'
);

-- =====================================================================
-- 7. Insert comprehensive test data
-- =====================================================================

-- Insert customer profile test data
INSERT INTO CUSTOMER_PROFILES (
    FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PHONE_NUMBER,
    SOCIAL_SECURITY_NUMBER, DATE_OF_BIRTH, CREDIT_CARD_NUMBER,
    STREET_ADDRESS, CITY, STATE, ZIP_CODE, ACCOUNT_BALANCE, 
    LAST_LOGIN_DATE, CUSTOMER_NOTES
) VALUES
('John', 'Doe', 'john.doe@example.com', '555-123-4567', '123-45-6789', '1980-01-15', '1234567890123456', '123 Main St', 'Anytown', 'CA', '90210', 1500.75, CURRENT_TIMESTAMP(), 'Prefers email communication.'),
('Jane', 'Smith', 'jane.smith@domain.net', '555-987-6543', '987-65-4321', '1992-05-20', '9876543210987654', '456 Oak Ave', 'Otherville', 'NY', '10001', 2300.50, CURRENT_TIMESTAMP(), 'VIP customer. SSN for tax purposes.'),
('Alice', 'Johnson', 'alice.j@service.org', '555-111-2222', '111-22-3333', '1975-11-30', '1122334455667788', '789 Pine Ln', 'Smallville', 'TX', '77001', 500.00, CURRENT_TIMESTAMP(), 'Recently updated email.'),
('Bob', 'Williams', 'bob.w@mail.com', '555-333-4444', '444-55-6666', '2001-03-01', '5566778899001122', '101 River Rd', 'Big City', 'FL', '33101', 750.20, CURRENT_TIMESTAMP(), 'Has two active credit cards.'),
('Charlie', 'Brown', 'charlie.b@test.co', '555-777-8888', '777-88-9999', '1968-09-10', '3344556677889900', '202 Forest Dr', 'Green Acres', 'WA', '98101', 3000.00, CURRENT_TIMESTAMP(), 'No specific notes.'),
('Diana', 'Prince', 'diana.p@hero.gov', '555-000-1111', '000-11-2222', '1941-10-21', '9988776655443322', '303 Paradise Is', 'Themyscira', 'DC', '20001', 10000.00, CURRENT_TIMESTAMP(), 'Special handling required for her SSN.'),
('Eve', 'Adams', 'eve.a@alpha.io', '555-222-3333', '222-33-4444', '1995-07-07', '2211443366558877', '404 Garden Way', 'Eden', 'GA', '30303', 1200.00, CURRENT_TIMESTAMP(), 'Email changed last month.'),
('Frank', 'White', 'frank.w@omega.org', '555-444-5555', '555-66-7777', '1988-02-29', '7766554433221100', '505 Mountain Peak', 'Highland', 'CO', '80202', 800.50, CURRENT_TIMESTAMP(), 'Has multiple accounts.'),
('Grace', 'Green', 'grace.g@beta.com', '555-666-7777', '666-77-8888', '1970-12-05', '0011223344556677', '606 Valley View', 'Lowlands', 'OR', '97201', 1800.00, CURRENT_TIMESTAMP(), 'Prefers phone calls.'),
('Henry', 'Black', 'henry.b@gamma.net', '555-888-9999', '888-99-0000', '1983-04-18', '4455667788990011', '707 Hilltop Rd', 'Summit', 'AZ', '85001', 250.00, CURRENT_TIMESTAMP(), 'Credit card expires next year.');

-- Insert employee records test data
INSERT INTO EMPLOYEE_RECORDS (
    EMPLOYEE_SSN, FULL_NAME, WORK_EMAIL, PERSONAL_EMAIL, HOME_PHONE, MOBILE_PHONE,
    HOME_ADDRESS, EMERGENCY_CONTACT_NAME, EMERGENCY_CONTACT_PHONE, SALARY,
    HIRE_DATE, DEPARTMENT, MANAGER_ID, PERFORMANCE_NOTES
) VALUES
('123-45-6789', 'John Smith', 'john.smith@company.com', 'john.personal@gmail.com', '555-111-1111', '555-222-2222', '123 Employee Lane, Worktown, ST 12345', 'Jane Smith', '555-333-3333', 75000.00, '2020-01-15', 'Engineering', 1, 'Excellent performance, meets all targets.'),
('987-65-4321', 'Sarah Johnson', 'sarah.johnson@company.com', 'sarah.j@yahoo.com', '555-444-4444', '555-555-5555', '456 Worker Street, Jobcity, ST 54321', 'Mike Johnson', '555-666-6666', 82000.00, '2019-03-22', 'Marketing', 2, 'Strong team player, creative solutions.'),
('456-78-9012', 'Michael Brown', 'michael.brown@company.com', 'mike.brown@hotmail.com', '555-777-7777', '555-888-8888', '789 Office Road, Workplace, ST 67890', 'Lisa Brown', '555-999-9999', 95000.00, '2018-07-10', 'Finance', 3, 'Excellent analytical skills.'),
('321-54-9876', 'Emily Davis', 'emily.davis@company.com', 'emily.d@outlook.com', '555-101-1010', '555-202-2020', '321 Business Ave, Corporate, ST 13579', 'David Davis', '555-303-3030', 68000.00, '2021-05-08', 'HR', 4, 'Great communication skills.'),
('654-32-1098', 'Robert Wilson', 'robert.wilson@company.com', 'rob.wilson@gmail.com', '555-404-4040', '555-505-5050', '654 Work Circle, Industry, ST 24680', 'Mary Wilson', '555-606-6060', 71000.00, '2020-11-12', 'Operations', 5, 'Reliable and detail-oriented.');

-- Insert financial transaction test data
INSERT INTO FINANCIAL_TRANSACTIONS (
    CUSTOMER_SSN, CREDIT_CARD_NUM, ACCOUNT_NUMBER, ROUTING_NUMBER,
    TRANSACTION_AMOUNT, TRANSACTION_DATE, MERCHANT_NAME, TRANSACTION_TYPE,
    CUSTOMER_EMAIL, BILLING_ADDRESS
) VALUES
('123-45-6789', '4532-1234-5678-9012', '1234567890', '021000021', 156.78, CURRENT_TIMESTAMP(), 'Amazon.com', 'PURCHASE', 'john.doe@example.com', '123 Main St, Anytown, CA 90210'),
('987-65-4321', '5555-4444-3333-2222', '9876543210', '121000248', 89.99, CURRENT_TIMESTAMP(), 'Target', 'PURCHASE', 'jane.smith@domain.net', '456 Oak Ave, Otherville, NY 10001'),
('111-22-3333', '4111-1111-1111-1111', '1111222233', '071000013', 1250.00, CURRENT_TIMESTAMP(), 'Rent Payment', 'TRANSFER', 'alice.j@service.org', '789 Pine Ln, Smallville, TX 77001'),
('444-55-6666', '3782-822463-10005', '4444555566', '091000019', 45.50, CURRENT_TIMESTAMP(), 'Starbucks', 'PURCHASE', 'bob.w@mail.com', '101 River Rd, Big City, FL 33101'),
('777-88-9999', '6011-1111-1111-1117', '7777888899', '111000025', 299.99, CURRENT_TIMESTAMP(), 'Best Buy', 'PURCHASE', 'charlie.b@test.co', '202 Forest Dr, Green Acres, WA 98101');

-- Insert patient records test data
INSERT INTO PATIENT_RECORDS (
    PATIENT_SSN, PATIENT_NAME, DATE_OF_BIRTH, PATIENT_EMAIL, PATIENT_PHONE,
    PATIENT_ADDRESS, INSURANCE_ID, MEDICAL_RECORD_NUMBER, DIAGNOSIS_CODES,
    TREATMENT_NOTES, DOCTOR_NAME, HOSPITAL_NAME, ADMISSION_DATE
) VALUES
('123-45-6789', 'John Patient', '1980-01-15', 'john.patient@email.com', '555-PAT-1234', '123 Health St, Wellness, ST 12345', 'INS123456789', 'MRN001234', 'M79.3, Z51.11', 'Patient presents with chronic back pain. Prescribed physical therapy.', 'Dr. Sarah Healer', 'General Hospital', '2024-01-15'),
('987-65-4321', 'Jane Sick', '1992-05-20', 'jane.sick@email.com', '555-PAT-5678', '456 Medicine Ave, Healthtown, ST 54321', 'INS987654321', 'MRN005678', 'E11.9, Z79.4', 'Diabetes follow-up visit. Medication adjustment needed.', 'Dr. Mike Physician', 'Medical Center', '2024-01-20'),
('111-22-3333', 'Bob Hurt', '1975-11-30', 'bob.hurt@email.com', '555-PAT-9012', '789 Clinic Road, Doctorville, ST 67890', 'INS111222333', 'MRN009012', 'J06.9, R50.9', 'Upper respiratory infection. Prescribed antibiotics.', 'Dr. Lisa Medicine', 'Health Clinic', '2024-01-25');

-- Insert student records test data
INSERT INTO STUDENT_RECORDS (
    STUDENT_SSN, FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PHONE_NUMBER,
    PARENT_EMAIL, HOME_ADDRESS, EMERGENCY_CONTACT, GPA, GRADUATION_YEAR,
    MAJOR, FINANCIAL_AID_AMOUNT
) VALUES
('123-45-6789', 'Alex', 'Student', 'alex.student@university.edu', '555-STU-1234', 'parent.alex@email.com', '123 Campus Dr, College Town, ST 12345', 'Alex Parent, 555-PAR-1234', 3.75, 2025, 'Computer Science', 15000.00),
('987-65-4321', 'Morgan', 'Learner', 'morgan.learner@university.edu', '555-STU-5678', 'parent.morgan@email.com', '456 Dorm Lane, University City, ST 54321', 'Morgan Parent, 555-PAR-5678', 3.92, 2024, 'Biology', 18500.00),
('456-78-9012', 'Jordan', 'Scholar', 'jordan.scholar@university.edu', '555-STU-9012', 'parent.jordan@email.com', '789 Academic Ave, Education, ST 67890', 'Jordan Parent, 555-PAR-9012', 3.58, 2026, 'Business', 12000.00);

-- =====================================================================
-- 8. Create additional tables with edge cases and variations
-- =====================================================================

-- Table with minimal sensitive data (for testing thresholds)
CREATE OR REPLACE TABLE PRODUCT_CATALOG (
    PRODUCT_ID INT AUTOINCREMENT,
    PRODUCT_NAME VARCHAR(255),
    PRODUCT_DESCRIPTION TEXT,
    PRICE DECIMAL(10, 2),
    CATEGORY VARCHAR(100),
    MANUFACTURER VARCHAR(255),
    SKU VARCHAR(50),
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Table with mixed data types and potential false positives
CREATE OR REPLACE TABLE SYSTEM_LOGS (
    LOG_ID STRING DEFAULT UUID_STRING(),
    TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    LOG_LEVEL VARCHAR(10),
    MESSAGE TEXT,
    USER_ID VARCHAR(50) COMMENT 'System user identifier',
    SESSION_ID VARCHAR(100),
    IP_ADDRESS VARCHAR(45) COMMENT 'User IP address, potentially sensitive',
    ERROR_CODE VARCHAR(20),
    STACK_TRACE TEXT
);

-- Insert sample product data (should not be detected as sensitive)
INSERT INTO PRODUCT_CATALOG (PRODUCT_NAME, PRODUCT_DESCRIPTION, PRICE, CATEGORY, MANUFACTURER, SKU) VALUES
('Laptop Computer', 'High-performance laptop for business use', 1299.99, 'Electronics', 'TechCorp', 'LAP-001'),
('Office Chair', 'Ergonomic office chair with lumbar support', 299.50, 'Furniture', 'ChairMaker', 'CHR-001'),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 79.99, 'Lighting', 'LightCo', 'LMP-001');

-- Insert sample system logs (with some potentially sensitive data)
INSERT INTO SYSTEM_LOGS (LOG_LEVEL, MESSAGE, USER_ID, SESSION_ID, IP_ADDRESS, ERROR_CODE) VALUES
('INFO', 'User login successful', 'user123', 'sess_abc123', '192.168.1.100', NULL),
('ERROR', 'Failed login attempt', 'admin', 'sess_def456', '10.0.0.1', 'AUTH001'),
('WARN', 'Unusual access pattern detected', 'user456', 'sess_ghi789', '172.16.0.1', 'SEC001');

-- =====================================================================
-- 9. Create views and additional database objects for testing
-- =====================================================================

-- Create a view that combines sensitive data (should be detected)
CREATE OR REPLACE VIEW CUSTOMER_SUMMARY AS
SELECT 
    CUSTOMER_ID,
    FIRST_NAME,
    LAST_NAME,
    EMAIL_ADDRESS,
    PHONE_NUMBER,
    CITY,
    STATE,
    ACCOUNT_BALANCE
FROM CUSTOMER_PROFILES;

-- Create a materialized view (if supported)
CREATE OR REPLACE VIEW EMPLOYEE_CONTACT_INFO AS
SELECT 
    EMP_ID,
    FULL_NAME,
    WORK_EMAIL,
    HOME_PHONE,
    DEPARTMENT
FROM EMPLOYEE_RECORDS;

-- =====================================================================
-- 10. Add column tags for testing tag-based detection
-- =====================================================================

-- Note: Uncomment these if your Snowflake account has tagging enabled
-- ALTER TABLE CUSTOMER_PROFILES MODIFY COLUMN SOCIAL_SECURITY_NUMBER SET TAG (SENSITIVITY = 'HIGH', PII = 'TRUE');
-- ALTER TABLE CUSTOMER_PROFILES MODIFY COLUMN EMAIL_ADDRESS SET TAG (PII = 'TRUE');
-- ALTER TABLE CUSTOMER_PROFILES MODIFY COLUMN CREDIT_CARD_NUMBER SET TAG (FINANCIAL = 'TRUE', PCI = 'TRUE');

-- =====================================================================
-- 11. Grant appropriate permissions (adjust roles as needed)
-- =====================================================================

-- Note: Uncomment and modify these grants based on your role structure
-- GRANT SELECT ON ALL TABLES IN SCHEMA TEST_SENSITIVE_DATA.DEMO_SCHEMA TO ROLE DATA_ANALYST;
-- GRANT USAGE ON SCHEMA TEST_SENSITIVE_DATA.DEMO_SCHEMA TO ROLE DATA_ANALYST;
-- GRANT USAGE ON DATABASE TEST_SENSITIVE_DATA TO ROLE DATA_ANALYST;

-- =====================================================================
-- 12. Verification queries
-- =====================================================================

-- Verify data creation
SELECT 'CUSTOMER_PROFILES' as table_name, COUNT(*) as row_count FROM CUSTOMER_PROFILES
UNION ALL
SELECT 'EMPLOYEE_RECORDS' as table_name, COUNT(*) as row_count FROM EMPLOYEE_RECORDS
UNION ALL
SELECT 'FINANCIAL_TRANSACTIONS' as table_name, COUNT(*) as row_count FROM FINANCIAL_TRANSACTIONS
UNION ALL
SELECT 'PATIENT_RECORDS' as table_name, COUNT(*) as row_count FROM PATIENT_RECORDS
UNION ALL
SELECT 'STUDENT_RECORDS' as table_name, COUNT(*) as row_count FROM STUDENT_RECORDS
UNION ALL
SELECT 'PRODUCT_CATALOG' as table_name, COUNT(*) as row_count FROM PRODUCT_CATALOG
UNION ALL
SELECT 'SYSTEM_LOGS' as table_name, COUNT(*) as row_count FROM SYSTEM_LOGS;

-- Show table structure for validation
SHOW TABLES IN SCHEMA TEST_SENSITIVE_DATA.DEMO_SCHEMA;

-- =====================================================================
-- 13. Usage instructions
-- =====================================================================

/*
USAGE INSTRUCTIONS:

1. Run this script in your Snowflake environment
2. Verify that all tables were created successfully
3. Use the TEST_SENSITIVE_DATA.DEMO_SCHEMA in your application
4. Expected detection results:
   - CUSTOMER_PROFILES: Should detect SSN, EMAIL, PHONE, CREDIT_CARD, ADDRESS, DOB
   - EMPLOYEE_RECORDS: Should detect SSN, EMAIL, PHONE, ADDRESS, NAME
   - FINANCIAL_TRANSACTIONS: Should detect SSN, CREDIT_CARD, ACCOUNT_NUMBER, EMAIL
   - PATIENT_RECORDS: Should detect SSN, EMAIL, PHONE, ADDRESS, NAME, DOB
   - STUDENT_RECORDS: Should detect SSN, EMAIL, PHONE, ADDRESS, NAME
   - PRODUCT_CATALOG: Should NOT detect sensitive data (control group)
   - SYSTEM_LOGS: May detect IP_ADDRESS depending on configuration

5. This dataset provides comprehensive test coverage for:
   - Different sensitive data types
   - Various data formats and patterns
   - Edge cases and potential false positives
   - Tables with no sensitive data (negative test cases)
   - Mixed sensitivity levels

6. Clean up when testing is complete:
   DROP DATABASE TEST_SENSITIVE_DATA CASCADE;
*/ 