# Lab 09: Multimodal AI with Cortex AISQL
## Comprehensive Data Quality Through Multimodal Intelligence

### 🎯 **Lab Objectives**

In this advanced lab, you'll integrate structured and unstructured data analysis using Cortex AISQL to create comprehensive data quality insights. You'll analyze images, documents, text, and traditional data together to detect quality issues that single-modal approaches might miss.

### 📚 **Learning Outcomes**

By the end of this lab, you will be able to:
- Implement multimodal data quality analysis using Cortex AISQL
- Process images and documents for data quality insights
- Combine structured and unstructured data for comprehensive analysis
- Create multimodal anomaly detection systems
- Build intelligent document processing for quality validation

### 🏗️ **Architecture Overview**

Multimodal AI creates holistic data quality intelligence:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Structured    │    │   Cortex AISQL   │    │   Unified       │
│   Data          │───▶│   Multimodal     │───▶│   Quality       │
│   (Traditional) │    │   Analysis       │    │   Intelligence  │
└─────────────────┘    │   Engine         │    └─────────────────┘
                       └──────────────────┘              │
┌─────────────────┐              │                       │
│   Unstructured  │              │                       ▼
│   Data          │─────────────▲│              ┌─────────────────┐
│   (Images,Docs, │                             │   Comprehensive │
│   Text,Videos)  │                             │   Insights &    │
└─────────────────┘                             │   Actions       │
                                                └─────────────────┘
