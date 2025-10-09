# 🏢 Snowflake Multi-Project Usage Monitor

A standalone application for monitoring usage and consumption across multiple Snowflake projects, specifically designed to track resource utilization for:

- **Sensitive Data Discovery & Masking** operations
- **Schema Mapping & Transformation** workflows  
- **Cross-project resource analytics** and optimization

## 🎯 Overview

This monitoring application provides enterprise-grade visibility into how different projects consume Snowflake resources, enabling cost optimization, performance analysis, and resource planning across your data ecosystem.

### Key Capabilities

- **Multi-Project Tracking**: Monitor multiple projects with custom identification patterns
- **Cost Analysis**: Real-time cost tracking with predictive analytics
- **Performance Monitoring**: Query performance, error rates, and resource utilization
- **Cross-Project Insights**: Comparative analysis and optimization recommendations
- **Resource Trends**: Historical usage patterns and forecasting
- **Automated Reporting**: Exportable reports in multiple formats

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or create the monitoring application directory
mkdir snowflake_project_monitor
cd snowflake_project_monitor

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create your Snowflake connection configuration:

```toml
# .streamlit/secrets.toml
[connections.snowflake]
account = "your-account-identifier"
user = "your-username"
password = "your-password"
database = "your-database"
schema = "your-schema"
warehouse = "your-warehouse"
role = "your-role"
```

### 3. Launch Application

```bash
streamlit run main.py
```

## 📊 Monitored Projects

### Sensitive Data Discovery Project
Tracks operations related to:
- Automated sensitive data discovery across databases
- AI-powered data classification using Snowflake Cortex
- Dynamic data masking policy creation and application
- Compliance reporting and audit trails

**Resource Identification Patterns:**
- Warehouses: `%SENSITIVE%`, `%DDM%`, `%DISCOVERY%`, `%PRIVACY%`
- Databases: `%SENSITIVE%`, `%PII%`, `%DISCOVERY%`, `%MASKING%`
- Users: `%DATA_DISCOVERY%`, `%PRIVACY%`, `%GOVERNANCE%`

### Schema Mapper Project
Tracks operations related to:
- Schema analysis and structure mapping
- Data transformation and ETL operations
- Migration and data pipeline execution
- Validation and testing workflows

**Resource Identification Patterns:**
- Warehouses: `%MAPPER%`, `%TRANSFORM%`, `%ETL%`, `%MIGRATION%`
- Databases: `%MAPPER%`, `%STAGING%`, `%TRANSFORM%`, `%ETL%`
- Users: `%MAPPER%`, `%ETL%`, `%ENGINEER%`, `%MIGRATION%`

## 🔧 Features

### 📊 Project Overview Dashboard

**Real-time Metrics:**
- Total cost across all projects
- Query volume and execution statistics
- Active user counts and error rates
- Resource utilization comparisons

**Visualizations:**
- Cost comparison charts
- Query distribution pie charts
- Performance trend analysis
- Resource utilization heatmaps

### 🔍 Cross-Project Insights

**Automated Analysis:**
- Cost variance detection between projects
- Usage pattern anomalies
- Performance bottleneck identification
- Resource optimization opportunities

**Smart Recommendations:**
- Right-sizing suggestions for underutilized resources
- Cost optimization strategies
- Performance improvement recommendations
- Resource allocation guidance

### 📈 Resource Utilization Trends

**Historical Analysis:**
- Credit consumption trends over time
- Query volume patterns by project
- Peak usage identification
- Seasonal pattern detection

**Forecasting:**
- Predictive cost modeling
- Capacity planning insights
- Budget variance alerts
- Growth trend analysis

### ⚙️ Project Configuration

**Flexible Project Definition:**
- Custom resource identification patterns
- Project metadata and categorization
- Cost center assignment
- Priority level configuration

**Dynamic Configuration:**
- Add new projects without code changes
- Modify identification patterns
- Update cost models and thresholds
- Configure alert parameters

## 📋 Required Snowflake Privileges

The monitoring application requires access to Snowflake account usage views:

```sql
-- Grant access to account usage for monitoring
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;

-- Specific privileges for cost and usage monitoring
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_EVENTS_HISTORY TO ROLE <your_role>;

-- Optional: For advanced monitoring
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY TO ROLE <your_role>;
```

## 🎨 Dashboard Views

### 1. Project Overview
- **Summary Cards**: Key metrics across all projects
- **Cost Comparison**: Bar charts showing relative project costs
- **Query Distribution**: Pie charts of query volume by project
- **Detailed Metrics Table**: Comprehensive project statistics

### 2. Cross-Project Insights
- **Priority-based Alert System**: High/Medium/Low priority insights
- **Comparative Analysis**: Project-to-project resource usage
- **Optimization Recommendations**: Actionable improvement suggestions
- **Trend Analysis**: Pattern identification across projects

### 3. Resource Trends
- **Time-series Charts**: Historical usage patterns
- **Stacked Area Charts**: Combined resource utilization
- **Trend Lines**: Query and credit consumption over time
- **Peak Usage Analysis**: Identification of high-demand periods

### 4. Configuration Management
- **Project Setup**: Define new projects and patterns
- **Pattern Configuration**: Warehouse, database, and user identification
- **Threshold Management**: Set alerts and limits
- **Cost Model Adjustment**: Update pricing and calculation models

### 5. Export & Reporting
- **Multi-format Export**: JSON, CSV, Excel report generation
- **Comprehensive Reports**: Metrics, insights, and recommendations
- **Automated Scheduling**: Configurable report generation
- **Historical Data**: Export trends and historical analysis

## 🔧 Configuration

### Project Definition

Projects are defined through identification patterns that match Snowflake resources:

