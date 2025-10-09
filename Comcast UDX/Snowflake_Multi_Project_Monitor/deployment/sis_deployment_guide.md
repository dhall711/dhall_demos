# 🏔️ Streamlit in Snowflake (SiS) Deployment Guide

## Overview

This guide walks through deploying the Multi-Project Usage Monitor as a native **Streamlit in Snowflake (SiS)** application. This provides secure, integrated monitoring directly within your Snowflake environment.

## 🎯 Benefits of SiS Deployment

### ✅ **Native Integration**
- **No external infrastructure** - runs entirely within Snowflake
- **Automatic authentication** - uses Snowflake's security model
- **Real-time data access** - direct connection to account usage views
- **Centralized management** - deploy once, access from anywhere

### ✅ **Enhanced Security**
- **Role-based access control** - leverages existing Snowflake permissions
- **No credential management** - uses execution context
- **Audit trail** - all queries logged in Snowflake
- **Network security** - no external connections required

### ✅ **Performance Optimization**
- **Reduced latency** - queries execute within Snowflake
- **Query optimization** - native query compilation
- **Caching benefits** - leverages Snowflake's result cache
- **Scalable compute** - uses Snowflake warehouses

## 📋 Prerequisites

### 1. **Snowflake Account Requirements**
- Snowflake account with **Enterprise Edition** or higher
- **Streamlit in Snowflake** feature enabled
- Access to **Account Usage** views
- Appropriate **warehouse** for the application

### 2. **Required Privileges**
```sql
-- Core account usage access
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <app_role>;

-- Query attribution (essential for cost consolidation)
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION TO ROLE <app_role>;

-- Cortex AI monitoring
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE TO ROLE <app_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.CORTEX_EMBEDDING_USAGE TO ROLE <app_role>;

-- Additional monitoring views
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY TO ROLE <app_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE TO ROLE <app_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_EVENTS_HISTORY TO ROLE <app_role>;

-- Warehouse access for app execution
GRANT USAGE ON WAREHOUSE <app_warehouse> TO ROLE <app_role>;
```

### 3. **Role Setup**
```sql
-- Create dedicated role for the monitoring app
CREATE ROLE IF NOT EXISTS MONITOR_APP_ROLE;

-- Grant necessary privileges (as shown above)
-- ... grant statements ...

-- Grant role to users who should access the app
GRANT ROLE MONITOR_APP_ROLE TO USER <username>;

-- Set as default role (optional)
ALTER USER <username> SET DEFAULT_ROLE = MONITOR_APP_ROLE;
```

## 🚀 Deployment Steps

### Step 1: Prepare Application Files

1. **Create SiS Application Structure**
```
sis_monitor_app/
├── streamlit_app.py          # Main SiS application (required name)
├── environment.yml           # Dependencies (optional)
└── README.md                 # Application documentation
```

2. **Use the SiS-Optimized Application**
- Copy `streamlit_app.py` content from the SiS-optimized version
- This version includes SiS-specific connection handling and error management

### Step 2: Create the Streamlit Application in Snowflake

```sql
-- Create the Streamlit application
CREATE STREAMLIT MONITOR_APP
ROOT_LOCATION = '@<your_stage>/sis_monitor_app'
MAIN_FILE = 'streamlit_app.py'
WAREHOUSE = '<app_warehouse>'
DEFAULT_ROLE = 'MONITOR_APP_ROLE';
```

### Step 3: Upload Application Files

#### Option A: Using Snowflake Web UI
1. Navigate to **Data > Databases > [Your Database] > Schemas > [Your Schema] > Stages**
2. Create a new **Internal Stage** or use existing
3. Upload the application files to the stage
4. Ensure the stage path matches the `ROOT_LOCATION` in the CREATE STREAMLIT command

#### Option B: Using SnowSQL
```bash
# Create stage (if needed)
snowsql -q "CREATE STAGE IF NOT EXISTS app_stage;"

# Upload files
snowsql -q "PUT file://streamlit_app.py @app_stage/sis_monitor_app/ AUTO_COMPRESS=FALSE;"
snowsql -q "PUT file://environment.yml @app_stage/sis_monitor_app/ AUTO_COMPRESS=FALSE;"
snowsql -q "PUT file://README.md @app_stage/sis_monitor_app/ AUTO_COMPRESS=FALSE;"
```

