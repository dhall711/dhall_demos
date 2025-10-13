# ⚙️ Configuration Guide

This guide provides detailed information about configuring and customizing the Enhanced Snowflake Sensitive Data Discovery & Masking application for your specific environment and requirements.

## 🎛️ Application Settings Overview

The application uses a hierarchical configuration system:
1. **Default Settings**: Built-in defaults for all configurations
2. **User Settings**: Customizable settings stored in session state
3. **Persistent Storage**: Settings saved to Snowflake tables
4. **Environment Variables**: Override settings via environment variables

## 🔍 Detection Configuration

### Confidence Thresholds

Configure how strict the detection algorithm should be:

```python
# Default confidence settings
detection_settings = {
    "confidence_threshold": 0.5,  # Minimum confidence to show results
    "high_confidence_threshold": 0.8,  # Auto-expand threshold
    "sample_size": 100  # Number of sample records to analyze
}
```

#### Confidence Levels Guide

| Threshold | Description | Use Case |
|-----------|-------------|----------|
| 0.3-0.4 | Very Permissive | Initial discovery, high recall |
| 0.5-0.6 | Balanced | Standard operation |
| 0.7-0.8 | Conservative | High precision, fewer false positives |
| 0.9+ | Very Strict | Only very obvious patterns |

### Detection Methods Configuration

Enable or disable specific detection methods:

```python
detection_rules = {
    "enable_tag_detection": True,      # Use Snowflake column tags
    "enable_comment_detection": True,  # Analyze column comments
    "enable_pattern_detection": True,  # Use regex patterns
    "enable_custom_rules": True        # Apply user-defined rules
}
```

### Sample Data Settings

Control how much data is analyzed:

```python
sampling_config = {
    "sample_size": 100,           # Records per column
    "max_tables_per_batch": 10,   # Tables processed simultaneously
    "timeout_seconds": 300,       # Query timeout
    "cache_sample_data": True     # Cache results for performance
}
```

## 🛡️ Masking Strategy Configuration

### Built-in Strategies

Customize the pre-built masking strategies:

```python
masking_strategies = {
    "PII_SSN": {
        "strategy_type": "partial_mask",
        "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '***-**-' || SUBSTR(VAL, 8, 4) END",
        "authorized_roles": ["ANALYST_ROLE", "HR_ROLE"],
        "description": "Show last 4 digits only",
        "example": "123-45-6789 → ***-**-6789"
    }
}
```

#### Strategy Types

| Type | Description | Example |
|------|-------------|---------|
| `full_mask` | Complete replacement | `John Doe → ****` |
| `partial_mask` | Show partial data | `john@email.com → ****@email.com` |
| `hash` | Replace with hash | `123456 → a1b2c3d4` |
| `custom` | User-defined SQL | Custom expression |

### Role-Based Access Control

Configure which roles can access unmasked data:

```python
role_configuration = {
    "PII_SSN": ["HR_ROLE", "COMPLIANCE_ROLE"],
    "PII_EMAIL": ["MARKETING_ROLE", "ADMIN_ROLE"],
    "FINANCIAL_CC": ["FINANCE_ROLE", "AUDIT_ROLE"],
    "PII_PHONE": ["SALES_ROLE", "SUPPORT_ROLE"]
}
```

### Custom Masking Templates

Create your own masking logic:

```sql
-- Template for email masking with domain preservation
CASE 
    WHEN CURRENT_ROLE() IN ({roles}) THEN VAL
    WHEN VAL IS NOT NULL THEN 
        '****@' || SPLIT_PART(VAL, '@', 2)
    ELSE NULL 
END

-- Template for partial credit card masking
CASE 
    WHEN CURRENT_ROLE() IN ({roles}) THEN VAL
    WHEN LENGTH(VAL) >= 16 THEN 
        '************' || RIGHT(VAL, 4)
    ELSE '****'
END

-- Template for date masking (show year only)
CASE 
    WHEN CURRENT_ROLE() IN ({roles}) THEN VAL
    WHEN VAL IS NOT NULL THEN 
        YEAR(VAL) || '-XX-XX'
    ELSE NULL 
END
```

