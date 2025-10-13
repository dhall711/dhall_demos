# 🔧 Technical Documentation

This document provides detailed technical information about the Enhanced Snowflake Sensitive Data Discovery & Masking application for developers, system administrators, and technical stakeholders.

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Settings  │  │ Detection   │  │  Masking    │  │   UI    │ │
│  │ Management  │  │   Engine    │  │  Strategy   │  │ Components│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                   Business Logic Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Connection  │  │    Data     │  │    SQL      │  │  Error  │ │
│  │  Manager    │  │  Profiler   │  │ Generator   │  │ Handler │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                     Data Access Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                     Snowflake Database                         │
└─────────────────────────────────────────────────────────────────┘
```

### Core Modules

#### 1. Connection Management
- **Purpose**: Handle Snowflake connections and session management
- **Key Functions**: `get_snowflake_connection()`, `safe_execute_query()`
- **Error Handling**: Comprehensive connection error detection and recovery

#### 2. Detection Engine
- **Purpose**: Identify sensitive data using multiple detection methods
- **Key Functions**: `detect_sensitive_data_enhanced()`, `load_custom_detection_rules()`
- **Algorithms**: Pattern matching, confidence scoring, rule prioritization

#### 3. Masking Strategy Manager  
- **Purpose**: Generate and manage Dynamic Data Masking policies
- **Key Functions**: `get_configurable_masking_recommendation()`, `generate_comprehensive_ddl_script_enhanced()`
- **Features**: Role-based access, customizable strategies, SQL generation

#### 4. User Interface Framework
- **Purpose**: Provide interactive web interface
- **Key Functions**: `create_settings_sidebar()`, `create_policy_application_interface()`
- **Features**: Progressive disclosure, real-time feedback, error visualization

## 🔍 Detection Algorithm Details

### Detection Pipeline

```python
def detection_pipeline(column_metadata, sample_data, settings):
    """
    Multi-stage detection pipeline
    
    Stage 1: Custom Rules (Priority 1)
    Stage 2: Tag-Based Detection (Priority 2)  
    Stage 3: Pattern Matching (Priority 3)
    Stage 4: Sample Data Analysis (Priority 4)
    Stage 5: Column Name Analysis (Priority 5)
    Stage 6: Comment Analysis (Priority 6)
    """
    
    for stage in detection_stages:
        result = stage.detect(column_metadata, sample_data)
        if result.confidence >= settings.threshold:
            return result
    
    return no_detection_result()
```

### Confidence Scoring Algorithm

```python
def calculate_confidence(detection_type, evidence):
    """
    Confidence scoring based on evidence strength
    
    Base Confidence by Detection Type:
    - Custom Rules: 0.95
    - Tag-Based: 0.95
    - Pattern Match (Name + Data): 0.90
    - Sample Data Only: 0.80
    - Column Name Only: 0.60
    - Comment Only: 0.50
    
    Adjustments:
    - Multiple evidence sources: +0.05
    - Strong pattern match: +0.10
    - Weak pattern match: -0.20
    """
    
    base_confidence = get_base_confidence(detection_type)
    
    adjustments = 0
    if evidence.has_multiple_sources():
        adjustments += 0.05
    if evidence.has_strong_pattern():
        adjustments += 0.10
    if evidence.has_weak_pattern():
        adjustments -= 0.20
    
    return min(1.0, max(0.0, base_confidence + adjustments))
