-- Setup script for Snowflake PDF Extractor App
-- Run these commands in your Snowflake worksheet before deploying the app

-- Step 1: Create database and schema
CREATE DATABASE IF NOT EXISTS PDF_EXTRACTION_DB;
CREATE SCHEMA IF NOT EXISTS PDF_EXTRACTION_DB.PUBLIC;

-- Step 2: Create stage for PDF uploads
CREATE STAGE IF NOT EXISTS PDF_EXTRACTION_DB.PUBLIC.PDF_STAGE
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
    COMMENT = 'Stage for uploaded PDF files';

-- Step 3: Create table to store extracted data
CREATE TABLE IF NOT EXISTS PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA (
    ID NUMBER AUTOINCREMENT,
    SOURCE_FILE VARCHAR(500),
    EXTRACTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA VARIANT,
    SCHEMA_TYPE VARCHAR(100),
    PRIMARY KEY (ID)
)
COMMENT = 'Table storing extracted and corrected data from PDFs';

-- Step 4: Grant CORTEX_USER role (REQUIRED for AI_EXTRACT)
-- You must have the SNOWFLAKE.CORTEX_USER database role to use AI_EXTRACT
-- GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE YOUR_ROLE;

-- Step 5: Grant necessary privileges (adjust role as needed)
-- GRANT USAGE ON DATABASE PDF_EXTRACTION_DB TO ROLE YOUR_ROLE;
-- GRANT USAGE ON SCHEMA PDF_EXTRACTION_DB.PUBLIC TO ROLE YOUR_ROLE;
-- GRANT READ, WRITE ON STAGE PDF_EXTRACTION_DB.PUBLIC.PDF_STAGE TO ROLE YOUR_ROLE;
-- GRANT SELECT, INSERT ON TABLE PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA TO ROLE YOUR_ROLE;

-- Step 6: Verify the setup
SHOW STAGES IN PDF_EXTRACTION_DB.PUBLIC;
SHOW TABLES IN PDF_EXTRACTION_DB.PUBLIC;

-- Step 7: Test AI_EXTRACT availability (requires a file in stage first)
-- Upload a test PDF first, then run:
-- SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
--   file => TO_FILE('@PDF_EXTRACTION_DB.PUBLIC.PDF_STAGE', 'test.pdf'),
--   responseFormat => {'name': 'What is mentioned in this document?'}
-- ) as test_result;

-- Optional: Create view for easier data access
CREATE OR REPLACE VIEW PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA_VIEW AS
SELECT 
    ID,
    SOURCE_FILE,
    EXTRACTION_TIMESTAMP,
    SCHEMA_TYPE,
    DATA,
    DATA:invoice_number::STRING as INVOICE_NUMBER,
    DATA:vendor_name::STRING as VENDOR_NAME,
    DATA:total_amount::FLOAT as TOTAL_AMOUNT
FROM PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA;

-- Optional: Create a sample query to view all extractions
-- SELECT * FROM PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA ORDER BY EXTRACTION_TIMESTAMP DESC LIMIT 10;

-- Example: Query bank statement data with flattened accounts
-- SELECT 
--     ID,
--     SOURCE_FILE,
--     EXTRACTION_TIMESTAMP,
--     SCHEMA_TYPE,
--     DATA:account_holder_name::STRING as ACCOUNT_HOLDER,
--     DATA:bank_name::STRING as BANK_NAME,
--     f.value::STRING as ACCOUNT_DETAILS
-- FROM PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA,
--      LATERAL FLATTEN(input => DATA:all_accounts_summary) f
-- WHERE SCHEMA_TYPE = 'Bank Statement'
-- ORDER BY EXTRACTION_TIMESTAMP DESC;