## 🎨 User Interface Configuration

### Display Settings

Customize the user interface:

```python
ui_preferences = {
    "show_debug_info": False,           # Show detailed error information
    "auto_expand_high_confidence": True, # Auto-expand high confidence results
    "max_sample_display": 15,           # Maximum sample values to show
    "show_progress_details": True,      # Show detailed progress information
    "enable_animations": True,          # Enable UI animations
    "theme": "auto"                     # UI theme (auto, light, dark)
}
```

### Progress and Performance Settings

Control how the application provides feedback:

```python
performance_config = {
    "progress_update_interval": 0.5,    # Seconds between progress updates
    "cache_enabled": True,              # Enable result caching
    "parallel_processing": True,        # Process multiple tables in parallel
    "batch_size": 5,                    # Tables per batch
    "show_timing_info": False           # Show execution timing
}
```

## 💾 Persistent Storage Configuration

### Storage Schema Setup

Configure persistent storage for classifications and rules:

```sql
-- Schema configuration
CREATE SCHEMA IF NOT EXISTS DATA_DISCOVERY_APP 
COMMENT = 'Schema for Sensitive Data Discovery & Masking Application';

-- Classification storage
CREATE TABLE IF NOT EXISTS DATA_DISCOVERY_APP.APPROVED_CLASSIFICATIONS (
    ID STRING DEFAULT UUID_STRING(),
    DATABASE_NAME STRING NOT NULL,
    SCHEMA_NAME STRING NOT NULL,
    TABLE_NAME STRING NOT NULL,
    COLUMN_NAME STRING NOT NULL,
    SENSITIVE_TYPE STRING NOT NULL,
    CONFIDENCE FLOAT NOT NULL,
    APPROVED_BY STRING DEFAULT CURRENT_USER(),
    APPROVED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    MASKING_STRATEGY STRING,
    NOTES STRING,
    PRIMARY KEY (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME, COLUMN_NAME)
);

-- Custom rules storage
CREATE TABLE IF NOT EXISTS DATA_DISCOVERY_APP.CUSTOM_DETECTION_RULES (
    RULE_ID STRING DEFAULT UUID_STRING(),
    RULE_NAME STRING NOT NULL,
    SENSITIVE_TYPE STRING NOT NULL,
    PATTERN_TYPE STRING NOT NULL,
    PATTERN_VALUE STRING NOT NULL,
    CONFIDENCE_SCORE FLOAT DEFAULT 0.8,
    CREATED_BY STRING DEFAULT CURRENT_USER(),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (RULE_ID)
);
```

### Data Retention Settings

Configure how long to keep stored data:

```python
storage_config = {
    "retention_days": 365,              # Keep classifications for 1 year
    "auto_cleanup": True,               # Automatically clean old data
    "backup_enabled": True,             # Create backups before cleanup
    "audit_log_retention": 2555         # Keep audit logs for 7 years
}
```

## 🔧 Custom Detection Rules

### Rule Types

Create custom detection patterns:

#### 1. Regex Pattern Rules
```python
regex_rule = {
    "rule_name": "Custom_SSN_Pattern",
    "sensitive_type": "PII_SSN",
    "pattern_type": "REGEX",
    "pattern_value": r"^\d{3}[\s-]?\d{2}[\s-]?\d{4}$",
    "confidence_score": 0.9
}
```

#### 2. Column Name Rules
```python
column_rule = {
    "rule_name": "Customer_ID_Pattern",
    "sensitive_type": "PII_CUSTOMER_ID",
    "pattern_type": "COLUMN_NAME",
    "pattern_value": r".*customer.*id.*",
    "confidence_score": 0.7
}
```

