import streamlit as st
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple
import traceback

# Set page configuration
st.set_page_config(
    page_title="Enhanced Schema Mapper with Vector Embeddings",
    page_icon="🧮",
    layout="wide"
)

# Initialize session state variables
if 'mapping_analysis' not in st.session_state:
    st.session_state.mapping_analysis = None
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = None
if 'master_prompt' not in st.session_state:
    st.session_state.master_prompt = None
if 'feedback_history' not in st.session_state:
    st.session_state.feedback_history = []
if 'input_metadata' not in st.session_state:
    st.session_state.input_metadata = None
if 'target_metadata' not in st.session_state:
    st.session_state.target_metadata = None
if 'selected_input_table' not in st.session_state:
    st.session_state.selected_input_table = None
if 'selected_target_table' not in st.session_state:
    st.session_state.selected_target_table = None
if 'similarity_results' not in st.session_state:
    st.session_state.similarity_results = None
if 'embeddings_initialized' not in st.session_state:
    st.session_state.embeddings_initialized = False

class VectorEmbeddingManager:
    """Handles vector embeddings and cosine similarity for schema metadata semantic matching"""
    
    def __init__(self, session):
        self.session = session
        self.database_name = "CUSTOMER_DATA_MAPPING"
        self.embeddings_table = "COLUMN_EMBEDDINGS"
        self.embedding_model = "snowflake-arctic-embed-l-v2.0"
        
    def initialize_embeddings(self) -> bool:
        """Initialize vector embeddings for all schema metadata"""
        try:
            # First, create a table with all column metadata
            st.info("Creating column metadata table...")
            metadata_table_sql = f"""
            CREATE OR REPLACE TABLE {self.database_name}.PUBLIC.COLUMN_METADATA_TABLE AS
            SELECT 
                table_schema,
                table_name,
                column_name,
                data_type,
                COALESCE(comment, '') as column_comment,
                CONCAT(
                    'Schema: ', table_schema, 
                    ' Table: ', table_name,
                    ' Column: ', column_name,
                    ' Type: ', data_type,
                    CASE WHEN comment IS NOT NULL AND comment != '' THEN ' Description: ' || comment ELSE '' END
                ) as searchable_content,
                CONCAT(table_schema, '.', table_name, '.', column_name) as full_column_path
            FROM {self.database_name}.INFORMATION_SCHEMA.COLUMNS
            WHERE table_schema IN ('SOURCE_SYSTEMS', 'TARGET_SCHEMA')
            ORDER BY table_schema, table_name, ordinal_position
            """
            
            self.session.sql(metadata_table_sql).collect()
            
            # Verify the table was created and has data
            count_result = self.session.sql(f"SELECT COUNT(*) as cnt FROM {self.database_name}.PUBLIC.COLUMN_METADATA_TABLE").collect()
            record_count = count_result[0]['CNT']
            st.info(f"Column metadata table created with {record_count} records")
            
            if record_count == 0:
                st.error("No metadata records found. Please ensure tables exist in SOURCE_SYSTEMS and TARGET_SCHEMA schemas.")
                return False
            
            # Create embeddings table
            st.info("Generating vector embeddings for column metadata...")
            embeddings_sql = f"""
            CREATE OR REPLACE TABLE {self.database_name}.PUBLIC.{self.embeddings_table} AS
            SELECT 
                table_schema,
                table_name,
                column_name,
                data_type,
                column_comment,
                searchable_content,
                full_column_path,
                SNOWFLAKE.CORTEX.EMBED_TEXT_1024('{self.embedding_model}', searchable_content) as embedding_vector
            FROM {self.database_name}.PUBLIC.COLUMN_METADATA_TABLE
            """
            
            self.session.sql(embeddings_sql).collect()
            st.success("Vector embeddings generated successfully!")
            
            return True
            
        except Exception as e:
            st.error(f"Error initializing vector embeddings: {str(e)}")
            st.error(f"Full error details: {repr(e)}")
            return False
    
    def check_embeddings_exist(self) -> bool:
        """Check if the embeddings table exists and has data"""
        try:
            result = self.session.sql(f"""
                SELECT COUNT(*) as cnt 
                FROM {self.database_name}.PUBLIC.{self.embeddings_table}
            """).collect()
            
            if result and result[0]['CNT'] > 0:
                st.info(f"Embeddings table found with {result[0]['CNT']} records")
                return True
            else:
                st.warning("Embeddings table not found or empty")
                return False
                
        except Exception as e:
            st.warning(f"Embeddings table not accessible: {str(e)}")
            return False
    
    def find_similar_columns(self, input_column: Dict, target_schema: str = "TARGET_SCHEMA", limit: int = 5) -> List[Dict]:
        """Find similar columns using cosine similarity"""
        try:
            # Create search content for the input column
            search_content = f"Schema: {input_column.get('schema', '')} Table: {input_column.get('table', '')} Column: {input_column['name']} Type: {input_column['type']}"
            if input_column.get('comment'):
                search_content += f" Description: {input_column['comment']}"
            
            # Generate embedding for the input column
            embedding_query = f"""
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024('{self.embedding_model}', '{search_content.replace("'", "''")}') as input_embedding
            """
            
            embedding_result = self.session.sql(embedding_query).collect()
            if not embedding_result:
                return []
            
            # Find similar columns using cosine similarity
            similarity_query = f"""
            WITH input_embedding AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024('{self.embedding_model}', '{search_content.replace("'", "''")}') as input_vector
            )
            SELECT 
                e.table_schema,
                e.table_name,
                e.column_name,
                e.data_type,
                e.column_comment,
                e.searchable_content,
                e.full_column_path,
                VECTOR_COSINE_SIMILARITY(i.input_vector, e.embedding_vector) as similarity_score
            FROM {self.database_name}.PUBLIC.{self.embeddings_table} e
            CROSS JOIN input_embedding i
            WHERE e.table_schema = '{target_schema}'
            ORDER BY similarity_score DESC
            LIMIT {limit}
            """
            
            result = self.session.sql(similarity_query).collect()
            return [
                {
                    'table_schema': row['TABLE_SCHEMA'],
                    'table_name': row['TABLE_NAME'],
                    'column_name': row['COLUMN_NAME'],
                    'data_type': row['DATA_TYPE'],
                    'column_comment': row['COLUMN_COMMENT'],
                    'searchable_content': row['SEARCHABLE_CONTENT'],
                    'full_column_path': row['FULL_COLUMN_PATH'],
                    'similarity_score': row['SIMILARITY_SCORE']
                } for row in result
            ]
            
        except Exception as e:
            st.error(f"Error finding similar columns: {str(e)}")
            return []
    
    def find_best_matches_for_all_columns(self, input_columns: List[Dict], target_schema: str = "TARGET_SCHEMA") -> Dict:
        """Find best matching columns for all input columns"""
        similarity_results = {}
        
        for column in input_columns:
            matches = self.find_similar_columns(column, target_schema)
            if matches:
                similarity_results[column['name']] = matches
        
        return similarity_results

