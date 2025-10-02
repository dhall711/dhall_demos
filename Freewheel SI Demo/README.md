## FreeWheel AdTech Analytics — Snowflake Intelligence Demo

This package provides a Snowflake Cortex Agent semantic model, synthetic dataset, and validation queries to demonstrate interactive AI analytics for a FreeWheel-style TV/video advertising environment.

### What’s included
- `freewheel_adtech_analytics.yaml` — Semantic model for Auctions, Bids, Wins/Impressions, Losses, Conversions, and Campaigns
- `create_freewheel_synthetic_data.sql` — Creates schemas/tables and loads 12 months of realistic synthetic data
- `test_freewheel_semantic_models.sql` — Validates the model with KPI queries and integrity checks

### Business model overview
- **Core logs**: `AUCTIONS` (requests), `BIDS`, `WINS_IMPRESSIONS` (wins and rendered impressions), `LOSSES`, `CONVERSIONS`
- **Dimensions**: `ADVERTISERS`, `CAMPAIGNS`, `LINE_ITEMS`, `CREATIVES`, `PUBLISHERS`, `SUPPLY_SOURCES`, `INVENTORY_UNITS`
- **Key relationships**:
  - `AUCTIONS.auction_id` → `BIDS.auction_id`
  - `BIDS.bid_id` → `WINS_IMPRESSIONS.bid_id`
  - `AUCTIONS.auction_id` → `WINS_IMPRESSIONS.auction_id`
  - `WINS_IMPRESSIONS.impression_id` → `CONVERSIONS.impression_id`
  - `CAMPAIGNS.campaign_id` → `WINS_IMPRESSIONS.campaign_id`

### Metrics
- **Spend (USD)**: SUM(clearing_price_cpm / 1000)
- **eCPM**: Spend / Impressions × 1000
- **CTR**: Clicks / Impressions
- **Viewability**: Viewable Impressions / Impressions
- **Win Rate**: Wins / Auctions
- **CVR**: Conversions / Impressions
- **CPA**: Spend / Conversions
- **ROAS**: Conversion Value / Spend

### Sample chat-style questions (for the agent)
1. “Show spend, impressions, CTR, CVR, CPA, and eCPM by campaign for the last 30 days.”
2. “Which SSP and publisher combinations have the highest win rate and viewability?”
3. “Compare bid prices versus floors by channel for the last quarter.”
4. “Are my active campaigns pacing to budget this month?”
5. “What is YTD ROAS by advertiser?”
6. “Break out CTV vs Mobile performance by ad format.”

### How to run
1. Execute `create_freewheel_synthetic_data.sql` in Snowflake to create the database `FREEWHEEL_DATA_PLATFORM` and load synthetic data.
2. **IMPORTANT - Date Adjustment**: The synthetic data uses dates from Aug 2024 - Jul 2025. Since the semantic model's verified queries use `CURRENT_DATE()` for relative date filtering (last 30 days, this month, last quarter), you have two options:
   - **Option A (Recommended)**: Run the commented UPDATE statements at the end of `create_freewheel_synthetic_data.sql` to shift all timestamps to be recent (last ~4 months)
   - **Option B**: Modify the verified queries to use absolute date ranges like `WHERE impression_timestamp >= '2024-08-01'`
3. Review `freewheel_adtech_analytics.yaml` and register it with your Snowflake Cortex Agent setup.
4. Execute `test_freewheel_semantic_models.sql` to validate KPIs, relationships, and sample queries.

### Data Volume & Coverage
The synthetic dataset includes:
- **10 Advertisers** across diverse verticals
- **17 Campaigns** with varied objectives and flight dates
- **24 Line Items** spanning CTV and Mobile channels
- **10 Publishers** and 12 inventory units
- **50+ Auctions**, **47+ Bids**, **40+ Wins/Impressions**, **4 Losses**, **20+ Conversions**

**Current Limitation**: Most event volume is concentrated in August 2024, with sparser data in subsequent months. For production-grade demos with hundreds or thousands of events per month, consider:
- Using Snowflake's `GENERATOR()` function (example provided at end of SQL script)
- Generating data programmatically (Python/dbt) with more events per day
- Running the date shift UPDATE to compress the 12 months into ~4 months for denser daily event counts

### Notes
- Conversions may arrive with delay relative to impressions (attribution windows reflected in the sample data).
- All identifiers are synthetic and safe for demos.
- The semantic model works best with data from the **last 90 days** due to relative date filters in verified queries.