```yaml
projects:
  my_project:
    name: "My Data Project"
    type: "custom"
    description: "Project description"
    cost_center: "Data Team"
    priority: "high"
    
    patterns:
      warehouses: ["%MY_PROJECT%", "%CUSTOM%"]
      databases: ["%MY_PROJECT%", "%CUSTOM_DB%"]
      users: ["%MY_USER%", "%PROJECT_USER%"]
```

### Cost Models

Configurable cost calculation models:

```yaml
cost_models:
  warehouse_credit_cost: 3.00    # $ per credit
  storage_cost_per_gb: 0.05      # $ per GB per month
  ai_request_cost: 0.01          # $ per AI request
```

### Alert Thresholds

Customizable thresholds for monitoring:

```yaml
thresholds:
  cost:
    daily_limit_per_project: 100.00
    weekly_limit_per_project: 500.00
  
  performance:
    max_error_rate: 5.0
    max_avg_execution_time: 30000
```

## 📊 Metrics Tracked

### Cost Metrics
- **Warehouse Credits**: Credit consumption by project
- **Storage Costs**: Data storage costs allocation
- **AI Request Costs**: Cortex AI usage costs
- **Total Project Costs**: Comprehensive cost calculation

### Performance Metrics
- **Query Volume**: Number of queries executed
- **Execution Time**: Average and peak execution times
- **Error Rates**: Failed query percentages
- **Resource Utilization**: Warehouse and compute usage

### Usage Metrics
- **Active Users**: Unique users per project
- **Data Scanned**: Volume of data processed
- **Cache Hit Rates**: Query result cache effectiveness
- **Concurrent Queries**: Peak simultaneous query loads

## 🔍 Cross-Project Analysis

### Comparative Insights
- **Cost Efficiency**: Cost per query comparisons
- **Resource Utilization**: Efficiency across projects
- **Performance Benchmarks**: Relative performance analysis
- **Usage Patterns**: Peak and off-peak consumption

### Optimization Recommendations
- **Right-sizing**: Warehouse size recommendations
- **Scheduling**: Optimal timing for resource-intensive operations
- **Resource Sharing**: Opportunities for shared resources
- **Cost Reduction**: Specific cost-saving suggestions

## 📈 Reporting & Analytics

### Real-time Dashboards
- **Live Metrics**: Current resource consumption
- **Active Monitoring**: Real-time cost tracking
- **Performance Alerts**: Immediate issue notification
- **Usage Trends**: Current vs historical patterns

### Historical Analysis
- **Trend Identification**: Usage pattern analysis
- **Seasonal Patterns**: Recurring usage cycles
- **Growth Tracking**: Resource consumption growth
- **Capacity Planning**: Future resource requirements

### Export Capabilities
- **Multiple Formats**: JSON, CSV, Excel exports
- **Comprehensive Reports**: All metrics and insights
- **Filtered Data**: Project-specific or time-range exports
- **Scheduled Reports**: Automated report generation

## 🛠️ Customization

### Adding New Projects

1. **Define Identification Patterns**: Create patterns to identify project resources
2. **Set Project Metadata**: Assign cost center, priority, and description
3. **Configure Thresholds**: Set project-specific limits and alerts
4. **Validate Detection**: Test pattern matching accuracy

### Custom Metrics

Extend the monitoring with custom metrics:
- **Business KPIs**: Project-specific success metrics
- **Custom Calculations**: Specialized cost or performance metrics
- **External Data**: Integration with other monitoring systems
- **Alerting Rules**: Custom threshold and alerting logic

### Integration Options

- **API Access**: Programmatic access to metrics and insights
- **Webhook Notifications**: Real-time alerts to external systems
- **Data Export**: Automated data feeds to BI tools
- **Custom Dashboards**: Integration with existing monitoring platforms

## 🚨 Monitoring & Alerts

### Alert Types
- **Cost Overruns**: Budget threshold breaches
- **Performance Issues**: High error rates or slow queries
- **Usage Anomalies**: Unusual resource consumption patterns
- **Resource Constraints**: Capacity or concurrent query limits

### Notification Options
- **Dashboard Alerts**: In-application notifications
- **Export Reports**: Include alerts in exported data
- **Custom Actions**: Configurable responses to alerts
- **Integration Ready**: Webhook and API support for external systems

## 🔒 Security & Compliance

### Data Privacy
- **Metadata Only**: No sensitive data content accessed
- **Query Analysis**: Only query patterns and metadata
- **Audit Trail**: All monitoring activities logged
- **Role-based Access**: Respects Snowflake security model

### Compliance Support
- **Cost Tracking**: Detailed audit trail for cost allocation
- **Usage Monitoring**: Comprehensive resource usage logs
- **Performance Documentation**: Query and resource performance history
- **Governance**: Project-level resource governance and oversight

---

## 📞 Support & Documentation

### Getting Started
1. Install and configure the application
2. Verify Snowflake connection and privileges
3. Review and customize project configurations
4. Explore the dashboard views and insights

### Best Practices
- **Regular Monitoring**: Check dashboards daily during initial setup
- **Threshold Tuning**: Adjust alert thresholds based on actual usage
- **Pattern Refinement**: Improve project identification patterns over time
- **Cost Review**: Weekly cost analysis and optimization reviews

### Troubleshooting
- **Connection Issues**: Verify Snowflake credentials and network access
- **Missing Data**: Check account usage privileges and data retention
- **Pattern Matching**: Validate project identification patterns
- **Performance**: Optimize queries for large-scale monitoring

This standalone monitoring application provides comprehensive visibility into your Snowflake projects, enabling data-driven decisions for cost optimization, performance improvement, and resource planning across your data ecosystem. 