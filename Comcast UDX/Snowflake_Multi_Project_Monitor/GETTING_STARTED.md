# 🚀 Quick Start Guide

## 1. Launch the Application

### Option A: Using the Launch Script (Recommended)
```bash
cd snowflake_project_monitor
./launch.sh
```

### Option B: Manual Setup
```bash
cd snowflake_project_monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Snowflake connection
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials

# Launch application
streamlit run main.py
```

## 2. Configure Snowflake Connection

Edit `.streamlit/secrets.toml`:

```toml
[connections.snowflake]
account = "your-account-identifier"
user = "your-username"
password = "your-password"
database = "your-database"
schema = "your-schema"
warehouse = "your-warehouse"
role = "your-role"
```

## 3. Grant Required Privileges

```sql
-- Essential privileges for monitoring
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE TO ROLE <your_role>;
```

## 4. Access the Dashboard

Once launched, open your browser to: **http://localhost:8501**

## 5. Dashboard Navigation

### 📊 Project Overview
- View cost summaries across all projects
- Compare resource utilization
- Monitor active users and error rates

### 🔍 Cross-Project Insights  
- Automated analysis and recommendations
- Cost variance detection
- Performance optimization suggestions

### 📈 Resource Trends
- Historical usage patterns
- Predictive cost modeling
- Peak usage identification

### ⚙️ Configuration
- Add new projects
- Customize identification patterns
- Set alert thresholds

### 📊 Export & Reports
- Generate comprehensive reports
- Export data in JSON/CSV formats
- Historical analysis downloads

## 6. Project Identification

The application automatically identifies project activity using patterns:

**Sensitive Data Project:**
- Warehouses: `%SENSITIVE%`, `%DDM%`, `%DISCOVERY%`, `%PRIVACY%`
- Databases: `%SENSITIVE%`, `%PII%`, `%MASKING%`, `%GDPR%`
- Users: `%DATA_DISCOVERY%`, `%PRIVACY%`, `%GOVERNANCE%`

**Schema Mapper Project:**
- Warehouses: `%MAPPER%`, `%TRANSFORM%`, `%ETL%`, `%MIGRATION%`
- Databases: `%MAPPER%`, `%STAGING%`, `%TRANSFORM%`, `%ETL%`
- Users: `%MAPPER%`, `%ETL%`, `%ENGINEER%`, `%MIGRATION%`

## 7. Troubleshooting

### Connection Issues
- Verify Snowflake credentials in `secrets.toml`
- Check network connectivity to Snowflake
- Ensure account usage privileges are granted

### Missing Data
- Verify account usage views have data (may take time to populate)
- Check if your resources match the identification patterns
- Review time range settings in the dashboard

### Pattern Matching
- Use the Configuration page to verify project patterns
- Test patterns with known warehouse/database names
- Add custom patterns for your specific naming conventions

## 8. Customization

### Add New Project
1. Go to Configuration page
2. Fill out the "Add New Project" form
3. Define identification patterns
4. Set cost center and priority
5. Save and validate detection

### Modify Cost Models
Edit `config/projects.yaml`:
```yaml
cost_models:
  warehouse_credit_cost: 3.00    # Your actual cost per credit
  storage_cost_per_gb: 0.05      # Your storage pricing
  ai_request_cost: 0.01          # Estimated AI cost
```

### Set Custom Thresholds
```yaml
thresholds:
  cost:
    daily_limit_per_project: 100.00
    weekly_limit_per_project: 500.00
  performance:
    max_error_rate: 5.0
    max_avg_execution_time: 30000
```

## 9. Best Practices

- **Monitor Daily**: Check dashboards regularly during initial setup
- **Tune Patterns**: Refine identification patterns based on actual usage
- **Set Realistic Thresholds**: Adjust cost and performance limits gradually
- **Export Reports**: Generate weekly/monthly reports for analysis
- **Review Insights**: Act on optimization recommendations

## 10. Support

For issues or questions:
1. Check the main README.md for detailed documentation
2. Review troubleshooting section above
3. Verify Snowflake privileges and connection settings
4. Test with known project resources first

Happy monitoring! 🎉 