#### Option C: Using Python/Snowpark
```python
from snowflake.snowpark import Session
import snowflake.connector

# Create session
session = Session.builder.configs(connection_params).create()

# Upload files
session.file.put("streamlit_app.py", "@app_stage/sis_monitor_app/", auto_compress=False)
session.file.put("environment.yml", "@app_stage/sis_monitor_app/", auto_compress=False)
```

### Step 4: Configure Environment (Optional)

Create `environment.yml` for additional dependencies:
```yaml
# Optional: Define additional Python packages
name: monitor_app
dependencies:
  - python=3.8
  - pip:
    - plotly>=5.15.0
    - pandas>=1.5.0
```

### Step 5: Launch the Application

```sql
-- Start the Streamlit application
ALTER STREAMLIT MONITOR_APP SET ROOT_LOCATION = '@app_stage/sis_monitor_app';

-- Grant access to users
GRANT USAGE ON STREAMLIT MONITOR_APP TO ROLE PUBLIC;
-- or more restrictive:
GRANT USAGE ON STREAMLIT MONITOR_APP TO ROLE MONITOR_APP_ROLE;
```

## 🔧 Configuration Options

### Application Settings

```sql
-- Configure warehouse for the app
ALTER STREAMLIT MONITOR_APP SET WAREHOUSE = '<warehouse_name>';

-- Set default role
ALTER STREAMLIT MONITOR_APP SET DEFAULT_ROLE = 'MONITOR_APP_ROLE';

-- Configure query tag for monitoring
ALTER STREAMLIT MONITOR_APP SET QUERY_TAG = 'SIS_MONITOR_APP';
```

### Resource Configuration

```sql
-- Optimize warehouse for monitoring workload
CREATE WAREHOUSE IF NOT EXISTS MONITOR_WH 
WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    COMMENT = 'Warehouse for monitoring Streamlit app';
```

## 🎨 Customization for Your Environment

### 1. **Update Workload Patterns**

Edit the workload patterns in `streamlit_app.py`:
```python
self.workload_patterns = {
    'your_project_name': {
        'query_tags': ['YOUR_TAG_1', 'YOUR_TAG_2'],
        'warehouses': ['%YOUR_WH%', '%PATTERN%'],
        'cortex_functions': ['CLASSIFY_TEXT', 'COMPLETE']
    }
}
```

### 2. **Cost Model Configuration**

Adjust cost models to match your pricing:
```python
self.cost_models = {
    'warehouse_credit_cost': 3.0,      # Your actual cost per credit
    'storage_cost_per_gb': 0.05,       # Your storage pricing
    'ai_request_cost': 0.01            # Estimated AI cost
}
```

### 3. **Custom Visualizations**

Add organization-specific charts and metrics by extending the dashboard classes.

## 🔒 Security Best Practices

### 1. **Principle of Least Privilege**
```sql
-- Create specific role with minimal required permissions
CREATE ROLE MONITOR_READ_ONLY;

-- Grant only necessary account usage views
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION TO ROLE MONITOR_READ_ONLY;
-- Add other specific grants as needed

-- Do NOT grant unnecessary privileges like:
-- GRANT ALL ON SNOWFLAKE.ACCOUNT_USAGE TO ROLE MONITOR_READ_ONLY; -- Too broad
```

### 2. **Network Access Control**
```sql
-- Restrict application access if needed
CREATE NETWORK POLICY monitor_app_policy
    ALLOWED_IP_LIST = ('192.168.1.0/24', '10.0.0.0/8')
    COMMENT = 'Restrict monitor app access to corporate network';

-- Apply to role
ALTER ROLE MONITOR_APP_ROLE SET NETWORK_POLICY = monitor_app_policy;
```

### 3. **Resource Governance**
```sql
-- Create resource monitor to control costs
CREATE RESOURCE MONITOR monitor_app_limit
WITH 
    CREDIT_QUOTA = 100
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS 
        ON 75 PERCENT DO NOTIFY
        ON 90 PERCENT DO SUSPEND
        ON 100 PERCENT DO SUSPEND_IMMEDIATE;

-- Apply to warehouse
ALTER WAREHOUSE MONITOR_WH SET RESOURCE_MONITOR = monitor_app_limit;
```

