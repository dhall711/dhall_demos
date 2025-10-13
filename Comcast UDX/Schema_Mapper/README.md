# Enhanced Schema Mapper with Vector Embeddings

An intelligent database schema mapping application powered by Snowflake Cortex AI, vector embeddings, and semantic similarity matching.

## 🚀 Overview

The Enhanced Schema Mapper automates the complex process of mapping fields between database tables using advanced AI technologies. It combines vector embeddings, Large Language Models (LLMs), and sample data analysis to provide intelligent mapping recommendations with confidence scores.

## ✨ Key Features

- **🧮 Vector Embeddings**: Semantic similarity matching using Snowflake's Arctic Embed model
- **🧠 AI-Powered Analysis**: Claude 3.5 Sonnet via Snowflake Cortex for intelligent mapping decisions
- **📊 Sample Data Analysis**: Validates mappings using actual data patterns
- **🔄 Interactive Feedback Loop**: Learn from user corrections to improve recommendations
- **⚡ Automated SQL Generation**: Produces executable INSERT statements with proper transformations

## 📁 Project Files

### Core Application
- `schema_mapper_app.py` - Main Streamlit application with AI-powered mapping functionality

### Documentation
- `SCHEMA_MAPPER_DOCUMENTATION.md` - Comprehensive technical documentation
- `USAGE_GUIDE.md` - Step-by-step user guide with best practices

### Test Data
- `CUSTOMER_DATA_GENERATOR.ipynb` - Jupyter notebook to generate sample customer data for testing

## 🛠️ Prerequisites

### Technical Requirements
- Snowflake account with Cortex LLM access enabled
- Streamlit-in-Snowflake environment
- Database with `SOURCE_SYSTEMS` and `TARGET_SCHEMA` schemas
- Appropriate permissions for creating tables and executing queries

### Required Snowflake Features
- Snowflake Cortex (claude-3-5-sonnet model)
- Arctic Embed (snowflake-arctic-embed-l-v2.0)
- Vector functions (VECTOR_COSINE_SIMILARITY)

## 🚀 Quick Start

### 1. Setup Test Data (Optional)
```sql
-- Run the CUSTOMER_DATA_GENERATOR.ipynb notebook to create sample tables
-- This creates SOURCE_SYSTEMS and TARGET_SCHEMA with customer data
```

### 2. Deploy Application
1. Upload `schema_mapper_app.py` to your Snowflake Streamlit environment
2. Ensure your database has the required schemas and tables
3. Launch the application

### 3. Initialize Vector Embeddings
- The application will automatically initialize vector embeddings on first run
- This process scans all tables in SOURCE_SYSTEMS and TARGET_SCHEMA
- Initial setup takes 1-2 minutes depending on schema size

### 4. Start Mapping
1. Select source table from `SOURCE_SYSTEMS` schema
2. Select target table from `TARGET_SCHEMA` schema  
3. Click "Map to Target Table (with Vector Embeddings)"
4. Review AI recommendations and similarity scores
5. Approve or provide feedback to refine mappings
6. Execute generated SQL to transfer data

## 🔧 Configuration

The application uses these default configurations:

```python
DATABASE_NAME = "CUSTOMER_DATA_MAPPING"
INPUT_SCHEMA = "SOURCE_SYSTEMS"      # Source tables
TARGET_SCHEMA = "TARGET_SCHEMA"      # Target tables
EMBEDDING_MODEL = "snowflake-arctic-embed-l-v2.0"
LLM_MODEL = "claude-3-5-sonnet"
```

## 📈 How It Works

### Phase 1: Vector Embedding Initialization
- Scans all table metadata (schemas, tables, columns, comments)
- Creates searchable content combining all metadata
- Generates 1024-dimensional vector embeddings
- Stores embeddings in `COLUMN_EMBEDDINGS` table

### Phase 2: Intelligent Mapping
- For each source column, finds top 5 semantically similar target columns
- Uses cosine similarity with vector embeddings
- Analyzes sample data patterns and formats
- Combines results with LLM analysis for comprehensive recommendations

### Phase 3: SQL Generation & Execution
- Generates complete INSERT INTO...SELECT statements
- Includes necessary data type conversions
- Handles NULL values and default values appropriately
- Provides executable Snowflake SQL with explanatory comments

## 🎯 Use Cases

- **Data Migration**: Map legacy system tables to modern schemas
- **Data Integration**: Connect disparate data sources
- **ETL Development**: Automate mapping for data pipelines  
- **Schema Evolution**: Map between different schema versions

## 📚 Documentation

- **Technical Details**: See `SCHEMA_MAPPER_DOCUMENTATION.md` for architecture and implementation details
- **User Instructions**: See `USAGE_GUIDE.md` for step-by-step usage instructions
- **Best Practices**: Both documentation files include optimization tips and troubleshooting guides

## 🤝 Contributing

This application demonstrates advanced AI-powered data engineering capabilities. Contributions and enhancements are welcome, particularly in areas of:

- Custom similarity threshold tuning
- Advanced data transformation support
- Multi-table join mapping
- Performance optimizations

## 📄 License

This project is provided as an example implementation of AI-powered schema mapping using Snowflake's advanced AI capabilities.

---

*Powered by Snowflake Cortex AI, Arctic Embed, and Claude 3.5 Sonnet* 