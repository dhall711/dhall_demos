-- =====================================================================
-- Snowflake AI-Powered Customer Call Analysis - Sample Data Setup
-- =====================================================================
-- This script creates the complete database structure and populates it
-- with realistic sample data for demonstrating AI call analysis capabilities
-- =====================================================================

-- Create database and schema
CREATE DATABASE IF NOT EXISTS CALL_ANALYTICS;
USE DATABASE CALL_ANALYTICS;

CREATE SCHEMA IF NOT EXISTS CUSTOMER_SERVICE;
USE SCHEMA CUSTOMER_SERVICE;

-- =====================================================================
-- 1. CREATE STAGES AND FILE FORMATS
-- =====================================================================

-- Create stage for audio files
CREATE OR REPLACE STAGE call_center_audio
    COMMENT = 'Stage for storing customer call audio files (.wav, .mp3, .flac)';

-- Create file format for CSV data loading (if needed)
CREATE OR REPLACE FILE FORMAT csv_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    TRIM_SPACE = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    ESCAPE = 'NONE'
    ESCAPE_UNENCLOSED_FIELD = '\134'
    DATE_FORMAT = 'AUTO'
    TIMESTAMP_FORMAT = 'AUTO'
    NULL_IF = ('NULL', 'null', '', 'N/A', 'n/a');

-- =====================================================================
-- 2. CREATE CORE TABLES
-- =====================================================================

