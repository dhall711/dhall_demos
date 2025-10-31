# 📄 Snowflake PDF Data Extractor with AI

Extract structured data from financial PDFs using Snowflake Cortex AI. Automatically process paystubs, bank statements, tax forms, investment statements, and more.

## 🌟 Key Features

- **AI-Powered Classification** - Automatically detects document type
- **Intelligent Extraction** - Extracts 20-60 fields per document with 90%+ accuracy
- **Multiple Document Types** - Paystubs, Bank Statements, W-2s, 1040s, Investment Statements
- **Review & Edit** - Validate extracted data before saving
- **Snowflake Native** - Built on Snowflake Cortex AI (no external services)

## 🚀 Quick Start

### Prerequisites
- Snowflake account with Cortex AI enabled
- Streamlit in Snowflake (SiS) or local Streamlit
- PDF_EXTRACTION_DB database (or configure your own)

### Installation

1. **Set up database:**
```sql
-- Run the setup script in Snowflake
source setup.sql
```

2. **Deploy app:**
   - Upload `streamlit_app.py` to Streamlit in Snowflake
   - Configure database access
   - Launch!

### Basic Usage

1. Upload a PDF document
2. Click "Detect Document Type" (or select manually)
3. Click "Extract Data with AI"
4. Review and edit extracted fields
5. Submit to database

## 📋 Supported Documents

| Document Type | Fields Extracted | Example Use Case |
|---------------|------------------|------------------|
| Paystub | 59 | Payroll processing, tax prep |
| Bank Statement | 5+ (multi-account) | Account reconciliation |
| W-2 Tax Form | 25+ | Tax filing, compliance |
| Tax Return (1040) | 20+ | Tax analysis, planning |
| Investment Statement | 11 | Portfolio tracking |

## 💡 Example Queries

```sql
-- View all extracted paystubs
SELECT 
    SOURCE_FILE,
    DATA:employee_name::STRING as EMPLOYEE,
    DATA:gross_pay_ytd::NUMBER as YTD_GROSS,
    DATA:net_pay::NUMBER as NET_PAY
FROM PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA
WHERE SCHEMA_TYPE = 'Paystub'
ORDER BY EXTRACTION_TIMESTAMP DESC;

-- Query bank accounts from statements
SELECT 
    DATA:bank_name::STRING as BANK,
    value::STRING as ACCOUNT_INFO
FROM PDF_EXTRACTION_DB.PUBLIC.EXTRACTED_DATA,
LATERAL FLATTEN(input => DATA:all_accounts_summary)
WHERE SCHEMA_TYPE = 'Bank Statement';
```

## 🏗️ Architecture

- **Frontend**: Streamlit
- **AI Engine**: Snowflake Cortex AI_EXTRACT
- **Storage**: Snowflake VARIANT columns
- **Processing**: 100% in Snowflake (no external calls)

## 📊 Data Storage

```sql
CREATE TABLE EXTRACTED_DATA (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SOURCE_FILE VARCHAR,
    EXTRACTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    DATA VARIANT,
    SCHEMA_TYPE VARCHAR
);
```

## 🎯 Tips for Best Results

1. Use text-based PDFs (not scanned images)
2. Standard formats work best (ADP, major banks, IRS forms)
3. Always review extracted data before submitting
4. Keep original PDFs for reference
5. Test with samples before production use

## 🐛 Troubleshooting

**No data extracted?**
- Ensure PDF has selectable text
- Try selecting document type manually
- Check file size (< 10MB recommended)

**Wrong values?**
- Review and edit before submitting
- Some layouts may need manual entry

**Permission errors?**
- Grant CREATE STAGE permission
- Verify Cortex AI access

## 📞 Support

- Check Snowflake Cortex AI documentation
- Review setup.sql for configuration
- Contact Snowflake support for Cortex AI issues

---

**Built with Snowflake Cortex AI** | Version 1.0 | October 2025
