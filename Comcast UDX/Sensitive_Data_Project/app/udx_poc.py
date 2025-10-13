import time
import re
from typing import List, Dict, Any, Optional

import pandas as pd
import streamlit as st


st.set_page_config(page_title="UDX Sensitive Data POC", layout="wide")
def run_sql_batch(conn, sql: str):
    # Snowflake/Streamlit connection expects single statement per execute; split on semicolons
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        try:
            conn.query(stmt)
        except Exception as e:
            # DDL/non-SELECT raises NotSupportedError on fetch_pandas_all; assume executed
            if e.__class__.__name__ == 'NotSupportedError' or 'NotSupportedError' in str(e):
                continue
            raise


def sql_quote(val: Any) -> str:
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    # numbers
    if isinstance(val, (int, float)):
        return str(val)
    # default: string
    s = str(val)
    s = s.replace("'", "''")
    return f"'{s}'"



@st.cache_data(ttl=300)
def get_databases(_conn) -> List[str]:
    try:
        df = _conn.query("""select database_name from snowflake.account_usage.databases order by 1""")
        return df["DATABASE_NAME"].tolist()
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_schemas(_conn, database: str) -> List[str]:
    try:
        df = _conn.query(
            f"""
            select schema_name
            from {database}.information_schema.schemata
            order by 1
            """
        )
        return df["SCHEMA_NAME"].tolist()
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_tables(_conn, database: str, schema: str) -> List[str]:
    try:
        df = _conn.query(
            f"""
            select table_name
            from {database}.information_schema.tables
            where table_schema = '{schema}'
            order by 1
            """
        )
        return df["TABLE_NAME"].tolist()
    except Exception:
        return []


def get_columns(conn, database: str, schema: str, table: str) -> pd.DataFrame:
    return conn.query(
        f"""
        select column_name, data_type, comment
        from {database}.information_schema.columns
        where table_schema = '{schema}' and table_name = '{table}'
        order by ordinal_position
        """
    )


def get_column_tags(conn, database: str, schema: str, table: str, column: str) -> str:
    # Snowflake exposes tags via tag references; for POC, fetch string aggregation if available
    try:
        df = conn.query(
            f"""
            select listagg(tag_database||'.'||tag_schema||'.'||tag_name||'='||tag_value, ',') within group(order by tag_name) as tags
            from table(
              information_schema.tag_references_all_columns(
                '{database}', '{schema}', '{table}', 'TABLE'
              )
            )
            where column_name = '{column}'
            """
        )
        if not df.empty and pd.notna(df.loc[0, "TAGS"]):
            return df.loc[0, "TAGS"]
    except Exception:
        pass
    return ""


def get_sample_values(conn, database: str, schema: str, table: str, column: str, sample_size: int) -> List[str]:
    # Use DISTINCT and LIMIT; add SAMPLE clause for large tables (simplified)
    try:
        df = conn.query(
            f"""
            select distinct {column} as sample_value
            from {database}.{schema}.{table}
            where {column} is not null
            limit {sample_size}
            """
        )
        return [str(x) for x in df["SAMPLE_VALUE"].dropna().astype(str).tolist()]
    except Exception:
        return []


def cortex_classify(conn, prompt: str, model: str = "mistral-large") -> Optional[str]:
    try:
        # POC: call Cortex complete for classification-like behavior
        df = conn.query(
            f"""
            select snowflake.cortex.complete('{model}', :prompt) as resp
            """,
            params={"prompt": prompt},
        )
        if not df.empty:
            # crude token/cost estimate and activity logging
            resp = df.loc[0, "RESP"]
            try:
                tokens = max(1, len(prompt.split()) + len(str(resp).split()))
                est_cost = tokens * 0.0001
                ctx_snip = (prompt[:160] + '...') if len(prompt) > 160 else prompt
                run_sql_batch(
                    conn,
                    (
                        "insert into UDX_POC.DATA_DISCOVERY_APP.AI_ACTIVITY(operation, model, tokens, est_cost, context_snippet) values ("
                        f"{sql_quote('CORTEX_COMPLETE')}, {sql_quote(model)}, {sql_quote(tokens)}, {sql_quote(est_cost)}, {sql_quote(ctx_snip)})"
                    ),
                )
            except Exception:
                pass
            return resp
    except Exception:
        return None
    return None


