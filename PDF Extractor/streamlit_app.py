import streamlit as st
from snowflake.snowpark.context import get_active_session
import json
import pandas as pd
import time

# Set page config
st.set_page_config(
    page_title="PDF Data Extractor",
    page_icon="📄",
    layout="wide"
)

# Get Snowflake session
session = get_active_session()

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'edited_data' not in st.session_state:
    st.session_state.edited_data = None
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'schema' not in st.session_state:
    st.session_state.schema = {}
if 'schema_template' not in st.session_state:
    st.session_state.schema_template = 'Custom'
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'last_classified_file' not in st.session_state:
    st.session_state.last_classified_file = None
if 'pending_classification' not in st.session_state:
    st.session_state.pending_classification = None
if 'file_staged' not in st.session_state:
    st.session_state.file_staged = False

# Title and description
col_title, col_reset = st.columns([5, 1])
with col_title:
    st.title("📄 PDF Data Extractor with AI")
with col_reset:
        if st.button("🗑️ Clear All", type="secondary", help="Clear all uploaded files and extracted data"):
            # Clear all session state
            st.session_state.extracted_data = None
            st.session_state.edited_data = None
            st.session_state.pdf_uploaded = False
            st.session_state.pdf_bytes = None
            st.session_state.uploader_key += 1  # Reset file uploader
            st.session_state.schema_template = "Custom"  # Reset to Custom
            st.session_state.pending_classification = None
            st.session_state.last_classified_file = None
            st.session_state.file_staged = False
            if 'schema' in st.session_state:
                del st.session_state.schema
            if 'file_name' in st.session_state:
                del st.session_state.file_name
            if 'account_identifiers' in st.session_state:
                del st.session_state.account_identifiers
            if 'use_batched_extraction' in st.session_state:
                del st.session_state.use_batched_extraction
            st.rerun()

