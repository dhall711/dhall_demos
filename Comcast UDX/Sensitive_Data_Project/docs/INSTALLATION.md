# 🛠️ Installation Guide

This guide provides detailed instructions for installing and configuring the Enhanced Snowflake Sensitive Data Discovery & Masking application.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 500MB available space

### Snowflake Requirements
- **Snowflake Account**: Active Snowflake account with appropriate permissions
- **Role Permissions**: DDL privileges and access to target databases/schemas
- **Warehouse**: Access to a running warehouse for query execution

### Required Snowflake Privileges
```sql
-- Database and schema access
GRANT USAGE ON DATABASE <target_database> TO ROLE <your_role>;
GRANT USAGE ON SCHEMA <target_database>.<target_schema> TO ROLE <your_role>;

-- Table access for analysis
GRANT SELECT ON ALL TABLES IN SCHEMA <target_database>.<target_schema> TO ROLE <your_role>;

-- Masking policy privileges
GRANT CREATE MASKING POLICY ON SCHEMA <target_database>.<target_schema> TO ROLE <your_role>;
GRANT APPLY MASKING POLICY ON ACCOUNT TO ROLE <your_role>;

-- Information schema access
GRANT SELECT ON SCHEMA <target_database>.INFORMATION_SCHEMA TO ROLE <your_role>;
```

## 🚀 Installation Methods

### Method 1: Streamlit-in-Snowflake (Recommended)

#### Step 1: Enable Streamlit in Snowflake
```sql
-- Enable Streamlit in your Snowflake account (if not already enabled)
USE ROLE ACCOUNTADMIN;
GRANT IMPORTED PRIVILEGES ON DATABASE STREAMLIT TO ROLE <your_role>;
```

#### Step 2: Create Streamlit Application
1. Navigate to Snowflake WebUI
2. Go to **Data** → **Streamlit**
3. Click **+ Streamlit App**
4. Configure the application:
   - **Name**: `Sensitive_Data_Discovery`
   - **Warehouse**: Select an appropriate warehouse
   - **App location**: Choose database and schema

#### Step 3: Upload Application Files
1. Upload `Sensitive_data.py` to the Streamlit application
2. Create `requirements.txt` with the necessary dependencies:
```text
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.21.0
snowflake-connector-python>=3.0.0
```

#### Step 4: Configure Connection
In Streamlit-in-Snowflake, the connection is automatically configured. No additional setup required.

### Method 2: Local Development Environment

#### Step 1: Clone Repository
```bash
# Create project directory
mkdir snowflake-sensitive-data-masking
cd snowflake-sensitive-data-masking

# Download or clone the application files
# Copy Sensitive_data.py and requirements.txt to this directory
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 4: Configure Snowflake Connection
Create a `.streamlit/secrets.toml` file in your project directory:

```toml
[connections.snowflake]
account = "your-account-identifier"
user = "your-username"
password = "your-password"
database = "your-default-database"
schema = "your-default-schema"
warehouse = "your-warehouse"
role = "your-role"

# Optional: Additional connection parameters
client_session_keep_alive = true
login_timeout = 60
network_timeout = 60
```

#### Step 5: Test Connection
```bash
# Test the application
streamlit run Sensitive_data.py

# The application should open in your default browser at http://localhost:8501
```

## 🔧 Configuration

### Environment Variables
You can also configure Snowflake connection using environment variables:

```bash
# Set environment variables
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_SCHEMA="your-schema"
export SNOWFLAKE_WAREHOUSE="your-warehouse"
export SNOWFLAKE_ROLE="your-role"
```

### Advanced Configuration
Create a `config.json` file for advanced settings:

```json
{
  "detection_settings": {
    "confidence_threshold": 0.5,
    "sample_size": 100,
    "enable_tag_detection": true,
    "enable_comment_detection": true
  },
  "ui_settings": {
    "show_debug_info": false,
    "auto_expand_high_confidence": true,
    "max_sample_display": 15
  },
  "security_settings": {
    "require_confirmation": true,
    "enable_dry_run": true,
    "log_all_operations": true
  }
}
```

## 🔍 Verification

### Test Database Connection
1. Launch the application
2. Check for the green "✅ Connected to Snowflake!" message
3. Verify that databases and schemas load correctly

### Test Sample Data
Use the provided sample data script to create test tables:

```sql
-- Create test database and schema
CREATE DATABASE IF NOT EXISTS TEST_SENSITIVE_DATA;
CREATE SCHEMA IF NOT EXISTS TEST_SENSITIVE_DATA.DEMO_SCHEMA;
USE DATABASE TEST_SENSITIVE_DATA;
USE SCHEMA DEMO_SCHEMA;

-- Create sample table (see sample data script in project)
-- This will help verify that detection patterns work correctly
```

### Run Compatibility Test
1. Enable "🧪 Show Compatibility Test" in the sidebar
2. Click "🔬 Run Compatibility Test"
3. Verify that all tests pass with high success rate

## 🐛 Troubleshooting

### Common Issues

#### Connection Problems
```
Error: Failed to connect to Snowflake
```
**Solutions:**
- Verify account identifier format: `<account>.<region>` or `<account>.<region>.<cloud>`
- Check username and password
- Ensure role has necessary privileges
- Verify warehouse is running

#### Permission Errors
```
Error: Insufficient privileges to access INFORMATION_SCHEMA
```
**Solutions:**
- Grant `SELECT` privileges on `INFORMATION_SCHEMA`
- Ensure role has `USAGE` on target database and schema
- Check if role has `CREATE MASKING POLICY` privileges

#### Module Import Errors
```
ModuleNotFoundError: No module named 'snowflake'
```
**Solutions:**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check virtual environment activation
- Verify Python version compatibility

#### Performance Issues
```
Application running slowly or timing out
```
**Solutions:**
- Reduce sample size in settings
- Use smaller tables for initial testing
- Ensure warehouse has adequate compute resources
- Check network connectivity

### Debug Mode
Enable debug mode for detailed error information:

1. In the sidebar, check "Show Debug Information"
2. Review detailed error messages in expandable sections
3. Check browser console for JavaScript errors

### Log Files
For local installations, check log files:
- **Streamlit logs**: Check terminal output
- **Application logs**: Enable logging in debug mode
- **Connection logs**: Check Snowflake connector logs

## 📞 Support

### Getting Help
1. **Documentation**: Review all documentation files
2. **Community**: Check GitHub issues and discussions
3. **Snowflake Support**: For Snowflake-specific connectivity issues
4. **Email Support**: Contact technical support team

### Reporting Issues
When reporting issues, please include:
- Operating system and Python version
- Streamlit and dependency versions
- Complete error messages
- Steps to reproduce the issue
- Sample data or table structures (anonymized)

### Performance Optimization
For large datasets:
- Increase warehouse size
- Reduce sample data size in settings
- Process tables in smaller batches
- Consider running during off-peak hours

---

## ✅ Next Steps

After successful installation:

1. **Read the [User Guide](USER_GUIDE.md)** for step-by-step usage instructions
2. **Review [Configuration Guide](CONFIGURATION.md)** for advanced settings
3. **Check [Technical Documentation](TECHNICAL_DOCS.md)** for developer information
4. **Run the compatibility test** to ensure everything works correctly

**🎉 You're ready to start discovering and masking sensitive data in Snowflake!** 