#### 3. Comment-Based Rules
```python
comment_rule = {
    "rule_name": "PII_Comment_Indicator",
    "sensitive_type": "PII_GENERAL",
    "pattern_type": "COMMENT",
    "pattern_value": r".*personal.*information.*",
    "confidence_score": 0.6
}
```

#### 4. Tag-Based Rules
```python
tag_rule = {
    "rule_name": "Sensitive_Tag_Detection",
    "sensitive_type": "PII_GENERAL",
    "pattern_type": "TAG",
    "pattern_value": "SENSITIVE:TRUE",
    "confidence_score": 0.95
}
```

### Rule Priority System

Rules are applied in priority order:
1. **Custom Rules** (highest priority)
2. **Tag-Based Detection**
3. **Pattern Matching** (column name + sample data)
4. **Sample Data Only**
5. **Column Name Only**
6. **Comment-Based** (lowest priority)

## 🌐 Environment Variables

Override settings using environment variables:

```bash
# Snowflake Connection
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_DATABASE="your-database"
export SNOWFLAKE_SCHEMA="your-schema"
export SNOWFLAKE_WAREHOUSE="your-warehouse"
export SNOWFLAKE_ROLE="your-role"

# Application Settings
export DDM_CONFIDENCE_THRESHOLD="0.7"
export DDM_SAMPLE_SIZE="200"
export DDM_ENABLE_TAG_DETECTION="true"
export DDM_ENABLE_DEBUG="false"
export DDM_MAX_TABLES_PER_BATCH="5"

# Security Settings
export DDM_REQUIRE_CONFIRMATION="true"
export DDM_ENABLE_AUDIT_LOG="true"
export DDM_LOG_LEVEL="INFO"
```

## 📋 Configuration Files

### Main Configuration File

Create `config.json` for comprehensive settings:

```json
{
  "application": {
    "name": "Enhanced Snowflake DDM",
    "version": "1.0.0",
    "debug_mode": false
  },
  "snowflake": {
    "connection_timeout": 60,
    "query_timeout": 300,
    "retry_attempts": 3,
    "connection_pool_size": 5
  },
  "detection": {
    "confidence_threshold": 0.5,
    "sample_size": 100,
    "enable_tag_detection": true,
    "enable_comment_detection": true,
    "enable_custom_rules": true,
    "max_columns_per_table": 1000
  },
  "masking": {
    "default_strategy_type": "partial_mask",
    "require_role_confirmation": true,
    "validate_roles_exist": true,
    "backup_before_apply": true
  },
  "ui": {
    "show_debug_info": false,
    "auto_expand_high_confidence": true,
    "max_sample_display": 15,
    "progress_update_interval": 0.5,
    "enable_keyboard_shortcuts": true
  },
  "performance": {
    "cache_enabled": true,
    "parallel_processing": true,
    "batch_size": 5,
    "memory_limit_mb": 1024
  },
  "security": {
    "require_confirmation_for_ddl": true,
    "enable_audit_logging": true,
    "log_sensitive_operations": true,
    "encrypt_stored_settings": false
  }
}
```

### Secrets Configuration

Create `.streamlit/secrets.toml` for sensitive data:

```toml
[connections.snowflake]
account = "your-account-identifier"
user = "your-username"
password = "your-password"
database = "your-database"
schema = "your-schema"
warehouse = "your-warehouse"
role = "your-role"
authenticator = "snowflake"
client_session_keep_alive = true

[ddm_settings]
encryption_key = "your-encryption-key"
api_keys = ["key1", "key2"]
admin_emails = ["admin1@company.com", "admin2@company.com"]

[logging]
level = "INFO"
file_path = "/tmp/ddm_app.log"
max_file_size_mb = 100
backup_count = 5
```

## 🔒 Security Configuration

### Access Control Settings

Configure application-level security:

