# 🚀 Enhanced Features Documentation

## Workload-Level Cost Consolidation

### Problem Solved
The original challenge was that Snowflake `ACCOUNT_USAGE` views show costs by **FEATURE** rather than **WORKLOAD**. For example, a SiS (Search in Snowflake) application would have:
- UI (Warehouse) Cost
- SQL (Warehouse) Cost  
- LLM (Warehouse AND Token) Usage Cost
- Vector Embedding Cost

### Solution Implemented

#### 🎯 **Query Attribution Integration**
- **Uses `SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION`** to get precise cost attribution per query
- **Consolidates shared warehouse costs** even when multiple queries run simultaneously
- **Ties costs together using warehouse names and query tagging**

#### 🏷️ **Workload Identification Strategy**
```sql
-- Workload classification logic
CASE 
    WHEN query_tag ILIKE ANY ('SIS_DISCOVERY', 'DDM_ANALYSIS', 'PRIVACY_SCAN')
         OR warehouse_name ILIKE ANY ('%SENSITIVE%', '%DDM%', '%DISCOVERY%')
    THEN 'sensitive_data_discovery'
    WHEN query_tag ILIKE ANY ('SCHEMA_MAP', 'ETL_TRANSFORM', 'MIGRATION')
         OR warehouse_name ILIKE ANY ('%MAPPER%', '%TRANSFORM%', '%ETL%')
    THEN 'schema_mapping'
    ELSE 'other'
END as workload_name
```

#### 💰 **Cost Component Consolidation**
For each workload, the system now tracks:

1. **LLM Costs**: Token usage from `CORTEX_LLM_USAGE`
2. **Embedding Costs**: Vector operations from `CORTEX_EMBEDDING_USAGE`
3. **UI Warehouse Costs**: Streamlit/UI queries identified by query patterns
4. **SQL Warehouse Costs**: Backend SQL operations

### 📊 **Cortex-Specific Account Usage Views**

#### Views Integrated:
- `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE`
- `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_EMBEDDING_USAGE`
- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION` (the game-changer!)

#### Sample Query Pattern:
```sql
WITH cortex_llm_usage AS (
    SELECT 
        DATE_TRUNC('day', request_time) as usage_date,
        warehouse_name,
        COALESCE(query_tag, 'untagged') as query_tag,
        model_name,
        COUNT(*) as llm_requests,
        SUM(total_tokens) as llm_tokens,
        SUM(credits_used) as llm_credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE
    WHERE request_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    GROUP BY usage_date, warehouse_name, query_tag, model_name
),
query_attribution AS (
    SELECT 
        warehouse_name,
        query_tag,
        COUNT(*) as query_count,
        SUM(credits_attributed_to_query) as attributed_credits,
        -- Classify query types
        SUM(CASE 
            WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                 OR UPPER(query_text) LIKE '%UI%' 
            THEN credits_attributed_to_query 
            ELSE 0 
        END) as ui_credits,
        SUM(CASE 
            WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                 AND UPPER(query_text) NOT LIKE '%UI%' 
            THEN credits_attributed_to_query 
            ELSE 0 
        END) as sql_credits
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    GROUP BY warehouse_name, query_tag
)
-- Join and consolidate costs by workload
```

## 📈 Enhanced Metrics & KPIs

### ✅ **Rows and GBs per Credit**
- **Efficiency Metrics**: `rows_per_credit = total_rows / total_credits`
- **Data Efficiency**: `gb_per_credit = total_gb / total_credits`
- **Better readability** than raw integer counts

### ✅ **Period Comparison Analysis**
- **Current vs Previous Period**: Automatic % change calculation
- **Cost Trend Detection**: Identifies significant increases/decreases
- **Visual Indicators**: 🔺 for increases, 🔻 for decreases

### ✅ **Enhanced Number Formatting**
```python
def format_large_number(number: float, number_type: str = 'count') -> str:
    if number_type == 'rows':
        if number >= 1e12: return f"{number/1e12:.1f}T"
        elif number >= 1e9: return f"{number/1e9:.1f}B"
        elif number >= 1e6: return f"{number/1e6:.1f}M"
        elif number >= 1e3: return f"{number/1e3:.1f}K"
    # Similar for bytes, currency
```

## 📊 Daily Ingestion Volume Enhancements

### ✅ **Revamped Visualization**
- **Bar & Line Charts**: GBs, Rows & Credits aligned for easy comparison
- **Efficiency Overlay**: Rows per credit trend analysis
- **Combined Views**: Volume and efficiency in synchronized charts

### ✅ **Period Selector Simplification**
- **Standard Periods**: 7, 30, 90, 180 days
- **Current vs Previous**: Automatic comparison with % changes
- **Missing Data Handling**: Error handling for partial periods

### ✅ **Enhanced Warehouse Performance**
- **Horizontal Bars**: Sorted by largest warehouse on top
- **% Change Indicators**: Period-over-period comparison for each warehouse
- **Efficiency Scoring**: Multi-factor analysis (cost, performance, error rates)

## 🎯 Key Implementation Features

### 1. **Query Attribution Game-Changer**
```sql
-- Before: Hard to calculate individual query costs
SELECT credits_used FROM query_history; -- Shared warehouse issue