class DatabaseManager:
    """Handles all database operations and queries"""
    
    def __init__(self, session):
        self.session = session
        self.database_name = "CUSTOMER_DATA_MAPPING"
        self.input_schema = "SOURCE_SYSTEMS"  # Input tables from source systems
        self.target_schema = "TARGET_SCHEMA"  # Target tables in target schema
    
    def get_available_tables(self, schema_name: str) -> List[str]:
        """Get list of available tables in the specified schema"""
        try:
            query = f"""
                SELECT table_name 
                FROM {self.database_name}.INFORMATION_SCHEMA.TABLES 
                WHERE table_schema = '{schema_name}'
                ORDER BY table_name
            """
            result = self.session.sql(query).collect()
            return [row['TABLE_NAME'] for row in result]
        except Exception as e:
            st.error(f"Error fetching tables from {schema_name}: {str(e)}")
            return []
    
    def get_table_ddl_and_metadata(self, schema_name: str, table_name: str) -> Dict:
        """Get comprehensive table metadata including DDL, comments, and tags"""
        try:
            # Get column information with comments
            columns_query = f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    comment as column_comment
                FROM {self.database_name}.INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema = '{schema_name}' 
                AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """
            columns_result = self.session.sql(columns_query).collect()
            
            # Get table comment
            table_query = f"""
                SELECT comment as table_comment
                FROM {self.database_name}.INFORMATION_SCHEMA.TABLES
                WHERE table_schema = '{schema_name}' 
                AND table_name = '{table_name}'
            """
            table_result = self.session.sql(table_query).collect()
            table_comment = table_result[0]['TABLE_COMMENT'] if table_result else None
            
            # Get table tags (if any)
            tags_info = "No tags available"
            try:
                tags_query = f"""
                    SELECT tag_name, tag_value
                    FROM {self.database_name}.INFORMATION_SCHEMA.TAG_REFERENCES
                    WHERE object_name = '{table_name}'
                    AND object_schema = '{schema_name}'
                """
                tags_result = self.session.sql(tags_query).collect()
                if tags_result:
                    tags_info = ", ".join([f"{row['TAG_NAME']}={row['TAG_VALUE']}" for row in tags_result])
            except:
                pass  # Tags query might fail if no tags exist
            
            return {
                'table_name': table_name,
                'schema_name': schema_name,
                'table_comment': table_comment,
                'tags': tags_info,
                'columns': [
                    {
                        'name': row['COLUMN_NAME'],
                        'type': row['DATA_TYPE'],
                        'nullable': row['IS_NULLABLE'],
                        'default': row['COLUMN_DEFAULT'],
                        'comment': row['COLUMN_COMMENT']
                    } for row in columns_result
                ]
            }
        except Exception as e:
            st.error(f"Error fetching metadata for {schema_name}.{table_name}: {str(e)}")
            return {}
    
    def get_sample_data(self, schema_name: str, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table"""
        try:
            sample_query = f"""
                SELECT * FROM {self.database_name}.{schema_name}.{table_name} 
                LIMIT {limit}
            """
            result = self.session.sql(sample_query).collect()
            
            if result:
                # Convert to pandas DataFrame
                df = pd.DataFrame([dict(row.asDict()) for row in result])
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.warning(f"Could not fetch sample data from {schema_name}.{table_name}: {str(e)}")
            return pd.DataFrame()
    
    def execute_sql(self, sql: str) -> bool:
        """Execute SQL and return success status"""
        try:
            self.session.sql(sql).collect()
            return True
        except Exception as e:
            st.error(f"Error executing SQL: {str(e)}")
            return False

