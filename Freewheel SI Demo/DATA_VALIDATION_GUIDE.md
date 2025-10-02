# FreeWheel Synthetic Data Validation Guide

## Semantic Model Query Compatibility

This guide shows which verified queries from `freewheel_adtech_analytics.yaml` will return meaningful results with the current synthetic dataset.

### ✅ Fully Supported Queries (after date adjustment)

These queries will return meaningful results once you run the date shift UPDATE statements:

#### 1. **viewability_and_ctr_by_channel**
```sql
-- Groups by CHANNEL and AD_FORMAT
-- Current data: 40+ impressions across CTV and Mobile channels
-- Status: ✅ WORKS - Good variety in viewability (TRUE/FALSE) and clicks
```

#### 2. **pricing_pressure_by_channel**
```sql
-- Compares bid prices vs floor prices by channel
-- Current data: 47+ bids with corresponding auctions
-- Status: ✅ WORKS - Shows CTV vs Mobile pricing dynamics
```

---

### ⚠️ Partially Supported Queries (limited results)

These queries will work but may return limited rows or small aggregations:

#### 3. **campaign_performance_last_30_days**
```sql
-- Requires: impressions, clicks, conversions per campaign in last 30 days
-- Current limitation: After date shift, most campaigns will have 5-15 impressions
-- Recommendation: Good for demo, but consider adding more events for production
```

#### 4. **supply_path_win_rate**
```sql
-- Groups by SSP_ID and PUBLISHER_ID
-- Current data: 3 SSPs × 10 Publishers = 30 potential combinations
-- Current limitation: Only ~8-10 combinations have actual auction/impression data
-- Recommendation: Acceptable for demo; shows varied win rates
```

#### 5. **pacing_vs_budget**
```sql
-- Compares month-to-date spend vs campaign budgets
-- Current limitation: After date shift, "current month" will have limited events
-- Recommendation: Works for demo; shows pacing calculation methodology
```

#### 6. **advertiser_roas_summary**
```sql
-- Calculates ROAS = conversion_value / spend by advertiser
-- Current data: 20+ conversions with varied values ($0, $4.99, $15.99, $22k, $25k, $28k)
-- Current limitation: Only 3-4 advertisers will show in results
-- Status: ⚠️ WORKS - Good for demo but limited advertiser coverage
```

---

## Data Density by Month (Pre-Date-Shift)

| Month | Auctions | Impressions | Conversions | Notes |
|-------|----------|-------------|-------------|-------|
| Aug 2024 | 24 | 20 | 10 | ✅ Best coverage |
| Sep 2024 | 4 | 3 | 1 | Sparse |
| Oct 2024 | 4 | 3 | 1 | Sparse |
| Nov 2024 | 4 | 3 | 1 | Sparse |
| Dec 2024 | 4 | 3 | 1 | Sparse |
| Jan-Jul 2025 | 1-4 each | 1-3 each | 1-2 each | Very sparse |

**After Date Shift**: The 12-month dataset compresses into ~4 months, making daily/weekly aggregations denser.

---

## Recommendations for Production Demos

### Option 1: Use Current Data (Quick Setup)
1. Run the date shift UPDATE statements
2. Accept limited event counts per month
3. Best for: Methodology demos, KPI calculations, semantic model testing

### Option 2: Generate More Events (Better Results)
Use Snowflake's `GENERATOR()` function to create more events:

```sql
-- Example: Add 50 daily impressions for last 60 days
INSERT INTO FREEWHEEL_DATA_PLATFORM.EXCHANGE_LOGS.WINS_IMPRESSIONS
SELECT 
  'I-GEN-' || UNIFORM(1, 999999, RANDOM(1)) || '-' || seq AS IMPRESSION_ID,
  NULL AS AUCTION_ID,
  NULL AS BID_ID,
  line_items.LINE_ITEM_ID,
  campaigns.CAMPAIGN_ID,
  advertisers.ADVERTISER_ID,
  publishers.PUBLISHER_ID,
  inventory.INVENTORY_ID,
  inventory.CHANNEL,
  inventory.PLATFORM AS DEVICE_TYPE,
  'Video' AS AD_FORMAT,
  'United States' AS GEO_COUNTRY,
  UNIFORM(8.0, 18.0, RANDOM(2))::DECIMAL(8,4) AS CLEARING_PRICE_CPM,
  DATEADD(minute, 
    UNIFORM(0, 1440, RANDOM(3)), 
    DATEADD(day, -day_offset, CURRENT_DATE())
  ) AS IMPRESSION_TIMESTAMP,
  UNIFORM(0, 1, RANDOM(4)) > 0.15 AS WAS_VIEWABLE,  -- 85% viewability
  UNIFORM(0, 1, RANDOM(5)) > 0.95 AS WAS_CLICKED    -- 5% CTR
FROM TABLE(GENERATOR(ROWCOUNT => 3000)) g  -- 50/day × 60 days
CROSS JOIN (
  SELECT UNIFORM(1, 60, RANDOM(6)) AS day_offset
) dates
CROSS JOIN (
  SELECT * FROM FREEWHEEL_DATA_PLATFORM.AD_SALES.LINE_ITEMS 
  ORDER BY RANDOM(7) LIMIT 1
) line_items
-- ... join to other dimension tables
WHERE campaigns.START_DATE <= CURRENT_DATE()
  AND campaigns.END_DATE >= CURRENT_DATE();
```

---

## KPI Calculation Validation

All KPI formulas from the semantic model are properly represented in the data:

| KPI | Formula | Data Support |
|-----|---------|--------------|
| **Spend** | SUM(clearing_price_cpm / 1000) | ✅ All impressions have clearing_price_cpm |
| **eCPM** | (Spend / Impressions) × 1000 | ✅ Calculated from spend and impression counts |
| **CTR** | Clicks / Impressions | ✅ WAS_CLICKED column populated with ~20% click rate |
| **Viewability** | Viewable Imps / Impressions | ✅ WAS_VIEWABLE column populated with ~85% viewability |
| **Win Rate** | Wins / Auctions | ✅ ~85% win rate (some auctions have no wins) |
| **CVR** | Conversions / Impressions | ✅ ~25-30% of impressions have conversions |
| **CPA** | Spend / Conversions | ✅ Conversions linked to impressions |
| **ROAS** | Conversion Value / Spend | ✅ Conversion_value populated with realistic amounts |

---

## Summary

**Current State**: 
- ✅ Dimensions are comprehensive (10 advertisers, 17 campaigns, 24 line items, etc.)
- ✅ August 2024 has rich event data with good variety
- ⚠️ Sept 2024 - Jul 2025 are sparse (suitable for demo, not load testing)
- ⚠️ Date range mismatch requires UPDATE statements

**After Running Date Shift**:
- ✅ All verified queries will return results
- ✅ Demonstrates all KPI calculations correctly
- ⚠️ Event counts will be modest (good for methodology, limited for scale)

**For Production-Grade Demos**:
- Consider using GENERATOR() to add 1,000-10,000 events
- Focus on last 90 days for semantic model compatibility
- Maintain realistic distributions (85% viewability, 5% CTR, 25% CVR, etc.)

