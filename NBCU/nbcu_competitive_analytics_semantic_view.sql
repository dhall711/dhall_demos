-- =============================================================================
-- NBCUniversal Project Nexus - CREATE SEMANTIC VIEW from YAML model
-- Semantic view name: STRATEGY_CLIENT.DEV.NBCU_COMPETITIVE_ANALYTICS
-- Mirrors nbcu_competitive_analytics.yaml using Snowflake CREATE SEMANTIC VIEW
-- Reference: Snowflake docs on semantic views
-- =============================================================================

USE DATABASE STRATEGY_CLIENT;
USE SCHEMA DEV;

CREATE OR REPLACE SEMANTIC VIEW NBCU_COMPETITIVE_ANALYTICS

  TABLES (
    competitor_profiles AS STRATEGY_CLIENT.DEV.COMPETITOR_PROFILES
      PRIMARY KEY (COMPETITOR_ID)
      WITH SYNONYMS ('competitors', 'media companies', 'entertainment companies', 'broadcasters', 'streaming services', 'company profiles')
      COMMENT = 'Media company profiles, market segments, and corporate information',

    advertising_revenue AS STRATEGY_CLIENT.DEV.MI_MICROSTRATEGY_FACT
      PRIMARY KEY (REVENUE_ID)
      WITH SYNONYMS ('ad revenue', 'advertising sales', 'revenue data', 'sales performance', 'quarterly results', 'financial metrics')
      COMMENT = 'Quarterly advertising revenue data across platforms and demographics',

    market_intelligence AS STRATEGY_CLIENT.DEV.MARKET_INTELLIGENCE
      PRIMARY KEY (INTELLIGENCE_ID)
      WITH SYNONYMS ('market data', 'competitive intelligence', 'industry analysis', 'content spend', 'subscriber metrics', 'streaming data')
      COMMENT = 'Content investment, subscriber metrics, pricing intelligence',

    performance_metrics AS STRATEGY_CLIENT.DEV.PERFORMANCE_METRICS
      PRIMARY KEY (METRIC_ID)
      WITH SYNONYMS ('performance data', 'audience metrics', 'engagement analytics', 'brand metrics', 'social media data', 'viewership stats')
      COMMENT = 'Viewership, engagement, retention, sentiment, social activity'
  )

  RELATIONSHIPS (
    competitor_revenue AS advertising_revenue (COMPETITOR_ID) REFERENCES competitor_profiles,
    competitor_intelligence AS market_intelligence (COMPETITOR_ID) REFERENCES competitor_profiles,
    competitor_performance AS performance_metrics (COMPETITOR_ID) REFERENCES competitor_profiles
  )

  FACTS (
    -- Advertising revenue facts (platform-level grain)
    advertising_revenue.ad_revenue_millions AS AD_REVENUE_MILLIONS,
    advertising_revenue.qoq_growth_percent AS QOQ_GROWTH_PERCENT,
    advertising_revenue.yoy_growth_percent AS YOY_GROWTH_PERCENT,
    advertising_revenue.market_share_percent AS MARKET_SHARE_PERCENT,
    advertising_revenue.average_cpm AS AVERAGE_CPM,

    -- Market intelligence facts (source/category grain)
    market_intelligence.content_investment_millions AS CONTENT_INVESTMENT_MILLIONS,
    market_intelligence.subscriber_count_millions AS SUBSCRIBER_COUNT_MILLIONS,
    market_intelligence.streaming_hours_billions AS STREAMING_HOURS_BILLIONS,
    market_intelligence.ad_inventory_available AS AD_INVENTORY_AVAILABLE,
    market_intelligence.pricing_premium_index AS PRICING_PREMIUM_INDEX,

    -- Performance metrics facts (metric category/type grain)
    performance_metrics.viewership_millions AS VIEWERSHIP_MILLIONS,
    performance_metrics.engagement_rate_percent AS ENGAGEMENT_RATE_PERCENT,
    performance_metrics.retention_rate_percent AS RETENTION_RATE_PERCENT,
    performance_metrics.brand_sentiment_score AS BRAND_SENTIMENT_SCORE,
    performance_metrics.social_media_mentions AS SOCIAL_MEDIA_MENTIONS
  )

  DIMENSIONS (
    -- Competitor profiles dimensions
    competitor_profiles.competitor_id AS COMPETITOR_ID,
    competitor_profiles.competitor_name AS COMPETITOR_NAME,
    competitor_profiles.company_type AS COMPANY_TYPE,
    competitor_profiles.market_segment AS MARKET_SEGMENT,
    competitor_profiles.parent_company AS PARENT_COMPANY,
    competitor_profiles.headquarters_region AS HEADQUARTERS_REGION,

    -- Advertising revenue dimensions
    advertising_revenue.revenue_id AS REVENUE_ID,
    advertising_revenue.competitor_id AS COMPETITOR_ID,
    advertising_revenue.revenue_quarter AS REVENUE_QUARTER,
    advertising_revenue.revenue_year AS REVENUE_YEAR,
    advertising_revenue.platform_type AS PLATFORM_TYPE,
    advertising_revenue.ad_format AS AD_FORMAT,
    advertising_revenue.audience_demographic AS AUDIENCE_DEMOGRAPHIC,
    advertising_revenue.content_category AS CONTENT_CATEGORY,
    advertising_revenue.revenue_date AS TO_DATE(CONCAT(advertising_revenue.REVENUE_YEAR, '-', CASE advertising_revenue.REVENUE_QUARTER WHEN 'Q1' THEN '03-31' WHEN 'Q2' THEN '06-30' WHEN 'Q3' THEN '09-30' WHEN 'Q4' THEN '12-31' END))
      COMMENT = 'Revenue reporting period end date',

    -- Market intelligence dimensions
    market_intelligence.intelligence_id AS INTELLIGENCE_ID,
    market_intelligence.competitor_id AS COMPETITOR_ID,
    market_intelligence.analysis_quarter AS ANALYSIS_QUARTER,
    market_intelligence.analysis_year AS ANALYSIS_YEAR,
    market_intelligence.data_source AS DATA_SOURCE,
    market_intelligence.content_investment_category AS CONTENT_INVESTMENT_CATEGORY,
    market_intelligence.analysis_date AS TO_DATE(CONCAT(market_intelligence.ANALYSIS_YEAR, '-', CASE market_intelligence.ANALYSIS_QUARTER WHEN 'Q1' THEN '03-31' WHEN 'Q2' THEN '06-30' WHEN 'Q3' THEN '09-30' WHEN 'Q4' THEN '12-31' END))
      COMMENT = 'Analysis period end date',

    -- Performance metrics dimensions
    performance_metrics.metric_id AS METRIC_ID,
    performance_metrics.competitor_id AS COMPETITOR_ID,
    performance_metrics.metric_quarter AS METRIC_QUARTER,
    performance_metrics.metric_year AS METRIC_YEAR,
    performance_metrics.metric_category AS METRIC_CATEGORY,
    performance_metrics.measurement_type AS MEASUREMENT_TYPE,
    performance_metrics.metric_date AS TO_DATE(CONCAT(performance_metrics.METRIC_YEAR, '-', CASE performance_metrics.METRIC_QUARTER WHEN 'Q1' THEN '03-31' WHEN 'Q2' THEN '06-30' WHEN 'Q3' THEN '09-30' WHEN 'Q4' THEN '12-31' END))
      COMMENT = 'Performance metric period end date'
  )

  METRICS (
    -- Core revenue KPIs (competitor-quarter-year)
    advertising_revenue.total_ad_revenue AS SUM(advertising_revenue.AD_REVENUE_MILLIONS)
      COMMENT = 'Total advertising revenue in millions (aggregated across platforms)',
    advertising_revenue.avg_market_share_percent AS AVG(advertising_revenue.MARKET_SHARE_PERCENT)
      COMMENT = 'Average market share percentage across platforms',
    advertising_revenue.qoq_growth AS AVG(advertising_revenue.QOQ_GROWTH_PERCENT)
      COMMENT = 'Quarter-over-quarter growth percentage',
    advertising_revenue.yoy_growth AS AVG(advertising_revenue.YOY_GROWTH_PERCENT)
      COMMENT = 'Year-over-year growth percentage',
    advertising_revenue.avg_cpm AS AVG(advertising_revenue.AVERAGE_CPM)
      COMMENT = 'Average CPM across platforms',
    advertising_revenue.platform_count AS COUNT(DISTINCT advertising_revenue.PLATFORM_TYPE)
      COMMENT = 'Number of active platforms per competitor-quarter-year'
  )

  COMMENT = 'Semantic view for NBCU competitive analytics: advertising revenue, market intelligence, and performance metrics with competitor-level relationships.';

-- Optional: Grant usage to analyst role (adjust role name as needed)
-- GRANT REFERENCES, SELECT ON SEMANTIC VIEW NBCU_COMPETITIVE_ANALYTICS TO ROLE ANALYST_ROLE;