class LLMManager:
    """Handles all LLM interactions using Snowflake Cortex with vector similarity enhancement"""
    
    def __init__(self, session, embedding_manager: VectorEmbeddingManager, db_manager: DatabaseManager):
        self.session = session
        self.embedding_manager = embedding_manager
        self.db_manager = db_manager
        self.model = "claude-3-5-sonnet"
    
    def call_cortex_llm(self, prompt: str) -> str:
        """Call Snowflake Cortex LLM with the given prompt"""
        try:
            # Use Snowflake Cortex Complete function
            query = f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    '{self.model}',
                    '{prompt.replace("'", "''")}'
                ) as response
            """
            result = self.session.sql(query).collect()
            return result[0]['RESPONSE'] if result else "No response received"
        except Exception as e:
            st.error(f"Error calling Cortex LLM: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate_enhanced_mapping_analysis(self, input_metadata: Dict, target_metadata: Dict) -> Tuple[str, Dict]:
        """Generate enhanced mapping analysis using vector embeddings and sample data"""
        # Get similarity results for each input column
        similarity_results = {}
        embedding_successful = True
        
        try:
            # Prepare input columns with schema and table info for embedding
            input_columns_with_context = []
            for column in input_metadata['columns']:
                column_with_context = column.copy()
                column_with_context['schema'] = input_metadata['schema_name']
                column_with_context['table'] = input_metadata['table_name']
                input_columns_with_context.append(column_with_context)
            
            similarity_results = self.embedding_manager.find_best_matches_for_all_columns(
                input_columns_with_context, target_metadata['schema_name']
            )
        except Exception as e:
            st.warning(f"Vector embeddings unavailable, falling back to traditional mapping: {str(e)}")
            embedding_successful = False
        
        # Store similarity results in session state
        st.session_state.similarity_results = similarity_results
        
        # Get sample data from both tables
        input_sample = self.db_manager.get_sample_data(
            input_metadata['schema_name'], input_metadata['table_name'], 3
        )
        target_sample = self.db_manager.get_sample_data(
            target_metadata['schema_name'], target_metadata['table_name'], 3
        )
        
        if embedding_successful and similarity_results:
            # Create enhanced prompt with similarity results and sample data
            similarity_context = self._format_similarity_results_for_prompt(similarity_results)
            
            prompt = f"""