```

### Pattern Recognition

#### Built-in Patterns

```python
DETECTION_PATTERNS = {
    "PII_SSN": {
        "column_patterns": [
            r".*ssn.*",
            r".*social.*security.*",
            r".*social.*security.*number.*"
        ],
        "data_patterns": [
            r"^\d{3}-\d{2}-\d{4}$",  # 123-45-6789
            r"^\d{9}$"               # 123456789
        ],
        "confidence_base": 0.9
    },
    "PII_EMAIL": {
        "column_patterns": [
            r".*email.*",
            r".*e.?mail.*"
        ],
        "data_patterns": [
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
        ],
        "confidence_base": 0.9
    }
    # ... additional patterns
}
```

#### Custom Rule Engine

```python
class CustomRuleEngine:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule):
        """Add custom detection rule"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def evaluate(self, column_data):
        """Evaluate all rules against column data"""
        for rule in self.rules:
            if rule.matches(column_data):
                return DetectionResult(
                    sensitive_type=rule.sensitive_type,
                    confidence=rule.confidence,
                    rationale=f"Matched custom rule: {rule.name}",
                    source="CUSTOM_RULE"
                )
        return None
```

## 🛡️ Security Architecture

### Data Protection Measures

#### 1. Connection Security
```python
def secure_connection():
    """
    Snowflake connection security measures:
    - TLS encryption for all communications
    - Session token management
    - Connection timeout controls
    - Credential masking in logs
    """
    connection_params = {
        'account': get_masked_account(),
        'user': get_user(),
        'password': get_password(),  # Never logged
        'client_session_keep_alive': True,
        'login_timeout': 60,
        'network_timeout': 60
    }
    return create_secure_connection(connection_params)
```

#### 2. SQL Injection Prevention
```python
def safe_sql_execution(query, params):
    """
    Prevent SQL injection through:
    - Parameterized queries
    - Input validation
    - Escape character handling
    - Query pattern whitelist
    """
    validated_query = validate_sql_pattern(query)
    escaped_params = escape_sql_parameters(params)
    return execute_with_parameters(validated_query, escaped_params)
```

#### 3. Audit Logging
```python
class AuditLogger:
    def log_detection(self, user, database, table, columns, results):
        """Log sensitive data detection events"""
        audit_record = {
            'timestamp': datetime.utcnow(),
            'user': user,
            'action': 'DETECTION',
            'target': f"{database}.{table}",
            'columns_analyzed': len(columns),
            'sensitive_found': len(results),
            'confidence_scores': [r.confidence for r in results]
        }
        self.write_audit_log(audit_record)
    
    def log_policy_application(self, user, policies, success):
        """Log masking policy application events"""
        audit_record = {
            'timestamp': datetime.utcnow(),
            'user': user,
            'action': 'POLICY_APPLICATION',
            'policies_applied': len(policies),
            'success': success
        }
        self.write_audit_log(audit_record)
```

### Permission Validation

```python
def validate_permissions(conn, required_privileges):
    """
    Validate user has required Snowflake privileges:
    - USAGE on database and schema
    - SELECT on INFORMATION_SCHEMA
    - CREATE MASKING POLICY
    - APPLY MASKING POLICY
    """
    current_role = get_current_role(conn)
    
    for privilege in required_privileges:
        if not has_privilege(conn, current_role, privilege):
            raise PermissionError(f"Missing privilege: {privilege}")
    
    return True
```

## 🔄 Data Processing Pipeline

### Table Profiling Workflow

```python
async def profile_tables(conn, database, schema, tables, settings):
    """
    Asynchronous table profiling pipeline
    
    1. Metadata Collection
    2. Sample Data Retrieval
    3. Detection Analysis
    4. Confidence Scoring
    5. Masking Recommendations
    """
    
    results = []
    
    # Parallel processing with semaphore
    semaphore = asyncio.Semaphore(settings.max_concurrent_tables)
    
    async def process_table(table):
        async with semaphore:
            return await analyze_table(conn, database, schema, table, settings)
    
    # Execute table processing in parallel
    tasks = [process_table(table) for table in tables]
    table_results = await asyncio.gather(*tasks)
    
    return flatten_results(table_results)
```

### Column Analysis Engine

```python
class ColumnAnalyzer:
    def __init__(self, settings):
        self.settings = settings
        self.cache = ColumnCache()
        
    def analyze_column(self, column_metadata, sample_data):
        """
        Comprehensive column analysis:
        1. Extract metadata (name, type, comment, tags)
        2. Collect sample data with smart sampling
        3. Apply detection algorithms
        4. Calculate confidence scores
        5. Generate masking recommendations
        """
        
        # Check cache first
        cache_key = self.generate_cache_key(column_metadata)
        if self.cache.has(cache_key):
            return self.cache.get(cache_key)
        
        # Perform analysis
        detection_result = self.detect_sensitive_data(
            column_metadata, sample_data
        )
        
        masking_recommendation = None
        if detection_result.is_sensitive:
            masking_recommendation = self.generate_masking_strategy(
                detection_result.sensitive_type
            )
        
        result = ColumnAnalysisResult(
            metadata=column_metadata,
            detection=detection_result,
            masking=masking_recommendation
        )
        
        # Cache result
        self.cache.set(cache_key, result)
        
        return result
```

## 📊 Performance Optimization

### Caching Strategy

```python
class PerformanceOptimizer:
    def __init__(self):
        self.metadata_cache = LRUCache(maxsize=1000)
        self.sample_cache = LRUCache(maxsize=500)
        self.detection_cache = LRUCache(maxsize=2000)
    
    @cached(cache=metadata_cache, key_func=table_key)
    def get_table_metadata(self, database, schema, table):
        """Cache table metadata to avoid repeated queries"""
        return fetch_table_metadata(database, schema, table)
    
    @cached(cache=sample_cache, key_func=column_key)
    def get_sample_data(self, database, schema, table, column, limit):
        """Cache sample data for frequently accessed columns"""
        return fetch_sample_data(database, schema, table, column, limit)
    
    def optimize_batch_size(self, table_count, column_count):
        """Dynamically adjust batch size based on workload"""
        if column_count > 100:
            return max(1, table_count // 10)
        elif column_count > 50:
            return max(2, table_count // 5)
        else:
            return min(5, table_count)
```

### Query Optimization

```python
def optimize_sample_query(database, schema, table, column, sample_size):
    """
    Generate optimized sample data query:
    - Use SAMPLE clause for large tables
    - Limit result set size
    - Filter out null values
    - Use appropriate sampling method
    """
    
    # For large tables, use SAMPLE clause
    if estimated_row_count(database, schema, table) > 1000000:
        sample_clause = f"SAMPLE SYSTEM ({sample_size * 100 / 1000000})"
    else:
        sample_clause = ""
    
    query = f"""
    SELECT DISTINCT "{column}" as sample_value
    FROM {database}.{schema}.{table} {sample_clause}
    WHERE "{column}" IS NOT NULL
    LIMIT {sample_size}
    """
    
    return query
```

## 🔧 Error Handling Framework

### Exception Hierarchy

```python
class DDMException(Exception):
    """Base exception for DDM application"""
    pass

class ConnectionError(DDMException):
    """Snowflake connection related errors"""
    pass

class PermissionError(DDMException):
    """Insufficient privileges for operation"""
    pass

class ValidationError(DDMException):
    """Data validation or configuration errors"""
    pass

class DetectionError(DDMException):
    """Errors during sensitive data detection"""
    pass

class PolicyError(DDMException):
    """Errors during masking policy operations"""
    pass
```

### Error Recovery Mechanisms

```python
class ErrorRecoveryManager:
    def __init__(self):
        self.retry_strategies = {
            ConnectionError: ExponentialBackoffRetry(max_attempts=3),
            TimeoutError: LinearBackoffRetry(max_attempts=2),
            PermissionError: NoRetryStrategy()
        }
    
    def execute_with_recovery(self, operation, *args, **kwargs):
        """Execute operation with automatic error recovery"""
        for attempt in range(self.max_attempts):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                strategy = self.retry_strategies.get(type(e))
                if strategy and strategy.should_retry(attempt):
                    strategy.wait(attempt)
                    continue
                else:
                    raise e
```

## 📋 SQL Generation Engine

### DDL Template System

```python
class DDLGenerator:
    def __init__(self):
        self.templates = {
            'create_policy': """
            CREATE OR REPLACE MASKING POLICY {database}.{schema}.{policy_name} 
            AS (VAL {data_type}) RETURNS {data_type} ->
              {masking_expression};
            """,
            'apply_policy': """
            ALTER TABLE {database}.{schema}.{table_name}
              MODIFY COLUMN {column_name} SET MASKING POLICY {database}.{schema}.{policy_name};
            """,
            'grant_policy': """
            GRANT USAGE ON MASKING POLICY {database}.{schema}.{policy_name} TO ROLE {role_name};
            """
        }
    
    def generate_policy_ddl(self, policy_config):
        """Generate complete DDL for masking policy"""
        statements = []
        
        # Create policy
        statements.append(
            self.templates['create_policy'].format(**policy_config)
        )
        
        # Apply to columns
        for column in policy_config['columns']:
            statements.append(
                self.templates['apply_policy'].format(
                    **policy_config, **column
                )
            )
        
        # Grant permissions
        for role in policy_config['authorized_roles']:
            statements.append(
                self.templates['grant_policy'].format(
                    **policy_config, role_name=role
                )
            )
        
        return statements
```

### SQL Validation Engine

```python
class SQLValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r'DROP\s+DATABASE',
            r'DROP\s+SCHEMA',  
            r'DELETE\s+FROM',
            r'TRUNCATE\s+TABLE'
        ]
        
        self.required_patterns = [
            r'CREATE\s+.*\s+MASKING\s+POLICY',
            r'ALTER\s+TABLE.*MODIFY\s+COLUMN'
        ]
    
    def validate_ddl(self, sql_statement):
        """Validate DDL statement for safety and correctness"""
        statement_upper = sql_statement.upper()
        
        # Check for dangerous operations
        for pattern in self.dangerous_patterns:
            if re.search(pattern, statement_upper):
                raise ValidationError(f"Dangerous operation detected: {pattern}")
        
        # Validate structure
        if not sql_statement.strip().endswith(';'):
            raise ValidationError("Statement must end with semicolon")
        
        # Additional validations...
        return True
```

## 🔍 Testing Framework

### Unit Tests

```python
class TestDetectionEngine(unittest.TestCase):
    def setUp(self):
        self.detection_engine = DetectionEngine()
        self.sample_data = load_test_data()
    
    def test_ssn_detection(self):
        """Test SSN pattern detection"""
        column_data = {
            'name': 'SOCIAL_SECURITY_NUMBER',
            'type': 'VARCHAR(11)',
            'comment': 'Customer SSN',
            'samples': ['123-45-6789', '987-65-4321']
        }
        
        result = self.detection_engine.detect(column_data)
        
        self.assertTrue(result.is_sensitive)
        self.assertEqual(result.sensitive_type, 'PII_SSN')
        self.assertGreater(result.confidence, 0.8)
    
    def test_false_positive_prevention(self):
        """Test that non-sensitive data is not flagged"""
        column_data = {
            'name': 'PRODUCT_CODE',
            'type': 'VARCHAR(20)',
            'comment': 'Product identifier',
            'samples': ['PROD123', 'ITEM456']
        }
        
        result = self.detection_engine.detect(column_data)
        
        self.assertFalse(result.is_sensitive)
```

### Integration Tests

```python
class TestEndToEndWorkflow(unittest.TestCase):
    def test_complete_workflow(self):
        """Test complete detection and masking workflow"""
        # Setup test environment
        test_db = create_test_database()
        test_table = create_test_table_with_sensitive_data()
        
        # Run detection
        app = DDMApplication()
        results = app.analyze_table(test_db, 'TEST_SCHEMA', 'TEST_TABLE')
        
        # Verify detection results
        sensitive_columns = [r for r in results if r.is_sensitive]
        self.assertGreater(len(sensitive_columns), 0)
        
        # Generate and apply policies
        ddl_script = app.generate_ddl(sensitive_columns)
        self.assertIn('CREATE MASKING POLICY', ddl_script)
        
        # Apply policies (in test mode)
        success = app.apply_policies(ddl_script, dry_run=True)
        self.assertTrue(success)
```

## 📈 Monitoring and Metrics

### Performance Metrics

```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'tables_analyzed': 0,
            'columns_analyzed': 0,
            'sensitive_columns_found': 0,
            'policies_created': 0,
            'avg_detection_time': 0,
            'cache_hit_ratio': 0
        }
    
    def record_detection_time(self, table_name, duration):
        """Record time taken for table detection"""
        self.metrics['tables_analyzed'] += 1
        self.update_avg_time('avg_detection_time', duration)
    
    def record_cache_hit(self, hit):
        """Record cache hit/miss for performance monitoring"""
        self.update_ratio('cache_hit_ratio', hit)
    
    def export_metrics(self):
        """Export metrics for monitoring dashboard"""
        return {
            'timestamp': datetime.utcnow(),
            'metrics': self.metrics,
            'performance_score': self.calculate_performance_score()
        }
```

### Health Checks

```python
def health_check():
    """Comprehensive application health check"""
    checks = {
        'snowflake_connection': test_snowflake_connection(),
        'detection_engine': test_detection_engine(),
        'sql_generator': test_sql_generator(),
        'cache_system': test_cache_system(),
        'persistent_storage': test_persistent_storage()
    }
    
    overall_health = all(checks.values())
    
    return {
        'healthy': overall_health,
        'checks': checks,
        'timestamp': datetime.utcnow()
    }
```

## 🔄 Deployment Considerations

### Streamlit-in-Snowflake Deployment

```python
# Environment-specific configurations
DEPLOYMENT_CONFIGS = {
    'development': {
        'debug_mode': True,
        'sample_size': 50,
        'enable_all_features': True
    },
    'staging': {
        'debug_mode': False,
        'sample_size': 100,
        'enable_audit_logging': True
    },
    'production': {
        'debug_mode': False,
        'sample_size': 200,
        'enable_audit_logging': True,
        'require_confirmation': True
    }
}
```

### Resource Requirements

| Environment | CPU | Memory | Storage | Concurrent Users |
|-------------|-----|--------|---------|------------------|
| Development | 1 core | 2GB | 1GB | 1-2 |
| Staging | 2 cores | 4GB | 5GB | 5-10 |
| Production | 4+ cores | 8GB+ | 20GB+ | 20+ |

### Monitoring and Alerting

```python
def setup_monitoring():
    """Configure monitoring and alerting"""
    monitors = [
        ConnectionHealthMonitor(interval=60),
        PerformanceMonitor(interval=300),
        ErrorRateMonitor(threshold=0.05),
        ResourceUsageMonitor(interval=120)
    ]
    
    for monitor in monitors:
        monitor.start()
    
    # Configure alerts
    alert_manager = AlertManager()
    alert_manager.add_alert(
        name='high_error_rate',
        condition='error_rate > 0.1',
        action=send_email_alert
    )
```

---

## 🔧 Development Guidelines

### Code Organization

```
src/
├── core/
│   ├── detection/          # Detection algorithms
│   ├── masking/           # Masking strategy logic
│   ├── sql/               # SQL generation
│   └── security/          # Security components
├── ui/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page implementations
│   └── utils/            # UI utilities
├── data/
│   ├── connectors/       # Database connectors
│   ├── cache/            # Caching implementations
│   └── storage/          # Persistent storage
└── tests/
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    └── fixtures/         # Test data
```

### Contributing Guidelines

1. **Code Style**: Follow PEP 8 guidelines
2. **Documentation**: Document all public functions
3. **Testing**: Maintain >90% test coverage
4. **Security**: All SQL must be parameterized
5. **Performance**: Profile performance-critical sections

### API Documentation

```python
def detect_sensitive_data_enhanced(
    column_name: str,
    data_type: str, 
    column_comment: Optional[str],
    sample_values: List[Any],
    tags: Optional[str] = None,
    custom_rules: Optional[List[Dict]] = None,
    settings: Optional[Dict] = None
) -> Tuple[bool, Optional[str], float, str, str]:
    """
    Enhanced sensitive data detection using multiple detection methods.
    
    Args:
        column_name: Name of the database column
        data_type: Snowflake data type of the column
        column_comment: Optional comment on the column
        sample_values: List of sample values from the column
        tags: Optional Snowflake tags on the column
        custom_rules: Optional custom detection rules
        settings: Optional detection settings override
    
    Returns:
        Tuple containing:
        - is_sensitive: Whether sensitive data was detected
        - sensitive_type: Type of sensitive data (PII_SSN, PII_EMAIL, etc.)
        - confidence: Confidence score (0.0-1.0)
        - rationale: Explanation of detection decision
        - detection_source: Source of detection (TAG, PATTERN_MATCH, etc.)
    
    Raises:
        DetectionError: If detection process fails
        ValidationError: If input parameters are invalid
    """
```

---

**This technical documentation provides the foundation for understanding, maintaining, and extending the Enhanced Snowflake Sensitive Data Discovery & Masking application.** 