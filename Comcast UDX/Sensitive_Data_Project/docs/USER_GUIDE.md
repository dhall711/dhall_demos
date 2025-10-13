# 👥 User Guide

This comprehensive guide walks you through using the Enhanced Snowflake Sensitive Data Discovery & Masking application to discover, analyze, and protect sensitive data in your Snowflake environment.

## 🎯 Overview

The application provides a complete workflow for sensitive data protection:
1. **Connect** to your Snowflake environment
2. **Select** databases, schemas, and tables to analyze
3. **Discover** sensitive data automatically using AI-enhanced detection
4. **Review** detected sensitive columns with detailed information
5. **Configure** masking strategies and authorized roles
6. **Generate** SQL scripts for Dynamic Data Masking policies
7. **Apply** policies safely with validation and confirmation

## 🚀 Getting Started

### Step 1: Launch the Application

**For Streamlit-in-Snowflake:**
1. Navigate to your Snowflake WebUI
2. Go to **Data** → **Streamlit**
3. Click on your "Sensitive_Data_Discovery" application

**For Local Development:**
```bash
streamlit run Sensitive_data.py
```

### Step 2: Verify Connection

Upon launch, you should see:
- ✅ **Connected as [username] with role [role_name]**
- The application interface with sidebar settings

If you see connection errors, refer to the [Installation Guide](INSTALLATION.md).

## ⚙️ Configuration & Settings

### Access the Settings Sidebar

The left sidebar contains all configuration options:

#### 🔍 Detection Settings
- **Enable Tag-Based Detection**: Use Snowflake column tags for identification
- **Enable Comment-Based Detection**: Analyze column comments for sensitive indicators
- **Confidence Threshold**: Minimum confidence score (0.0-1.0) for detection
- **Sample Data Size**: Number of records to analyze (10-1000)

#### 🎨 UI Preferences
- **Show Debug Information**: Display detailed error information
- **Auto-expand High Confidence Results**: Automatically expand results with confidence > 0.8
- **Max Sample Values to Display**: Limit sample data shown (5-50)

#### 🛡️ Masking Strategies
- **Configure Masking Strategies**: Customize SQL templates and authorized roles
- **Strategy Types**: Full mask, partial mask, hashing, custom SQL

### Save Your Settings
Click **💾 Save Settings** to persist your configuration across sessions.

## 🗃️ Database and Schema Selection

### Step 1: Select Target Database

1. In the main interface, find **"🗃️ Database and Schema Selection"**
2. Use the **"Select Database"** dropdown to choose your target database
3. The application will load all available databases from your Snowflake account

### Step 2: Choose Schema

1. After selecting a database, the **"Select Schema"** dropdown will populate
2. Choose the schema containing tables you want to analyze
3. The application will load all schemas from the selected database

### Step 3: Select Tables

1. The **"Select Tables"** multi-select will show all tables in your chosen schema
2. Select one or more tables for analysis
3. You can select multiple tables for batch processing

### Step 4: Verify Selection

The interface will show your selections:
- **Database**: Selected database name
- **Schema**: Selected schema name  
- **Tables**: List of selected tables

## 🔍 Data Profiling and Discovery

### Start the Analysis

1. Click **🔍 Profile Selected Tables** to begin analysis
2. The application will show progress indicators for:
   - Table-level progress (1/3 tables processed)
   - Column-level progress (5/23 columns analyzed)

### What Happens During Profiling

The application performs these operations:
1. **Metadata Extraction**: Gets column names, data types, comments, and tags
2. **Sample Data Collection**: Retrieves sample values for pattern analysis
3. **Sensitive Data Detection**: Applies AI-enhanced detection rules
4. **Confidence Scoring**: Assigns confidence levels to detections
5. **Masking Recommendations**: Generates appropriate masking strategies

### View Profiling Results

After completion, you'll see:
- **📊 Data Profiling Results** section
- Summary metrics showing total and sensitive columns
- Sensitivity rate percentage and average confidence score

## 🚨 Sensitive Data Review

### Understanding Detection Results

The application displays detected sensitive columns with:

| Column | Type | Confidence | Detection Source |
|--------|------|------------|------------------|
| EMAIL_ADDRESS | PII_EMAIL | 0.95 | Column name + Sample data |
| SSN | PII_SSN | 0.90 | Pattern match |

### Review Individual Columns

