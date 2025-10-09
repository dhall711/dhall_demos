# Lab 01: Environment Setup

## 🎯 Objectives
- Set up Snowflake database and schema for UDX operations
- Enable Cortex AI functionality
- Load sample theme park datasets
- Verify data quality monitoring foundation

## 📋 Prerequisites
- Snowflake account with ACCOUNTADMIN or similar privileges
- Cortex AI enabled (contact your Snowflake rep if needed)
- Ability to create databases and warehouses

## 🏗️ What We're Building
A complete data environment representing:
- **6 Theme Parks** across different regions
- **50+ Rides and Attractions** with varying capacities
- **1M+ Guest Records** with realistic behavior patterns
- **Operational Data** including weather, maintenance, staffing
- **Quality Issues** intentionally introduced for detection

## 🚀 Setup Steps

### 1. Run Initial Setup
Execute `setup.sql` to create:
- `UDX_DATA_QUALITY_PROJECT` database
- `DATA_QUALITY` schema
- Virtual warehouse for AI workloads
- Initial data quality monitoring tables

### 2. Load Sample Data
Execute `../sample-data/load_all_data.sql` to populate:
- Guest profiles and preferences
- Ride configurations and capacity
- Ticket sales and attendance
- Weather and operational data
- Intentional data quality issues

### 3. Verify Installation
Run the verification queries in `verify_setup.sql` to confirm:
- All tables are loaded with expected row counts
- Cortex AI functions are accessible
- Sample data quality issues are present

## 🎢 Sample Data Overview

| Dataset | Records | Purpose |
|---------|---------|---------|
| GUESTS | 100,000 | Customer demographics and preferences |
| RIDES | 52 | Attraction details and capacity |
| TICKETS | 500,000 | Daily ticket sales and usage |
| RIDE_OPERATIONS | 1,000,000 | Hourly ride performance metrics |
| WEATHER | 2,000 | Daily weather conditions |
| STAFF_SCHEDULE | 50,000 | Employee scheduling and performance |

## 🔧 Configuration Notes

### Warehouse Sizing
- **SMALL**: Sufficient for most exercises
- **MEDIUM**: Recommended for large dataset analysis
- **LARGE**: For complex AI model training

### Cortex AI Models Available
- **llama3-8b**: Fast responses, good for summaries
- **mixtral-8x7b**: Balanced performance and quality
- **llama3-70b**: Highest quality, slower responses

## ⚠️ Important Reminders
- Some data quality issues are **intentional** - don't fix them yet!
- We'll use these issues in later labs for detection practice
- Keep track of your warehouse usage and suspend when not in use

## ✅ Success Criteria
- [ ] Database and schema created successfully
- [ ] All sample tables loaded with data
- [ ] Cortex AI functions respond to test queries
- [ ] Data quality baseline established

**Next**: Proceed to Lab 02 for data exploration! 