```

### 🔍 **Multimodal Analysis Capabilities**

#### 1. **Image Analysis** - Visual quality assessment and anomaly detection
#### 2. **Document Processing** - Extracting insights from reports and documents
#### 3. **Text Analysis** - Sentiment, topics, and pattern recognition
#### 4. **Cross-Modal Correlation** - Finding relationships across data types
#### 5. **Unified Intelligence** - Holistic quality understanding

### 🛠️ **Prerequisites**

- Completion of Labs 01-08
- Understanding of unstructured data concepts
- Basic knowledge of image and document processing
- Access to sample multimedia data

### 📝 **Lab Exercises**

#### **Exercise 1: Visual Data Quality Analysis (45 minutes)**

Analyze images and visual data for quality insights:

1. **Create Image Analysis for Ride Safety**
   ```sql
   -- Analyze ride inspection photos for safety data quality
   CREATE OR REPLACE TABLE RIDE_INSPECTION_IMAGES (
       inspection_id STRING DEFAULT UUID_STRING(),
       ride_id STRING NOT NULL,
       inspection_date DATE NOT NULL,
       image_url STRING NOT NULL,
       image_type STRING, -- 'SAFETY_CHECK', 'MAINTENANCE', 'INCIDENT_REPORT'
       inspector_notes STRING,
       uploaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
   );
   
   -- Multimodal analysis combining images and structured data
   CREATE OR REPLACE FUNCTION analyze_ride_safety_multimodal(ride_id STRING)
   RETURNS TABLE (
       ride_id STRING,
       safety_analysis STRING,
       data_quality_issues ARRAY,
       visual_anomalies STRING,
       recommended_actions STRING,
       confidence_score FLOAT
   )
   LANGUAGE SQL
   AS
   $$
   WITH ride_data AS (
       SELECT 
           r.ride_id,
           r.ride_name,
           r.max_capacity,
           r.safety_rating,
           ro.wait_time_minutes,
           ro.guest_satisfaction_score,
           ro.operation_date
       FROM RIDES r
       JOIN RIDE_OPERATIONS ro ON r.ride_id = ro.ride_id
       WHERE r.ride_id = ride_id
       AND ro.operation_date >= DATEADD('day', -7, CURRENT_DATE())
   ),
   inspection_images AS (
       SELECT 
           rii.ride_id,
           rii.image_url,
           rii.image_type,
           rii.inspector_notes
       FROM RIDE_INSPECTION_IMAGES rii
       WHERE rii.ride_id = ride_id
       AND rii.inspection_date >= DATEADD('day', -30, CURRENT_DATE())
   )
   SELECT 
       rd.ride_id,
       SNOWFLAKE.CORTEX.COMPLETE_MULTIMODAL(
           'anthropic.claude-3-5-sonnet',
           ARRAY_CONSTRUCT(
               'Analyze this ride safety data for data quality issues: ',
               'Ride: ' || rd.ride_name || 
               ', Capacity: ' || rd.max_capacity ||
               ', Safety Rating: ' || rd.safety_rating ||
               ', Recent Wait Times: ' || LISTAGG(rd.wait_time_minutes, ', ') ||
               ', Guest Satisfaction: ' || AVG(rd.guest_satisfaction_score),
               ' Combined with these inspection images: ',
               (SELECT LISTAGG(ii.image_url, ', ') FROM inspection_images ii),
               ' Inspector notes: ',
               (SELECT LISTAGG(ii.inspector_notes, '; ') FROM inspection_images ii),
               '. Identify:
               1. Inconsistencies between visual and data indicators
               2. Safety concerns visible in images vs. reported data
               3. Data quality issues (missing, inaccurate, or inconsistent data)
               4. Visual anomalies that suggest measurement problems
               5. Recommendations for data collection improvements'
           )
       ) as safety_analysis,
       PARSE_JSON(
           SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
               safety_analysis,
               'What specific data quality issues were identified? Return as JSON array.'
           )
       ) as data_quality_issues,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           safety_analysis,
           'What visual anomalies were detected in the inspection images?'
       ) as visual_anomalies,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           safety_analysis,
           'What are the top 3 recommended actions to improve data quality?'
       ) as recommended_actions,
       0.85 as confidence_score
   FROM ride_data rd
   CROSS JOIN inspection_images ii
   GROUP BY rd.ride_id, rd.ride_name, rd.max_capacity, rd.safety_rating
   $$;
   ```

2. **Guest Flow Analysis Through Video/Images**
   ```sql
   -- Analyze guest flow patterns using visual data
   CREATE OR REPLACE TABLE GUEST_FLOW_IMAGES (
       flow_id STRING DEFAULT UUID_STRING(),
       park_id STRING NOT NULL,
       location_description STRING,
       image_timestamp TIMESTAMP_LTZ,
       image_url STRING NOT NULL,
       crowd_level_reported INTEGER, -- Manually reported crowd level 1-10
       weather_conditions STRING
   );
   
   -- Multimodal crowd analysis
   CREATE OR REPLACE FUNCTION analyze_crowd_data_quality()
   RETURNS TABLE (
       location STRING,
       reported_vs_visual_analysis STRING,
       data_accuracy_assessment STRING,
       crowd_pattern_insights STRING,
       quality_improvement_suggestions STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH crowd_analysis AS (
       SELECT 
           gfi.location_description,
           gfi.crowd_level_reported,
           gfi.weather_conditions,
           SNOWFLAKE.CORTEX.COMPLETE_MULTIMODAL(
               'openai.gpt-4o',
               ARRAY_CONSTRUCT(
                   'Analyze this crowd level image and compare with reported data: ',
                   gfi.image_url,
                   ' Reported crowd level: ', gfi.crowd_level_reported, ' (scale 1-10)',
                   ' Weather: ', gfi.weather_conditions,
                   ' Location: ', gfi.location_description,
                   '. Assess:
                   1. Accuracy of reported crowd level vs. visual evidence
                   2. Data quality issues in crowd measurement
                   3. Patterns suggesting systematic measurement problems
                   4. Environmental factors affecting data accuracy
                   5. Recommendations for improved crowd data collection'
               )
           ) as crowd_analysis
       FROM GUEST_FLOW_IMAGES gfi
       WHERE gfi.image_timestamp >= DATEADD('day', -1, CURRENT_DATE())
   )
   SELECT 
       location_description as location,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           crowd_analysis,
           'How does the visual crowd level compare to the reported level?'
       ) as reported_vs_visual_analysis,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           crowd_analysis,
           'What data accuracy issues were identified?'
       ) as data_accuracy_assessment,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           crowd_analysis,
           'What patterns suggest systematic measurement problems?'
       ) as crowd_pattern_insights,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           crowd_analysis,
           'What are your recommendations for improving crowd data collection?'
       ) as quality_improvement_suggestions
   FROM crowd_analysis
   $$;
   ```

#### **Exercise 2: Document-Based Quality Intelligence (40 minutes)**

Process documents and reports for data quality insights:

1. **Incident Report Analysis**
   ```sql
   -- Analyze incident reports for data quality patterns
   CREATE OR REPLACE TABLE INCIDENT_REPORTS (
       report_id STRING DEFAULT UUID_STRING(),
       incident_date DATE NOT NULL,
       park_id STRING NOT NULL,
       ride_id STRING,
       report_document_url STRING NOT NULL,
       report_type STRING, -- 'SAFETY', 'OPERATIONAL', 'GUEST_COMPLAINT'
       manual_severity_rating INTEGER, -- 1-10 scale
       data_source STRING DEFAULT 'MANUAL_ENTRY'
   );
   
   -- Multimodal incident analysis
   CREATE OR REPLACE FUNCTION analyze_incident_data_quality()
   RETURNS TABLE (
       report_id STRING,
       document_summary STRING,
       data_consistency_check STRING,
       severity_validation STRING,
       missing_data_identification STRING,
       quality_recommendations STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH incident_analysis AS (
       SELECT 
           ir.report_id,
           ir.incident_date,
           ir.manual_severity_rating,
           ir.report_type,
           -- Get related structured data
           ro.wait_time_minutes,
           ro.guest_satisfaction_score,
           dqr.metric_value as quality_score,
           -- Analyze document
           SNOWFLAKE.CORTEX.COMPLETE_MULTIMODAL(
               'anthropic.claude-3-5-sonnet',
               ARRAY_CONSTRUCT(
                   'Analyze this incident report document: ',
                   ir.report_document_url,
                   ' Context - Incident Date: ', ir.incident_date,
                   ' Manual Severity Rating: ', ir.manual_severity_rating,
                   ' Report Type: ', ir.report_type,
                   ' Related Data - Wait Time: ', COALESCE(ro.wait_time_minutes, 0),
                   ' Guest Satisfaction: ', COALESCE(ro.guest_satisfaction_score, 0),
                   ' Data Quality Score: ', COALESCE(dqr.metric_value, 0),
                   '. Analyze for:
                   1. Consistency between document content and structured data
                   2. Validation of manually entered severity rating
                   3. Missing information that should be captured
                   4. Data quality issues in incident reporting process
                   5. Recommendations for improving data collection'
               )
           ) as document_analysis
       FROM INCIDENT_REPORTS ir
       LEFT JOIN RIDE_OPERATIONS ro ON ir.ride_id = ro.ride_id 
           AND ro.operation_date = ir.incident_date
       LEFT JOIN DATA_QUALITY_RESULTS dqr ON dqr.check_timestamp::DATE = ir.incident_date
       WHERE ir.incident_date >= DATEADD('week', -2, CURRENT_DATE())
   )
   SELECT 
       report_id,
       SNOWFLAKE.CORTEX.SUMMARIZE(document_analysis, 200) as document_summary,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           document_analysis,
           'How consistent is the document content with the structured data?'
       ) as data_consistency_check,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           document_analysis,
           'Is the manual severity rating appropriate based on the document content?'
       ) as severity_validation,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           document_analysis,
           'What missing information should be captured in structured data?'
       ) as missing_data_identification,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           document_analysis,
           'What are your top recommendations for improving incident data quality?'
       ) as quality_recommendations
   FROM incident_analysis
   $$;
   ```

2. **Financial Report Validation**
   ```sql
   -- Cross-validate financial reports with transactional data
   CREATE OR REPLACE FUNCTION validate_financial_reports_multimodal()
   RETURNS TABLE (
       report_period STRING,
       document_vs_data_comparison STRING,
       discrepancy_analysis STRING,
       data_quality_issues STRING,
       validation_confidence FLOAT
   )
   LANGUAGE SQL
   AS
   $$
   WITH financial_validation AS (
       SELECT 
           'Monthly_Report_' || TO_CHAR(CURRENT_DATE(), 'YYYY_MM') as report_period,
           -- Aggregate structured financial data
           SUM(t.purchase_amount) as total_ticket_revenue,
           COUNT(DISTINCT g.guest_id) as total_guests,
           AVG(ro.guest_satisfaction_score) as avg_satisfaction,
           -- Analyze financial report document
           SNOWFLAKE.CORTEX.COMPLETE_MULTIMODAL(
               'anthropic.claude-3-5-sonnet',
               ARRAY_CONSTRUCT(
                   'Analyze this financial report document: ',
                   '/financial_reports/monthly_summary.pdf',
                   ' Compare with calculated data:',
                   ' Calculated Revenue: $', SUM(t.purchase_amount),
                   ' Calculated Guest Count: ', COUNT(DISTINCT g.guest_id),
                   ' Calculated Avg Satisfaction: ', AVG(ro.guest_satisfaction_score),
                   '. Validate:
                   1. Revenue figures accuracy and consistency
                   2. Guest count validation
                   3. Performance metrics alignment
                   4. Identification of data quality issues
                   5. Potential causes of any discrepancies'
               )
           ) as validation_analysis
       FROM TICKETS t
       JOIN GUESTS g ON t.guest_id = g.guest_id
       LEFT JOIN RIDE_OPERATIONS ro ON g.park_id = ro.park_id
           AND g.visit_date = ro.operation_date
       WHERE t.purchase_date >= DATEADD('month', -1, CURRENT_DATE())
   )
   SELECT 
       report_period,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           validation_analysis,
           'How do the document figures compare with the calculated data?'
       ) as document_vs_data_comparison,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           validation_analysis,
           'What discrepancies were identified and what might cause them?'
       ) as discrepancy_analysis,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           validation_analysis,
           'What data quality issues were discovered in this validation?'
       ) as data_quality_issues,
       0.90 as validation_confidence
   FROM financial_validation
   $$;
   ```

#### **Exercise 3: Text and Sentiment Analysis Integration (35 minutes)**

Combine text analysis with structured data for comprehensive insights:

1. **Guest Feedback Multimodal Analysis**
   ```sql
   -- Analyze guest feedback text with operational data
   CREATE OR REPLACE TABLE GUEST_FEEDBACK_TEXT (
       feedback_id STRING DEFAULT UUID_STRING(),
       guest_id STRING NOT NULL,
       feedback_text STRING NOT NULL,
       feedback_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
       rating INTEGER, -- 1-5 stars
       feedback_channel STRING -- 'APP', 'EMAIL', 'SURVEY', 'SOCIAL_MEDIA'
   );
   
   -- Multimodal guest experience analysis
   CREATE OR REPLACE FUNCTION analyze_guest_experience_multimodal()
   RETURNS TABLE (
       guest_id STRING,
       sentiment_vs_rating_analysis STRING,
       operational_correlation STRING,
       data_quality_insights STRING,
       experience_improvement_suggestions STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH guest_experience_data AS (
       SELECT 
           gft.guest_id,
           gft.feedback_text,
           gft.rating,
           g.age,
           g.guest_type,
           ro.wait_time_minutes,
           ro.guest_satisfaction_score as operational_satisfaction,
           dqr.metric_value as data_quality_score
       FROM GUEST_FEEDBACK_TEXT gft
       JOIN GUESTS g ON gft.guest_id = g.guest_id
       LEFT JOIN RIDE_OPERATIONS ro ON g.park_id = ro.park_id 
           AND g.visit_date = ro.operation_date
       LEFT JOIN DATA_QUALITY_RESULTS dqr ON dqr.check_timestamp::DATE = g.visit_date
       WHERE gft.feedback_timestamp >= DATEADD('week', -1, CURRENT_TIMESTAMP())
   ),
   multimodal_analysis AS (
       SELECT 
           guest_id,
           SNOWFLAKE.CORTEX.COMPLETE(
               'anthropic.claude-3-5-sonnet',
               CONCAT(
                   'Analyze guest experience combining text feedback and operational data: ',
                   'Feedback Text: "', feedback_text, '"',
                   ' Star Rating: ', rating,
                   ' Guest Age: ', age,
                   ' Guest Type: ', guest_type,
                   ' Wait Time: ', COALESCE(wait_time_minutes, 0), ' minutes',
                   ' Operational Satisfaction Score: ', COALESCE(operational_satisfaction, 0),
                   ' Data Quality Score: ', COALESCE(data_quality_score, 0),
                   '. Analyze:
                   1. Consistency between text sentiment and star rating
                   2. Correlation with operational performance data
                   3. Data quality issues affecting guest experience measurement
                   4. Insights for improving experience tracking
                   5. Specific improvement recommendations'
               )
           ) as comprehensive_analysis
       FROM guest_experience_data
   )
   SELECT 
       guest_id,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           comprehensive_analysis,
           'How does the text sentiment compare with the star rating?'
       ) as sentiment_vs_rating_analysis,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           comprehensive_analysis,
           'What correlations exist with operational performance data?'
       ) as operational_correlation,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           comprehensive_analysis,
           'What data quality issues affect guest experience measurement?'
       ) as data_quality_insights,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           comprehensive_analysis,
           'What specific improvements would enhance guest experience tracking?'
       ) as experience_improvement_suggestions
   FROM multimodal_analysis
   $$;
   ```

2. **Social Media and Operational Data Integration**
   ```sql
   -- Analyze social media mentions with park performance
   CREATE OR REPLACE FUNCTION analyze_social_media_operational_correlation()
   RETURNS TABLE (
       analysis_date DATE,
       social_sentiment_summary STRING,
       operational_performance_correlation STRING,
       data_quality_impact_assessment STRING,
       actionable_insights STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH daily_social_operational AS (
       SELECT 
           CURRENT_DATE() as analysis_date,
           -- Simulated social media data analysis
           SNOWFLAKE.CORTEX.COMPLETE(
               'anthropic.claude-3-5-sonnet',
               CONCAT(
                   'Analyze correlation between social media sentiment and operational performance: ',
                   'Today Social Mentions: "Great ride experience at UDX!", "Long wait times disappointing", "Safety protocols excellent"',
                   ' Operational Data - Avg Wait Time: ', 
                   (SELECT AVG(wait_time_minutes) FROM RIDE_OPERATIONS WHERE operation_date = CURRENT_DATE()),
                   ' Guest Satisfaction: ',
                   (SELECT AVG(guest_satisfaction_score) FROM RIDE_OPERATIONS WHERE operation_date = CURRENT_DATE()),
                   ' Data Quality Score: ',
                   (SELECT AVG(metric_value) FROM DATA_QUALITY_RESULTS WHERE check_timestamp::DATE = CURRENT_DATE()),
                   '. Analyze:
                   1. Correlation between social sentiment and operational metrics
                   2. Data quality issues affecting public perception
                   3. Operational performance reflected in social feedback
                   4. Recommendations for improving both data collection and operations'
               )
           ) as correlation_analysis
   )
   SELECT 
       analysis_date,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           correlation_analysis,
           'What is the overall social media sentiment and key themes?'
       ) as social_sentiment_summary,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           correlation_analysis,
           'How does social sentiment correlate with operational performance?'
       ) as operational_performance_correlation,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           correlation_analysis,
           'What data quality issues might be affecting public perception?'
       ) as data_quality_impact_assessment,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           correlation_analysis,
           'What actionable insights can improve both operations and data quality?'
       ) as actionable_insights
   FROM daily_social_operational
   $$;
   ```

#### **Exercise 4: Integrated Multimodal Quality Dashboard (40 minutes)**

Create a comprehensive multimodal data quality monitoring system:

1. **Unified Multimodal Quality Assessment**
   ```sql
   -- Comprehensive multimodal data quality dashboard
   CREATE OR REPLACE VIEW MULTIMODAL_QUALITY_DASHBOARD AS
   WITH traditional_metrics AS (
       SELECT 
           'TRADITIONAL' as data_type,
           'Structured Data' as source_description,
           AVG(metric_value) as quality_score,
           COUNT(*) as data_points,
           'Standard SQL analysis' as analysis_method
       FROM DATA_QUALITY_RESULTS
       WHERE check_timestamp >= DATEADD('day', -1, CURRENT_DATE())
   ),
   visual_analysis AS (
       SELECT 
           'VISUAL' as data_type,
           'Images and Visual Data' as source_description,
           85.0 as quality_score, -- Simulated from image analysis
           (SELECT COUNT(*) FROM RIDE_INSPECTION_IMAGES 
            WHERE inspection_date >= DATEADD('day', -1, CURRENT_DATE())) as data_points,
           'Multimodal AI vision analysis' as analysis_method
   ),
   document_analysis AS (
       SELECT 
           'DOCUMENT' as data_type,
           'Reports and Documents' as source_description,
           78.5 as quality_score, -- Simulated from document analysis
           (SELECT COUNT(*) FROM INCIDENT_REPORTS 
            WHERE incident_date >= DATEADD('day', -1, CURRENT_DATE())) as data_points,
           'Document processing and NLP' as analysis_method
   ),
   text_sentiment AS (
       SELECT 
           'TEXT' as data_type,
           'Guest Feedback and Text' as source_description,
           (SELECT AVG(rating) * 20 FROM GUEST_FEEDBACK_TEXT 
            WHERE feedback_timestamp >= DATEADD('day', -1, CURRENT_DATE())) as quality_score,
           (SELECT COUNT(*) FROM GUEST_FEEDBACK_TEXT 
            WHERE feedback_timestamp >= DATEADD('day', -1, CURRENT_DATE())) as data_points,
           'Sentiment analysis and text processing' as analysis_method
   )
   SELECT * FROM traditional_metrics
   UNION ALL SELECT * FROM visual_analysis
   UNION ALL SELECT * FROM document_analysis
   UNION ALL SELECT * FROM text_sentiment;
   ```

2. **Multimodal Anomaly Detection System**
   ```sql
   -- Advanced multimodal anomaly detection
   CREATE OR REPLACE FUNCTION detect_multimodal_anomalies()
   RETURNS TABLE (
       anomaly_id STRING,
       data_sources_involved ARRAY,
       anomaly_description STRING,
       severity_level STRING,
       cross_modal_correlations STRING,
       recommended_investigation_steps STRING,
       confidence_score FLOAT
   )
   LANGUAGE SQL
   AS
   $$
   WITH cross_modal_analysis AS (
       SELECT SNOWFLAKE.CORTEX.COMPLETE(
           'anthropic.claude-3-5-sonnet',
           CONCAT(
               'Perform multimodal anomaly detection across these data sources: ',
               'Structured Data Quality: ', 
               (SELECT AVG(metric_value) FROM DATA_QUALITY_RESULTS 
                WHERE check_timestamp >= DATEADD('hour', -6, CURRENT_TIMESTAMP())),
               ' Visual Inspection Score: 85.0 (from image analysis)',
               ' Document Compliance Score: 78.5 (from report analysis)', 
               ' Guest Sentiment Score: ',
               (SELECT AVG(rating) * 20 FROM GUEST_FEEDBACK_TEXT 
                WHERE feedback_timestamp >= DATEADD('hour', -6, CURRENT_TIMESTAMP())),
               '. Detect anomalies by:
               1. Identifying inconsistencies across data types
               2. Finding unusual patterns in cross-modal correlations
               3. Detecting data quality issues that span multiple modalities
               4. Assessing severity based on business impact
               5. Recommending investigation steps for each anomaly'
           )
       ) as anomaly_analysis
   )
   SELECT 
       UUID_STRING() as anomaly_id,
       ARRAY_CONSTRUCT('STRUCTURED', 'VISUAL', 'DOCUMENT', 'TEXT') as data_sources_involved,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           anomaly_analysis,
           'What anomalies were detected across the different data modalities?'
       ) as anomaly_description,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           anomaly_analysis,
           'What is the severity level of the most critical anomaly found?'
       ) as severity_level,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           anomaly_analysis,
           'What cross-modal correlations suggest data quality issues?'
       ) as cross_modal_correlations,
       SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
           anomaly_analysis,
           'What investigation steps should be taken for the detected anomalies?'
       ) as recommended_investigation_steps,
       0.88 as confidence_score
   FROM cross_modal_analysis
   $$;
   ```

3. **Multimodal Agent Integration**
   ```sql
   -- Enhanced agents with multimodal capabilities
   CREATE OR REPLACE AGENT multimodal_quality_agent
   WITH (
       INSTRUCTIONS = 'You are a multimodal data quality agent for UDX theme parks.
                      Analyze structured data, images, documents, and text together
                      to provide comprehensive quality insights. Look for patterns
                      and anomalies that single-modal analysis might miss.',
       TOOLS = [
           'cortex_multimodal', 'image_analysis', 'document_processing',
           'sentiment_analysis', 'cross_modal_correlation'
       ],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view'],
       MULTIMODAL_CAPABILITIES = TRUE,
       SUPPORTED_FORMATS = ['IMAGE', 'PDF', 'TEXT', 'VIDEO']
   );
   
   -- Execute multimodal analysis
   EXECUTE AGENT multimodal_quality_agent
   WITH CONTEXT = 'Perform comprehensive multimodal data quality analysis across all available data sources';
   ```

### 🎯 **Success Criteria**

By the end of this lab, you should have:

✅ **Implemented** multimodal data quality analysis using images and documents  
✅ **Created** cross-modal validation and correlation systems  
✅ **Built** comprehensive text and sentiment analysis integration  
✅ **Established** unified multimodal quality monitoring  
✅ **Deployed** multimodal anomaly detection capabilities  
✅ **Enhanced** AI agents with multimodal intelligence  

### 📊 **Testing Your Multimodal System**

Validate your multimodal AI implementation:

```sql
-- Test 1: Multimodal ride safety analysis
SELECT * FROM analyze_ride_safety_multimodal('RIDE_001');

-- Test 2: Crowd data quality validation
SELECT * FROM analyze_crowd_data_quality();

-- Test 3: Incident report analysis
SELECT * FROM analyze_incident_data_quality();

-- Test 4: Guest experience multimodal analysis
SELECT * FROM analyze_guest_experience_multimodal();

-- Test 5: Multimodal anomaly detection
SELECT * FROM detect_multimodal_anomalies();

-- Test 6: Comprehensive dashboard view
SELECT * FROM MULTIMODAL_QUALITY_DASHBOARD;
```

### 🚀 **Next Steps**

In **Lab 10: Complete Autonomous Data Quality Assistant**, you'll learn:
- Integration of all previous lab components
- Building the ultimate autonomous data quality system
- Real-world deployment and scaling considerations
- Advanced governance and monitoring

Your multimodal AI capabilities will complete the foundation for the autonomous assistant!

### 📚 **Additional Resources**

- [Multimodal AI Best Practices](link-to-resource)
- [Image Analysis for Data Quality](link-to-resource)
- [Document Processing Techniques](link-to-resource)

---

**Continue to Lab 10 to build your complete autonomous data quality assistant!** 