-- After: Precise attribution even with shared warehouses
SELECT credits_attributed_to_query FROM query_attribution;
```

### 2. **Workload Consolidation Logic**
```python
# Consolidate by workload patterns
workload_patterns = {
    'sensitive_data_discovery': {
        'query_tags': ['SIS_DISCOVERY', 'DDM_ANALYSIS', 'PRIVACY_SCAN'],
        'warehouses': ['%SENSITIVE%', '%DDM%', '%DISCOVERY%'],
        'cortex_functions': ['CLASSIFY_TEXT', 'EXTRACT_SEMANTIC_PATTERN']
    },
    'schema_mapping': {
        'query_tags': ['SCHEMA_MAP', 'ETL_TRANSFORM', 'MIGRATION'],
        'warehouses': ['%MAPPER%', '%TRANSFORM%', '%ETL%'],
        'cortex_functions': ['COMPLETE', 'SEMANTIC_SIMILARITY']
    }
}
```

### 3. **Sample Data Generator**
```python
def generate_sample_data(self) -> Dict[str, CortexUsageMetrics]:
    """Generate sample data for testing when connection fails"""
    # Provides realistic sample data for demonstration
    # Enables testing without live Snowflake connection
```

### 4. **Multi-Component Cost Tracking**
```python
@dataclass
class CortexUsageMetrics:
    # LLM Costs
    llm_requests: int
    llm_tokens_processed: int
    llm_cost_estimate: float
    
    # Vector Embedding Costs
    embedding_requests: int
    embedding_cost_estimate: float
    
    # UI Warehouse Costs
    ui_query_count: int
    ui_credits_used: float
    
    # SQL Warehouse Costs
    sql_query_count: int
    sql_credits_used: float
    
    # Consolidated totals
    total_cost_estimate: float
    cost_change_percent: Optional[float]
```

## 🎨 Advanced Visualizations

### 1. **Efficiency Scatter Plot**
- **X-axis**: Cost per Query
- **Y-axis**: Rows per Credit  
- **Size**: Total Cost
- **Color**: Error Rate
- **Insight**: Identify optimal efficiency vs cost balance

### 2. **Hierarchical Cost Breakdown**
- **Sunburst Chart**: Component → Workload breakdown
- **Stacked Bar Chart**: Cost by component and workload
- **Interactive**: Drill-down capabilities

### 3. **Period Comparison Charts**
- **Grouped Bar Charts**: Current vs Previous side-by-side
- **Annotations**: % change directly on charts
- **Color Coding**: Green for decreases, red for increases

## 🔧 Required Snowflake Privileges

### Enhanced Privilege Set:
```sql
-- Core account usage (existing)
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <role>;

-- Enhanced for Query Attribution
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION TO ROLE <role>;

-- Cortex-specific monitoring
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE TO ROLE <role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.CORTEX_EMBEDDING_USAGE TO ROLE <role>;

-- Optional for complete monitoring
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY TO ROLE <role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE TO ROLE <role>;
```

## 🚀 Dashboard Features

### New Dashboard Sections:
1. **🤖 Cortex AI Workloads**: Workload-level cost consolidation
2. **📈 Daily Ingestion Analysis**: Enhanced volume tracking with efficiency
3. **📊 Enhanced Project Overview**: Efficiency scatter plots and period comparison

### Enhanced Navigation:
- **Auto-refresh**: 30-second intervals
- **Period Selectors**: 1h, 6h, 24h, 48h, 7d options
- **Sample Data Mode**: For testing without live connection
- **Connection Status**: Real-time connection and feature availability

## 💡 Benefits Delivered

### ✅ **Solved Original Challenge**
- **Workload-level visibility** instead of feature-level
- **Accurate cost attribution** using Query Attribution
- **Consolidated Cortex AI costs** (LLM + Embedding + Warehouse)

### ✅ **Enhanced User Experience**
- **Intuitive number formatting** (K, M, B, T)
- **Period comparison analysis** with automatic % changes
- **Efficiency metrics** for better resource optimization
- **Interactive visualizations** with drill-down capabilities

### ✅ **Enterprise-Ready Features**
- **Sample data generation** for testing
- **Error handling** for missing data periods
- **Scalable architecture** for additional workloads
- **Comprehensive documentation** and setup guides

This enhanced monitoring application now provides enterprise-grade visibility into Snowflake workload costs with the precision and consolidation capabilities requested in your original requirements. 