You are an expert data engineer tasked with mapping fields between two database tables, enhanced with vector similarity results and sample data.

INPUT TABLE: {input_metadata['schema_name']}.{input_metadata['table_name']}
Table Comment: {input_metadata.get('table_comment', 'No comment')}
Table Tags: {input_metadata.get('tags', 'No tags')}

INPUT TABLE COLUMNS:
{self._format_columns_for_prompt(input_metadata['columns'])}

INPUT TABLE SAMPLE DATA:
{self._format_sample_data_for_prompt(input_sample)}

TARGET TABLE: {target_metadata['schema_name']}.{target_metadata['table_name']}
Table Comment: {target_metadata.get('table_comment', 'No comment')}
Table Tags: {target_metadata.get('tags', 'No tags')}

TARGET TABLE COLUMNS:
{self._format_columns_for_prompt(target_metadata['columns'])}

TARGET TABLE SAMPLE DATA:
{self._format_sample_data_for_prompt(target_sample)}

VECTOR SIMILARITY RESULTS:
The following are the top matching columns found using vector embeddings and cosine similarity:

{similarity_context}

TASK: Analyze how fields from the INPUT table should be mapped to the TARGET table.

REQUIREMENTS:
1. PRIORITIZE the vector similarity results above when making mapping decisions
2. ANALYZE the sample data patterns to understand data formats, ranges, and content
3. Consider exact column name matches, but also leverage semantic similarity from vector results
4. Look for patterns in the similarity results that indicate strong semantic relationships
5. Use sample data to validate mapping decisions and identify potential data transformations
6. Consider column comments, data types, and semantic meanings
7. Identify any transformations needed (data type conversions, formatting, etc.)
8. Note any input columns that cannot be mapped despite similarity results
9. Note any target columns that will remain NULL
10. Provide confidence scores for each mapping based on similarity results, sample data patterns, and other factors

Please provide a comprehensive analysis that leverages vector similarity results, sample data patterns, and traditional mapping logic.
"""
        else:
            # Fallback to traditional mapping with sample data
            prompt = f"""
You are an expert data engineer tasked with mapping fields between two database tables using sample data analysis.

INPUT TABLE: {input_metadata['schema_name']}.{input_metadata['table_name']}
Table Comment: {input_metadata.get('table_comment', 'No comment')}
Table Tags: {input_metadata.get('tags', 'No tags')}

INPUT TABLE COLUMNS:
{self._format_columns_for_prompt(input_metadata['columns'])}

INPUT TABLE SAMPLE DATA:
{self._format_sample_data_for_prompt(input_sample)}

TARGET TABLE: {target_metadata['schema_name']}.{target_metadata['table_name']}
Table Comment: {target_metadata.get('table_comment', 'No comment')}
Table Tags: {target_metadata.get('tags', 'No tags')}

TARGET TABLE COLUMNS:
{self._format_columns_for_prompt(target_metadata['columns'])}

TARGET TABLE SAMPLE DATA:
{self._format_sample_data_for_prompt(target_sample)}

TASK: Analyze how fields from the INPUT table should be mapped to the TARGET table.

REQUIREMENTS:
1. ANALYZE the sample data patterns to understand data formats, ranges, and content
2. Consider column names, data types, and semantic meanings from comments
3. Look for exact matches first, then semantic matches based on column names, descriptions, and sample data patterns
4. Use sample data to validate mapping decisions and identify potential data transformations
5. Identify any transformations needed (data type conversions, formatting, etc.)
6. Note any input columns that cannot be mapped
7. Note any target columns that will remain NULL
8. Provide confidence scores for each mapping based on similarity and data type compatibility