Click on any detected column to see detailed information:

#### 📊 Column Information
- **Table**: Source table name
- **Column Name**: Full column name
- **Data Type**: Snowflake data type
- **Sample Count**: Number of sample values analyzed

#### 🔍 Detection Details
- **Sensitive Type**: Classification (PII_SSN, PII_EMAIL, etc.)
- **Confidence Score**: Detection confidence (0.0-1.0)
- **Detection Source**: How it was detected (TAG, PATTERN_MATCH, COMMENT, etc.)
- **Detection Rationale**: Explanation of why it was flagged

#### 🏷️ Tags & Comments
- **Tags**: Snowflake column tags (if any)
- **Comment**: Column comments from Snowflake

#### 📝 Sample Values
- First 15 sample values from the column
- Masked display for sensitive content
- Total count indicator

#### 🛡️ Recommended Masking Strategy
- **Strategy Description**: What the masking will do
- **Authorized Roles**: Who can see unmasked data
- **Example**: Before/after masking example
- **Masking Expression**: SQL code that will be used

### Select Columns for Masking

1. **Quick Selection**: Use checkboxes in the summary table
2. **Detailed Selection**: Use checkboxes in individual column reviews
3. **Bulk Operations**: Select multiple columns at once

### Save Classifications

For important classifications, click **💾 Save Classification** to store the approved detection in persistent storage for future reference.

## 🔧 Configure Masking Strategies

### Access Strategy Configuration

1. In the sidebar, click **🔧 Configure Masking Strategies**
2. This opens the strategy configuration interface

### Customize Strategies by Type

For each sensitive data type (PII_SSN, PII_EMAIL, etc.):

#### Strategy Type Options
- **full_mask**: Complete replacement with asterisks
- **partial_mask**: Show partial data (e.g., last 4 digits)
- **hash**: Replace with hash values
- **custom**: Your own SQL expression

#### Configure Authorized Roles
- List roles that can see unmasked data
- One role per line
- These roles will be inserted into the SQL template

#### Custom SQL Template
- Write your own masking logic
- Use `{roles}` placeholder for authorized roles
- Use `VAL` to reference the column value
- Example: `CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '****' END`

### Save Strategy Changes

Click **💾 Save Masking Config** to apply your customizations.

## 📜 Generate SQL Scripts

### Create Complete DDL Script

1. After selecting columns for masking, click **📜 Generate Complete DDL Script**
2. The application generates a comprehensive SQL script including:
   - CREATE MASKING POLICY statements
   - ALTER TABLE statements to apply policies
   - GRANT statements for role permissions

### Review Generated Script

The script includes:
- **Header**: Timestamp and configuration summary
- **Policy Creation**: One policy per sensitive data type
- **Column Application**: ALTER TABLE statements for each selected column
- **Permission Grants**: Role-based access grants (commented out)

### Script Analysis

View the **🔍 Script Analysis** tab to see:
- **Total Statements**: Count of SQL statements
- **Statement Breakdown**: CREATE, ALTER, GRANT statement counts
- **Statement Details**: Preview of each statement type

## 🚀 Apply Masking Policies

### Choose Application Method

#### Option 1: Automatic Application (Recommended)

1. **Check Permissions**: Click **🔍 Check Database Permissions**
   - Verify you have required privileges
   - Fix any permission issues before proceeding

2. **Dry Run Validation**: Click **🔍 Dry Run (Validate Only)**
   - Tests all statements without executing
   - Shows validation results and warnings
   - Identifies potential issues

3. **Apply Policies**: 
   - Check the confirmation box
   - Click **🚀 Apply Masking Policies to Database**
   - Confirm in the final dialog
   - Monitor real-time progress

#### Option 2: Manual Execution

1. **Copy Script**: Copy SQL from the text area
2. **Download Script**: Click **📥 Download SQL Script**
3. **Execute Externally**: Use Snowflake WebUI, SnowSQL, or other clients

### Monitor Application Progress

During automatic application, you'll see:
- Real-time progress indicators
- Current operation being performed
- Success/failure status for each statement
- Detailed error messages if issues occur

### Review Results

After completion:
- **Success Summary**: Count of successful operations
- **Applied Policies Status**: Persistent status display
- **Error Details**: Information about any failures
- **Policy Breakdown**: Summary by operation type

## 🧪 Testing and Validation

### Built-in Compatibility Test

