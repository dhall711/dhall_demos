# 🧪 UDX AI Hackathon Validation Guide

## 🎯 **Validation Overview**

This guide walks you through connecting to your Snowflake instance and validating that the consolidated UDX AI Hackathon project works correctly for both learning tracks.

---

## 🔗 **Step 1: Connect to Your Snowflake Instance**

### **Method 1: Interactive Setup (Recommended)**
Run this command and follow the prompts:

```bash
export PATH="/Users/dhall/Library/Python/3.11/bin:$PATH"
snow connection add --connection-name udx_hackathon --default
```

**You'll be prompted for:**
- **Account**: Your Snowflake account identifier (e.g., `abc12345.us-west-2.aws`)
- **Username**: Your Snowflake username
- **Password**: Your Snowflake password
- **Role**: Recommended `ACCOUNTADMIN` or `SYSADMIN` for testing
- **Warehouse**: Leave blank (we'll create `UDX_AI_WAREHOUSE`)
- **Database**: Leave blank (we'll create `UDX_AI_HACKATHON`)
- **Schema**: Leave blank (we'll create multiple schemas)

### **Method 2: Command Line Setup**
If you prefer to specify everything at once:

```bash
snow connection add \
  --connection-name udx_hackathon \
  --account YOUR_ACCOUNT \
  --user YOUR_USERNAME \
  --password YOUR_PASSWORD \
  --role ACCOUNTADMIN \
  --default
```

### **Method 3: Environment Variables**
Set these environment variables and use interactive setup:

```bash
export SNOWFLAKE_ACCOUNT="your_account_here"
export SNOWFLAKE_USER="your_username_here"
export SNOWFLAKE_PASSWORD="your_password_here"
export SNOWFLAKE_ROLE="ACCOUNTADMIN"
```

---

## 🚀 **Step 2: Run the Validation**

### **2.1 Test Connection**
```bash
snow connection test --connection udx_hackathon
```

### **2.2 Run Foundation Setup**
```bash
snow sql -f "00-shared-foundation/setup/unified_setup.sql" --connection udx_hackathon
```

### **2.3 Load Business Data**
```bash
snow sql -f "00-shared-foundation/business-data/unified_business_data.sql" --connection udx_hackathon
```

### **2.4 Run Complete Validation**
```bash
snow sql -f "validate_consolidation.sql" --connection udx_hackathon
```

---

## ✅ **Step 3: Expected Results**

If everything is working correctly, you should see:

### **Database Structure:**
- ✅ `UDX_AI_HACKATHON` database created
- ✅ `BUSINESS_ANALYTICS` schema with business data
- ✅ `SHARED_FOUNDATION` schema with AI functions
- ✅ `NLP2SQL_TRACK` schema for Track A
- ✅ `DATA_QUALITY_TRACK` schema for Track B

### **Data Validation:**
- ✅ 6 Universal Studios parks
- ✅ 50,000+ customer records
- ✅ 1,000,000+ sales transactions
- ✅ 2 years of park performance data

### **AI Functions:**
- ✅ Model selection: `get_ai_model_for_task()`
- ✅ Context enhancement: `add_business_context()`
- ✅ NLP2SQL intent: `extract_query_intent()`
- ✅ Quality classification: `classify_quality_issue()`

### **Final Validation Summary:**
```
🎉 UDX AI HACKATHON VALIDATION RESULTS 🎉
Foundation Setup     ✅ PASS
Business Data        ✅ PASS  
AI Functions         ✅ PASS
Track A Setup        ✅ PASS
Track B Setup        ✅ PASS
🚀 ALL SYSTEMS GO! Project ready for production use!
```

---

## 🛠️ **Troubleshooting**

### **Connection Issues**
- **Account not found**: Check your account identifier format
- **Authentication failed**: Verify username/password
- **Permission denied**: Ensure your role has `ACCOUNTADMIN` or sufficient privileges

### **Cortex AI Issues**
- **Cortex functions fail**: Cortex AI might not be enabled on your account
- **Model not available**: Some models may not be available in your region
- **Functions return errors**: This is expected if Cortex AI isn't enabled (functions include error handling)

### **Data Loading Issues**
- **Table creation fails**: Check role permissions
- **Large dataset timeout**: Increase warehouse size or break up data loading
- **Memory issues**: Use `LARGE` or `X-LARGE` warehouse for data generation

---

## 🎯 **Track-Specific Validation**

### **Track A (NLP2SQL) - Business Intelligence Focus**
Test these components work:
- ✅ Query intent analysis: `extract_query_intent()`
- ✅ Business context: Universal Studios theme park data
- ✅ Executive summary views
- ✅ Natural language to SQL patterns

### **Track B (Data Quality) - Data Engineering Focus**  
Test these components work:
- ✅ Quality classification: `classify_quality_issue()`
- ✅ Data quality metrics and monitoring
- ✅ Anomaly detection patterns
- ✅ Quality dashboard views

---

## 🚀 **Next Steps After Validation**

### **For Track A (NLP2SQL) Workshop:**
1. Navigate to `TRACK-A-NLP2SQL/01-basic-translation/`
2. Follow `DOCUMENTATION/STUDENT_GUIDE_NLP2SQL.md`
3. Estimated time: 5 hours

### **For Track B (Data Quality) Workshop:**
1. Navigate to `TRACK-B-DATA-QUALITY/01-quality-fundamentals/`
2. Follow `DOCUMENTATION/STUDENT_GUIDE_QUALITY.md`
3. Estimated time: 8 hours

### **For Complete Experience:**
1. Start with Track A (5 hours)
2. Continue with Track B (8 hours)
3. Explore `ADVANCED-SHARED/` modules
4. Total time: 2-day comprehensive workshop

---

## 📞 **Support**

If you encounter issues:

1. **Check validation output** for specific error messages
2. **Verify permissions** - ACCOUNTADMIN role recommended for testing
3. **Confirm Cortex AI** availability in your Snowflake account
4. **Review setup logs** for detailed error information

---

## 🎉 **Success!**

Once validation passes, you have a fully functional, consolidated UDX AI Hackathon environment ready for:

- ✅ **Track A**: Natural Language to SQL workshops (5 hours)
- ✅ **Track B**: Data Quality & Monitoring workshops (8 hours)  
- ✅ **Flexible delivery**: 3-hour intro, single tracks, or 2-day comprehensive
- ✅ **Production ready**: Error handling, monitoring, and scalable architecture

**Happy learning! 🚀** 