-- ============================================================
-- FIVETRAN RETAIL DEMO - Database & Synthetic Data Setup
-- ============================================================
-- This script creates the database, schemas, and synthetic
-- e-commerce data simulating Fivetran-landed tables
-- ============================================================

USE ROLE SYSADMIN;

CREATE OR REPLACE DATABASE FIVETRAN_RETAIL_DEMO
  COMMENT = 'Fivetran SE Demo - Retail E-Commerce Analytics Pipeline';

CREATE SCHEMA FIVETRAN_RETAIL_DEMO.BRONZE
  COMMENT = 'Raw data landing zone - simulates Fivetran ELT output';
CREATE SCHEMA FIVETRAN_RETAIL_DEMO.SILVER
  COMMENT = 'Cleaned and enriched data - manual transforms';
CREATE SCHEMA FIVETRAN_RETAIL_DEMO.SILVER_DBT
  COMMENT = 'Cleaned and enriched data - dbt managed';
CREATE SCHEMA FIVETRAN_RETAIL_DEMO.GOLD
  COMMENT = 'Aggregated analytics - Dynamic Tables';
CREATE SCHEMA FIVETRAN_RETAIL_DEMO.ANALYTICS
  COMMENT = 'Semantic models, search services, and agents';

-- ============================================================
-- BRONZE LAYER: Simulated Fivetran-landed tables
-- All tables include _FIVETRAN_SYNCED and _FIVETRAN_DELETED
-- Some intentional duplicates to demonstrate dbt dedup
-- ============================================================

-- Counts after setup:
-- RAW_CUSTOMERS: ~1,036 rows (1,000 unique)
-- RAW_PRODUCTS:  ~64 rows (56 unique)
-- RAW_ORDERS:    ~5,941 rows (5,675 unique)
-- RAW_INVENTORY: ~2,688 rows
-- RAW_REVIEWS:   ~5,454 rows