1. Enable **🧪 Show Compatibility Test** in the sidebar
2. Click **🔬 Run Compatibility Test**
3. Review test results to ensure detection patterns work correctly

### Test Applied Policies

After applying policies:
1. **Change Role**: Switch to different Snowflake roles
2. **Query Data**: Test that masking works as expected
3. **Verify Access**: Confirm authorized roles see unmasked data

### Validate Detection

Use the sample data provided:
- **SSN**: `123-45-6789` should be detected as PII_SSN
- **Email**: `john.doe@example.com` should be detected as PII_EMAIL
- **Phone**: `555-123-4567` should be detected as PII_PHONE
- **Credit Card**: `1234567890123456` should be detected as FINANCIAL_CC

## 🔧 Advanced Features

### Persistent Storage

1. **Initialize Storage**: Click **🔧 Initialize Persistent Storage**
2. **Save Classifications**: Store approved detections for reuse
3. **Custom Rules**: Define and save custom detection patterns
4. **Audit Trail**: Track all masking activities

### Custom Detection Rules

Create custom patterns for your specific data:
1. Access the custom rules interface
2. Define pattern types: REGEX, COLUMN_NAME, TAG, COMMENT
3. Set confidence scores and sensitive types
4. Save rules for persistent use

### Batch Processing

For large environments:
1. Process tables in smaller batches
2. Save progress between sessions
3. Use higher-confidence thresholds to reduce false positives
4. Schedule runs during off-peak hours

## 📊 Understanding Results

### Confidence Scores

- **0.9-1.0**: Very High Confidence (🔴)
  - Strong pattern matches + column name matches
  - Recommended for immediate masking

- **0.7-0.89**: High Confidence (🟡)
  - Good pattern matches or strong column indicators
  - Review before masking

- **0.5-0.69**: Medium Confidence (🟠)
  - Weak patterns or comment-based detection
  - Manual review recommended

- **Below 0.5**: Not displayed (filtered out)

### Detection Sources

- **PATTERN_MATCH**: Column name + sample data patterns match
- **SAMPLE_DATA**: Sample data matches known patterns
- **COLUMN_NAME**: Column name suggests sensitive data
- **TAG**: Snowflake tag indicates sensitivity
- **COMMENT**: Column comment suggests sensitivity
- **CUSTOM_RULE**: Matches user-defined rule

## 🚨 Troubleshooting

### Common Issues

#### No Sensitive Data Detected
- Lower confidence threshold in settings
- Check if sample data contains actual sensitive information
- Verify detection rules are enabled
- Review custom patterns

#### Permission Errors During Application
- Verify role has CREATE MASKING POLICY privilege
- Check APPLY MASKING POLICY privilege
- Ensure warehouse is running
- Validate database/schema access

#### Slow Performance
- Reduce sample data size
- Process fewer tables at once
- Use larger warehouse
- Enable only necessary detection methods

#### False Positives
- Increase confidence threshold
- Review and adjust detection patterns
- Use custom rules to exclude certain patterns
- Add manual review step

## 💡 Best Practices

### Before You Start
1. **Test in Development**: Always test in non-production environment first
2. **Backup Policies**: Export and save your masking configurations
3. **Validate Roles**: Ensure all required Snowflake roles exist
4. **Plan Access**: Design role-based access patterns before implementation

### During Analysis
1. **Start Small**: Begin with a few tables to understand the process
2. **Review Results**: Manually verify high-confidence detections
3. **Adjust Settings**: Fine-tune confidence thresholds based on results
4. **Save Progress**: Use persistent storage to save important classifications

### After Implementation
1. **Test Thoroughly**: Verify masking works with different roles
2. **Monitor Performance**: Check query performance impact
3. **Update Documentation**: Document your masking policies and roles
4. **Regular Reviews**: Periodically review and update masking strategies

---

## 🎉 Congratulations!

You now have a comprehensive understanding of how to use the Enhanced Snowflake Sensitive Data Discovery & Masking application. 

**Next Steps:**
- Start with sample data to practice
- Gradually expand to production tables
- Customize detection rules for your specific needs
- Build a comprehensive data protection strategy

**Need Help?**
- Check the [Technical Documentation](TECHNICAL_DOCS.md) for advanced topics
- Review the [Configuration Guide](CONFIGURATION.md) for detailed settings
- Contact support for specific questions or issues 