Please provide a comprehensive analysis of the field mappings using sample data patterns and traditional mapping logic.
"""
        
        analysis = self.call_cortex_llm(prompt)
        return analysis, similarity_results
    
    def _format_similarity_results_for_prompt(self, similarity_results: Dict) -> str:
        """Format similarity results for LLM prompt"""
        if not similarity_results:
            return "No vector similarity results available."
        
        formatted_results = []
        for input_column, matches in similarity_results.items():
            formatted_results.append(f"\nInput Column: {input_column}")
            if matches:
                formatted_results.append("  Top semantic matches:")
                for i, match in enumerate(matches[:3], 1):  # Show top 3 matches
                    formatted_results.append(
                        f"    {i}. {match['full_column_path']} "
                        f"(Similarity: {match['similarity_score']:.3f}, Type: {match['data_type']})"
                    )
                    if match['column_comment']:
                        formatted_results.append(f"       Comment: {match['column_comment']}")
            else:
                formatted_results.append("  No semantic matches found")
        
        return "\n".join(formatted_results)
    
    def _format_sample_data_for_prompt(self, sample_df: pd.DataFrame) -> str:
        """Format sample data for LLM prompt"""
        if sample_df.empty:
            return "No sample data available."
        
        try:
            # Convert DataFrame to string representation
            sample_str = sample_df.to_string(index=False, max_cols=20, max_rows=5)
            return f"Sample records:\n{sample_str}"
        except Exception as e:
            return f"Error formatting sample data: {str(e)}"
    
    def regenerate_mapping_analysis(self, master_prompt: str, user_feedback: str) -> str:
        """Regenerate mapping analysis based on user feedback"""
        enhanced_prompt = f"""
{master_prompt}

PREVIOUS ANALYSIS FEEDBACK:
{user_feedback}

INSTRUCTIONS:
Please regenerate the field mapping analysis taking into account the user's feedback above.
Continue to leverage the vector similarity results and sample data patterns provided, but adjust the mappings based on the user's guidance.
Provide an updated, improved analysis that addresses the user's concerns and suggestions.
"""
        
        return self.call_cortex_llm(enhanced_prompt)
    
    def generate_sql_from_analysis(self, input_metadata: Dict, target_metadata: Dict, analysis: str) -> str:
        """Generate SQL INSERT statement based on mapping analysis"""
        prompt = f"""
You are an expert SQL developer. Based on the field mapping analysis provided (which includes vector similarity results and sample data patterns), generate a SQL INSERT statement to copy data from the input table to the target table.

INPUT TABLE: {input_metadata['schema_name']}.{input_metadata['table_name']}
INPUT COLUMNS:
{self._format_columns_for_prompt(input_metadata['columns'])}

TARGET TABLE: {target_metadata['schema_name']}.{target_metadata['table_name']}
TARGET COLUMNS:
{self._format_columns_for_prompt(target_metadata['columns'])}

MAPPING ANALYSIS (with vector similarity results and sample data):
{analysis}

REQUIREMENTS:
1. Generate a complete INSERT INTO ... SELECT statement
2. Use the mappings recommended in the analysis, which incorporates vector similarity results and sample data patterns
3. Include necessary data type conversions based on sample data observations
4. Handle NULL values appropriately
5. Use fully qualified table names
6. Make the SQL executable in Snowflake
7. Include comments in the SQL explaining key mappings based on vector similarity and sample data insights