st.markdown("""
Upload a PDF file to extract structured data using Snowflake's AI_EXTRACT functionality.
Review and correct the extracted data before submitting it to the database.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Database and table configuration
    try:
        # Get list of databases
        databases_df = session.sql("SHOW DATABASES").collect()
        databases = [row['name'] for row in databases_df]
        
        # Add option to create new database
        databases_with_new = ["📝 Create New..."] + databases
        
        database_selection = st.selectbox(
            "Database",
            options=databases_with_new,
            index=databases_with_new.index("PDF_EXTRACTION_DB") if "PDF_EXTRACTION_DB" in databases_with_new else 0
        )
        
        if database_selection == "📝 Create New...":
            database_name = st.text_input("New Database Name", value="PDF_EXTRACTION_DB")
        else:
            database_name = database_selection
        
        # Get list of schemas in selected database
        schemas = []
        if database_name and database_name != "📝 Create New...":
            try:
                schemas_df = session.sql(f"SHOW SCHEMAS IN DATABASE {database_name}").collect()
                schemas = [row['name'] for row in schemas_df]
            except:
                schemas = ["PUBLIC"]
        
        schemas_with_new = ["📝 Create New..."] + schemas
        
        schema_selection = st.selectbox(
            "Schema",
            options=schemas_with_new,
            index=schemas_with_new.index("PUBLIC") if "PUBLIC" in schemas_with_new else 0
        )
        
        if schema_selection == "📝 Create New...":
            schema_name = st.text_input("New Schema Name", value="PUBLIC")
        else:
            schema_name = schema_selection
        
        # Get list of tables in selected database and schema
        tables = []
        if database_name and schema_name and database_name != "📝 Create New..." and schema_name != "📝 Create New...":
            try:
                tables_df = session.sql(f"SHOW TABLES IN {database_name}.{schema_name}").collect()
                tables = [row['name'] for row in tables_df]
            except:
                tables = []
        
        tables_with_new = ["📝 Create New..."] + tables
        
        table_selection = st.selectbox(
            "Table",
            options=tables_with_new,
            index=tables_with_new.index("EXTRACTED_DATA") if "EXTRACTED_DATA" in tables_with_new else 0
        )
        
        if table_selection == "📝 Create New...":
            table_name = st.text_input("New Table Name", value="EXTRACTED_DATA")
        else:
            table_name = table_selection
        
        # Get list of stages in selected database and schema
        stages = []
        if database_name and schema_name and database_name != "📝 Create New..." and schema_name != "📝 Create New...":
            try:
                stages_df = session.sql(f"SHOW STAGES IN {database_name}.{schema_name}").collect()
                stages = [row['name'] for row in stages_df]
            except:
                stages = []
        
        stages_with_new = ["📝 Create New..."] + stages
        
        stage_selection = st.selectbox(
            "Stage",
            options=stages_with_new,
            index=stages_with_new.index("PDF_STAGE") if "PDF_STAGE" in stages_with_new else 0
        )
        
        if stage_selection == "📝 Create New...":
            stage_name = st.text_input("New Stage Name", value="PDF_STAGE")
        else:
            stage_name = stage_selection
            
    except Exception as e:
        st.warning(f"Could not load database objects. Using default values.")
        database_name = st.text_input("Database Name", value="PDF_EXTRACTION_DB")
        schema_name = st.text_input("Schema Name", value="PUBLIC")
        table_name = st.text_input("Table Name", value="EXTRACTED_DATA")
        stage_name = st.text_input("Stage Name", value="PDF_STAGE")
    
    st.markdown("---")
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Upload a PDF file
    2. Define extraction schema
    3. Review extracted data
    4. Correct any errors
    5. Submit to database
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1️⃣ Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload the PDF file you want to extract data from",
        key=f"pdf_uploader_{st.session_state.uploader_key}"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        file_size = len(uploaded_file.getvalue()) / 1024  # Size in KB
        st.info(f"File size: {file_size:.2f} KB")
        
        # Store uploaded file info for auto-detection later
        st.session_state.pending_classification = uploaded_file.name
        st.session_state.file_staged = False  # Reset staging flag when new file uploaded
        
        # Display PDF preview options
        with st.expander("👁️ View Document", expanded=False):
            st.markdown("**Document Actions:**")
            col_dl, col_info = st.columns([1, 2])
            with col_dl:
                st.download_button(
                    label="📥 Download PDF",
                    data=uploaded_file.getvalue(),
                    file_name=uploaded_file.name,
                    mime="application/pdf",
                    help="Download the PDF to view in your default PDF viewer"
                )
            with col_info:
                st.info("💡 Download the PDF to view it in your browser or PDF viewer for comparison during data review")

with col2:
    st.header("2️⃣ Define Extraction Schema")
    st.markdown("Specify the fields you want to extract from the PDF:")
    
    # Predefined schema templates (Custom first, then alphabetical)
    template_options = ["Custom", "Bank Statement", "Contract", "Invoice", "Investment Statement", "Paystub", "Receipt", "Resume", "Tax Return", "W-2 Tax Form"]
    
    # Use session state to determine the index
    try:
        template_index = template_options.index(st.session_state.schema_template)
    except (ValueError, AttributeError):
        template_index = 0  # Default to "Custom"
    
    schema_template = st.selectbox(
        "Choose a template or create custom",
        template_options,
        index=template_index
    )
    
    # Update session state when user changes selection
    st.session_state.schema_template = schema_template
    
    # Auto-detect document type button
    if uploaded_file is not None:
        if st.button("🔍 Detect Document Type", type="primary", help="Automatically detect the type of document", use_container_width=True):
            with st.spinner("Analyzing document type..."):
                try:
                    # Create stage if it doesn't exist
                    session.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}").collect()
                    session.sql(f"CREATE SCHEMA IF NOT EXISTS {database_name}.{schema_name}").collect()
                    session.sql(f"""
                        CREATE STAGE IF NOT EXISTS {database_name}.{schema_name}.{stage_name}
                        ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
                    """).collect()
                    
                    # Upload PDF to stage for detection
                    file_name = uploaded_file.name
                    put_result = session.file.put_stream(
                        uploaded_file,
                        f"@{database_name}.{schema_name}.{stage_name}/{file_name}",
                        auto_compress=False,
                        overwrite=True
                    )
                    
                    # Use AI_EXTRACT to classify the document
                    classification_schema = {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "document_type": {
                                    "description": "Analyze the document carefully. Look for these SPECIFIC indicators: First check if it's a TAX RETURN (Form 1040, 1040-SR, 1040-EZ) - these are multi-page documents with sections like 'Income', 'Adjusted Gross Income', 'Tax and Credits', 'Payments', 'Refund', Schedule A/B/C/D/E/F attachments. Tax returns show LINE NUMBERS (like Line 1, Line 2, etc.) and have 'Form 1040' at the top. Next check if it's a W-2 FORM - this is a single page with BOXES numbered 1-20, shows employer info in box c, wages in box 1, federal tax withheld in box 2. W-2s are wage statements from employers, NOT full tax returns. Then check other types: 'Bank Statement' (account transactions), 'Paystub' (pay period earnings), 'Invoice', 'Receipt', 'Resume', 'Contract', or 'Other'. Return EXACTLY one of these values: 'Tax Return', 'W-2 Tax Form', 'Bank Statement', 'Paystub', 'Invoice', 'Receipt', 'Resume', 'Contract', 'Other'.",
                                    "type": "string"
                                }
                            }
                        }
                    }
                    
                    classification_sql = json.dumps(classification_schema).replace("'", "''")
                    result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{classification_sql}')
                    ) as classification_result
                    """).collect()
                    
                    if result:
                        classification_data = result[0]['CLASSIFICATION_RESULT']
                        if isinstance(classification_data, str):
                            classification_json = json.loads(classification_data)
                        else:
                            classification_json = classification_data
                        
                        detected_type = classification_json.get('response', {}).get('document_type', '')
                        
                        # Debug: Show what the AI detected
                        if detected_type:
                            st.info(f"🤖 AI detected: '{detected_type}'")
                            
                            # Map detected type to our template options
                            template_mapping = {
                                # Check most specific phrases first (exact matches from AI)
                                "bank statement": "Bank Statement",
                                "investment statement": "Investment Statement",
                                "tax return": "Tax Return",
                                "w-2 tax form": "W-2 Tax Form",
                                
                                # Investment/brokerage keywords
                                "portfolio": "Investment Statement",
                                "brokerage": "Investment Statement",
                                "securities": "Investment Statement",
                                "holdings": "Investment Statement",
                                
                                # Tax keywords
                                "1040": "Tax Return",
                                "form 1040": "Tax Return",
                                "irs": "Tax Return",
                                
                                "w-2": "W-2 Tax Form",
                                "w2": "W-2 Tax Form",
                                
                                # Generic terms last (only if nothing else matched)
                                "invoice": "Invoice",
                                "receipt": "Receipt", 
                                "resume": "Resume",
                                "contract": "Contract",
                                "paystub": "Paystub",
                                "pay stub": "Paystub",
                                "pay-stub": "Paystub",
                                "payslip": "Paystub",
                                "earnings statement": "Paystub"
                            }
                            
                            # Find matching template
                            detected_template = "Custom"
                            detected_type_lower = detected_type.lower()
                            
                            # First try exact match
                            if detected_type in template_options:
                                detected_template = detected_type
                            else:
                                # Then try mapping with longer phrases checked first
                                for key, value in template_mapping.items():
                                    if key in detected_type_lower:
                                        detected_template = value
                                        break
                            
                            if detected_template != "Custom":
                                st.session_state.schema_template = detected_template
                                st.session_state.file_staged = True  # Mark file as already staged
                                st.success(f"✅ Detected document type: **{detected_template}**")
                                st.rerun()
                            else:
                                st.warning(f"⚠️ Document type detected as '{detected_type}' - please select a template manually or use Custom")
                                st.session_state.file_staged = True  # Mark file as already staged even if Custom
                        else:
                            st.warning("⚠️ Could not determine document type - please select a template manually")
                            st.session_state.file_staged = True
                    
                except Exception as e:
                    st.error(f"Error detecting document type: {str(e)}")
        else:
            st.info("💡 Click 'Detect Document Type' to automatically identify your PDF")
    
    # Default schemas for different document types
    default_schemas = {
        "Invoice": {
            "invoice_number": "string",
            "invoice_date": "date",
            "vendor_name": "string",
            "total_amount": "number",
            "due_date": "date",
            "items": "array"
        },
        "Receipt": {
            "merchant_name": "string",
            "transaction_date": "date",
            "total_amount": "number",
            "payment_method": "string",
            "items": "array"
        },
        "Resume": {
            "full_name": "string",
            "email": "string",
            "phone": "string",
            "experience_years": "number",
            "skills": "array",
            "education": "array"
        },
        "Contract": {
            "contract_number": "string",
            "parties": "array",
            "start_date": "date",
            "end_date": "date",
            "contract_value": "number",
            "terms": "string"
        },
        "Paystub": {
            "employee_name": "string",
            "employee_address": "string",
            "employer_name": "string",
            "employer_address": "string",
            "advice_number": "string",
            "pay_period_start": "date",
            "pay_period_end": "date",
            "pay_date": "date",
            "filing_status": "string",
            "regular_rate": "number",
            "regular_hours": "number",
            "regular_pay_current": "number",
            "regular_pay_ytd": "number",
            "overtime_hours": "number",
            "overtime_pay_current": "number",
            "overtime_pay_ytd": "number",
            "commission_current": "number",
            "commission_ytd": "number",
            "bonus_current": "number",
            "bonus_ytd": "number",
            "stock_units_current": "number",
            "stock_units_ytd": "number",
            "gross_pay_current": "number",
            "gross_pay_ytd": "number",
            "federal_income_tax_current": "number",
            "federal_income_tax_ytd": "number",
            "social_security_tax_current": "number",
            "social_security_tax_ytd": "number",
            "medicare_tax_current": "number",
            "medicare_tax_ytd": "number",
            "state_income_tax_current": "number",
            "state_income_tax_ytd": "number",
            "local_tax_current": "number",
            "local_tax_ytd": "number",
            "retirement_401k_current": "number",
            "retirement_401k_ytd": "number",
            "health_insurance_current": "number",
            "health_insurance_ytd": "number",
            "dental_insurance_current": "number",
            "dental_insurance_ytd": "number",
            "vision_insurance_current": "number",
            "vision_insurance_ytd": "number",
            "hsa_fsa_current": "number",
            "hsa_fsa_ytd": "number",
            "espp_current": "number",
            "espp_ytd": "number",
            "std_premium_current": "number",
            "std_premium_ytd": "number",
            "ltd_premium_current": "number",
            "ltd_premium_ytd": "number",
            "other_deductions_current": "array",
            "other_deductions_ytd": "number",
            "net_pay": "number",
            "deposit_account_number": "string",
            "deposit_amount": "number",
            "federal_taxable_wages": "number",
            "total_hours_worked": "number",
            "group_term_life_current": "number",
            "group_term_life_ytd": "number"
        },
        "Bank Statement": {
            "account_holder_name": "string",
            "bank_name": "string",
            "statement_period_start": "date",
            "statement_period_end": "date",
            "all_accounts_summary": "array"
        },
        "W-2 Tax Form": {
            "tax_year": "string",
            "employee_name": "string",
            "employee_ssn": "string",
            "employee_address": "string",
            "employer_name": "string",
            "employer_ein": "string",
            "employer_address": "string",
            "wages_tips_compensation": "number",
            "federal_income_tax_withheld": "number",
            "social_security_wages": "number",
            "social_security_tax_withheld": "number",
            "medicare_wages": "number",
            "medicare_tax_withheld": "number",
            "social_security_tips": "number",
            "allocated_tips": "number",
            "dependent_care_benefits": "number",
            "nonqualified_plans": "number",
            "box12_codes": "array",
            "retirement_plan": "string",
            "third_party_sick_pay": "string",
            "state": "string",
            "state_wages": "number",
            "state_income_tax": "number",
            "local_wages": "number",
            "local_income_tax": "number",
            "locality_name": "string"
        },
        "Tax Return": {
            "tax_year": "string",
            "filing_status": "string",
            "taxpayer_name": "string",
            "taxpayer_ssn": "string",
            "spouse_name": "string",
            "spouse_ssn": "string",
            "address": "string",
            "wages_salaries_tips": "number",
            "taxable_interest": "number",
            "tax_exempt_interest": "number",
            "ordinary_dividends": "number",
            "qualified_dividends": "number",
            "capital_gain_loss": "number",
            "other_income": "number",
            "total_income": "number",
            "adjusted_gross_income": "number",
            "standard_deduction": "number",
            "itemized_deductions": "number",
            "taxable_income": "number",
            "tax_liability": "number",
            "total_tax": "number",
            "federal_income_tax_withheld": "number",
            "estimated_tax_payments": "number",
            "earned_income_credit": "number",
            "child_tax_credit": "number",
            "total_payments": "number",
            "refund_amount": "number",
            "amount_owed": "number",
            "state_tax_info": "array"
        },
        "Investment Statement": {
            "account_holder_name": "string",
            "account_number": "string",
            "brokerage_name": "string",
            "statement_period": "string",
            "opening_balance": "number",
            "closing_balance": "number",
            "total_deposits": "number",
            "total_withdrawals": "number",
            "dividends_received": "number",
            "interest_earned": "number",
            "securities_held": "array"
        }
    }
    
    if schema_template != "Custom":
        selected_schema = default_schemas[schema_template]
        # Schema will be verified during extraction - no need to display here
    else:
        # Custom schema input
        st.info("📝 **Custom Template**: Please define the fields you want to extract from your document. Supported field types: `string`, `number`, `date`, `array`")
        schema_input = st.text_area(
            "Enter your extraction schema (JSON format)",
            value='{\n  "field_name": "string",\n  "field_date": "date",\n  "field_amount": "number"\n}',
            height=200,
            help="Define the fields you want to extract. Example: {\"invoice_number\": \"string\", \"total\": \"number\", \"date\": \"date\"}"
        )
        try:
            selected_schema = json.loads(schema_input)
            if not selected_schema:
                st.warning("⚠️ Please define at least one field in your custom schema before extracting data.")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format. Please correct your schema.")
            selected_schema = {}

# Extract data button
st.markdown("---")
st.header("3️⃣ Extract Data")

