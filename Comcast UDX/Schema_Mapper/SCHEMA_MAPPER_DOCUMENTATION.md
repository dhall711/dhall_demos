# Enhanced Schema Mapper with Vector Embeddings

## Overview

The Enhanced Schema Mapper is a sophisticated Streamlit application designed to intelligently map database table schemas using advanced AI technologies. Built specifically for Snowflake environments, it leverages vector embeddings, semantic similarity matching, and Large Language Models (LLMs) to automate the complex process of mapping fields between source and target database tables.

## Key Features

### 🧮 **Vector Embeddings & Semantic Matching**
- Uses Snowflake's Arctic Embed model (`snowflake-arctic-embed-l-v2.0`) to generate vector embeddings for all column metadata
- Performs cosine similarity calculations to find semantically similar columns across schemas
- Goes beyond simple name matching to understand semantic relationships between fields

### 🧠 **AI-Powered Analysis**
- Integrates Snowflake Cortex LLM (Claude 3.5 Sonnet) for intelligent mapping analysis
- Analyzes table comments, column descriptions, data types, and sample data
- Provides confidence scores and reasoning for mapping decisions

### 📊 **Sample Data Analysis**
- Examines actual data patterns to validate mapping decisions
- Identifies data transformation requirements
- Helps detect format differences and data type compatibility issues

### 🔄 **Interactive Feedback Loop**
- Allows users to review and provide feedback on mapping suggestions
- Regenerates analysis based on user input
- Maintains feedback history for iterative improvement

### ⚡ **Automated SQL Generation**
- Generates complete INSERT INTO...SELECT statements
- Includes necessary data type conversions
- Handles NULL values appropriately
- Produces executable Snowflake SQL

## Architecture

### Core Components

#### 1. **VectorEmbeddingManager**
```python
class VectorEmbeddingManager:
    """Handles vector embeddings and cosine similarity for schema metadata semantic matching"""
```

**Responsibilities:**
- Initialize vector embeddings for schema metadata
- Create and manage the `COLUMN_EMBEDDINGS` table
- Find similar columns using cosine similarity
- Generate embeddings for searchable content (schema, table, column names, types, and comments)

**Key Methods:**
- `initialize_embeddings()`: Creates embeddings for all column metadata
- `find_similar_columns()`: Returns top N similar columns with similarity scores
- `find_best_matches_for_all_columns()`: Batch processing for all input columns

#### 2. **DatabaseManager**
```python
class DatabaseManager:
    """Handles all database operations and queries"""
```

**Responsibilities:**
- Manage database connections and queries
- Retrieve table metadata including DDL, comments, and tags
- Fetch sample data for analysis
- Execute generated SQL statements

**Schema Structure:**
- **Input Schema**: `SOURCE_SYSTEMS` - Contains source tables from various systems
- **Target Schema**: `TARGET_SCHEMA` - Contains target tables for data integration
- **Database**: `CUSTOMER_DATA_MAPPING` - Main database for the application

#### 3. **LLMManager**
```python
class LLMManager:
    """Handles all LLM interactions using Snowflake Cortex with vector similarity enhancement"""
```

**Responsibilities:**
- Interface with Snowflake Cortex LLM
- Generate enhanced mapping analysis using vector similarity results
- Create SQL statements from mapping analysis
- Handle user feedback and regenerate improved analyses

## Workflow

### Phase 1: Initialization
1. **Snowflake Session Setup**: Establishes connection to Snowflake environment
2. **Vector Embeddings Initialization**: 
   - Scans all tables in `SOURCE_SYSTEMS` and `TARGET_SCHEMA`
   - Creates searchable content combining schema, table, column names, types, and comments
   - Generates vector embeddings using Arctic Embed model
   - Stores embeddings in `COLUMN_EMBEDDINGS` table

### Phase 2: Table Selection
1. **Source Table Selection**: User selects input table from `SOURCE_SYSTEMS` schema
2. **Target Table Selection**: User selects target table from `TARGET_SCHEMA` schema
3. **Metadata Loading**: Application retrieves comprehensive metadata for both tables:
   - Column names, data types, nullability, defaults
   - Table and column comments
   - Table tags (if any)
   - Sample data (first 5 records)

### Phase 3: Intelligent Mapping Analysis
1. **Vector Similarity Calculation**:
   - For each input column, finds top 5 semantically similar target columns
   - Uses cosine similarity with configurable thresholds
   - Considers column names, data types, and descriptions

2. **LLM Analysis**:
   - Combines vector similarity results with sample data analysis
   - Evaluates data patterns, formats, and ranges
   - Considers table/column comments and semantic meanings
   - Generates comprehensive mapping recommendations with confidence scores

3. **Enhanced Context**:
   - Traditional name-based matching as fallback
   - Data type compatibility analysis
   - Sample data pattern recognition
   - Transformation requirement identification

### Phase 4: User Review & Feedback
1. **Analysis Presentation**: 
   - Shows detailed mapping analysis with reasoning
   - Displays vector similarity results
   - Presents sample data comparisons

2. **User Interaction**:
   - **Approve**: Proceeds to SQL generation
   - **Reject**: Opens feedback form for refinement

3. **Iterative Improvement**:
   - Incorporates user feedback into analysis
   - Regenerates mappings with enhanced context
   - Maintains feedback history for learning

