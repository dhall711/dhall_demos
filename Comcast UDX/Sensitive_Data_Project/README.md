# 🔒 Sensitive Data Project

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Snowflake](https://img.shields.io/badge/Snowflake-Compatible-blue.svg)](https://snowflake.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)

A comprehensive Streamlit application for discovering, analyzing, and implementing Dynamic Data Masking (DDM) policies in Snowflake environments. This enterprise-grade tool provides automated sensitive data detection, configurable masking strategies, and safe policy deployment with extensive validation and error handling.

## 🌟 Key Features

### 🔍 **Advanced Sensitive Data Detection**
- **Multi-Source Detection**: Column names, sample data patterns, comments, and Snowflake tags
- **AI-Enhanced Patterns**: Sophisticated regex patterns for PII, financial data, and personal information
- **Configurable Confidence Thresholds**: Adjustable sensitivity levels for detection accuracy
- **Custom Detection Rules**: User-defined patterns stored persistently

### 🏢 **Manager Dashboard & Cost Control** ⭐ NEW
- **Real-time Cost Monitoring**: Track warehouse credits, AI token consumption, and storage costs
- **Predictive Analytics**: Forecast future costs based on usage trends
- **Automated Alerts**: Get notified when costs exceed configurable thresholds
- **Cost Controls**: Implement automated measures to prevent runaway costs
- **Optimization Recommendations**: AI-powered suggestions for cost reduction

### 🛡️ **Configurable Masking Strategies**
- **Role-Based Access Control**: Granular permissions based on Snowflake roles
- **Multiple Masking Types**: Full masking, partial masking, hashing, and custom SQL expressions
- **Strategy Templates**: Pre-built strategies for common sensitive data types
- **Real-Time Preview**: See masking results before implementation

### 🚀 **Safe Policy Deployment**
- **Dry Run Validation**: Test policies without making database changes
- **Permission Verification**: Automatic validation of required Snowflake privileges
- **Progressive Confirmations**: Multi-level safety checks before deployment
- **Detailed Execution Tracking**: Real-time progress and comprehensive error reporting

### 📊 **Enhanced User Experience**
- **Interactive Interface**: Modern, intuitive UI with comprehensive feedback
- **Progress Tracking**: Visual indicators for long-running operations
- **Export Capabilities**: Download generated SQL scripts for manual execution
- **Persistent Storage**: Save approved classifications and custom rules

## 📁 Project Structure

This project is organized into logical folders for easy navigation and maintenance:

```
Sensitive_Data_Project/
├── README.md                    # Project overview and documentation
├── requirements.txt             # Python dependencies
│
├── app/                        # 🚀 Main Application Files
│   ├── Sensitive_data.py       # Primary Streamlit application
│   ├── manager_dashboard.py    # ⭐ NEW: Standalone cost monitoring dashboard
│   ├── integrated_dashboard.py # ⭐ NEW: Combined data discovery + cost management
│   └── sensitive_data_backup.py # Application backup
│
├── app/core/                   # 🏗️ Core Application Modules
│   ├── __init__.py
│   ├── database.py            # Optimized Snowflake database operations
│   ├── config.py              # Type-safe configuration management
│   ├── detection.py           # Sensitive data detection algorithms
│   ├── ai_enhancer.py         # Snowflake Cortex AI integration
│   └── cost_monitor.py        # ⭐ NEW: Advanced cost monitoring and control
│
├── app/components/             # 🎨 Reusable UI Components
│   ├── __init__.py
│   └── ui_components.py       # Modular UI components
│
├── docs/                       # 📚 Documentation
│   ├── INSTALLATION.md         # Setup and installation guide
│   ├── USER_GUIDE.md          # End-user documentation
│   ├── CONFIGURATION.md       # Configuration options
│   ├── TECHNICAL_DOCS.md      # Technical implementation details
│   ├── PROJECT_STRUCTURE.md   # Detailed project organization
│   ├── MANAGER_DASHBOARD_GUIDE.md      # ⭐ NEW: Manager dashboard documentation
│   └── COST_CONTROL_IMPLEMENTATION.md # ⭐ NEW: Technical cost control guide
│
├── performance/                # ⚡ Performance Optimization
│   ├── PERFORMANCE_OPTIMIZATION_SUMMARY.md    # Executive summary
│   ├── QUICK_IMPLEMENTATION_GUIDE.md         # Quick start guide
│   ├── ADVANCED_PERFORMANCE_INVESTIGATION.md # Deep-dive analysis
│   ├── PERFORMANCE_OPTIMIZATION_GUIDE.md     # Implementation guide
│   ├── advanced_performance_optimizations.py # Advanced implementations
│   └── performance_optimizations.py          # Core optimizations
│
├── enhancements/              # 🔧 Feature Enhancements
│   ├── PCI_COMPLIANCE_ENHANCEMENT.md    # PCI DSS compliance guide
│   ├── AI_FEATURES_SUMMARY.md           # AI capabilities overview
│   ├── AI_ENHANCED_FEATURES_GUIDE.md    # AI feature documentation
│   ├── CORTEX_AI_INTEGRATION_GUIDE.md   # Snowflake Cortex AI integration
│   └── cortex_ai_examples.py            # AI implementation examples
│
└── data/                      # 📊 Sample Data & Scripts
    └── sample_data.sql        # Sample data for testing
```

### Folder Descriptions:

- **`app/`**: Contains the main Streamlit application and backup files
- **`app/core/`**: Core application modules with optimized architecture ⭐ NEW
- **`app/components/`**: Reusable UI components ⭐ NEW  
- **`docs/`**: Comprehensive documentation for users, administrators, and developers
- **`performance/`**: Performance optimization guides and implementations for enterprise-scale deployments
- **`enhancements/`**: Advanced features including PCI compliance and AI-powered enhancements
- **`data/`**: Sample datasets and SQL scripts for testing and demonstration

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Snowflake Account**: With appropriate privileges for DDL operations
- **Streamlit**: 1.28.0 or higher
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### Snowflake Privileges Required

#### Basic Application Usage
- `USAGE` on target database and schema
- `CREATE MASKING POLICY` privilege
- `APPLY MASKING POLICY` privilege  
- `SELECT` on `INFORMATION_SCHEMA` views
- Access to target tables for sample data analysis

#### Manager Dashboard (Additional Requirements) ⭐ NEW
```sql
-- Grant access to account usage views for cost monitoring
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;

-- Warehouse management privileges for cost controls
GRANT USAGE ON WAREHOUSE <warehouse_name> TO ROLE <your_role>;
GRANT OPERATE ON WAREHOUSE <warehouse_name> TO ROLE <your_role>;

-- Specific cost monitoring privileges
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY TO ROLE <your_role>;
GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE TO ROLE <your_role>;
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or download the repository
git clone <repository-url>
cd Sensitive_Data_Project

# Install dependencies
pip install -r requirements.txt

# Deploy to Snowflake (Streamlit-in-Snowflake)
# Upload app files to your Snowflake environment
```

### 2. Configuration
```python
# Configure Snowflake connection in your Streamlit secrets
# .streamlit/secrets.toml
[connections.snowflake]
account = "your-account"
user = "your-username"
password = "your-password"
database = "your-database"
schema = "your-schema"
warehouse = "your-warehouse"
role = "your-role"
```

### 3. Launch Application

Choose your preferred application mode:

#### Option A: Integrated Application (Recommended) ⭐ NEW
```bash
streamlit run app/integrated_dashboard.py
```
*Combines sensitive data discovery with real-time cost monitoring*

#### Option B: Sensitive Data Discovery Only
```bash
streamlit run app/Sensitive_data.py
```
*Traditional data discovery and masking functionality*

#### Option C: Manager Dashboard Only ⭐ NEW
```bash
streamlit run app/manager_dashboard.py
```
*Standalone cost monitoring and control dashboard*

## 📖 Documentation

### Quick Reference Guides
- [🛠️ Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [👥 User Guide](docs/USER_GUIDE.md) - Step-by-step usage instructions  
- [⚙️ Configuration Guide](docs/CONFIGURATION.md) - Advanced configuration options
- [🔧 Technical Documentation](docs/TECHNICAL_DOCS.md) - Developer and administrator guide
- [📁 Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed project organization

### Manager Dashboard Documentation ⭐ NEW
- [🏢 Manager Dashboard Guide](docs/MANAGER_DASHBOARD_GUIDE.md) - Comprehensive cost monitoring setup
- [🎛️ Cost Control Implementation](docs/COST_CONTROL_IMPLEMENTATION.md) - Technical implementation guide

### Performance & Optimization
- [⚡ Performance Summary](performance/PERFORMANCE_OPTIMIZATION_SUMMARY.md) - Executive performance overview
- [🚀 Quick Implementation](performance/QUICK_IMPLEMENTATION_GUIDE.md) - Fast optimization setup
- [🔬 Advanced Performance](performance/ADVANCED_PERFORMANCE_INVESTIGATION.md) - Deep-dive optimization

### Advanced Features
- [🤖 AI Features Summary](enhancements/AI_FEATURES_SUMMARY.md) - AI capabilities overview
- [🔗 Cortex AI Integration](enhancements/CORTEX_AI_INTEGRATION_GUIDE.md) - Snowflake AI integration
- [🏦 PCI Compliance](enhancements/PCI_COMPLIANCE_ENHANCEMENT.md) - Financial data compliance

## 🎯 Use Cases

### **Data Privacy Compliance**
- GDPR, CCPA, and HIPAA compliance
- Automated PII discovery and protection
- Audit trail for data access patterns

### **Cost Management** ⭐ NEW
- Real-time Snowflake warehouse cost monitoring
- AI token usage tracking and optimization
- Automated cost controls and alerting
- Predictive cost forecasting and budgeting

### **Development & Testing**
- Safe data sharing across environments
- Automated masking for non-production systems
- Developer-friendly data access controls

### **Analytics & Business Intelligence**
- Preserve data utility while protecting sensitive information
- Role-based data access for different user groups
- Consistent masking across reporting tools

## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  Detection       │────│   Snowflake     │
│   Interface     │    │  Engine          │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                        │
         │              ┌──────────────────┐              │
         └──────────────│  Configuration   │──────────────┘
                        │  Management      │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │  Cost Monitor    │  ⭐ NEW
                        │  & Controls      │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │  Persistent      │
                        │  Storage         │
                        └──────────────────┘
```

## 🛡️ Security Features

- **Secure Connections**: All communication encrypted via Snowflake's security model
- **Audit Logging**: Comprehensive tracking of all detection and masking activities  
- **Permission Validation**: Pre-execution verification of required privileges
- **Safe Deployment**: Multiple confirmation steps and dry-run capabilities
- **Error Handling**: Graceful failure handling with detailed error reporting
- **Cost Controls**: Automated monitoring to prevent unauthorized resource usage ⭐ NEW

## 📊 Supported Data Types

### **Personal Identifiable Information (PII)**
- Social Security Numbers (SSN)
- Email addresses
- Phone numbers
- Personal names (first, last, full)
- Postal addresses
- Date of birth

### **Financial Data**
- Credit card numbers
- Account numbers
- Routing numbers
- Financial identifiers

### **Healthcare Data**
- Medical record numbers
- Patient identifiers
- Health insurance information

### **Custom Patterns**
- User-defined regex patterns
- Comment-based detection
- Tag-based classification

## 🎨 Sample Detection Results

| Column Name | Detection Type | Confidence | Detection Method | Cost Impact ⭐ |
|-------------|----------------|------------|------------------|---------------|
| `SOCIAL_SECURITY_NUMBER` | PII_SSN | 0.95 | Column name + Sample data | Low |
| `EMAIL_ADDRESS` | PII_EMAIL | 0.90 | Pattern match + Comment | Low |
| `CREDIT_CARD_NUMBER` | FINANCIAL_CC | 0.85 | Sample data pattern | Medium |
| `CUSTOMER_PHONE` | PII_PHONE | 0.80 | Column name + Comment | Low |
| `AI_ENHANCED_ANALYSIS` | Various | 0.92 | Cortex AI Classification | Medium ⭐ |

## 💰 Cost Monitoring Features ⭐ NEW

### **Real-time Tracking**
- Warehouse credit consumption monitoring
- AI token usage and cost estimation
- Storage cost tracking
- Query performance metrics

### **Predictive Analytics**
- 24-hour cost forecasting
- Usage trend analysis
- Budget variance alerts
- Optimization recommendations

### **Automated Controls**
- Warehouse auto-suspend configuration
- AI request rate limiting
- Cost threshold alerts
- Emergency cost controls

### **Optimization Insights**
- Warehouse utilization analysis
- AI cost-effectiveness metrics
- Query performance recommendations
- Resource right-sizing suggestions

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Comprehensive guides in the `/docs` folder
- **Issues**: Report bugs via GitHub Issues
- **Discussion**: Join our community discussions
- **Email**: Contact support at [support@example.com]

## 🎖️ Acknowledgments

- Snowflake team for the excellent Streamlit-in-Snowflake platform
- Snowflake Cortex AI team for advanced AI capabilities ⭐ NEW
- Open source community for inspiration and best practices
- Security researchers for guidance on data protection patterns

## 📈 Roadmap

### **Version 2.0** (Planned)
- [ ] Machine learning-based cost optimization models ⭐ NEW
- [ ] Integration with external cost management platforms ⭐ NEW
- [ ] Advanced predictive analytics dashboard
- [ ] Multi-cloud database support

### **Version 1.5** (In Development)
- [ ] Real-time cost alerting and notifications ⭐ NEW
- [ ] API interface for programmatic cost monitoring ⭐ NEW
- [ ] Enhanced reporting features
- [ ] Integration with data catalogs

### **Version 1.3** (Current) ⭐ NEW
- [x] Manager Dashboard with cost monitoring
- [x] Real-time warehouse usage tracking
- [x] AI token consumption monitoring
- [x] Automated cost controls and alerting
- [x] Predictive cost forecasting
- [x] Optimization recommendations engine

---

**Made with ❤️ for data privacy, security, and cost optimization** ⭐ NEW