def detect_pii_rules(column_name: str, comment: Optional[str], samples: List[str]) -> Optional[Dict[str, Any]]:
    name = column_name.lower()
    comment_l = (comment or "").lower()
    sample_strs = [str(s) for s in samples if s is not None]

    def match_any(regexes: List[str]) -> bool:
        return any(re.match(rx, s) for rx in regexes for s in sample_strs)

    patterns = [
        {
            "type": "FINANCIAL_CC",
            "conf": 0.9,
            "col": ["credit_card", "card_pan", "cc", "cardnumber", "card_number"],
            "rx": [r"^\d{16}$", r"^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$"],
        },
        {
            "type": "PII_SSN",
            "conf": 0.9,
            "col": ["ssn", "social_security"],
            "rx": [r"^\d{3}-\d{2}-\d{4}$", r"^\d{9}$"],
        },
        {
            "type": "PII_EMAIL",
            "conf": 0.9,
            "col": ["email", "e_mail", "contact_email", "corp_email", "personal_email"],
            "rx": [r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"],
        },
        {
            "type": "PII_PHONE",
            "conf": 0.8,
            "col": ["phone", "contact_phone"],
            "rx": [r"^\+?\d{1,3}?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}$"],
        },
        {
            "type": "PII_PERSON_NAME",
            "conf": 0.6,
            "col": ["full_name", "first_name", "last_name", "name"],
            "rx": [],
        },
        {
            "type": "PII_DOB",
            "conf": 0.7,
            "col": ["dob", "date_of_birth", "birthdate"],
            "rx": [r"^\d{4}-\d{2}-\d{2}$"],
        },
    ]

    # Column-name based first
    for p in patterns:
        if any(c in name for c in p["col"]):
            if p["rx"] and sample_strs and match_any(p["rx"]):
                return {"sensitive_type": p["type"], "confidence": p["conf"], "source": "PATTERN_MATCH"}
            return {"sensitive_type": p["type"], "confidence": max(0.5, p["conf"] - 0.2), "source": "COLUMN_NAME"}

    # Sample-only pattern match
    for p in patterns:
        if p["rx"] and sample_strs and match_any(p["rx"]):
            return {"sensitive_type": p["type"], "confidence": max(0.6, p["conf"] - 0.1), "source": "SAMPLE_DATA"}

    # Comment hints
    hints = {
        "pci": ("FINANCIAL_CC", 0.6),
        "ssn": ("PII_SSN", 0.6),
        "email": ("PII_EMAIL", 0.6),
        "phone": ("PII_PHONE", 0.6),
        "name": ("PII_PERSON_NAME", 0.55),
        "birth": ("PII_DOB", 0.6),
    }
    for k, (t, c) in hints.items():
        if k in comment_l:
            return {"sensitive_type": t, "confidence": c, "source": "COMMENT"}

    return None


def domain_from_path(database: str, schema: str, table: str) -> str:
    s = schema.upper()
    if "HR" in s or "TEAM" in s:
        return "TEAM_MEMBER"
    if "VENDOR" in s:
        return "VENDOR"
    if "PAY" in s or "FIN" in s:
        return "PAYMENTS"
    if "OPS" in s:
        return "OPERATIONS"
    return "CONSUMER"


def tier_from_type_and_domain(sensitive_type: str, domain: str, co_occurs_sso_and_name: bool) -> str:
    if sensitive_type == "FINANCIAL_CC":
        return "TIER_4"
    if co_occurs_sso_and_name and domain == "TEAM_MEMBER":
        return "TIER_4"
    if sensitive_type in ("PII_SSN",):
        return "TIER_4"
    if sensitive_type in ("PII_EMAIL", "PII_PHONE", "PII_DOB", "PII_PERSON_NAME"):
        # Consumer email often Tier 4 per Nick; team-member variants typically lower unless combined
        return "TIER_3" if domain == "CONSUMER" else "TIER_2"
    return "TIER_2"


def masking_template(sensitive_type: str, domain: str, tier: str) -> str:
    roles_by_domain = {
        "CONSUMER": ["MARKETING_OPS_ROLE"],
        "TEAM_MEMBER": ["HR_OPS_ROLE"],
        "VENDOR": ["VENDOR_MGMT_ROLE"],
        "OPERATIONS": ["PARK_OPS_ROLE"],
        "PAYMENTS": ["PCI_SEC_ROLE"],
    }
    roles_sql = "'" + "', '".join(roles_by_domain.get(domain, ["DATA_OWNER_ROLE"])) + "'"
    if sensitive_type == "FINANCIAL_CC":
        return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE '************' || SUBSTR(VAL, 13, 4) END"
    if sensitive_type == "PII_SSN":
        return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE '***-**-' || SUBSTR(VAL, 8, 4) END"
    if sensitive_type == "PII_EMAIL":
        return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE REGEXP_REPLACE(VAL, '^([^@]+)@(.+)$', '****@\\2') END"
    if sensitive_type == "PII_PHONE":
        return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE '***-***-' || RIGHT(VAL, 4) END"
    if sensitive_type == "PII_PERSON_NAME":
        return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE '****' END"
    if sensitive_type == "PII_DOB":
        return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE '1900-01-01' END"
    return f"CASE WHEN CURRENT_ROLE() IN ({roles_sql}) THEN VAL ELSE '****' END"


def ensure_staging(conn) -> None:
    run_sql_batch(
        conn,
        """
        create database if not exists UDX_POC;
        create schema if not exists UDX_POC.DATA_DISCOVERY_APP;
        create table if not exists UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS (
          id number autoincrement,
          database_name string,
          schema_name string,
          table_name string,
          column_name string,
          sensitive_type string,
          confidence float,
          detection_source string,
          domain string,
          tier string,
          proposed_policy_sql string,
          status string default 'PENDING',
          reviewer string,
          reviewer_notes string,
          created_at timestamp_ltz default current_timestamp(),
          updated_at timestamp_ltz
        );
        alter table UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS add column if not exists rationale string;
        alter table UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS add column if not exists ai_reasoning string;
        alter table UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS add column if not exists sample_example string;
        create table if not exists UDX_POC.DATA_DISCOVERY_APP.AI_ACTIVITY (
          id number autoincrement,
          ts timestamp_ltz default current_timestamp(),
          operation string,
          model string,
          tokens number,
          est_cost float,
          context_snippet string
        );
        """,
    )


def insert_recommendation(conn, rec: Dict[str, Any]) -> None:
    sql = (
        "insert into UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS("
        "database_name, schema_name, table_name, column_name, "
        "sensitive_type, confidence, detection_source, domain, tier, proposed_policy_sql, rationale, ai_reasoning, sample_example) values ("
        f"{sql_quote(rec['database'])}, {sql_quote(rec['schema'])}, {sql_quote(rec['table'])}, {sql_quote(rec['column'])}, "
        f"{sql_quote(rec['sensitive_type'])}, {sql_quote(rec['confidence'])}, {sql_quote(rec['detection_source'])}, "
        f"{sql_quote(rec['domain'])}, {sql_quote(rec['tier'])}, {sql_quote(rec['policy_sql'])}, "
        f"{sql_quote(rec.get('rationale'))}, {sql_quote(rec.get('ai_reasoning'))}, {sql_quote(rec.get('sample_example'))})"
    )
    # Use non-SELECT executor to avoid NotSupportedError from fetch_pandas_all
    run_sql_batch(conn, sql)


def recommendations_df(conn, filters: Dict[str, Any]) -> pd.DataFrame:
    base = "select * from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS where 1=1"
    if filters.get("status"):
        base += f" and status = {sql_quote(filters['status'])}"
    if filters.get("domain"):
        base += f" and domain = {sql_quote(filters['domain'])}"
    if filters.get("min_conf") is not None:
        base += f" and confidence >= {sql_quote(float(filters['min_conf']))}"
    return conn.query(base)


def apply_bulk_update(conn, ids: List[int], status: str, reviewer: str, notes: str) -> None:
    if not ids:
        return
    id_list = ",".join(str(i) for i in ids)
    sql = (
        "update UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS set "
        f"status = {sql_quote(status)}, "
        f"reviewer = {sql_quote(reviewer)}, "
        f"reviewer_notes = {sql_quote(notes)}, "
        "updated_at = current_timestamp() "
        f"where id in ({id_list})"
    )
    run_sql_batch(conn, sql)


def generate_ddl_for_ids(conn, ids: List[int], policy_db: str, policy_schema: str) -> str:
    if not ids:
        return "-- No approved recommendations selected"
    id_list = ",".join(str(i) for i in ids)
    df = conn.query(
        f"""
        select database_name, schema_name, table_name, column_name, sensitive_type, proposed_policy_sql
        from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS where id in ({id_list})
        and status = 'APPROVED'
        order by database_name, schema_name, table_name
        """
    )
    statements: List[str] = [
        "-- Generated Dynamic Data Masking Policies",
        f"-- Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # group by sensitive_type for policy reuse
    policy_names: Dict[str, str] = {}
    for _, row in df.iterrows():
        stype = row["SENSITIVE_TYPE"]
        if stype not in policy_names:
            policy_name = f"MASK_{stype}_{int(time.time())}"
            policy_names[stype] = policy_name
            statements += [
                f"create or replace masking policy {policy_db}.{policy_schema}.{policy_name} as (val string) returns string ->",
                f"  {row['PROPOSED_POLICY_SQL']};",
                "",
            ]

    for _, row in df.iterrows():
        policy_name = policy_names[row["SENSITIVE_TYPE"]]
        statements += [
            f"alter table {row['DATABASE_NAME']}.{row['SCHEMA_NAME']}.{row['TABLE_NAME']}",
            f"  modify column {row['COLUMN_NAME']} set masking policy {policy_db}.{policy_schema}.{policy_name};",
            "",
        ]

    return "\n".join(statements)


def section_setup_and_sample_data(conn):
    st.subheader("Setup & UDX Sample Data")
    st.write("Create UDX_POC database, schemas, tags, and insert synthetic data for demo.")
    if st.button("Create UDX sample data (idempotent)"):
        with st.spinner("Creating sample data..."):
            run_sql_batch(
                conn,
                """
                create database if not exists UDX_POC;
                create schema if not exists UDX_POC.RAW_CONSUMER;
                create schema if not exists UDX_POC.HR_TEAM_MEMBER;
                create schema if not exists UDX_POC.VENDOR_MGMT;
                create schema if not exists UDX_POC.OPS_GUEST_EXPERIENCE;
                create schema if not exists UDX_POC.PAYMENTS;

                create tag if not exists UDX_POC.PUBLIC.GEO_PARK;
                create tag if not exists UDX_POC.PUBLIC.DATA_DOMAIN;
                create tag if not exists UDX_POC.PUBLIC.SENSITIVITY_TIER;

                create or replace table UDX_POC.RAW_CONSUMER.CUSTOMERS (
                  customer_id number,
                  email string,
                  first_name string,
                  last_name string,
                  dob date,
                  phone string,
                  address string,
                  city string,
                  state string,
                  postal_code string,
                  country string
                );

                create or replace table UDX_POC.HR_TEAM_MEMBER.EMPLOYEES (
                  emp_id number,
                  sso_id string,
                  corp_email string,
                  personal_email string,
                  full_name string,
                  dob date,
                  phone string,
                  address string,
                  status string
                );

                create or replace table UDX_POC.VENDOR_MGMT.VENDORS (
                  vendor_id number,
                  name string,
                  contact_email string,
                  contact_phone string,
                  address string
                );

                create or replace table UDX_POC.OPS_GUEST_EXPERIENCE.GUEST_INTERACTIONS (
                  event_id number,
                  customer_email string,
                  park string,
                  event_type string,
                  details string,
                  ts timestamp_ntz
                );

                create or replace table UDX_POC.PAYMENTS.TRANSACTIONS (
                  txn_id number,
                  customer_email string,
                  card_pan string,
                  amount number(10,2),
                  currency string,
                  txn_ts timestamp_ntz
                );

                alter table UDX_POC.PAYMENTS.TRANSACTIONS set tag UDX_POC.PUBLIC.DATA_DOMAIN = 'PAYMENTS';
                alter table UDX_POC.RAW_CONSUMER.CUSTOMERS set tag UDX_POC.PUBLIC.DATA_DOMAIN = 'CONSUMER';
                alter table UDX_POC.HR_TEAM_MEMBER.EMPLOYEES set tag UDX_POC.PUBLIC.DATA_DOMAIN = 'TEAM_MEMBER';

                insert into UDX_POC.RAW_CONSUMER.CUSTOMERS values
                  (1, 'sarah.james@example.com','Sarah','James','1990-05-10','407-555-1212','123 Main St','Orlando','FL','32801','USA'),
                  (2, 'taro.yamada@example.jp','Taro','Yamada','1985-11-20','080-5555-2222','1-2-3 Shibuya','Tokyo',null,'150-0002','JPN');

                insert into UDX_POC.HR_TEAM_MEMBER.EMPLOYEES values
                  (1001, 'udx_sjames','sarah.james@universal.com','sarah.james@example.com','Sarah James','1990-05-10','407-555-1313','123 Main St','ACTIVE'),
                  (1002, 'udx_nyamada','naoki.yamada@universal.com','taro.yamada@example.jp','Naoki Yamada','1984-03-15','321-555-4545','5 Park Ave','INACTIVE');

                insert into UDX_POC.VENDOR_MGMT.VENDORS values
                  (2001,'Epic Snacks Co','contact@epicsnacks.com','818-555-4444','42 Sunset Blvd'),
                  (2002,'Ride Repair LLC','support@riderepair.com','818-555-7777','10 Mechanic Way');

                insert into UDX_POC.OPS_GUEST_EXPERIENCE.GUEST_INTERACTIONS values
                  (5001,'sarah.james@example.com','ORLANDO','COMPLAINT','Express pass failed','2024-08-01 10:15:00'),
                  (5002,'taro.yamada@example.jp','JAPAN','REFUND','Merchandise return','2024-08-02 13:45:00');

                insert into UDX_POC.PAYMENTS.TRANSACTIONS values
                  (9001,'sarah.james@example.com','4242424242424242',129.99,'USD','2024-08-01 10:10:00'),
                  (9002,'taro.yamada@example.jp','5555555555554444',89.50,'JPY','2024-08-02 13:40:00');
                """,
            )
            st.success("UDX sample data created (or already existed).")


def section_scan_and_classify(conn):
    st.subheader("Scan & Classify")
    col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
    with col1:
        databases = get_databases(conn)
        db = st.selectbox("Database", options=databases, index=(databases.index("UDX_POC") if "UDX_POC" in databases else 0) if databases else 0)
    with col2:
        schemas = get_schemas(conn, db) if db else []
        schema = st.selectbox("Schema", options=schemas)
    with col3:
        tables = get_tables(conn, db, schema) if db and schema else []
        selected_tables = st.multiselect("Tables", options=tables, default=tables[:2])
    with col4:
        sample_size = st.slider("Sample size", 5, 200, 30, 5)

    st.markdown("---")
    st.caption("Detection settings")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ai_mode = st.toggle("Enable Cortex AI", value=False, help="When enabled, supplement rules with a Cortex prompt for semantic hints.")
    with c2:
        auto_threshold = st.slider("Auto-apply threshold", 0.50, 1.00, 0.95, 0.01)
    with c3:
        review_threshold = st.slider("Review min threshold", 0.40, 0.99, 0.60, 0.01)
    with c4:
        run_btn = st.button("Scan selected tables")

    ensure_staging(conn)

    if run_btn and db and schema and selected_tables:
        with st.spinner("Scanning tables and staging recommendations..."):
            total = 0
            staged = 0
            staged_preview: List[Dict[str, Any]] = []
            for tbl in selected_tables:
                cols = get_columns(conn, db, schema, tbl)
                colnames = cols["COLUMN_NAME"].tolist()
                co_occurs_sso_and_name = any("SSO" in c.upper() for c in colnames) and any("NAME" in c.upper() for c in colnames)
                for _, c in cols.iterrows():
                    colname = c["COLUMN_NAME"]
                    samples = get_sample_values(conn, db, schema, tbl, colname, sample_size)
                    base = detect_pii_rules(colname, c.get("COMMENT"), samples)
                    det = base
                    ai_reasoning = None
                    if ai_mode:
                        ctx = f"Column {db}.{schema}.{tbl}.{colname} samples: {samples[:5]}"
                        ai_resp = cortex_classify(conn, f"You are a data classifier. Identify if this is PII/PCI column and type. {ctx}")
                        if ai_resp and base is None:
                            # Simplistic mapping hint
                            hint = ai_resp.lower()
                            if "credit" in hint or "card" in hint:
                                det = {"sensitive_type": "FINANCIAL_CC", "confidence": 0.7, "source": "CORTEX"}
                            elif "email" in hint:
                                det = {"sensitive_type": "PII_EMAIL", "confidence": 0.65, "source": "CORTEX"}
                            elif "phone" in hint:
                                det = {"sensitive_type": "PII_PHONE", "confidence": 0.6, "source": "CORTEX"}
                            elif "name" in hint:
                                det = {"sensitive_type": "PII_PERSON_NAME", "confidence": 0.55, "source": "CORTEX"}
                            ai_reasoning = ai_resp[:600]

                    if det:
                        domain = domain_from_path(db, schema, tbl)
                        tier = tier_from_type_and_domain(det["sensitive_type"], domain, co_occurs_sso_and_name)
                        policy_sql = masking_template(det["sensitive_type"], domain, tier)
                        confidence = float(det["confidence"])
                        # Build rationale text
                        rationale_parts = [f"source={det['source']}"]
                        if det["source"] == "PATTERN_MATCH":
                            example = samples[0] if samples else None
                            if example:
                                rationale_parts.append(f"matched sample '{example}'")
                        if det["source"] == "COLUMN_NAME":
                            rationale_parts.append("column indicator")
                        rationale = ", ".join(rationale_parts)

                        # Stage recommendation with status based on thresholds
                        rec = {
                            "database": db,
                            "schema": schema,
                            "table": tbl,
                            "column": colname,
                            "sensitive_type": det["sensitive_type"],
                            "confidence": confidence,
                            "detection_source": det["source"],
                            "domain": domain,
                            "tier": tier,
                            "policy_sql": policy_sql,
                            "rationale": rationale,
                            "ai_reasoning": ai_reasoning,
                            "sample_example": (samples[0] if samples else None),
                        }
                        insert_recommendation(conn, rec)
                        staged += 1
                        if len(staged_preview) < 25:
                            preview_copy = rec.copy()
                            if preview_copy.get("ai_reasoning"):
                                preview_copy["ai_reasoning"] = preview_copy["ai_reasoning"][:120] + "..."
                            staged_preview.append(preview_copy)
                    total += 1
            st.success(f"Completed. Analyzed {total} columns. Staged {staged} recommendations.")
            if staged_preview:
                st.caption("Recent staged recommendations (sample)")
                st.dataframe(pd.DataFrame(staged_preview))

    # Always show latest few from the table for user feedback
    try:
        latest = conn.query(
            """
            select database_name, schema_name, table_name, column_name, sensitive_type, confidence,
                   detection_source, domain, tier, sample_example, left(rationale,120) as rationale_snippet,
                   left(ai_reasoning, 120) as ai_snippet, created_at
            from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
            order by created_at desc
            limit 20
            """
        )
        if not latest.empty:
            st.markdown("---")
            st.caption("Latest 20 recommendations (from staging table)")
            st.dataframe(latest)
    except Exception:
        pass


def section_review_and_generate(conn):
    st.subheader("Review & Generate Policies")
    st.info("Use filters to find staged recommendations. Tip: set Min confidence to 0.4 to include column-name-only matches (e.g., name fields).")
    # Quick status metrics to orient the user
    try:
        kpi = conn.query(
            """
            select status, count(*) cnt from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS group by 1
            """
        )
        total_cnt = conn.query("select count(*) as c from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS")
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total staged", int(total_cnt.loc[0, 'C']) if not total_cnt.empty else 0)
        for i, row in (kpi.iterrows() if not kpi.empty else []):
            with cols[(i % 3) + 1]:
                st.metric(f"{row['STATUS']}", int(row['CNT']))
    except Exception:
        pass
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        status = st.selectbox("Status filter", options=["PENDING", "APPROVED", "REJECTED"], index=0)
    with c2:
        domain = st.selectbox("Domain filter", options=["", "CONSUMER", "TEAM_MEMBER", "VENDOR", "OPERATIONS", "PAYMENTS"], index=0)
    with c3:
        min_conf = st.slider("Min confidence", 0.0, 1.0, 0.4, 0.01)
    with c4:
        _ = st.empty()

    df = recommendations_df(conn, {"status": status, "domain": domain or None, "min_conf": min_conf})
    if df.empty:
        st.warning("No recommendations match the current filters. Showing the latest 20 unfiltered results below.")
        try:
            fallback = conn.query(
                """
                select * from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
                order by created_at desc
                limit 20
                """
            )
            if not fallback.empty:
                st.dataframe(fallback)
            else:
                st.info("No staged recommendations yet. Go to 'Scan & Classify' to stage findings.")
        except Exception:
            st.info("No staged recommendations yet. Go to 'Scan & Classify' to stage findings.")
        return

    st.dataframe(df)
    ids = df["ID"].tolist()
    chosen = st.multiselect("Select IDs to update/generate", options=ids, default=ids[: min(10, len(ids))])
    st.caption("Use the checkboxes above to pick rows. Set status to APPROVED to include in generated DDL.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        reviewer = st.text_input("Reviewer", value="demo_user")
    with col_b:
        notes = st.text_input("Notes", value="Bulk action from demo")
    with col_c:
        act_col = st.selectbox("Set status", options=["APPROVED", "REJECTED", "PENDING"], index=0)

    if st.button("Apply bulk status") and chosen:
        apply_bulk_update(conn, chosen, act_col, reviewer, notes)
        st.success("Updated statuses.")
        st.caption("Re-run generation below or adjust filters to see updated results.")

    st.markdown("---")
    st.caption("Generate DDL for approved items")
    policy_db = st.text_input("Policy DB", value="UDX_POC")
    policy_schema = st.text_input("Policy Schema", value="RAW_CONSUMER")
    if st.button("Generate DDL from approved"):
        ddl = generate_ddl_for_ids(conn, chosen, policy_db, policy_schema)
        st.code(ddl, language="sql")


def section_manager_dashboard(conn):
    st.subheader("Manager Dashboard")
    c1, c2, c3 = st.columns(3)
    # Basic account usage stats (last 24h)
    q1 = conn.query(
        """
        select coalesce(sum(credits_used),0) as credits_24h
        from snowflake.account_usage.warehouse_metering_history
        where start_time >= dateadd('hour', -24, current_timestamp())
        """
    )
    q2 = conn.query(
        """
        select count(*) as queries_24h
        from snowflake.account_usage.query_history
        where start_time >= dateadd('hour', -24, current_timestamp())
        """
    )
    q3 = conn.query(
        """
        select status, count(*) cnt
        from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
        group by 1
        """
    )
    with c1:
        st.metric("Warehouse credits (24h)", f"{float(q1.loc[0, 'CREDITS_24H']):.2f}")
    with c2:
        st.metric("Queries (24h)", int(q2.loc[0, "QUERIES_24H"]))
    with c3:
        st.dataframe(q3)

    st.markdown("---")
    # Sensitive type distribution
    dist = conn.query(
        """
        select sensitive_type, count(*) cnt
        from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
        group by 1 order by 2 desc
        """
    )
    st.bar_chart(dist.set_index("SENSITIVE_TYPE"))

    # Show a small sample of Cortex reasoning, if any
    try:
        ai_samples = conn.query(
            """
            select database_name||'.'||schema_name||'.'||table_name||'.'||column_name as col,
                   left(ai_reasoning, 180) as ai_reasoning,
                   created_at
            from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
            where ai_reasoning is not null
            order by created_at desc
            limit 5
            """
        )
        if not ai_samples.empty:
            st.caption("Recent Cortex reasoning (sample)")
            st.table(ai_samples)
    except Exception:
        pass


def section_usage_dashboard(conn):
    st.subheader("Usage Dashboard")
    # Domain distribution and confidence bands
    dom = conn.query(
        """
        select domain, count(*) cnt from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS group by 1 order by 2 desc
        """
    )
    st.write("By domain")
    st.bar_chart(dom.set_index("DOMAIN"))

    conf = conn.query(
        """
        select
          case
            when confidence >= 0.95 then '>=0.95'
            when confidence >= 0.80 then '0.80-0.94'
            when confidence >= 0.60 then '0.60-0.79'
            else '<0.60'
          end as band,
          count(*) cnt
        from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
        group by 1 order by 1
        """
    )
    st.write("Confidence bands")
    st.bar_chart(conf.set_index("BAND"))

    # Recent items table
    recent = conn.query(
        """
        select created_at, status, domain, sensitive_type, confidence,
               database_name, schema_name, table_name, column_name,
               left(rationale, 120) as rationale_snippet
        from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
        order by created_at desc
        limit 50
        """
    )
    st.markdown("---")
    st.caption("Recent 50 staged items")
    st.dataframe(recent)


def main():
    st.title("UDX Sensitive Data POC (Streamlit in Snowflake)")
    st.caption("Scan schemas/tables, detect sensitive data with rules + optional Cortex, stage recommendations, review and generate masking policies, and monitor usage.")

    conn = st.connection("snowflake")

    tabs = st.tabs([
        "Setup", "Scan & Classify", "Review & Generate", "Manager Dashboard", "Usage Dashboard",
    ])

    with tabs[0]:
        section_setup_and_sample_data(conn)
    with tabs[1]:
        section_scan_and_classify(conn)
    with tabs[2]:
        section_review_and_generate(conn)
    with tabs[3]:
        section_manager_dashboard(conn)
    with tabs[4]:
        section_usage_dashboard(conn)


if __name__ == "__main__":
    main()