CRITICAL OUTPUT REQUIREMENTS:
- Do NOT use any backticks (`) in the response
- Do NOT wrap the SQL in code blocks or markdown formatting
- Do NOT include any explanatory text before or after the SQL
- Return ONLY raw, executable SQL code
- The response should start with INSERT and end with a semicolon

Please provide ONLY the SQL statement, no explanations or additional text.
"""
        
        return self.call_cortex_llm(prompt)
    
    def _format_columns_for_prompt(self, columns: List[Dict]) -> str:
        """Format column information for LLM prompt"""
        formatted = []
        for col in columns:
            comment_text = f" -- {col['comment']}" if col['comment'] else ""
            formatted.append(f"- {col['name']} ({col['type']}){comment_text}")
        return "\n".join(formatted)

def get_snowflake_session():
    """Get Snowflake session object for SiS"""
    try:
        # Method 1: Try using st.connection() (modern approach)
        return st.connection("snowflake").session()
    except Exception as e1:
        try:
            # Method 2: Try using snowflake.snowpark.context (alternative)
            from snowflake.snowpark.context import get_active_session
            return get_active_session()
        except Exception as e2:
            # Method 3: Check if session exists in session_state
            if hasattr(st.session_state, 'session'):
                return st.session_state.session
            else:
                st.error("Unable to connect to Snowflake session")
                st.error(f"Method 1 error: {str(e1)}")
                st.error(f"Method 2 error: {str(e2)}")
                st.error("Make sure you're running this as a Streamlit-in-Snowflake application")
                return None

def main():
    """Main Streamlit application"""
    st.title("🧮 Enhanced Schema Mapper with Vector Embeddings")
    st.markdown("*Powered by Snowflake Cortex LLM, Vector Embeddings, and Sample Data Analysis*")
    st.markdown("---")
    
    # Initialize Snowflake connection for Streamlit-in-Snowflake
    session = get_snowflake_session()
    if session is None:
        st.stop()
    
    try:
        # Initialize managers
        db_manager = DatabaseManager(session)
        embedding_manager = VectorEmbeddingManager(session)
        
        # Initialize Vector Embeddings if not already done
        if not st.session_state.embeddings_initialized:
            with st.spinner("Initializing vector embeddings for schema metadata..."):
                if embedding_manager.initialize_embeddings():
                    st.session_state.embeddings_initialized = True
                    st.success("✅ Vector embeddings initialized successfully!")
                else:
                    st.error("Failed to initialize vector embeddings")
                    st.stop()
        else:
            # Verify embeddings still exist
            if not embedding_manager.check_embeddings_exist():
                st.warning("⚠️ Vector embeddings not found. Reinitializing...")
                with st.spinner("Reinitializing vector embeddings..."):
                    if embedding_manager.initialize_embeddings():
                        st.session_state.embeddings_initialized = True
                        st.success("✅ Vector embeddings reinitialized successfully!")
                    else:
                        st.error("Failed to reinitialize vector embeddings")
                        st.stop()
        
        # Add a manual reinitialize button
        if st.button("🔄 Reinitialize Embeddings", help="Click if you're having issues with the embeddings"):
            st.session_state.embeddings_initialized = False
            st.rerun()
        
        llm_manager = LLMManager(session, embedding_manager, db_manager)
        
    except Exception as e:
        st.error(f"Failed to initialize application managers: {str(e)}")
        st.stop()
    
    # Create two columns for table selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Select Input Table")
        st.caption(f"Tables from {db_manager.input_schema} schema")
        try:
            input_tables = db_manager.get_available_tables(db_manager.input_schema)
            if not input_tables:
                st.warning(f"No tables found in {db_manager.input_schema}")
                st.stop()
            
            selected_input_table = st.selectbox(
                "Choose Input Table:",
                options=input_tables,
                index=input_tables.index(st.session_state.selected_input_table) if st.session_state.selected_input_table in input_tables else 0,
                key="input_table_select"
            )
            # Update session state when selection changes
            if selected_input_table != st.session_state.selected_input_table:
                st.session_state.selected_input_table = selected_input_table
                st.session_state.input_metadata = None  # Reset metadata when table changes
        except Exception as e:
            st.error(f"Error loading input tables: {str(e)}")
            st.stop()
    
    with col2:
        st.subheader("📤 Select Target Table")
        st.caption(f"Tables from {db_manager.target_schema} schema")
        try:
            target_tables = db_manager.get_available_tables(db_manager.target_schema)
            if not target_tables:
                st.warning(f"No tables found in {db_manager.target_schema}")
                st.stop()
            
            selected_target_table = st.selectbox(
                "Choose Target Table:",
                options=target_tables,
                index=target_tables.index(st.session_state.selected_target_table) if st.session_state.selected_target_table in target_tables else 0,
                key="target_table_select"
            )
            # Update session state when selection changes
            if selected_target_table != st.session_state.selected_target_table:
                st.session_state.selected_target_table = selected_target_table
                st.session_state.target_metadata = None  # Reset metadata when table changes
        except Exception as e:
            st.error(f"Error loading target tables: {str(e)}")
            st.stop()
    
    # Display table information
    if selected_input_table and selected_target_table:
        st.markdown("---")
        
        # Show table metadata and sample data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 Input Table: {selected_input_table}")
            try:
                # Load metadata only if not already cached or table changed
                if st.session_state.input_metadata is None or st.session_state.input_metadata.get('table_name') != selected_input_table:
                    input_metadata = db_manager.get_table_ddl_and_metadata(
                        db_manager.input_schema, selected_input_table
                    )
                    st.session_state.input_metadata = input_metadata
                else:
                    input_metadata = st.session_state.input_metadata
                
                if input_metadata:
                    st.text(f"Comment: {input_metadata.get('table_comment', 'No comment')}")
                    st.text(f"Tags: {input_metadata.get('tags', 'No tags')}")
                    
                    # Show columns
                    columns_df = pd.DataFrame(input_metadata['columns'])
                    st.dataframe(columns_df, use_container_width=True)
                    
                    # Show sample data
                    with st.expander("📋 Sample Data", expanded=False):
                        sample_data = db_manager.get_sample_data(db_manager.input_schema, selected_input_table)
                        if not sample_data.empty:
                            st.dataframe(sample_data, use_container_width=True)
                        else:
                            st.info("No sample data available")
                else:
                    st.error("Failed to load input table metadata")
                    st.stop()
            except Exception as e:
                st.error(f"Error loading input table metadata: {str(e)}")
                st.stop()
        
        with col2:
            st.subheader(f"📊 Target Table: {selected_target_table}")
            try:
                # Load metadata only if not already cached or table changed
                if st.session_state.target_metadata is None or st.session_state.target_metadata.get('table_name') != selected_target_table:
                    target_metadata = db_manager.get_table_ddl_and_metadata(
                        db_manager.target_schema, selected_target_table
                    )
                    st.session_state.target_metadata = target_metadata
                else:
                    target_metadata = st.session_state.target_metadata
                
                if target_metadata:
                    st.text(f"Comment: {target_metadata.get('table_comment', 'No comment')}")
                    st.text(f"Tags: {target_metadata.get('tags', 'No tags')}")
                    
                    # Show columns
                    columns_df = pd.DataFrame(target_metadata['columns'])
                    st.dataframe(columns_df, use_container_width=True)
                    
                    # Show sample data
                    with st.expander("📋 Sample Data", expanded=False):
                        sample_data = db_manager.get_sample_data(db_manager.target_schema, selected_target_table)
                        if not sample_data.empty:
                            st.dataframe(sample_data, use_container_width=True)
                        else:
                            st.info("No sample data available")
                else:
                    st.error("Failed to load target table metadata")
                    st.stop()
            except Exception as e:
                st.error(f"Error loading target table metadata: {str(e)}")
                st.stop()
        
        st.markdown("---")
        
        # Map to Target Table button with enhanced embeddings
        if st.button("🧮 Map to Target Table (with Vector Embeddings)", type="primary"):
            try:
                with st.spinner("Analyzing field mappings with vector embeddings and sample data..."):
                    # Ensure we have valid metadata
                    if not st.session_state.input_metadata or not st.session_state.target_metadata:
                        st.error("Missing table metadata. Please ensure both tables are selected.")
                        st.stop()
                    
                    # Generate enhanced mapping analysis using vector embeddings
                    analysis, similarity_results = llm_manager.generate_enhanced_mapping_analysis(
                        st.session_state.input_metadata, st.session_state.target_metadata
                    )
                    
                    # Store in session state
                    st.session_state.mapping_analysis = analysis
                    st.session_state.similarity_results = similarity_results
                    st.session_state.master_prompt = f"""
INPUT TABLE: {st.session_state.input_metadata['schema_name']}.{st.session_state.input_metadata['table_name']}
Table Comment: {st.session_state.input_metadata.get('table_comment', 'No comment')}
Table Tags: {st.session_state.input_metadata.get('tags', 'No tags')}

INPUT TABLE COLUMNS:
{llm_manager._format_columns_for_prompt(st.session_state.input_metadata['columns'])}

TARGET TABLE: {st.session_state.target_metadata['schema_name']}.{st.session_state.target_metadata['table_name']}
Table Comment: {st.session_state.target_metadata.get('table_comment', 'No comment')}
Table Tags: {st.session_state.target_metadata.get('tags', 'No tags')}

TARGET TABLE COLUMNS:
{llm_manager._format_columns_for_prompt(st.session_state.target_metadata['columns'])}

VECTOR SIMILARITY RESULTS:
{llm_manager._format_similarity_results_for_prompt(similarity_results)}

ORIGINAL ANALYSIS:
{analysis}
"""
                    st.session_state.feedback_history = []
                    
                st.success("Enhanced mapping analysis completed with vector embeddings!")
                
            except Exception as e:
                st.error(f"Error during mapping analysis: {str(e)}")
                st.error(f"Traceback: {traceback.format_exc()}")
        
        # Display vector similarity results if available
        if st.session_state.similarity_results:
            st.markdown("---")
            st.subheader("🧮 Vector Similarity Results")
            
            with st.expander("View Detailed Similarity Results", expanded=False):
                for input_column, matches in st.session_state.similarity_results.items():
                    st.write(f"**Input Column: {input_column}**")
                    if matches:
                        similarity_df = pd.DataFrame(matches)
                        st.dataframe(similarity_df, use_container_width=True)
                    else:
                        st.write("No similarity matches found")
                    st.write("---")
        
        # Display mapping analysis if available
        if st.session_state.mapping_analysis:
            st.markdown("---")
            st.subheader("🧠 Enhanced LLM Mapping Analysis")
            
            # Show analysis in an expandable section
            with st.expander("View Full Analysis", expanded=True):
                st.markdown(st.session_state.mapping_analysis)
            
            # Approval/Rejection buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Approve Analysis", type="primary"):
                    try:
                        with st.spinner("Generating SQL from enhanced analysis..."):
                            # Use persisted metadata from session state
                            sql = llm_manager.generate_sql_from_analysis(
                                st.session_state.input_metadata, st.session_state.target_metadata, st.session_state.mapping_analysis
                            )
                            st.session_state.generated_sql = sql
                        st.success("SQL generated successfully with vector-enhanced mappings!")
                    except Exception as e:
                        st.error(f"Error generating SQL: {str(e)}")
            
            with col2:
                if st.button("❌ Reject Analysis"):
                    st.session_state.show_feedback = True
            
            # Show feedback form if analysis was rejected
            if st.session_state.get('show_feedback', False):
                st.markdown("---")
                st.subheader("💭 Provide Feedback")
                
                user_feedback = st.text_area(
                    "Please provide specific feedback on what needs to be improved:",
                    height=100,
                    key="user_feedback"
                )
                
                if st.button("🔄 Resubmit with Feedback"):
                    if user_feedback.strip():
                        try:
                            with st.spinner("Regenerating analysis with your feedback..."):
                                # Ensure we have the metadata from session state
                                if st.session_state.input_metadata is None or st.session_state.target_metadata is None:
                                    st.error("Missing table metadata. Please reselect your tables.")
                                    st.stop()
                                
                                # Add feedback to history
                                st.session_state.feedback_history.append(user_feedback)
                                
                                # Regenerate analysis using persisted metadata
                                new_analysis = llm_manager.regenerate_mapping_analysis(
                                    st.session_state.master_prompt, user_feedback
                                )
                                
                                # Update session state
                                st.session_state.mapping_analysis = new_analysis
                                st.session_state.master_prompt += f"\n\nUSER FEEDBACK: {user_feedback}\nUPDATED ANALYSIS: {new_analysis}"
                                st.session_state.show_feedback = False
                                
                            st.success("Analysis regenerated based on your feedback!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error regenerating analysis: {str(e)}")
                    else:
                        st.warning("Please provide feedback before resubmitting.")
        
        # Display generated SQL if available
        if st.session_state.generated_sql:
            st.markdown("---")
            st.subheader("🔧 Generated SQL (Enhanced with Vector Embeddings)")
            
            # Show SQL in a code block
            st.code(st.session_state.generated_sql, language="sql")
            
            # Execute SQL button
            if st.button("⚡ Execute SQL and Insert Records", type="primary"):
                try:
                    with st.spinner("Executing SQL..."):
                        success = db_manager.execute_sql(st.session_state.generated_sql)
                        
                    if success:
                        st.success("🎉 SUCCESSFULLY EXECUTED!")
                        st.balloons()
                    else:
                        st.error("SQL execution failed. Please check the logs above.")
                        
                except Exception as e:
                    st.error(f"Error executing SQL: {str(e)}")
                    st.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 