-- Main transcription table
CREATE OR REPLACE TABLE call_transcriptions (
    call_id STRING PRIMARY KEY,
    audio_file_name STRING NOT NULL,
    transcription TEXT,
    call_duration_seconds INTEGER,
    agent_id STRING,
    customer_phone STRING,
    customer_id STRING,
    call_start_time TIMESTAMP_LTZ,
    call_end_time TIMESTAMP_LTZ,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- AI analysis results table
CREATE OR REPLACE TABLE call_analysis (
    analysis_id STRING PRIMARY KEY,
    call_id STRING NOT NULL,
    call_category STRING,
    sentiment_score FLOAT,
    sentiment_label STRING,
    urgency_level STRING,
    key_topics VARCHAR,
    customer_satisfaction_score FLOAT,
    requires_escalation BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT,
    analysis_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Alert and escalation tracking
CREATE OR REPLACE TABLE call_alerts (
    alert_id STRING PRIMARY KEY,
    call_id STRING NOT NULL,
    alert_type STRING,
    alert_reason TEXT,
    priority_level STRING,
    assigned_to STRING,
    status STRING DEFAULT 'OPEN',
    resolution_notes TEXT,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    resolved_at TIMESTAMP_LTZ
);

-- Agent information table
CREATE OR REPLACE TABLE agents (
    agent_id STRING PRIMARY KEY,
    agent_name STRING NOT NULL,
    department STRING,
    hire_date DATE,
    performance_rating FLOAT,
    specialization VARCHAR,
    status STRING DEFAULT 'ACTIVE'
);

-- Customer information table
CREATE OR REPLACE TABLE customers (
    customer_id STRING PRIMARY KEY,
    customer_name STRING,
    customer_phone STRING,
    account_type STRING,
    registration_date DATE,
    lifetime_value FLOAT,
    preferred_contact_method STRING,
    status STRING DEFAULT 'ACTIVE'
);

-- =====================================================================
-- 3. POPULATE SAMPLE DATA
-- =====================================================================

-- Insert sample agents
INSERT INTO agents (agent_id, agent_name, department, hire_date, performance_rating, specialization, status) VALUES
    ('AGENT_001', 'Sarah Mitchell', 'Customer Support', '2022-03-15', 4.2, 'Technical Support, Billing', 'ACTIVE'),
    ('AGENT_002', 'Mike Rodriguez', 'Customer Support', '2021-08-22', 4.7, 'Sports Programs, Account Management', 'ACTIVE'),
    ('AGENT_003', 'Jennifer Chen', 'Customer Support', '2023-01-10', 3.9, 'General Inquiries, Complaints', 'ACTIVE'),
    ('AGENT_004', 'David Thompson', 'Technical Support', '2020-11-05', 4.5, 'Technical Issues, Installation', 'ACTIVE'),
    ('AGENT_005', 'Lisa Johnson', 'Sales Support', '2022-07-12', 4.1, 'Sales, Upselling', 'ACTIVE');

-- Insert sample customers
INSERT INTO customers (customer_id, customer_name, customer_phone, account_type, registration_date, lifetime_value, preferred_contact_method, status) VALUES
    ('CUST_001', 'John Williams', '+1234567890', 'Premium', '2020-05-15', 2500.00, 'Phone', 'ACTIVE'),
    ('CUST_002', 'Maria Garcia', '+1234567891', 'Standard', '2021-02-28', 1200.00, 'Email', 'ACTIVE'),
    ('CUST_003', 'Robert Brown', '+1234567892', 'Premium', '2019-11-10', 3200.00, 'Phone', 'ACTIVE'),
    ('CUST_004', 'Emily Davis', '+1234567893', 'Standard', '2022-01-20', 800.00, 'Text', 'ACTIVE'),
    ('CUST_005', 'Michael Wilson', '+1234567894', 'Premium', '2020-09-05', 2800.00, 'Phone', 'ACTIVE'),
    ('CUST_006', 'Jessica Taylor', '+1234567895', 'Standard', '2021-06-15', 950.00, 'Email', 'ACTIVE'),
    ('CUST_007', 'Christopher Lee', '+1234567896', 'Premium', '2019-03-22', 4100.00, 'Phone', 'ACTIVE'),
    ('CUST_008', 'Amanda Moore', '+1234567897', 'Standard', '2022-04-18', 650.00, 'Text', 'ACTIVE');

-- Insert sample call transcriptions with realistic scenarios
INSERT INTO call_transcriptions (
    call_id, audio_file_name, transcription, call_duration_seconds, 
    agent_id, customer_phone, customer_id, call_start_time, call_end_time
) VALUES
    -- Baseball program inquiry (POSITIVE MATCH)
    ('CALL_001', 'baseball_inquiry_001.wav', 
     'Hi, I''m calling about the baseball program that was mentioned in your recent newsletter. My son is really interested in joining the little league program this summer. Can you tell me more about the schedule and registration process? I want to make sure we don''t miss the deadline for the program enrollment.',
     420, 'AGENT_002', '+1234567890', 'CUST_001', 
     '2024-03-15 09:15:00'::timestamp_ltz, '2024-03-15 09:22:00'::timestamp_ltz),
     
    -- Baseball equipment complaint (POSITIVE MATCH)  
    ('CALL_002', 'baseball_equipment_002.wav',
     'I''m really frustrated with the baseball equipment delivery. I ordered bats and gloves for our team''s program three weeks ago and they still haven''t arrived. The season program starts next week and we need this equipment urgently. This is affecting our entire training schedule.',
     315, 'AGENT_001', '+1234567891', 'CUST_002',
     '2024-03-15 14:30:00'::timestamp_ltz, '2024-03-15 14:35:15'::timestamp_ltz),
     
    -- Soccer discussion (NEGATIVE MATCH - should be excluded)
    ('CALL_003', 'soccer_discussion_003.wav',
     'Hello, I wanted to ask about the sports channel package. My daughter loves soccer and we want to watch the World Cup games. Do you have any soccer-specific packages? Also, I heard there might be some baseball games included, but we''re primarily interested in soccer coverage.',
     280, 'AGENT_003', '+1234567892', 'CUST_003',
     '2024-03-15 11:45:00'::timestamp_ltz, '2024-03-15 11:49:40'::timestamp_ltz),
     
    -- Baseball coaching program (POSITIVE MATCH)
    ('CALL_004', 'baseball_coaching_004.wav',
     'I''m interested in the baseball coaching certification program you offer. I''ve been coaching youth baseball for five years and want to advance my skills. Can you provide details about the program curriculum and the schedule for the upcoming sessions?',
     380, 'AGENT_002', '+1234567893', 'CUST_004',
     '2024-03-16 10:20:00'::timestamp_ltz, '2024-03-16 10:26:20'::timestamp_ltz),
     
    -- General billing inquiry (NEUTRAL)
    ('CALL_005', 'billing_inquiry_005.wav',
     'Hi, I''m calling about my monthly bill. There seems to be an extra charge that I don''t understand. Can you help me review my account and explain what this fee is for? I''ve been a customer for three years and this is the first time I''ve seen this charge.',
     195, 'AGENT_001', '+1234567894', 'CUST_005',
     '2024-03-16 13:10:00'::timestamp_ltz, '2024-03-16 13:13:15'::timestamp_ltz),
     
    -- Baseball fantasy league (POSITIVE MATCH)
    ('CALL_006', 'baseball_fantasy_006.wav',
     'I''m calling about the fantasy baseball program that was advertised. I want to know more about how the league works and what the schedule looks like for the season. Is there a specific program fee and when does registration close?',
     255, 'AGENT_005', '+1234567895', 'CUST_006',
     '2024-03-17 16:45:00'::timestamp_ltz, '2024-03-17 16:49:15'::timestamp_ltz),
     
    -- Technical support call
    ('CALL_007', 'technical_support_007.wav',
     'My internet has been really slow for the past week. I''m having trouble streaming videos and my work calls keep dropping. Can you run a diagnostic test on my connection? This is affecting my productivity and I need this resolved quickly.',
     445, 'AGENT_004', '+1234567896', 'CUST_007',
     '2024-03-17 08:30:00'::timestamp_ltz, '2024-03-17 08:37:25'::timestamp_ltz),
     
    -- Baseball tournament coverage (POSITIVE MATCH)
    ('CALL_008', 'baseball_tournament_008.wav',
     'I''m trying to find information about the college baseball tournament coverage. My nephew is playing and I want to make sure I can watch the games. Do you have a special sports program or package that includes the tournament schedule?',
     290, 'AGENT_003', '+1234567897', 'CUST_008',
     '2024-03-18 12:15:00'::timestamp_ltz, '2024-03-18 12:19:50'::timestamp_ltz);

-- Insert AI analysis results for each call
INSERT INTO call_analysis (
    analysis_id, call_id, call_category, sentiment_score, sentiment_label, urgency_level, 
    key_topics, customer_satisfaction_score, requires_escalation, confidence_score
) VALUES
    ('ANALYSIS_001', 'CALL_001', 'Sports Program Inquiry', 0.7, 'POSITIVE', 'MEDIUM', 
     'baseball, program, schedule, registration', 8.5, FALSE, 0.92),
     
    ('ANALYSIS_002', 'CALL_002', 'Equipment Complaint', -0.6, 'NEGATIVE', 'HIGH', 
     'baseball, equipment, delivery, delay, program', 3.2, TRUE, 0.88),
     
    ('ANALYSIS_003', 'CALL_003', 'Sports Package Inquiry', 0.3, 'NEUTRAL', 'LOW', 
     'soccer, sports, package, baseball', 7.0, FALSE, 0.85),
     
    ('ANALYSIS_004', 'CALL_004', 'Training Program Inquiry', 0.8, 'POSITIVE', 'MEDIUM', 
     'baseball, coaching, program, certification, schedule', 9.1, FALSE, 0.94),
     
    ('ANALYSIS_005', 'CALL_005', 'Billing Question', -0.2, 'NEUTRAL', 'MEDIUM', 
     'billing, charge, account, fee', 6.5, FALSE, 0.79),
     
    ('ANALYSIS_006', 'CALL_006', 'Fantasy League Inquiry', 0.6, 'POSITIVE', 'LOW', 
     'baseball, fantasy, program, league, schedule', 8.0, FALSE, 0.87),
     
    ('ANALYSIS_007', 'CALL_007', 'Technical Support', -0.4, 'NEGATIVE', 'HIGH', 
     'internet, slow, technical, streaming', 4.1, TRUE, 0.91),
     
    ('ANALYSIS_008', 'CALL_008', 'Sports Coverage Inquiry', 0.5, 'POSITIVE', 'MEDIUM', 
     'baseball, tournament, sports, program, schedule', 7.8, FALSE, 0.89);

-- Insert alerts for calls requiring escalation
INSERT INTO call_alerts (
    alert_id, call_id, alert_type, alert_reason, priority_level, assigned_to, status
) VALUES
    ('ALERT_001', 'CALL_002', 'DELIVERY_ISSUE', 
     'Customer frustrated about delayed baseball equipment delivery affecting program start', 
     'HIGH', 'MANAGER_001', 'OPEN'),
     
    ('ALERT_002', 'CALL_007', 'TECHNICAL_ISSUE', 
     'Persistent internet connectivity problems affecting customer productivity', 
     'HIGH', 'TECH_MANAGER_001', 'IN_PROGRESS');

-- =====================================================================
-- 4. CREATE VIEWS FOR ANALYSIS
-- =====================================================================

-- View for baseball-related calls (matching the notebook requirements)
CREATE OR REPLACE VIEW baseball_alerts AS
SELECT
    ct.call_id,
    ct.transcription,
    ca.call_category,
    ca.sentiment_score,
    ca.urgency_level,
    -- Simulate the AI proximity analysis result
    CASE 
        WHEN (CONTAINS(LOWER(ct.transcription), 'baseball') 
              AND (CONTAINS(LOWER(ct.transcription), 'program') 
                   OR CONTAINS(LOWER(ct.transcription), 'schedule'))
              AND NOT CONTAINS(LOWER(ct.transcription), 'soccer'))
        THEN 'Yes'
        ELSE 'No'
    END AS is_baseball_near_program,
    -- Generate summary (simulated)
    CASE 
        WHEN ct.call_id = 'CALL_001' THEN 'Customer inquiry about youth baseball program registration and schedule'
        WHEN ct.call_id = 'CALL_002' THEN 'Urgent complaint about delayed baseball equipment delivery for team program'
        WHEN ct.call_id = 'CALL_004' THEN 'Request for information about baseball coaching certification program'
        WHEN ct.call_id = 'CALL_006' THEN 'Interest in fantasy baseball league program and schedule'
        WHEN ct.call_id = 'CALL_008' THEN 'Inquiry about college baseball tournament coverage program'
        ELSE 'General customer service call'
    END AS summary
FROM call_transcriptions ct
LEFT JOIN call_analysis ca ON ct.call_id = ca.call_id
WHERE CONTAINS(LOWER(ct.transcription), 'baseball')
  AND NOT CONTAINS(LOWER(ct.transcription), 'soccer');

-- Analytics view for dashboard metrics
CREATE OR REPLACE VIEW call_analytics_summary AS
SELECT
    DATE(ct.call_start_time) as call_date,
    COUNT(*) as total_calls,
    COUNT(CASE WHEN ca.sentiment_label = 'POSITIVE' THEN 1 END) as positive_calls,
    COUNT(CASE WHEN ca.sentiment_label = 'NEGATIVE' THEN 1 END) as negative_calls,
    COUNT(CASE WHEN ca.requires_escalation = TRUE THEN 1 END) as escalated_calls,
    AVG(ca.customer_satisfaction_score) as avg_satisfaction,
    COUNT(CASE WHEN CONTAINS(LOWER(ct.transcription), 'baseball') THEN 1 END) as baseball_mentions
FROM call_transcriptions ct
LEFT JOIN call_analysis ca ON ct.call_id = ca.call_id
GROUP BY DATE(ct.call_start_time)
ORDER BY call_date DESC;

-- =====================================================================
-- 5. SAMPLE QUERIES FOR TESTING
-- =====================================================================

-- Test query 1: Find all baseball-related calls with proximity analysis
SELECT 
    call_id,
    LEFT(summary, 100) as summary_preview,
    is_baseball_near_program
FROM baseball_alerts
WHERE is_baseball_near_program = 'Yes';

-- Test query 2: Get escalation alerts
SELECT 
    a.alert_id,
    ct.customer_phone,
    a.alert_reason,
    a.priority_level,
    a.status
FROM call_alerts a
JOIN call_transcriptions ct ON a.call_id = ct.call_id
WHERE a.status = 'OPEN';

-- Test query 3: Daily analytics summary
SELECT * FROM call_analytics_summary;

-- Test query 4: Sentiment analysis by category
SELECT 
    call_category,
    COUNT(*) as call_count,
    AVG(sentiment_score) as avg_sentiment,
    AVG(customer_satisfaction_score) as avg_satisfaction
FROM call_analysis
GROUP BY call_category
ORDER BY avg_sentiment DESC;

-- =====================================================================
-- 6. VERIFICATION QUERIES
-- =====================================================================

-- Verify data loading
SELECT 'call_transcriptions' as table_name, COUNT(*) as record_count FROM call_transcriptions
UNION ALL
SELECT 'call_analysis' as table_name, COUNT(*) as record_count FROM call_analysis
UNION ALL
SELECT 'call_alerts' as table_name, COUNT(*) as record_count FROM call_alerts
UNION ALL
SELECT 'agents' as table_name, COUNT(*) as record_count FROM agents
UNION ALL
SELECT 'customers' as table_name, COUNT(*) as record_count FROM customers;

-- Show sample of each table
SELECT 'Recent Calls' as section, call_id, audio_file_name, agent_id, customer_phone
FROM call_transcriptions 
ORDER BY created_at DESC 
LIMIT 3;

-- =====================================================================
-- END OF SETUP SCRIPT
-- =====================================================================

-- Script execution summary
SELECT 
    'Setup Complete!' as status,
    CURRENT_TIMESTAMP() as completed_at,
    'Database: CALL_ANALYTICS, Schema: CUSTOMER_SERVICE' as location,
    'Ready for AI analysis demonstration' as next_steps;