## 📊 Monitoring the Monitor

### Query Tagging
All application queries are automatically tagged with `SiS_MONITOR` for tracking:

```sql
-- Monitor the monitoring app's usage
SELECT 
    DATE_TRUNC('hour', start_time) as hour,
    COUNT(*) as query_count,
    SUM(credits_attributed_to_query) as credits_used,
    AVG(execution_time_ms) as avg_execution_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
WHERE query_tag = 'SiS_MONITOR'
    AND start_time >= CURRENT_DATE - 7
GROUP BY DATE_TRUNC('hour', start_time)
ORDER BY hour DESC;
```

### Performance Optimization
```sql
-- Check app performance
SELECT 
    query_text,
    execution_time_ms,
    credits_attributed_to_query,
    start_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
WHERE query_tag = 'SiS_MONITOR'
    AND start_time >= CURRENT_DATE - 1
ORDER BY execution_time_ms DESC
LIMIT 10;
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **Connection Errors**
```
Error: Unable to establish SiS connection
```
**Solution:**
- Verify the role has `IMPORTED PRIVILEGES` on `SNOWFLAKE` database
- Check warehouse access permissions
- Ensure the role is granted to the user

#### 2. **Missing Data**
```
Warning: No Cortex usage data found
```
**Solution:**
- Verify access to `CORTEX_LLM_USAGE` and `CORTEX_EMBEDDING_USAGE` views
- Check if your account has Cortex AI features enabled
- Ensure sufficient historical data (views may be empty for new accounts)

#### 3. **Query Attribution Issues**
```
Error fetching workload usage
```
**Solution:**
- Verify `QUERY_ATTRIBUTION` view access
- Check that warehouse names match your patterns
- Ensure query tags are being set correctly

### Debug Mode

Enable debug mode by adding this to the application:
```python
# Add to main() function
if st.sidebar.checkbox("Debug Mode"):
    st.sidebar.subheader("Debug Info")
    st.sidebar.write(f"User: {conn_info['user']}")
    st.sidebar.write(f"Role: {conn_info['role']}")
    st.sidebar.write(f"Warehouse: {conn_info['warehouse']}")
    
    # Show sample queries for debugging
    with st.expander("🔍 Sample Queries"):
        st.code(query, language='sql')
```

## 📈 Scaling and Performance

### For Large Environments

1. **Optimize Queries**
   - Add date filters to limit data scanned
   - Use appropriate time windows
   - Consider materialized views for frequently accessed data

2. **Warehouse Sizing**
   - Start with XSMALL for testing
   - Scale to SMALL or MEDIUM for production with heavy usage
   - Enable auto-suspend to control costs

3. **Caching Strategy**
   - Leverage Streamlit's `@st.cache_data` for expensive operations
   - Use Snowflake's result cache for repeated queries
   - Consider scheduled refresh for summary data

### Production Deployment Checklist

- [ ] **Privileges**: All required account usage grants applied
- [ ] **Security**: Network policies and resource monitors configured
- [ ] **Performance**: Appropriate warehouse size selected
- [ ] **Monitoring**: Query tagging enabled for app tracking
- [ ] **Documentation**: Custom workload patterns documented
- [ ] **Testing**: Application tested with multiple roles and datasets
- [ ] **Backup**: Application files backed up in version control

## 🎉 Next Steps

After successful deployment:

1. **Configure Workload Patterns**: Customize for your specific projects
2. **Set Up Alerts**: Create automated alerts for cost thresholds
3. **Train Users**: Provide training on dashboard features and interpretation
4. **Monitor Performance**: Track the app's own resource usage
5. **Iterate**: Gather feedback and enhance based on user needs

## 📞 Support

For issues specific to SiS deployment:

1. **Snowflake Documentation**: [Streamlit in Snowflake docs](https://docs.snowflake.com/en/developer-guide/streamlit/)
2. **Account Usage Views**: [Account Usage reference](https://docs.snowflake.com/en/sql-reference/account-usage/)
3. **Query Attribution**: [Query Attribution documentation](https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution)

Your monitoring application is now ready to provide enterprise-grade workload cost consolidation directly within Snowflake! 🚀 