### Phase 5: SQL Generation & Execution
1. **SQL Generation**:
   - Creates complete INSERT INTO...SELECT statement
   - Includes necessary data type conversions
   - Handles NULL values and default values
   - Adds explanatory comments

2. **Execution**:
   - Validates SQL syntax
   - Executes against Snowflake database
   - Provides success/failure feedback

## User Interface

### Main Layout
- **Two-Column Selection**: Side-by-side input and target table selection
- **Metadata Display**: Comprehensive table information with expandable sample data
- **Analysis Section**: Detailed mapping analysis with similarity results
- **SQL Section**: Generated SQL with execution controls
- **Feedback Interface**: Interactive feedback form for refinements

### Key Controls
- **Table Selectors**: Dropdowns for source and target table selection
- **Map to Target Table**: Primary action button to start analysis
- **Reinitialize Embeddings**: Reset vector embeddings if needed
- **Approve/Reject Analysis**: User decision points
- **Execute SQL**: Final execution control

## Data Flow

```
[Source Systems] → [Vector Embeddings] → [Similarity Analysis] → [LLM Analysis] → [User Review] → [SQL Generation] → [Target Schema]
```

1. **Input**: Source table metadata + Target table metadata
2. **Processing**: Vector similarity + LLM analysis + Sample data analysis
3. **Output**: Intelligent field mappings + Executable SQL
4. **Feedback Loop**: User refinement → Enhanced analysis

## Configuration

### Database Configuration
- **Database**: `CUSTOMER_DATA_MAPPING`
- **Input Schema**: `SOURCE_SYSTEMS`
- **Target Schema**: `TARGET_SCHEMA`
- **Embeddings Table**: `COLUMN_EMBEDDINGS`

### AI Model Configuration
- **Embedding Model**: `snowflake-arctic-embed-l-v2.0`
- **LLM Model**: `claude-3-5-sonnet` (via Snowflake Cortex)
- **Similarity Threshold**: Configurable (default top 5 matches)

## Session State Management

The application maintains several session state variables:
- `mapping_analysis`: Current mapping analysis results
- `generated_sql`: Generated SQL statement
- `master_prompt`: Base prompt for LLM interactions
- `feedback_history`: User feedback for iterative improvement
- `input_metadata`/`target_metadata`: Cached table metadata
- `similarity_results`: Vector similarity calculations
- `embeddings_initialized`: Embedding initialization status

## Error Handling

### Robust Error Management
- **Connection Failures**: Graceful degradation with multiple connection methods
- **Missing Embeddings**: Automatic reinitialization capabilities
- **SQL Errors**: Detailed error reporting with traceback
- **LLM Failures**: Fallback to traditional mapping methods

### Validation
- **Metadata Validation**: Ensures tables exist and have accessible metadata
- **Embedding Validation**: Verifies embeddings table exists and contains data
- **SQL Validation**: Checks generated SQL before execution

## Performance Considerations

### Optimizations
- **Metadata Caching**: Avoids redundant metadata queries
- **Lazy Loading**: Loads embeddings only when needed
- **Batch Processing**: Efficient similarity calculations for multiple columns
- **Sample Data Limits**: Restricts sample data to first 5 records

### Scalability
- **Vector Storage**: Embeddings stored in Snowflake for persistence
- **Incremental Updates**: Can reinitialize embeddings without full rebuild
- **Memory Management**: Efficient handling of large metadata sets

## Use Cases

### Primary Applications
1. **Data Migration**: Mapping legacy system tables to modern schema
2. **Data Integration**: Connecting disparate data sources
3. **ETL Development**: Automated mapping for data pipelines
4. **Schema Evolution**: Mapping between different versions of schemas

### Benefits
- **Reduced Manual Effort**: Automates 80%+ of mapping decisions
- **Improved Accuracy**: Semantic understanding reduces mapping errors
- **Faster Time-to-Value**: Accelerates data integration projects
- **Knowledge Capture**: Documents mapping decisions and reasoning

## Prerequisites

### Technical Requirements
- Snowflake account with Cortex LLM access
- Streamlit-in-Snowflake environment
- Tables in `SOURCE_SYSTEMS` and `TARGET_SCHEMA` schemas
- Appropriate database permissions for creating tables and executing queries

### Data Requirements
- Well-documented table and column comments (recommended)
- Representative sample data in source and target tables
- Consistent naming conventions (helpful but not required)

## Future Enhancements

### Planned Features
- **Custom Similarity Thresholds**: User-configurable similarity scoring
- **Mapping Templates**: Reusable mapping patterns for common scenarios
- **Bulk Operations**: Support for mapping multiple table pairs
- **Audit Trail**: Complete history of mapping decisions and changes
- **Advanced Transformations**: Support for complex data transformations
- **Integration APIs**: REST endpoints for programmatic access

### Advanced Capabilities
- **Multi-table Joins**: Support for complex source queries
- **Data Quality Checks**: Validation rules for mapped data
- **Performance Optimization**: Query optimization suggestions
- **Schema Drift Detection**: Monitoring for schema changes

## Conclusion

The Enhanced Schema Mapper represents a significant advancement in automated database schema mapping, combining the power of vector embeddings, artificial intelligence, and human expertise to solve one of data engineering's most time-consuming challenges. By leveraging Snowflake's advanced AI capabilities, it provides intelligent, context-aware mapping suggestions that dramatically reduce the time and effort required for data integration projects. 