```python
security_config = {
    "require_confirmation_for_ddl": True,
    "enable_audit_logging": True,
    "log_sensitive_operations": True,
    "mask_credentials_in_logs": True,
    "session_timeout_minutes": 30,
    "max_failed_attempts": 3
}
```

### Audit Logging Configuration

Track all sensitive operations:

```python
audit_config = {
    "log_detection_results": True,
    "log_policy_applications": True,
    "log_configuration_changes": True,
    "log_data_access": True,
    "retention_days": 2555,  # 7 years
    "export_format": "JSON"
}
```

## 📊 Performance Tuning

### Memory Management

Configure memory usage:

```python
memory_config = {
    "max_sample_cache_size_mb": 512,
    "max_results_cache_size_mb": 256,
    "garbage_collection_interval": 300,
    "cache_compression": True
}
```

### Query Optimization

Optimize database queries:

```python
query_config = {
    "use_query_caching": True,
    "partition_large_tables": True,
    "sample_method": "SYSTEM",  # or "BERNOULLI"
    "parallel_query_execution": True,
    "query_result_cache_ttl": 3600
}
```

## 🔄 Advanced Workflows

### Batch Processing Configuration

Configure for large-scale operations:

```python
batch_config = {
    "max_tables_per_batch": 10,
    "batch_processing_delay": 1.0,
    "retry_failed_batches": True,
    "save_progress_interval": 50,
    "resume_from_checkpoint": True
}
```

### Integration Settings

Configure external integrations:

```python
integration_config = {
    "enable_slack_notifications": False,
    "slack_webhook_url": "https://hooks.slack.com/...",
    "enable_email_alerts": False,
    "smtp_server": "smtp.company.com",
    "email_recipients": ["team@company.com"]
}
```

## 🧪 Testing Configuration

### Test Environment Settings

Configure for testing:

```python
test_config = {
    "use_test_database": True,
    "test_database_name": "TEST_DDM",
    "create_test_data": True,
    "cleanup_after_tests": True,
    "mock_external_services": True
}
```

### Validation Settings

Configure validation behavior:

```python
validation_config = {
    "validate_sql_syntax": True,
    "dry_run_by_default": True,
    "require_manual_review": True,
    "validate_role_permissions": True,
    "check_policy_conflicts": True
}
```

## 📝 Configuration Best Practices

### 1. Environment-Specific Configs

Use different configurations for different environments:

```
configs/
├── development.json
├── staging.json
├── production.json
└── test.json
```

### 2. Security Considerations

- Store sensitive information in secrets management
- Use environment variables for passwords
- Enable audit logging in production
- Regularly rotate credentials

### 3. Performance Optimization

- Start with conservative settings
- Monitor performance metrics
- Adjust batch sizes based on data volume
- Use appropriate warehouse sizes

### 4. Maintenance

- Regularly review and update detection rules
- Clean up old audit logs
- Update role configurations as needed
- Test configuration changes in development first

---

## 🔧 Troubleshooting Configuration Issues

### Common Configuration Problems

#### Invalid JSON Configuration
```
Error: JSONDecodeError: Expecting ',' delimiter
```
**Solution**: Validate JSON syntax using a JSON validator

#### Permission Denied
```
Error: Access denied when trying to create masking policy
```
**Solution**: Verify role has `CREATE MASKING POLICY` privilege

#### Connection Timeout
```
Error: Snowflake connection timeout
```
**Solution**: Increase `connection_timeout` and check network connectivity

#### Memory Issues
```
Error: Application running out of memory
```
**Solution**: Reduce `sample_size` and `batch_size`, increase available memory

### Configuration Validation

Use the built-in validation to check your configuration:

1. Enable "Show Debug Information" in the sidebar
2. Look for configuration validation messages
3. Check the compatibility test results
4. Review error logs for specific issues

---

**Next Steps:**
- Start with default settings and gradually customize
- Test configuration changes in a development environment
- Document your configuration choices for team reference
- Regularly review and update settings based on usage patterns 