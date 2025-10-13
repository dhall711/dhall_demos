-- =====================================================================
-- Snowflake AI_SQL Functions - Live Examples with Sample Data
-- =====================================================================
-- This script demonstrates how to use Snowflake AI_SQL functions
-- with the sample data created in setup_sample_data.sql
-- =====================================================================

-- Make sure you're using the correct database and schema
USE DATABASE CALL_ANALYTICS;
USE SCHEMA CUSTOMER_SERVICE;

-- =====================================================================
-- 1. SENTIMENT ANALYSIS WITH AI_SENTIMENT()
-- =====================================================================

-- Analyze sentiment of all call transcriptions
SELECT 
    call_id,
    audio_file_name,
    AI_SENTIMENT(LEFT(transcription, 4000)) as ai_sentiment_object,
    AI_SENTIMENT(LEFT(transcription, 4000)):sentiment::FLOAT as ai_sentiment_score,
    AI_SENTIMENT(LEFT(transcription, 4000)):label::STRING as ai_sentiment_label,
    LEFT(transcription, 100) as transcript_preview
FROM call_transcriptions
ORDER BY ai_sentiment_score DESC;

-- Compare with pre-populated sentiment scores
SELECT 
    ct.call_id,
    AI_SENTIMENT(LEFT(ct.transcription, 4000)) as ai_sentiment,
    ca.sentiment_score as manual_sentiment,
    ca.sentiment_label,
    -- Extract sentiment score from the AI_SENTIMENT result object
    AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT as ai_sentiment_score,
    ABS(AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT - ca.sentiment_score) as sentiment_difference
FROM call_transcriptions ct
JOIN call_analysis ca ON ct.call_id = ca.call_id
ORDER BY sentiment_difference DESC;

-- =====================================================================
-- 2. CLASSIFICATION WITH AI_CLASSIFY()
-- =====================================================================

-- Classify calls into predefined categories
SELECT 
    call_id,
    audio_file_name,
    AI_CLASSIFY(
        LEFT(transcription, 4000),
        ARRAY_CONSTRUCT('Sales Inquiry', 'Technical Support', 'Billing Question', 'Sports Program Inquiry', 'Equipment Complaint', 'General Conversation')
    ) as ai_classification,
    LEFT(transcription, 150) as transcript_preview
FROM call_transcriptions
ORDER BY call_id;

-- Multi-label classification for call topics
SELECT 
    call_id,
    AI_CLASSIFY(
        LEFT(transcription, 4000),
        ARRAY_CONSTRUCT('Baseball', 'Soccer', 'Equipment', 'Billing', 'Technical', 'Program Registration')
    ) as primary_topic,
    AI_CLASSIFY(
        LEFT(transcription, 4000),
        ARRAY_CONSTRUCT('Urgent', 'Normal', 'Low Priority')
    ) as urgency_classification
FROM call_transcriptions
WHERE CONTAINS(LOWER(transcription), 'baseball') OR CONTAINS(LOWER(transcription), 'soccer');

-- =====================================================================
-- 3. SUMMARIZATION WITH AI_COMPLETE()
-- =====================================================================

-- Generate summaries for all calls using AI_COMPLETE
SELECT 
    call_id,
    audio_file_name,
    AI_COMPLETE('llama2-70b-chat', CONCAT('Summarize this customer service call in 2-3 sentences: ', LEFT(transcription, 4000))) as ai_summary,
    LENGTH(transcription) as original_length,
    LENGTH(AI_COMPLETE('llama2-70b-chat', CONCAT('Summarize this customer service call in 2-3 sentences: ', LEFT(transcription, 4000)))) as summary_length
FROM call_transcriptions
ORDER BY original_length DESC;

-- Generate summaries specifically for baseball-related calls
SELECT 
    call_id,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('Summarize this customer call about baseball programs in 2-3 sentences: ', LEFT(transcription, 4000))
    ) as detailed_summary
FROM call_transcriptions
WHERE CONTAINS(LOWER(transcription), 'baseball')
  AND NOT CONTAINS(LOWER(transcription), 'soccer');

-- =====================================================================
-- 4. ADVANCED ANALYSIS WITH AI_COMPLETE()
-- =====================================================================

-- Proximity analysis: Check if "baseball" is mentioned near "program" or "schedule"
SELECT 
    call_id,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT(
            'Analyze this customer service call transcript and determine if the word "baseball" ',
            'appears within 50 words of either "program" or "schedule". ',
            'Respond with only "Yes" or "No". ',
            'Transcript: ', LEFT(transcription, 4000)
        )
    ) as baseball_proximity_check,
    LEFT(transcription, 200) as transcript_preview
FROM call_transcriptions
WHERE CONTAINS(LOWER(transcription), 'baseball');

-- Extract specific information using AI_COMPLETE
SELECT 
    call_id,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT(
            'From this customer service call, extract the following information in JSON format: ',
            '{"customer_issue": "brief description", "urgency": "low/medium/high", ',
            '"requires_followup": "yes/no", "mentioned_programs": ["list of programs mentioned"]}. ',
            'Call transcript: ', LEFT(transcription, 4000)
        )
    ) as extracted_info