if uploaded_file is not None and selected_schema:
    if st.button("🚀 Extract Data with AI", type="primary", use_container_width=True):
        with st.spinner("Extracting data from PDF..."):
            try:
                file_name = uploaded_file.name
                
                # Only upload to stage if not already done by the detect button
                if not st.session_state.get('file_staged', False):
                    # Create stage if it doesn't exist
                    session.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}").collect()
                    session.sql(f"CREATE SCHEMA IF NOT EXISTS {database_name}.{schema_name}").collect()
                    session.sql(f"""
                        CREATE STAGE IF NOT EXISTS {database_name}.{schema_name}.{stage_name}
                        ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
                    """).collect()
                    
                    # Upload PDF to stage
                    pdf_bytes = uploaded_file.getvalue()
                    
                    # Store PDF bytes in session state for later preview
                    st.session_state.pdf_bytes = pdf_bytes
                    
                    # Put file to stage
                    put_result = session.file.put_stream(
                        uploaded_file,
                        f"@{database_name}.{schema_name}.{stage_name}/{file_name}",
                        auto_compress=False,
                        overwrite=True
                    )
                    
                    st.success("✅ PDF uploaded to Snowflake stage")
                else:
                    st.info("✅ Using previously uploaded PDF from stage")
                    # Still store PDF bytes if not already stored
                    if 'pdf_bytes' not in st.session_state:
                        st.session_state.pdf_bytes = uploaded_file.getvalue()
                
                # Check if this is a Bank Statement that needs account discovery
                is_bank_statement = schema_template == "Bank Statement"
                
                # Note: For now, using single-pass extraction for bank statements
                # Multi-pass was too unreliable with AI_EXTRACT
                if is_bank_statement and False:  # Disabled multi-pass
                    st.info("🔍 Pass 1: Thoroughly scanning statement for ALL accounts...")
                    
                    # PASS 1A: First scan to get account count and initial list
                    st.write("Step 1a: Initial account scan...")
                    pass1a_schema = {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "total_accounts_found": {
                                    "description": "How many different account sections are in this entire statement? Count every account header/section that shows account details. Include accounts with $0 balances.",
                                    "type": "string"
                                },
                                "account_identifiers": {
                                    "description": "List EVERY account in this statement. For each account, look at the header section showing the account name and number. Return format: 'Name: [account type and number] | Number: [account number digits only]'. Search through ALL pages systematically. Include: Savings, Checking, Christmas Club, Surprise Savings, Credit Lines, Loans, Money Market. Do NOT skip any accounts.",
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                            "required": ["total_accounts_found", "account_identifiers"]
                        }
                    }
                    
                    pass1a_schema_sql = json.dumps(pass1a_schema).replace("'", "''")
                    
                    pass1a_query = f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{pass1a_schema_sql}')
                    ) as extraction_result
                    """
                    
                    pass1a_result = session.sql(pass1a_query).collect()
                    
                    account_identifiers = []
                    expected_count = 0
                    
                    if pass1a_result:
                        pass1a_data = pass1a_result[0]['EXTRACTION_RESULT']
                        if isinstance(pass1a_data, str):
                            pass1a_json = json.loads(pass1a_data)
                        else:
                            pass1a_json = pass1a_data
                        
                        response_data = pass1a_json.get('response', {})
                        expected_count_str = response_data.get('total_accounts_found', '0')
                        try:
                            expected_count = int(expected_count_str.split()[0]) if expected_count_str else 0
                        except:
                            expected_count = 0
                        
                        account_identifiers = response_data.get('account_identifiers', [])
                        
                        st.write(f"Initial scan found {len(account_identifiers)} accounts (AI reports ~{expected_count} total exist)")
                        
                        # If we found fewer than expected, do a second verification pass
                        if expected_count > len(account_identifiers) or len(account_identifiers) < 10:
                            st.write("Step 1b: Verification scan to catch any missed accounts...")
                            
                            pass1b_schema = {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "additional_accounts": {
                                            "description": f"Review the entire statement carefully. We already found these accounts: {'; '.join(account_identifiers)}. Are there ANY other account sections not in this list? Check later pages thoroughly for additional accounts. Return any missed accounts in format: 'Name: [type] | Number: [digits]'. If no additional accounts found, return empty array.",
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                            
                            pass1b_schema_sql = json.dumps(pass1b_schema).replace("'", "''")
                            
                            pass1b_query = f"""
                            SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                                file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                                responseFormat => PARSE_JSON('{pass1b_schema_sql}')
                            ) as extraction_result
                            """
                            
                            pass1b_result = session.sql(pass1b_query).collect()
                            
                            if pass1b_result:
                                pass1b_data = pass1b_result[0]['EXTRACTION_RESULT']
                                if isinstance(pass1b_data, str):
                                    pass1b_json = json.loads(pass1b_data)
                                else:
                                    pass1b_json = pass1b_data
                                
                                additional = pass1b_json.get('response', {}).get('additional_accounts', [])
                                if additional:
                                    st.write(f"✓ Found {len(additional)} additional accounts in verification scan")
                                    account_identifiers.extend(additional)
                        
                        # Debug: show raw response
                        st.write("**Pass 1 Complete Results:**")
                        st.json({"initial_scan": len(account_identifiers), "accounts": account_identifiers})
                        
                        # Filter out any duplicates
                        seen_numbers = set()
                        unique_accounts = []
                        for acct in account_identifiers:
                            if '|' in acct and 'Number:' in acct:
                                number_part = acct.split('Number:')[-1].strip()
                                if number_part not in seen_numbers and number_part:
                                    seen_numbers.add(number_part)
                                    unique_accounts.append(acct)
                            else:
                                unique_accounts.append(acct)
                        
                        account_identifiers = unique_accounts
                        num_accounts = len(account_identifiers)
                        
                        # Store in session state for Pass 2
                        st.session_state.account_identifiers = account_identifiers
                        
                        st.success(f"✅ Pass 1 complete: Found {num_accounts} unique accounts")
                        
                        # Show what was found
                        with st.expander("🔍 Accounts Discovered (will extract details for these)", expanded=True):
                            for i, acct in enumerate(account_identifiers, 1):
                                st.text(f"{i}. {acct}")
                    else:
                        st.error("❌ Pass 1 failed - no results returned")
                        st.session_state.account_identifiers = []
                    
                    st.info("🤖 Pass 2: Extracting detailed information for all accounts...")
                
                else:
                    # Single-pass for non-bank statements
                    st.info("🤖 Extracting structured data with AI_EXTRACT...")
                
                # Build JSON schema for AI_EXTRACT
                # AI_EXTRACT requires a specific JSON schema format
                properties = {}
                
                # Special descriptions for Paystub fields to handle multi-column layout
                paystub_descriptions = {
                    "employee_name": "What is the employee's full name on this earnings statement?",
                    "employee_address": "What is the employee's complete mailing address?",
                    "employer_name": "What is the employer/company name?",
                    "employer_address": "What is the employer's complete address?",
                    "advice_number": "What is the advice number or check number?",
                    "pay_period_start": "What is the Period Beginning date? (format: YYYY-MM-DD)",
                    "pay_period_end": "What is the Period Ending date? (format: YYYY-MM-DD)",
                    "pay_date": "What is the Pay Date? (format: YYYY-MM-DD)",
                    "filing_status": "What is the Filing Status (e.g., Married, Single)?",
                    "regular_rate": "In the Earnings section Regular row, look at the FIRST column (leftmost). Is there a small hourly rate number (like 50.00 or 75.00) before the hours column? If you only see larger numbers like 7,355.78, then there is NO rate column and you should return 0 for salary positions.",
                    "regular_hours": "In the Earnings section, find the 'Regular' row. What is the second number shown under 'salary/hours' column?",
                    "regular_pay_current": "In the Earnings section, find the 'Regular' row. Look for the third number - this is the current period earnings (labeled 'this period'). What is it?",
                    "regular_pay_ytd": "In the Earnings section, find the 'Regular' row. Look for the fourth/last number on that row - this is the year to date total (labeled 'year to date'). What is it?",
                    "overtime_hours": "What are the overtime hours worked this period?",
                    "overtime_pay_current": "What is the overtime pay for this period?",
                    "overtime_pay_ytd": "What is the overtime pay year to date?",
                    "commission_current": "In the Earnings section, look for a 'Commission' row. Count how many numbers appear on that row. If Commission only has ONE number total (XX,XXX.XX), that single number is the YEAR TO DATE value ONLY, so return 0 for current period. Only return a non-zero value if there are TWO separate numbers and you can identify which is 'this period'. If no Commission row exists, return 0.",
                    "commission_ytd": "In the Earnings section, look for a 'Commission' row. The Commission row should have exactly ONE number shown on it: XX,XXX.XX. This single number is the year to date total. Return that number. If no Commission row exists, return 0.",
                    "bonus_current": "In the Earnings section, look for a 'Bonus' row. If it exists and has a value in the 'this period' column (third position), return that value. If Bonus only has ONE number, that's YTD not current, so return 0. If no Bonus row exists, return 0.",
                    "bonus_ytd": "In the Earnings section, look for a 'Bonus' row. If it exists, find the number in the 'year to date' column (rightmost position). If no Bonus row exists, return 0.",
                    "stock_units_current": "In the Earnings section, find the 'Rest Stock Unit' row. If this row only has ONE number shown (around 25,974), that number belongs in year to date, not current period - so return 0. If Rest Stock Unit has values in both 'this period' AND 'year to date' columns, return the 'this period' value. If no such row exists, return 0.",
                    "stock_units_ytd": "In the Earnings section, find the 'Rest Stock Unit' row. If it exists, find the single number shown on that row (around 25,974, in the rightmost position). That is the year to date total. This should NOT be 184,832 (which is Gross Pay). If no such row exists, return 0.",
                    "gross_pay_current": "Find the Gross Pay row in the Earnings section. What is the dollar amount in the 'this period' column (third column, before year to date)?",
                    "gross_pay_ytd": "Find the Gross Pay row in the Earnings section. What is the dollar amount in the 'year to date' column (fourth/last column)?",
                    "federal_income_tax_current": "In the Deductions Statutory section, find the Federal Income Tax row. Look at the first dollar amount shown for that row (this will be the current period deduction, usually a negative number). What is that amount?",
                    "federal_income_tax_ytd": "In the Deductions Statutory section, find the Federal Income Tax row. Look at the second dollar amount (furthest right, the year to date total). What is that amount?",
                    "social_security_tax_current": "In the Deductions Statutory section, find the Social Security Tax row. The first amount shown is the current period deduction. What is that negative amount?",
                    "social_security_tax_ytd": "In the Deductions Statutory section, find the Social Security Tax row. The second amount shown (on the right) is the year to date total. What is that amount?",
                    "medicare_tax_current": "In the Deductions Statutory section, find the Medicare Tax row. The first amount shown is the current period deduction. What is that negative amount?",
                    "medicare_tax_ytd": "In the Deductions Statutory section, find the Medicare Tax row. The second amount shown (on the right) is the year to date total. What is that amount?",
                    "state_income_tax_current": "In the Deductions section, what is the State Income Tax (CO State Income Tax) for this period?",
                    "state_income_tax_ytd": "In the Deductions section, what is the State Income Tax year to date?",
                    "local_tax_current": "What is the local or city tax for this period?",
                    "local_tax_ytd": "What is the local or city tax year to date?",
                    "retirement_401k_current": "In the Deductions Other section, find the 'Roth 401K' row and the 'Trdl 401K' (or Traditional 401K) row. For each row, take the first number shown (current period deduction, will be negative). Add the absolute values of these two numbers together. What is the combined total (as a positive number)?",
                    "retirement_401k_ytd": "In the Deductions Other section, find the 'Roth 401K' row and the 'Trdl 401K' (or Traditional 401K) row. For each row, take the second number shown (year to date total). Add these two year-to-date amounts together. What is the combined total?",
                    "health_insurance_current": "In the Deductions Other section, find the 'Medical Premium' row. What is the first number shown (current period deduction)?",
                    "health_insurance_ytd": "In the Deductions Other section, find the 'Medical Premium' row. What is the second number shown (year to date total)?",
                    "dental_insurance_current": "In the Deductions Other section, find the 'Dental Premium' row. What is the first number shown (current period deduction)?",
                    "dental_insurance_ytd": "In the Deductions Other section, find the 'Dental Premium' row. What is the second number shown (year to date total)?",
                    "vision_insurance_current": "In the Deductions Other section, find the 'Vision Premium' row. What is the first number shown (current period deduction)?",
                    "vision_insurance_ytd": "In the Deductions Other section, find the 'Vision Premium' row. What is the second number shown (year to date total)?",
                    "hsa_fsa_current": "In the Deductions Other section, find the 'Regular FSA' row. What is the first number shown (current period deduction)?",
                    "hsa_fsa_ytd": "In the Deductions Other section, find the 'Regular FSA' row. What is the second number shown (year to date total)?",
                    "espp_current": "In the Deductions Other section, find the 'ESPP' row. What is the first number shown (current period deduction, will be negative)?",
                    "espp_ytd": "In the Deductions Other section, find the 'ESPP' row. What is the second number shown (year to date total)?",
                    "std_premium_current": "In the Deductions Other section, find the 'STD Premium' row. Look at the FIRST number on that row (the leftmost number after the label, current period deduction). This should be a small negative number like -14.71. What is it?",
                    "std_premium_ytd": "In the Deductions Other section, find the 'STD Premium' row specifically. Look at the SECOND number on that row (to the right of the current period amount). This STD Premium year to date value should be a few hundred dollars, NOT 1,691.81 (which is a different field). What is the second number on the STD Premium row?",
                    "ltd_premium_current": "In the Deductions Other section, find the 'LTD Premium' row. Look at the FIRST number on that row (current period deduction). This should be a small negative number like -9.81. What is it?",
                    "ltd_premium_ytd": "In the Deductions Other section, find the 'LTD Premium' row specifically. Look at the SECOND number on that row (to the right of the current period amount). This is the LTD Premium year to date total. If there's only one number on the LTD Premium row, check if it might be in a different location. What is the year to date value for LTD Premium?",
                    "other_deductions_current": "What are any other deductions listed for this period that haven't been captured?",
                    "other_deductions_ytd": "What is the total of other deductions year to date?",
                    "net_pay": "Look for 'Net Pay' or 'Net Check' on the statement. What is the dollar amount shown next to it (this is the take-home pay)?",
                    "deposit_account_number": "At the bottom of the statement in the deposit section, what is the account number shown?",
                    "deposit_amount": "At the bottom of the statement in the 'Deposited to the account of' section, what is the dollar amount deposited?",
                    "federal_taxable_wages": "In the notes or tax information section, what amount is listed as 'Your federal taxable wages this period are'?",
                    "total_hours_worked": "What are the total hours worked this period?",
                    "group_term_life_current": "In Other Benefits section, what is the Group Term Life amount for this period?",
                    "group_term_life_ytd": "In Other Benefits section, what is the Group Term Life total to date?"
                }
                
                # Special descriptions for Bank Statement fields to handle multi-account structure
                bank_statement_descriptions = {
                    "account_holder_name": "Who is the primary account holder listed on this statement?",
                    "bank_name": "What is the name of the bank or credit union?",
                    "statement_period_start": "What is the statement start date? (format: YYYY-MM-DD)",
                    "statement_period_end": "What is the statement end date? (format: YYYY-MM-DD)",
                    "all_accounts_summary": None  # Will be handled with two-query approach
                }
                
                # Two-query approach for bank statements to avoid AI limits
                is_bank_statement_two_query = schema_template == "Bank Statement"
                
                for field_name, field_type in selected_schema.items():
                    # Create a descriptive question for each field
                    field_label = field_name.replace('_', ' ').title()
                    
                    # Use specialized descriptions for paystub, bank statement, stock award, or commission fields if available
                    if field_name in paystub_descriptions:
                        description = paystub_descriptions[field_name]
                    elif field_name in bank_statement_descriptions:
                        description = bank_statement_descriptions[field_name]
                    elif field_name in stock_award_descriptions:
                        description = stock_award_descriptions[field_name]
                    elif field_name in commission_descriptions:
                        description = commission_descriptions[field_name]
                    else:
                        # Generic description for other document types
                        if field_type == "date":
                            description = f"What is the {field_label}? (format: YYYY-MM-DD)"
                        elif field_type == "array":
                            description = f"What are the {field_label}?"
                        else:
                            description = f"What is the {field_label}?"
                    
                    # Special handling for W-2 fields that need specific box references
                    if schema_template == "W-2 Tax Form":
                        w2_descriptions = {
                            "employee_ssn": "Find Box 'a' - Employee's social security number",
                            "employer_ein": "Find Box 'b' - Employer identification number (EIN)",
                            "wages_tips_compensation": "Find Box '1' - Wages, tips, other compensation",
                            "federal_income_tax_withheld": "Find Box '2' - Federal income tax withheld",
                            "social_security_wages": "Find Box '3' - Social security wages",
                            "social_security_tax_withheld": "Find Box '4' - Social security tax withheld",
                            "medicare_wages": "Find Box '5' - Medicare wages and tips",
                            "medicare_tax_withheld": "Find Box '6' - Medicare tax withheld",
                            "social_security_tips": "Find Box '7' - Social security tips (if any)",
                            "allocated_tips": "Find Box '8' - Allocated tips (if any)",
                            "dependent_care_benefits": "Find Box '10' - Dependent care benefits (if any)",
                            "nonqualified_plans": "Find Box '11' - Nonqualified plans (if any)",
                            "box12_codes": "Find Box '12' - List all codes and amounts (e.g., 'D-15000', 'W-5000')",
                            "retirement_plan": "Find Box '13' - Is 'Retirement plan' box checked? (yes/no)",
                            "third_party_sick_pay": "Find Box '13' - Is 'Third-party sick pay' box checked? (yes/no)",
                            "state": "Find Box '15' - State abbreviation",
                            "state_wages": "Find Box '16' - State wages, tips, etc.",
                            "state_income_tax": "Find Box '17' - State income tax",
                            "local_wages": "Find Box '18' - Local wages, tips, etc.",
                            "local_income_tax": "Find Box '19' - Local income tax",
                            "locality_name": "Find Box '20' - Locality name"
                        }
                        if field_name in w2_descriptions:
                            description = w2_descriptions[field_name]
                    
                    if field_type == "string":
                        properties[field_name] = {
                            "description": description,
                            "type": "string"
                        }
                    elif field_type == "number":
                        properties[field_name] = {
                            "description": description,
                            "type": "string"  # AI_EXTRACT only supports string type
                        }
                    elif field_type == "date":
                        properties[field_name] = {
                            "description": description,
                            "type": "string"
                        }
                    elif field_type == "array":
                        # AI_EXTRACT only supports string items in arrays, not objects
                        properties[field_name] = {
                            "description": description,
                            "type": "array"
                        }
                    else:
                        properties[field_name] = {
                            "description": description,
                            "type": "string"
                        }
                
                # Check if we need batched extraction for bank statements
                if st.session_state.get('use_batched_extraction', False) and hasattr(st.session_state, 'account_identifiers'):
                    # SINGLE-PASS extraction with all accounts at once
                    st.info(f"🔄 Extracting details for all {len(st.session_state.account_identifiers)} accounts...")
                    
                    # Use simple single-pass extraction - let AI extract all accounts at once
                    # Revert to the approach that was working reasonably well
                    st.session_state.use_batched_extraction = False
                    all_account_details = []
                    
                    # Now extract other fields (non-array fields)
                    st.write("Extracting statement header info...")
                    header_properties = {}
                    for field_name, field_type in selected_schema.items():
                        if field_name != "all_accounts_summary":
                            field_label = field_name.replace('_', ' ').title()
                            if field_name in bank_statement_descriptions:
                                description = bank_statement_descriptions[field_name]
                            else:
                                description = f"What is the {field_label}?"
                            
                            header_properties[field_name] = {
                                "description": description,
                                "type": "string"
                            }
                    
                    header_schema = {
                        "schema": {
                            "type": "object",
                            "properties": header_properties
                        }
                    }
                    
                    header_schema_sql = json.dumps(header_schema).replace("'", "''")
                    
                    header_query = f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{header_schema_sql}')
                    ) as extraction_result
                    """
                    
                    header_result = session.sql(header_query).collect()
                    
                    if header_result:
                        header_data = header_result[0]['EXTRACTION_RESULT']
                        if isinstance(header_data, str):
                            header_json = json.loads(header_data)
                        else:
                            header_json = header_data
                        
                        extracted_data = header_json.get('response', {})
                        extracted_data['all_accounts_summary'] = all_account_details
                        
                        st.session_state.extracted_data = extracted_data
                        st.session_state.pdf_uploaded = True
                        st.session_state.schema = selected_schema
                        st.session_state.schema_template = schema_template
                        st.session_state.file_name = file_name
                        
                        st.success(f"✅ Batched extraction complete! Extracted {len(all_account_details)} accounts total")
                        st.rerun()
                
                elif is_bank_statement_two_query:
                    # TWO-QUERY APPROACH FOR BANK STATEMENTS
                    st.info("🔄 Using two-query extraction for better account coverage...")
                    
                    # Query 1: Extract accounts on early pages (accounts 1-5)
                    st.write("Query 1: Extracting accounts from first half of statement...")
                    query1_properties = {
                        "accounts_batch1": {
                            "description": "Find accounts on the first pages of the statement (typically pages 1-4). Look for: Primary Savings (XXXXXX01), Platinum Checking (XXXXXX85), Christmas Club Savings (XXXXXX09), Savings XXXXXX80, Savings XXXXXX18. For each found, return: 'AccountName: [name] | Number: [number] | Type: [type] | Opening: [amt] | Closing: [amt] | Interest: [amt] | Deposits: [amt] | Withdrawals: [amt]'. Include all labels, use ' | ' separator.",
                            "type": "array"
                        }
                    }
                    
                    query1_schema = {"schema": {"type": "object", "properties": query1_properties}}
                    query1_sql = json.dumps(query1_schema).replace("'", "''")
                    
                    query1_result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{query1_sql}')
                    ) as extraction_result
                    """).collect()
                    
                    batch1_accounts = []
                    if query1_result:
                        q1_data = query1_result[0]['EXTRACTION_RESULT']
                        if isinstance(q1_data, str):
                            q1_json = json.loads(q1_data)
                        else:
                            q1_json = q1_data
                        batch1_accounts = q1_json.get('response', {}).get('accounts_batch1', [])
                        st.write(f"✓ Query 1: Found {len(batch1_accounts)} accounts")
                    
                    # Query 2: Extract accounts on later pages (accounts 6-10)
                    st.write("Query 2: Extracting accounts from second half of statement...")
                    query2_properties = {
                        "accounts_batch2": {
                            "description": "Find accounts on later pages of the statement (typically pages 5-8). Look for: Christmas Club Savings XXXXXX15, Surprise Savings XXXXXX06, Surprise Savings XXXXXX14, Savings XXXXXX67, Surprise Savings XXXXXX66. For each found, return: 'AccountName: [name] | Number: [number] | Type: [type] | Opening: [amt] | Closing: [amt] | Interest: [amt] | Deposits: [amt] | Withdrawals: [amt]'. Include all labels, use ' | ' separator.",
                            "type": "array"
                        }
                    }
                    
                    query2_schema = {"schema": {"type": "object", "properties": query2_properties}}
                    query2_sql = json.dumps(query2_schema).replace("'", "''")
                    
                    query2_result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{query2_sql}')
                    ) as extraction_result
                    """).collect()
                    
                    batch2_accounts = []
                    if query2_result:
                        q2_data = query2_result[0]['EXTRACTION_RESULT']
                        if isinstance(q2_data, str):
                            q2_json = json.loads(q2_data)
                        else:
                            q2_json = q2_data
                        batch2_accounts = q2_json.get('response', {}).get('accounts_batch2', [])
                        st.write(f"✓ Query 2: Found {len(batch2_accounts)} accounts")
                    
                    # Merge results
                    all_accounts = batch1_accounts + batch2_accounts
                    st.success(f"✅ Combined total: {len(all_accounts)} accounts extracted")
                    
                    # Extract header fields separately
                    st.write("Extracting statement header info...")
                    header_properties = {k: v for k, v in properties.items() if k != "all_accounts_summary"}
                    header_schema = {"schema": {"type": "object", "properties": header_properties}}
                    header_sql = json.dumps(header_schema).replace("'", "''")
                    
                    header_result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{header_sql}')
                    ) as extraction_result
                    """).collect()
                    
                    if header_result:
                        h_data = header_result[0]['EXTRACTION_RESULT']
                        if isinstance(h_data, str):
                            h_json = json.loads(h_data)
                        else:
                            h_json = h_data
                        
                        extracted_data = h_json.get('response', {})
                        extracted_data['all_accounts_summary'] = all_accounts
                        
                        st.session_state.extracted_data = extracted_data
                        st.session_state.pdf_uploaded = True
                        st.session_state.schema = selected_schema
                        st.session_state.schema_template = schema_template
                        st.session_state.file_name = file_name
                        
                        st.success("✅ Two-query extraction complete!")
                        st.rerun()
                
                else:
                    # STANDARD SINGLE-PASS EXTRACTION
                    # Build the complete schema for AI_EXTRACT
                    ai_extract_schema = {
                        "schema": {
                            "type": "object",
                            "properties": properties
                        }
                    }
                    
                    # Convert schema to proper SQL format
                    schema_sql = json.dumps(ai_extract_schema).replace("'", "''")
                    
                    # Use AI_EXTRACT function
                    extract_query = f"""
                    SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                        file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{file_name}'),
                        responseFormat => PARSE_JSON('{schema_sql}')
                    ) as extraction_result
                    """
                    
                    extract_result = session.sql(extract_query).collect()
                    
                    if extract_result:
                        extraction_result = extract_result[0]['EXTRACTION_RESULT']
                        
                        # Parse the AI_EXTRACT response
                        # AI_EXTRACT returns: {"error": null, "response": {...}}
                        try:
                            if isinstance(extraction_result, str):
                                result_json = json.loads(extraction_result)
                            else:
                                result_json = extraction_result
                            
                            # Check for errors
                            if result_json.get('error'):
                                st.error(f"AI_EXTRACT error: {result_json['error']}")
                                st.session_state.extracted_data = {}
                            else:
                                # Get the extracted data from the response
                                extracted_data = result_json.get('response', {})
                                
                                # Store in session state
                                st.session_state.extracted_data = extracted_data
                                st.session_state.pdf_uploaded = True
                                st.session_state.schema = selected_schema
                                st.session_state.schema_template = schema_template
                                st.session_state.file_name = file_name
                                
                                st.success("✅ Data extracted successfully with AI_EXTRACT!")
                                st.rerun()
                                
                        except (json.JSONDecodeError, TypeError) as e:
                            st.error(f"Failed to parse AI_EXTRACT response: {str(e)}")
                            st.text_area("Raw Response", str(extraction_result), height=200)
                            st.session_state.extracted_data = {}
                    else:
                        st.error("No data returned from AI_EXTRACT")
                    
            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                st.exception(e)

# Display and edit extracted data
if st.session_state.extracted_data is not None:
    st.markdown("---")
    st.header("4️⃣ Review & Correct Extracted Data")
    
    # Parse the extracted content
    try:
        if isinstance(st.session_state.extracted_data, str):
            try:
                content = json.loads(st.session_state.extracted_data)
            except:
                content = {}
        else:
            content = st.session_state.extracted_data
        
        # Display AI-extracted structured data
        with st.expander("🤖 View AI_EXTRACT Response"):
            st.json(content)
            st.caption("Data extracted directly from PDF using Snowflake's AI_EXTRACT function")
        
        # Add document download for comparison
        with st.expander("📄 View Original Document", expanded=False):
            try:
                # Provide download option for the PDF
                if st.session_state.pdf_bytes is not None and 'file_name' in st.session_state:
                    st.markdown("**Compare extracted values against the original document:**")
                    
                    col_download, col_tip = st.columns([1, 2])
                    with col_download:
                        st.download_button(
                            label="📥 Download Original PDF",
                            data=st.session_state.pdf_bytes,
                            file_name=st.session_state.file_name,
                            mime="application/pdf",
                            help="Download the PDF to compare with extracted data",
                            key="download_for_review"
                        )
                    with col_tip:
                        st.info("💡 Open the PDF in a separate window/tab to compare values side-by-side")
                else:
                    st.warning("PDF not available. Please re-upload and extract again.")
            except Exception as e:
                st.warning(f"Unable to provide document download: {str(e)}")
        
        st.markdown("### ✏️ Edit Extracted Fields")
        st.markdown("Review the AI-extracted values and make corrections as needed:")
        st.info("ℹ️ **Note:** Deduction amounts are automatically converted to positive values for cleaner data storage (e.g., -313.74 → 313.74)")
        
        # Create editable form
        with st.form("data_correction_form"):
            edited_values = {}
            
            # Create two columns for better layout
            form_col1, form_col2 = st.columns(2)
            
            schema_fields = list(st.session_state.schema.keys())
            mid_point = len(schema_fields) // 2
            
            for idx, (field_name, field_type) in enumerate(st.session_state.schema.items()):
                # Alternate between columns
                current_col = form_col1 if idx < mid_point else form_col2
                
                with current_col:
                    # Get the extracted value from AI
                    extracted_value = content.get(field_name, "")
                    
                    # Convert extracted value to appropriate format
                    if field_type == "string":
                        default_value = str(extracted_value) if extracted_value else ""
                        edited_values[field_name] = st.text_input(
                            f"{field_name.replace('_', ' ').title()}",
                            value=default_value,
                            key=f"edit_{field_name}"
                        )
                    elif field_type == "number":
                        # Clean and parse numeric values
                        try:
                            if extracted_value is None or str(extracted_value).strip().lower() in ['none', 'n/a', '']:
                                default_value = 0.0
                            else:
                                # Remove dollar signs, commas, quotes, and whitespace
                                cleaned = str(extracted_value).replace('$', '').replace(',', '').replace('"', '').strip()
                                # Handle "Net Pay $5,035.49" format - extract just the number
                                if ' ' in cleaned:
                                    parts = cleaned.split()
                                    for part in parts:
                                        try:
                                            default_value = float(part)
                                            break
                                        except:
                                            continue
                                    else:
                                        default_value = 0.0
                                else:
                                    default_value = float(cleaned)
                                
                                # Normalize deduction fields to positive values
                                # Deductions on paystubs are often negative, but we store them as positive
                                deduction_fields = [
                                    'federal_income_tax_current', 'federal_income_tax_ytd',
                                    'social_security_tax_current', 'social_security_tax_ytd',
                                    'medicare_tax_current', 'medicare_tax_ytd',
                                    'state_income_tax_current', 'state_income_tax_ytd',
                                    'local_tax_current', 'local_tax_ytd',
                                    'retirement_401k_current', 'retirement_401k_ytd',
                                    'health_insurance_current', 'health_insurance_ytd',
                                    'dental_insurance_current', 'dental_insurance_ytd',
                                    'vision_insurance_current', 'vision_insurance_ytd',
                                    'hsa_fsa_current', 'hsa_fsa_ytd',
                                    'espp_current', 'espp_ytd',
                                    'std_premium_current', 'std_premium_ytd',
                                    'ltd_premium_current', 'ltd_premium_ytd'
                                ]
                                if field_name in deduction_fields:
                                    default_value = abs(default_value)
                                    
                        except (ValueError, TypeError, AttributeError):
                            default_value = 0.0
                        edited_values[field_name] = st.number_input(
                            f"{field_name.replace('_', ' ').title()}",
                            value=default_value,
                            key=f"edit_{field_name}",
                            format="%.2f"
                        )
                    elif field_type == "date":
                        # Try to parse date if available
                        from datetime import datetime, date
                        default_date = None
                        if extracted_value:
                            try:
                                if isinstance(extracted_value, str):
                                    default_date = datetime.strptime(extracted_value, "%Y-%m-%d").date()
                                elif isinstance(extracted_value, date):
                                    default_date = extracted_value
                            except:
                                pass
                        
                        if default_date:
                            edited_values[field_name] = st.date_input(
                                f"{field_name.replace('_', ' ').title()}",
                                value=default_date,
                                key=f"edit_{field_name}"
                            )
                        else:
                            edited_values[field_name] = st.date_input(
                                f"{field_name.replace('_', ' ').title()}",
                                key=f"edit_{field_name}"
                            )
                    elif field_type == "array":
                        # Convert array to formatted display
                        if isinstance(extracted_value, list):
                            # For all_accounts_summary, display one per line for better readability
                            if field_name == "all_accounts_summary":
                                default_value = "\n".join(str(item) for item in extracted_value)
                                height = 300
                                help_text = "Each line represents one account with format: AccountName: [name] | Number: [number] | Type: [type] | Opening: [amt] | Closing: [amt] | Interest: [amt] | Deposits: [amt] | Withdrawals: [amt]"
                            else:
                                default_value = ", ".join(str(item) for item in extracted_value)
                                height = 100
                                help_text = "Comma-separated list"
                        else:
                            default_value = str(extracted_value) if extracted_value else ""
                            height = 100
                            help_text = None
                            
                        edited_values[field_name] = st.text_area(
                            f"{field_name.replace('_', ' ').title()}",
                            value=default_value,
                            key=f"edit_{field_name}",
                            height=height,
                            help=help_text
                        )
                    else:
                        default_value = str(extracted_value) if extracted_value else ""
                        edited_values[field_name] = st.text_input(
                            f"{field_name.replace('_', ' ').title()}",
                            value=default_value,
                            key=f"edit_{field_name}"
                        )
            
            # Submit buttons
            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            
            with col_submit1:
                submit_button = st.form_submit_button(
                    "💾 Submit to Database",
                    type="primary",
                    use_container_width=True
                )
            
            with col_submit2:
                preview_button = st.form_submit_button(
                    "👁️ Preview Data",
                    use_container_width=True
                )
            
            with col_submit3:
                reset_button = st.form_submit_button(
                    "🔄 Reset",
                    use_container_width=True
                )
            
            if submit_button:
                try:
                    # Create table if it doesn't exist
                    create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {database_name}.{schema_name}.{table_name} (
                        ID NUMBER AUTOINCREMENT,
                        SOURCE_FILE VARCHAR,
                        EXTRACTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                        DATA VARIANT,
                        SCHEMA_TYPE VARCHAR,
                        PRIMARY KEY (ID)
                    )
                    """
                    session.sql(create_table_query).collect()
                    
                    # Add SCHEMA_TYPE column if it doesn't exist (for existing tables)
                    try:
                        session.sql(f"""
                        ALTER TABLE {database_name}.{schema_name}.{table_name}
                        ADD COLUMN SCHEMA_TYPE VARCHAR
                        """).collect()
                    except:
                        # Column already exists, that's fine
                        pass
                    
                    # Prepare data for insert - convert array strings back to proper arrays
                    prepared_data = {}
                    for field_name, field_value in edited_values.items():
                        field_type = st.session_state.schema.get(field_name, "string")
                        
                        if field_type == "array":
                            # Handle different array formats
                            if field_name == "all_accounts_summary" and isinstance(field_value, str):
                                # all_accounts_summary uses newline separation
                                prepared_data[field_name] = [item.strip() for item in field_value.split('\n') if item.strip()]
                            elif isinstance(field_value, str):
                                # Other arrays use comma separation
                                prepared_data[field_name] = [item.strip() for item in field_value.split(',') if item.strip()]
                            elif isinstance(field_value, list):
                                prepared_data[field_name] = field_value
                            else:
                                prepared_data[field_name] = []
                        elif field_type == "date":
                            # Convert date objects to strings for JSON serialization
                            prepared_data[field_name] = str(field_value) if field_value else None
                        else:
                            prepared_data[field_name] = field_value
                    
                    # Insert data using regular staging table (temp tables not supported in SiS)
                    from snowflake.snowpark.functions import parse_json
                    import time
                    
                    # Determine schema type for easier querying later
                    schema_type = st.session_state.get('schema_template', 'Custom')
                    
                    # Convert prepared_data to JSON string
                    data_json = json.dumps(prepared_data)
                    
                    # Create staging table name
                    staging_table = f"{database_name}.{schema_name}.STAGING_INSERT_{int(time.time())}"
                    
                    # Create DataFrame with JSON as string
                    df = session.create_dataframe([
                        (st.session_state.file_name, data_json, schema_type)
                    ], schema=["SOURCE_FILE", "DATA_JSON", "SCHEMA_TYPE"])
                    
                    # Save to regular staging table
                    df.write.mode("overwrite").save_as_table(staging_table)
                    
                    # Insert from staging table with PARSE_JSON
                    insert_sql = f"""
                    INSERT INTO {database_name}.{schema_name}.{table_name} 
                        (SOURCE_FILE, DATA, SCHEMA_TYPE)
                    SELECT 
                        SOURCE_FILE,
                        PARSE_JSON(DATA_JSON),
                        SCHEMA_TYPE
                    FROM {staging_table}
                    """
                    session.sql(insert_sql).collect()
                    
                    # Clean up staging table
                    session.sql(f"DROP TABLE IF EXISTS {staging_table}").collect()
                    
                    st.success("✅ Data successfully submitted to database!")
                    st.balloons()
                    
                    # Clear form data for next submission
                    st.session_state.extracted_data = {}
                    st.session_state.pdf_uploaded = False
                    st.session_state.uploaded_pdf = None
                    st.session_state.file_name = ""
                    st.session_state.schema = {}
                    st.session_state.schema_template = "Custom"
                    st.session_state.uploader_key += 1  # Reset file uploader
                    st.session_state.pending_classification = None
                    st.session_state.last_classified_file = None
                    
                    # Wait a moment for user to see the success message
                    time.sleep(2)
                    st.rerun()
                    
                    # Show submitted data with proper structure
                    st.markdown("**Data stored in Snowflake (VARIANT format):**")
                    st.json(prepared_data)
                    
                    st.info("💡 **Pro Tip:** Use Snowflake's FLATTEN function to query nested arrays. Example: `SELECT * FROM TABLE, LATERAL FLATTEN(input => DATA:all_accounts_summary)`")
                    
                except Exception as e:
                    st.error(f"❌ Error submitting to database: {str(e)}")
                    st.exception(e)
            
            if preview_button:
                st.info("📊 Preview of data to be submitted:")
                st.json(edited_values)
            
            if reset_button:
                st.session_state.extracted_data = None
                st.session_state.pdf_uploaded = False
                st.rerun()
                
    except Exception as e:
        st.error(f"Error processing extracted data: {str(e)}")
        st.exception(e)

# View submitted data
st.markdown("---")
st.header("View Submitted Records")

if st.button("🔍 Load Recent Submissions"):
    try:
        query = f"""
        SELECT 
            ID,
            SOURCE_FILE,
            EXTRACTION_TIMESTAMP,
            DATA
        FROM {database_name}.{schema_name}.{table_name}
        ORDER BY EXTRACTION_TIMESTAMP DESC
        LIMIT 20
        """
        df = session.sql(query).to_pandas()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="extracted_data.csv",
                mime="text/csv"
            )
        else:
            st.info("No records found in the database yet.")
            
    except Exception as e:
        st.info("Database table not yet created. Submit your first extraction to create it.")

# Create new template from document
st.markdown("---")
st.header("🔬 Template Management")

# Template management section
with st.expander("📋 Manage Existing Templates", expanded=False):
    st.info("View and manage your custom templates")
    
    # Get list of templates
    template_list = ["Bank Statement", "Contract", "Invoice", "Paystub", "Receipt", "Resume", "Tax Return", "W-2 Tax Form"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_template = st.selectbox(
            "Select a template to view",
            template_list,
            help="Choose a template to view its configuration"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacer
        if st.button("📝 View Schema", type="secondary"):
            if selected_template in default_schemas:
                st.json(default_schemas[selected_template])
                st.info("💡 To modify this template, copy the schema above, make changes, and use the template builder below to test and save your modified version.")
    
    st.warning("⚠️ Note: Template deletion/modification is not implemented in this demo. In production, templates would be stored in a database with full CRUD operations.")

st.markdown("---")
st.header("🔬 Create New Template from Document")

with st.expander("Build a custom template by analyzing an unknown document", expanded=False):
    st.info("Upload a document and let AI discover its structure to create a reusable template")
    
    # Add example use cases
    st.markdown("**Perfect for documents like:**")
    st.markdown("- Investment/Brokerage Statements (Robinhood, E*TRADE, etc.)")
    st.markdown("- Credit Card Statements")
    st.markdown("- Utility Bills")
    st.markdown("- Insurance Documents")
    st.markdown("- Medical Records")
    st.markdown("- Custom Business Reports")
    
    # File uploader for template creation
    template_file = st.file_uploader(
        "Choose a PDF to analyze",
        type=['pdf'],
        key="template_builder_uploader",
        help="Upload a PDF to discover its fields and create a new template"
    )
    
    if template_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🤖 Discover Fields", type="primary", use_container_width=True):
                with st.spinner("Analyzing document structure..."):
                    try:
                        # Upload to stage for analysis
                        session.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}").collect()
                        session.sql(f"CREATE SCHEMA IF NOT EXISTS {database_name}.{schema_name}").collect()
                        session.sql(f"""
                            CREATE STAGE IF NOT EXISTS {database_name}.{schema_name}.{stage_name}
                            ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
                        """).collect()
                        
                        # Upload file
                        temp_filename = f"template_discovery_{template_file.name}"
                        put_result = session.file.put_stream(
                            template_file,
                            f"@{database_name}.{schema_name}.{stage_name}/{temp_filename}",
                            auto_compress=False,
                            overwrite=True
                        )
                        
                        # Discovery schema - find all possible fields
                        discovery_schema = {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "document_type_guess": {
                                        "description": "What type of document does this appear to be? (e.g., Invoice, Report, Statement, Form, etc.)",
                                        "type": "string"
                                    },
                                    "discovered_fields": {
                                        "description": "Analyze the ENTIRE document and list EVERY data field you can find. Look for: account numbers, names, dates, monetary amounts, percentages, lists of items, totals, subtotals, addresses, IDs, reference numbers, etc. For EACH field, return a string formatted EXACTLY as: 'field_name|sample_value|type|description'. The type MUST be one of: string, number, date, or array. Include AT LEAST 10-20 fields. Examples: 'account_number|#60701338765|string|The customer account number', 'total_amount|1223.74|number|Total portfolio value', 'statement_date|09/01/2025 to 09/30/2025|string|Statement period dates', 'holdings|RYCEY|array|List of securities held'",
                                        "type": "array"
                                    }
                                }
                            }
                        }
                        
                        discovery_sql = json.dumps(discovery_schema).replace("'", "''")
                        result = session.sql(f"""
                        SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                            file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{temp_filename}'),
                            responseFormat => PARSE_JSON('{discovery_sql}')
                        ) as discovery_result
                        """).collect()
                        
                        if result:
                            discovery_data = result[0]['DISCOVERY_RESULT']
                            if isinstance(discovery_data, str):
                                discovery_json = json.loads(discovery_data)
                            else:
                                discovery_json = discovery_data
                            
                            discovered_fields = discovery_json.get('response', {}).get('discovered_fields', [])
                            doc_type_guess = discovery_json.get('response', {}).get('document_type_guess', 'Custom Document')
                            
                            # Validate discovered fields
                            valid_fields = []
                            for field in discovered_fields:
                                if isinstance(field, str) and '|' in field:
                                    parts = field.split('|')
                                    if len(parts) >= 3:  # At minimum need name, value, type
                                        valid_fields.append(field)
                            
                            if not valid_fields:
                                st.error("❌ No valid fields were discovered. The AI response was:")
                                st.json(discovery_json)
                                st.info("💡 Tips: Try uploading a clearer PDF or use a predefined template from Step 2")
                            else:
                                # Store in session state for editing
                                st.session_state.discovered_fields = valid_fields
                                st.session_state.doc_type_guess = doc_type_guess
                                st.session_state.template_filename = temp_filename
                                
                                st.success(f"✅ Discovered {len(valid_fields)} fields in this {doc_type_guess}")
                                st.rerun()
                            
                    except Exception as e:
                        st.error(f"Error analyzing document: {str(e)}")
        
        # Show discovered fields for editing
        if 'discovered_fields' in st.session_state and st.session_state.discovered_fields:
            st.markdown("### 📝 Review and Edit Discovered Fields")
            st.caption("Adjust field names, types, and descriptions as needed")
            
            # Template name
            template_name = st.text_input(
                "Template Name",
                value=st.session_state.get('doc_type_guess', 'Custom Document'),
                help="Give this template a descriptive name"
            )
            
            # Parse and display fields for editing
            edited_fields = {}
            removed_fields = []
            skipped_fields = []
            
            # Debug info
            st.info(f"🔍 Processing {len(st.session_state.discovered_fields)} discovered fields...")
            
            # Add bulk operations for many fields
            if len(st.session_state.discovered_fields) > 20:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("✅ Keep First 20", help="Keep only the first 20 discovered fields"):
                        st.session_state.discovered_fields = st.session_state.discovered_fields[:20]
                        st.rerun()
                with col2:
                    if st.button("📊 Keep Numeric Only", help="Keep only fields with numeric type"):
                        numeric_fields = []
                        for field in st.session_state.discovered_fields:
                            parts = field.split('|')
                            if len(parts) >= 3 and parts[2].strip().lower() in ['number', 'numeric', 'float', 'int']:
                                numeric_fields.append(field)
                        if numeric_fields:
                            st.session_state.discovered_fields = numeric_fields
                            st.rerun()
                with col3:
                    if st.button("🗑️ Clear All", help="Remove all discovered fields"):
                        st.session_state.discovered_fields = []
                        st.rerun()
            
            # Use a more compact display for many fields
            use_compact_view = len(st.session_state.discovered_fields) > 15
            
            if use_compact_view:
                st.markdown("### 📋 Discovered Fields (Compact View)")
                st.caption("Too many fields to display individually. Showing compact view.")
                
                # Show a summary table of fields
                with st.expander("View all discovered fields", expanded=True):
                    field_summary = []
                    for field_str in st.session_state.discovered_fields:
                        parts = field_str.split('|')
                        if len(parts) >= 3:
                            field_summary.append({
                                "Field": parts[0].strip(),
                                "Sample": parts[1].strip()[:50] + "..." if len(parts[1].strip()) > 50 else parts[1].strip(),
                                "Type": parts[2].strip(),
                            })
                    
                    if field_summary:
                        import pandas as pd
                        df = pd.DataFrame(field_summary)
                        st.dataframe(df, use_container_width=True, height=300)
            
            for idx, field_str in enumerate(st.session_state.discovered_fields):
                # Parse the field string
                parts = field_str.split('|')
                if len(parts) >= 3:
                    # Clean field name - remove special characters and make valid identifier
                    raw_field_name = parts[0].strip()
                    field_name = raw_field_name.lower().replace(' ', '_').replace('-', '_').replace('%', '_percent').replace('.', '_').replace('/', '_')
                    # Remove any remaining special characters
                    field_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in field_name)
                    # Remove duplicate underscores and leading/trailing underscores
                    field_name = '_'.join(filter(None, field_name.split('_')))
                    
                    sample_value = parts[1].strip() if len(parts) > 1 else ""
                    suggested_type = parts[2].strip().lower() if len(parts) > 2 else "string"
                    # Normalize type
                    if suggested_type not in ["string", "number", "date", "array"]:
                        if any(t in suggested_type for t in ["num", "float", "int", "amount", "percent", "price", "value", "qty", "quantity"]):
                            suggested_type = "number"
                        elif any(t in suggested_type for t in ["date", "time", "period"]):
                            suggested_type = "date"
                        elif any(t in suggested_type for t in ["list", "array", "items"]):
                            suggested_type = "array"
                        else:
                            suggested_type = "string"
                    description = parts[3].strip() if len(parts) > 3 else f"The {field_name.replace('_', ' ')}"
                    
                    if use_compact_view:
                        # Compact view - just add to edited_fields without UI
                        # Check for duplicates and add suffix if needed
                        final_field_name = field_name
                        if field_name in edited_fields:
                            suffix = 2
                            while f"{field_name}_{suffix}" in edited_fields:
                                suffix += 1
                            final_field_name = f"{field_name}_{suffix}"
                        
                        edited_fields[final_field_name] = {
                            "type": suggested_type,
                            "description": description,
                            "sample": sample_value
                        }
                    else:
                        # Full view with expanders (for fewer fields)
                        # Only show first 10 fields expanded, rest collapsed to avoid UI overload
                        is_expanded = idx < 10
                        with st.expander(f"Field {idx + 1}: **{field_name}**", expanded=is_expanded):
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                # Allow editing field name
                                new_field_name = st.text_input(
                                    "Field Name",
                                    value=field_name,
                                    key=f"field_name_{idx}",
                                    help="Use snake_case naming convention"
                                )
                            
                                # Show sample value (read-only)
                                st.text_input(
                                    "Sample Value",
                                    value=sample_value,
                                    key=f"sample_{idx}",
                                    disabled=True,
                                    help="Sample value found in document"
                                )
                        
                            with col2:
                                # Allow editing field type
                                field_type = st.selectbox(
                                    "Data Type",
                                    ["string", "number", "date", "array"],
                                    index=["string", "number", "date", "array"].index(suggested_type) if suggested_type in ["string", "number", "date", "array"] else 0,
                                    key=f"type_{idx}",
                                    help="Note: 'date' will be converted to 'string' for AI_EXTRACT compatibility"
                                )
                            
                                # Allow editing description
                                field_description = st.text_input(
                                    "Description",
                                    value=description,
                                    key=f"desc_{idx}",
                                    help="Describe what this field contains"
                                )
                        
                            # Option to remove field
                            if st.checkbox("Remove this field", key=f"remove_{idx}"):
                                removed_fields.append(field_name)
                                continue
                        
                            # Clean the new field name as well
                            clean_new_field_name = new_field_name.lower().replace(' ', '_').replace('-', '_').replace('%', '_percent').replace('.', '_').replace('/', '_')
                            clean_new_field_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_new_field_name)
                            clean_new_field_name = '_'.join(filter(None, clean_new_field_name.split('_')))
                            
                            # Store edited field
                            # Check for duplicate field names
                            if clean_new_field_name in edited_fields:
                                # Add a suffix to make it unique
                                suffix = 2
                                while f"{clean_new_field_name}_{suffix}" in edited_fields:
                                    suffix += 1
                                clean_new_field_name = f"{clean_new_field_name}_{suffix}"
                            
                            edited_fields[clean_new_field_name] = {
                                "type": field_type,
                                "description": field_description,
                                "sample": sample_value
                            }
                else:
                    skipped_fields.append(f"Invalid format: {field_str}")
            
            # Add manual field button
            st.markdown("### ➕ Add Custom Fields")
            
            # Initialize manual fields in session state if not exists
            if 'manual_fields' not in st.session_state:
                st.session_state.manual_fields = []
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("➕ Add Field", type="secondary"):
                    st.session_state.manual_fields.append({
                        'name': f'custom_field_{len(st.session_state.manual_fields) + 1}',
                        'type': 'string',
                        'description': ''
                    })
                    st.rerun()
            
            # Display manual fields for editing
            for idx, manual_field in enumerate(st.session_state.manual_fields):
                with st.expander(f"Custom Field {idx + 1}: **{manual_field['name']}**", expanded=True):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        new_name = st.text_input(
                            "Field Name",
                            value=manual_field['name'],
                            key=f"manual_name_{idx}",
                            help="Use snake_case naming"
                        )
                    
                    with col2:
                        new_type = st.selectbox(
                            "Data Type",
                            ["string", "number", "date", "array"],
                            index=["string", "number", "date", "array"].index(manual_field['type']),
                            key=f"manual_type_{idx}"
                        )
                    
                    with col3:
                        if st.button("❌", key=f"remove_manual_{idx}"):
                            st.session_state.manual_fields.pop(idx)
                            st.rerun()
                    
                    new_desc = st.text_input(
                        "Description",
                        value=manual_field.get('description', ''),
                        key=f"manual_desc_{idx}",
                        help="Describe what to extract"
                    )
                    
                    # Update manual field
                    clean_manual_name = new_name.lower().replace(' ', '_').replace('-', '_').replace('%', '_percent').replace('.', '_').replace('/', '_')
                    clean_manual_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_manual_name)
                    clean_manual_name = '_'.join(filter(None, clean_manual_name.split('_')))
                    
                    edited_fields[clean_manual_name] = {
                        "type": new_type,
                        "description": new_desc or f"Extract the {new_name.replace('_', ' ')}",
                        "sample": "[User defined]"
                    }
            
            # Show debug info if fields were skipped or there are duplicates
            duplicate_count = len(st.session_state.discovered_fields) - len(set(field_name for field_name in edited_fields.keys() if not field_name.startswith('custom_field_')))
            
            if skipped_fields or duplicate_count > 0:
                with st.expander(f"⚠️ Field Processing Report", expanded=False):
                    if skipped_fields:
                        st.write(f"**{len(skipped_fields)} fields skipped due to invalid format:**")
                        for skip in skipped_fields:
                            st.write(f"- {skip}")
                    if duplicate_count > 0:
                        st.write(f"**{duplicate_count} duplicate field names were given unique suffixes**")
            
            # Preview the schema
            st.markdown("### 🔍 Schema Preview")
            st.info(f"📊 Total fields: {len(edited_fields)} (Discovered: {len(st.session_state.discovered_fields) - len(removed_fields) - len(skipped_fields)}, Added: {len(st.session_state.manual_fields)})")
            
            # Show the schema with type conversions applied (as it will be sent to AI_EXTRACT)
            schema_preview = {}
            for k, v in edited_fields.items():
                field_type = v["type"]
                # Apply same conversions as in test extraction
                if field_type == "date":
                    schema_preview[k] = "string"  # Dates are converted to strings
                else:
                    schema_preview[k] = field_type
            
            st.json(schema_preview)
            
            # Show note about type conversions
            if any(v["type"] == "date" for v in edited_fields.values()):
                st.caption("📝 Note: Date fields will be extracted as strings for compatibility")
            
            # Test extraction with this schema
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🧪 Test Extraction", type="secondary", use_container_width=True):
                    with st.spinner("Testing extraction with your schema..."):
                        try:
                            # Build properties for AI_EXTRACT
                            properties = {}
                            for field_name, field_info in edited_fields.items():
                                # Field names should already be clean from the parsing phase
                                # Map our types to Snowflake AI_EXTRACT types
                                field_type = field_info["type"]
                                description = field_info.get("description", "")
                                
                                # AI_EXTRACT expects specific type values
                                if field_type == "date":
                                    # Date might not be a valid type for AI_EXTRACT, use string instead
                                    properties[field_name] = {
                                        "type": "string"
                                    }
                                    if description:
                                        properties[field_name]["description"] = description
                                elif field_type == "array":
                                    # Array needs to be specified differently
                                    properties[field_name] = {
                                        "type": "array",
                                        "items": {"type": "string"}  # Default array items to string
                                    }
                                    if description:
                                        properties[field_name]["description"] = description
                                else:
                                    # For string and number, use as is
                                    properties[field_name] = {
                                        "type": field_type
                                    }
                                    if description:
                                        properties[field_name]["description"] = description
                            
                            # Build the complete schema in the exact format AI_EXTRACT expects
                            full_schema = {
                                "schema": {
                                    "type": "object",
                                    "properties": properties
                                }
                            }
                            
                            # Debug: Show the schema being sent
                            with st.expander("🔍 Debug: Schema being sent to AI_EXTRACT", expanded=False):
                                st.json(full_schema)
                            
                            test_sql = json.dumps(full_schema).replace("'", "''")
                            
                            test_result = session.sql(f"""
                            SELECT SNOWFLAKE.CORTEX.AI_EXTRACT(
                                file => TO_FILE('@{database_name}.{schema_name}.{stage_name}', '{st.session_state.template_filename}'),
                                responseFormat => PARSE_JSON('{test_sql}')
                            ) as test_result
                            """).collect()
                            
                            if test_result:
                                test_data = test_result[0]['TEST_RESULT']
                                if isinstance(test_data, str):
                                    test_json = json.loads(test_data)
                                else:
                                    test_json = test_data
                                
                                # Check for errors in the response
                                if 'error' in test_json or 'ERROR' in test_json:
                                    st.error("❌ AI_EXTRACT returned an error:")
                                    st.json(test_json)
                                    st.info("💡 This often happens with too many fields or complex schemas. Try:")
                                    st.write("- Using 'Keep First 20' to reduce fields")
                                    st.write("- Removing fields with special characters in names")
                                    st.write("- Simplifying field descriptions")
                                else:
                                    st.success("✅ Extraction successful!")
                                    extracted_data = test_json.get('response', {})
                                    
                                    # Show extraction results
                                    st.markdown("### 📄 Extracted Data")
                                    st.json(extracted_data)
                                    
                                    # Show field coverage
                                    extracted_fields = set(extracted_data.keys())
                                    expected_fields = set(properties.keys())
                                    missing_fields = expected_fields - extracted_fields
                                    
                                    if missing_fields:
                                        with st.expander(f"ℹ️ {len(missing_fields)} fields were not found in the document"):
                                            for field in sorted(missing_fields):
                                                st.write(f"- {field}")
                                    
                                    # Store for saving
                                    st.session_state.test_passed = True
                                    st.session_state.final_schema = schema_preview
                                    st.session_state.final_template_name = template_name
                                
                        except Exception as e:
                            st.error(f"Extraction test failed: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
            
            with col2:
                # Save template button (only enabled after successful test)
                if st.session_state.get('test_passed', False):
                    if st.button("💾 Save as Template", type="primary", use_container_width=True):
                        # In a real implementation, you would save this to a database
                        # For now, we'll just show the user what would be saved
                        st.success(f"✅ Template '{st.session_state.final_template_name}' would be saved!")
                        st.info("Note: Template saving to database is not implemented in this demo. The template configuration is:")
                        st.code(f"""
# Add this to your default_schemas dictionary:
"{st.session_state.final_template_name}": {json.dumps(st.session_state.final_schema, indent=4)}
                        """)
                        
                        # Clear session state
                        for key in ['discovered_fields', 'doc_type_guess', 'template_filename', 'test_passed', 'final_schema', 'final_template_name', 'manual_fields']:
                            if key in st.session_state:
                                del st.session_state[key]
                else:
                    st.info("Test extraction first to enable saving")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with Streamlit on Snowflake | Powered by Snowflake Cortex AI</p>
</div>
""", unsafe_allow_html=True)