FROM call_transcriptions
WHERE call_id IN ('CALL_001', 'CALL_002', 'CALL_004');

-- Customer satisfaction analysis
SELECT 
    call_id,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT(
            'Rate the customer satisfaction level in this call on a scale of 1-10 ',
            'and explain why. Consider tone, resolution, and customer responses. ',
            'Format: "Score: X/10. Reason: [explanation]". ',
            'Transcript: ', LEFT(transcription, 4000)
        )
    ) as satisfaction_analysis
FROM call_transcriptions
WHERE call_id IN ('CALL_002', 'CALL_007'); -- Focus on complaint calls

-- =====================================================================
-- 5. INFORMATION EXTRACTION WITH AI_COMPLETE()
-- =====================================================================

-- Extract specific answers from call transcripts using AI_COMPLETE
SELECT 
    call_id,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('What program is mentioned? Answer briefly: ', LEFT(transcription, 1000))
    ) as program_inquiry,
    AI_COMPLETE(
        'llama2-70b-chat', 
        CONCAT('Main issue? Answer briefly: ', LEFT(transcription, 1000))
    ) as main_concern,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('Any timeline mentioned? Yes/No: ', LEFT(transcription, 1000))
    ) as timeline_mentioned
FROM call_transcriptions
WHERE CONTAINS(LOWER(transcription), 'baseball');

-- Extract sports-related information using AI_COMPLETE
SELECT 
    call_id,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('What sports mentioned? Answer briefly: ', LEFT(transcription, 1000))
    ) as sports_mentioned,
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('Youth or adult programs? Answer: ', LEFT(transcription, 1000))
    ) as program_type
FROM call_transcriptions
WHERE CONTAINS(LOWER(transcription), 'baseball') OR CONTAINS(LOWER(transcription), 'soccer');

-- =====================================================================
-- 6. ADVANCED FILTERING AND ANALYSIS COMBINATIONS
-- =====================================================================

-- Create comprehensive analysis view using multiple AI_SQL functions
CREATE OR REPLACE VIEW ai_call_analysis AS
SELECT 
    ct.call_id,
    ct.audio_file_name,
    ct.agent_id,
    ct.customer_phone,
    
    -- Sentiment Analysis
    AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT as ai_sentiment_score,
    
    -- Classification
    AI_CLASSIFY(
        LEFT(ct.transcription, 4000),
        ARRAY_CONSTRUCT('Sports Program Inquiry', 'Equipment Issue', 'Billing Question', 'Technical Support', 'General Inquiry')
    ) as call_category,
    
    -- Summarization
    AI_COMPLETE('llama2-70b-chat', CONCAT('Summarize this call in 1-2 sentences: ', LEFT(ct.transcription, 4000))) as call_summary,
    
    -- Baseball proximity check
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT(
            'Does this call mention "baseball" within 50 words of "program" or "schedule"? ',
            'Answer only "Yes" or "No". Text: ', LEFT(ct.transcription, 4000)
        )
    ) as baseball_program_proximity,
    
    -- Extract key information using AI_COMPLETE
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('Customer main request? Answer briefly: ', LEFT(ct.transcription, 1000))
    ) as main_request,
    
    ct.created_at
FROM call_transcriptions ct;

-- Query the comprehensive analysis
SELECT 
    call_id,
    call_category,
    ai_sentiment_score,
    baseball_program_proximity,
    call_summary,
    main_request
FROM ai_call_analysis
ORDER BY ai_sentiment_score ASC; -- Show most negative calls first

-- =====================================================================
-- 7. BASEBALL PROGRAM SPECIFIC ANALYSIS
-- =====================================================================

-- Enhanced baseball alerts using live AI_SQL functions
CREATE OR REPLACE VIEW live_baseball_alerts AS
SELECT
    ct.call_id,
    ct.customer_phone,
    ct.agent_id,
    
    -- Use AI_COMPLETE to analyze baseball program relevance
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT(
            'Analyze this customer service call and determine: ',
            '1) Is this about baseball programs/services? ',
            '2) What type of baseball-related request is this? ',
            '3) Does this require immediate attention? ',
            'Format as: "Relevant: Yes/No | Type: [type] | Urgent: Yes/No | Reason: [brief reason]" ',
            'Call: ', LEFT(ct.transcription, 4000)
        )
    ) as baseball_analysis,
    
    AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT as sentiment_score,
    AI_COMPLETE('llama2-70b-chat', CONCAT('Summarize this baseball-related call in 1-2 sentences: ', LEFT(ct.transcription, 4000))) as summary,
    
    -- Check for exclusion criteria (soccer mentions)
    CASE 
        WHEN CONTAINS(LOWER(ct.transcription), 'soccer') THEN 'EXCLUDED'
        ELSE 'INCLUDED'
    END as filter_status,
    
    ct.created_at
FROM call_transcriptions ct
WHERE CONTAINS(LOWER(ct.transcription), 'baseball')
ORDER BY ct.created_at DESC;

-- Query live baseball alerts
SELECT * FROM live_baseball_alerts 
WHERE filter_status = 'INCLUDED';

-- SIMPLE BASEBALL ANALYSIS: Basic AI-powered detection
SELECT 
    call_id,
    customer_phone,
    agent_id,
    
    -- Simple AI classification
    AI_CLASSIFY(
        LEFT(transcription, 2000),
        ARRAY_CONSTRUCT('Baseball Program', 'Baseball Equipment', 'Other Baseball', 'Not Baseball')
    ) as category,
    
    -- Basic sentiment
    AI_SENTIMENT(LEFT(transcription, 2000)):sentiment::FLOAT as sentiment,
    
    -- Simple proximity check
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT('Does this mention baseball programs? Yes/No: ', LEFT(transcription, 2000))
    ) as program_related,
    
    LEFT(transcription, 150) as preview
FROM call_transcriptions
WHERE CONTAINS(LOWER(transcription), 'baseball')
  AND NOT CONTAINS(LOWER(transcription), 'soccer');

-- =====================================================================
-- 8. ESCALATION DETECTION USING AI
-- =====================================================================

-- Identify calls that should be escalated using AI_SQL functions
SELECT 
    ct.call_id,
    ct.customer_phone,
    ct.agent_id,
    
    AI_COMPLETE(
        'llama2-70b-chat',
        CONCAT(
            'Based on this customer service call, should this be escalated to management? ',
            'Consider: customer frustration, unresolved issues, complaints, urgent needs. ',
            'Respond with: "ESCALATE: Yes/No | REASON: [brief reason] | PRIORITY: High/Medium/Low" ',
            'Call transcript: ', LEFT(ct.transcription, 4000)
        )
    ) as escalation_recommendation,
    
    AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT as sentiment,
    AI_COMPLETE('llama2-70b-chat', CONCAT('Summarize this call for management review: ', LEFT(ct.transcription, 4000))) as summary
    
FROM call_transcriptions ct
WHERE AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT < -0.3 -- Focus on negative sentiment calls
ORDER BY AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT ASC;

-- =====================================================================
-- 9. PERFORMANCE METRICS AND REPORTING
-- =====================================================================

-- Daily performance report using AI_SQL functions
SELECT 
    DATE(ct.created_at) as call_date,
    COUNT(*) as total_calls,
    
    -- Sentiment distribution
    COUNT(CASE WHEN AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT > 0.2 THEN 1 END) as positive_calls,
    COUNT(CASE WHEN AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT BETWEEN -0.2 AND 0.2 THEN 1 END) as neutral_calls,
    COUNT(CASE WHEN AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT < -0.2 THEN 1 END) as negative_calls,
    
    -- Baseball program mentions
    COUNT(CASE WHEN CONTAINS(LOWER(ct.transcription), 'baseball') 
               AND NOT CONTAINS(LOWER(ct.transcription), 'soccer') THEN 1 END) as baseball_program_calls,
    
    -- Average sentiment
    AVG(AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT) as avg_sentiment
    
FROM call_transcriptions ct
GROUP BY DATE(ct.created_at)
ORDER BY call_date DESC;

-- =====================================================================
-- 10. TESTING AND VALIDATION QUERIES
-- =====================================================================

-- Test all AI_SQL functions on a single call
SELECT 
    'CALL_001' as test_call,
    
    -- Original data
    transcription as original_transcript,
    
    -- AI_SQL function results
    AI_SENTIMENT(LEFT(transcription, 4000)):sentiment::FLOAT as sentiment,
    AI_CLASSIFY(LEFT(transcription, 4000), ARRAY_CONSTRUCT('Positive', 'Negative', 'Neutral')) as classification,
    AI_COMPLETE('llama2-70b-chat', CONCAT('Summarize this call: ', LEFT(transcription, 4000))) as summary,
    AI_COMPLETE('llama2-70b-chat', CONCAT('Customer request? Answer: ', LEFT(transcription, 1000))) as extracted_request
    
FROM call_transcriptions 
WHERE call_id = 'CALL_001';

-- Performance comparison: Manual vs AI_SQL analysis
SELECT 
    ct.call_id,
    
    -- Manual analysis (from setup data)
    ca.sentiment_score as manual_sentiment,
    ca.call_category as manual_category,
    
    -- AI_SQL analysis
    AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT as ai_sentiment,
    AI_CLASSIFY(
        LEFT(ct.transcription, 4000), 
        ARRAY_CONSTRUCT('Sports Program Inquiry', 'Equipment Complaint', 'Billing Question', 'Technical Support')
    ) as ai_category,
    
    -- Differences
    ABS(ca.sentiment_score - AI_SENTIMENT(LEFT(ct.transcription, 4000)):sentiment::FLOAT) as sentiment_diff
    
FROM call_transcriptions ct
JOIN call_analysis ca ON ct.call_id = ca.call_id
ORDER BY sentiment_diff DESC;

-- =====================================================================
-- END OF AI_SQL EXAMPLES
-- =====================================================================

SELECT 
    'AI_SQL Analysis Complete!' as status,
    CURRENT_TIMESTAMP() as completed_at,
    COUNT(*) as calls_analyzed
FROM call_transcriptions;
