import time
import re
from typing import List, Dict, Any, Optional

import pandas as pd
import streamlit as st


st.set_page_config(page_title="UDX Sensitive Data – Guided Workflow", layout="wide")


# --------- Utilities ---------
def sql_quote(val: Any) -> str:
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).replace("'", "''")
    return f"'{s}'"


def run_sql_batch(conn, sql: str):
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        try:
            conn.query(stmt)
        except Exception as e:
            if e.__class__.__name__ == 'NotSupportedError' or 'NotSupportedError' in str(e):
                continue
            raise


@st.cache_data(ttl=300)
def get_databases(_conn) -> List[str]:
    try:
        df = _conn.query("select database_name from snowflake.account_usage.databases order by 1")
        return df["DATABASE_NAME"].tolist()
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_schemas(_conn, database: str) -> List[str]:
    try:
        df = _conn.query(f"select schema_name from {database}.information_schema.schemata order by 1")
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


def get_sample_values(conn, database: str, schema: str, table: str, column: str, sample_size: int) -> List[str]:
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
          updated_at timestamp_ltz,
          rationale string,
          ai_reasoning string,
          sample_example string
        );
        """,
    )


# --------- Minimal detection and helpers (rules-only for demo) ---------
def detect_pii_rules(column_name: str, comment: Optional[str], samples: List[str]) -> Optional[Dict[str, Any]]:
    name = column_name.lower()
    comment_l = (comment or "").lower()
    sample_strs = [str(s) for s in samples if s is not None]

    def match_any(regexes: List[str]) -> bool:
        return any(re.match(rx, s) for rx in regexes for s in sample_strs)

    patterns = [
        {"type": "FINANCIAL_CC", "conf": 0.9, "col": ["card_pan", "credit_card", "card_number"], "rx": [r"^\d{16}$"]},
        {"type": "PII_SSN", "conf": 0.9, "col": ["ssn", "social_security"], "rx": [r"^\d{3}-\d{2}-\d{4}$", r"^\d{9}$"]},
        {"type": "PII_EMAIL", "conf": 0.9, "col": ["email", "contact_email"], "rx": [r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"]},
        {"type": "PII_PHONE", "conf": 0.8, "col": ["phone", "contact_phone"], "rx": []},
        {"type": "PII_PERSON_NAME", "conf": 0.6, "col": ["full_name", "first_name", "last_name", "name"], "rx": []},
        {"type": "PII_DOB", "conf": 0.7, "col": ["dob", "date_of_birth"], "rx": [r"^\d{4}-\d{2}-\d{2}$"]},
    ]

    for p in patterns:
        if any(c in name for c in p["col"]):
            if p["rx"] and sample_strs and match_any(p["rx"]):
                return {"sensitive_type": p["type"], "confidence": p["conf"], "source": "PATTERN_MATCH"}
            return {"sensitive_type": p["type"], "confidence": max(0.5, p["conf"] - 0.2), "source": "COLUMN_NAME"}
    for p in patterns:
        if p["rx"] and sample_strs and match_any(p["rx"]):
            return {"sensitive_type": p["type"], "confidence": max(0.6, p["conf"] - 0.1), "source": "SAMPLE_DATA"}
    hints = {"pci": ("FINANCIAL_CC", 0.6), "ssn": ("PII_SSN", 0.6), "email": ("PII_EMAIL", 0.6)}
    for k, (t, c) in hints.items():
        if k in comment_l:
            return {"sensitive_type": t, "confidence": c, "source": "COMMENT"}
    return None


def domain_from_path(schema: str) -> str:
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


def tier_from_type_and_domain(sensitive_type: str, domain: str, sso_and_name: bool) -> str:
    if sensitive_type == "FINANCIAL_CC":
        return "TIER_4"
    if sso_and_name and domain == "TEAM_MEMBER":
        return "TIER_4"
    if sensitive_type in ("PII_SSN",):
        return "TIER_4"
    if sensitive_type in ("PII_EMAIL", "PII_PHONE", "PII_DOB", "PII_PERSON_NAME"):
        return "TIER_3" if domain == "CONSUMER" else "TIER_2"
    return "TIER_2"


def ensure_policy_name(stype: str) -> str:
    return f"MASK_{stype}_{int(time.time())}"


# --------- Persistence APIs ---------
def insert_recommendation(conn, rec: Dict[str, Any]) -> None:
    sql = (
        "insert into UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS("
        "database_name, schema_name, table_name, column_name, "
        "sensitive_type, confidence, detection_source, domain, tier, proposed_policy_sql, rationale, sample_example) values ("
        f"{sql_quote(rec['database'])}, {sql_quote(rec['schema'])}, {sql_quote(rec['table'])}, {sql_quote(rec['column'])}, "
        f"{sql_quote(rec['sensitive_type'])}, {sql_quote(rec['confidence'])}, {sql_quote(rec['detection_source'])}, "
        f"{sql_quote(rec['domain'])}, {sql_quote(rec['tier'])}, {sql_quote(rec['policy_sql'])}, "
        f"{sql_quote(rec.get('rationale'))}, {sql_quote(rec.get('sample_example'))})"
    )
    run_sql_batch(conn, sql)


def fetch_staged(conn, status: Optional[str] = None) -> pd.DataFrame:
    q = "select * from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS"
    if status:
        q += f" where status = {sql_quote(status)}"
    q += " order by created_at desc"
    return conn.query(q)


def update_status(conn, ids: List[int], status: str, reviewer: str, notes: str):
    if not ids:
        return
    id_list = ",".join(str(i) for i in ids)
    sql = (
        "update UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS set "
        f"status = {sql_quote(status)}, reviewer = {sql_quote(reviewer)}, reviewer_notes = {sql_quote(notes)}, updated_at = current_timestamp() "
        f"where id in ({id_list})"
    )
    run_sql_batch(conn, sql)


def generate_policy_preview(conn, ids: List[int], policy_db: str, policy_schema: str) -> str:
    if not ids:
        return "-- No items selected"
    id_list = ",".join(str(i) for i in ids)
    df = conn.query(
        f"""
        select database_name, schema_name, table_name, column_name, sensitive_type, proposed_policy_sql
        from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS
        where id in ({id_list}) and status = 'APPROVED'
        order by database_name, schema_name, table_name
        """
    )
    if df.empty:
        return "-- No APPROVED items selected"
    statements: List[str] = [
        "-- Masking Policies (Preview)", f"-- Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}", "",
    ]
    policy_names: Dict[str, str] = {}
    for _, row in df.iterrows():
        stype = row["SENSITIVE_TYPE"]
        if stype not in policy_names:
            policy_names[stype] = ensure_policy_name(stype)
            statements += [
                f"create or replace masking policy {policy_db}.{policy_schema}.{policy_names[stype]} as (val string) returns string ->",
                f"  {row['PROPOSED_POLICY_SQL']};",
                "",
            ]
    for _, row in df.iterrows():
        statements += [
            f"alter table {row['DATABASE_NAME']}.{row['SCHEMA_NAME']}.{row['TABLE_NAME']}",
            f"  modify column {row['COLUMN_NAME']} set masking policy {policy_db}.{policy_schema}.{policy_names[row['SENSITIVE_TYPE']]};",
            "",
        ]
    return "\n".join(statements)


# --------- Wizard Steps ---------
def step_1_scope(conn):
    st.markdown("**Step 1: Select scope** – Choose the area to scan")
    databases = get_databases(conn)
    db = st.selectbox("Database", databases, index=(databases.index("UDX_POC") if "UDX_POC" in databases else 0) if databases else 0)
    schemas = get_schemas(conn, db) if db else []
    schema = st.selectbox("Schema", schemas)
    tables = get_tables(conn, db, schema) if db and schema else []
    selected = st.multiselect("Tables", tables, default=tables[:2])
    sample_size = st.slider("Sample size per column", 5, 200, 30, 5)
    st.session_state.scope = {"db": db, "schema": schema, "tables": selected, "sample_size": sample_size}
    st.caption("Click Next to scan. You can return to change scope later.")


def step_2_scan(conn):
    st.markdown("**Step 2: Scan** – Detect sensitive columns and stage findings")
    scope = st.session_state.get("scope") or {}
    if not scope.get("db") or not scope.get("schema") or not scope.get("tables"):
        st.info("Set your scope in Step 1, then return here.")
        return
    db, schema, tables, sample_size = scope["db"], scope["schema"], scope["tables"], scope["sample_size"]
    ensure_staging(conn)
    if st.button("Run scan for selected tables"):
        with st.spinner("Scanning and staging recommendations..."):
            staged = 0
            for tbl in tables:
                cols = get_columns(conn, db, schema, tbl)
                colnames = cols["COLUMN_NAME"].tolist()
                sso_and_name = any("SSO" in c.upper() for c in colnames) and any("NAME" in c.upper() for c in colnames)
                for _, c in cols.iterrows():
                    col = c["COLUMN_NAME"]
                    samples = get_sample_values(conn, db, schema, tbl, col, sample_size)
                    det = detect_pii_rules(col, c.get("COMMENT"), samples)
                    if not det:
                        continue
                    domain = domain_from_path(schema)
                    tier = tier_from_type_and_domain(det["sensitive_type"], domain, sso_and_name)
                    policy_sql = "CASE WHEN CURRENT_ROLE() IN ('DATA_OWNER_ROLE') THEN VAL ELSE '****' END"
                    rationale = f"source={det['source']}"
                    rec = {
                        "database": db,
                        "schema": schema,
                        "table": tbl,
                        "column": col,
                        "sensitive_type": det["sensitive_type"],
                        "confidence": float(det["confidence"]),
                        "detection_source": det["source"],
                        "domain": domain,
                        "tier": tier,
                        "policy_sql": policy_sql,
                        "rationale": rationale,
                        "sample_example": (samples[0] if samples else None),
                    }
                    insert_recommendation(conn, rec)
                    staged += 1
        st.success(f"Staged {staged} recommendations. Proceed to Step 3: Review.")

    latest = fetch_staged(conn)
    if not latest.empty:
        st.caption("Recent findings")
        show = latest[["ID", "DATABASE_NAME", "SCHEMA_NAME", "TABLE_NAME", "COLUMN_NAME", "SENSITIVE_TYPE", "CONFIDENCE", "RATIONALE", "STATUS"]].head(20)
        st.dataframe(show)


def step_3_review(conn):
    st.markdown("**Step 3: Review** – Triage findings and mark for approval")
    df = fetch_staged(conn, status="PENDING")
    if df.empty:
        st.info("No PENDING items. Run a scan or adjust statuses in Step 4.")
        return
    st.caption("Filter")
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        domain = st.selectbox("Domain", ["", "CONSUMER", "TEAM_MEMBER", "VENDOR", "OPERATIONS", "PAYMENTS"], index=0)
    with colf2:
        stype = st.selectbox("Type", ["", *sorted(df["SENSITIVE_TYPE"].unique().tolist())], index=0)
    with colf3:
        minc = st.slider("Min confidence", 0.0, 1.0, 0.6, 0.01)
    filt = df.copy()
    if domain:
        filt = filt[filt["DOMAIN"] == domain]
    if stype:
        filt = filt[filt["SENSITIVE_TYPE"] == stype]
    filt = filt[filt["CONFIDENCE"] >= minc]

    if filt.empty:
        st.warning("No items match the filters.")
        return

    st.write("Select the rows you want to APPROVE or REJECT. Use the preview to verify relevance.")
    st.dataframe(filt[["ID", "TABLE_NAME", "COLUMN_NAME", "SENSITIVE_TYPE", "CONFIDENCE", "RATIONALE", "SAMPLE_EXAMPLE"]].head(100))
    chosen = st.multiselect("IDs to update", options=filt["ID"].tolist())
    colr1, colr2, colr3 = st.columns(3)
    with colr1:
        reviewer = st.text_input("Reviewer", value="demo_user")
    with colr2:
        notes = st.text_input("Notes", value="Reviewed in wizard")
    with colr3:
        action = st.selectbox("Set status", ["APPROVED", "REJECTED"], index=0)
    if st.button("Apply to selected") and chosen:
        update_status(conn, chosen, action, reviewer, notes)
        st.success(f"Marked {len(chosen)} as {action}.")


def step_4_policies(conn):
    st.markdown("**Step 4: Policies** – Preview and apply masking policies")
    df = fetch_staged(conn, status="APPROVED")
    if df.empty:
        st.info("No APPROVED items. Approve some in Step 3.")
        return
    st.caption("Select approved items to include in the policy script.")
    st.dataframe(df[["ID", "TABLE_NAME", "COLUMN_NAME", "SENSITIVE_TYPE", "DOMAIN", "TIER", "CONFIDENCE"]].head(200))
    chosen = st.multiselect("IDs to include", options=df["ID"].tolist(), default=df["ID"].tolist()[:20])
    colp1, colp2 = st.columns(2)
    with colp1:
        policy_db = st.text_input("Policy DB", value="UDX_POC")
    with colp2:
        policy_schema = st.text_input("Policy Schema", value="RAW_CONSUMER")
    if st.button("Generate policy preview") and chosen:
        ddl = generate_policy_preview(conn, chosen, policy_db, policy_schema)
        st.code(ddl, language="sql")


def step_5_verify(conn):
    st.markdown("**Step 5: Verify & Monitor** – Check outcomes and usage")
    cols = st.columns(3)
    try:
        total = conn.query("select count(*) as c from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS")
        with cols[0]:
            st.metric("Total Findings", int(total.loc[0, 'C']))
    except Exception:
        pass
    try:
        status = conn.query("select status, count(*) cnt from UDX_POC.DATA_DISCOVERY_APP.RECOMMENDATIONS group by 1")
        with cols[1]:
            st.dataframe(status)
    except Exception:
        pass
    try:
        latest = fetch_staged(conn).head(30)
        with cols[2]:
            st.dataframe(latest[["CREATED_AT", "STATUS", "DOMAIN", "SENSITIVE_TYPE", "TABLE_NAME", "COLUMN_NAME"]])
    except Exception:
        pass
    st.caption("Return to earlier steps to iterate. This flow guides you from scope to scan, review, policies, and verification.")


def main():
    st.title("UDX Sensitive Data – Guided Workflow")
    st.caption("A step-by-step flow to identify sensitive data, triage findings, and build/apply masking policies.")

    conn = st.connection("snowflake")

    steps = ["1. Scope", "2. Scan", "3. Review", "4. Policies", "5. Verify"]
    step = st.sidebar.radio("Workflow", steps, index=0, help="Follow steps in order for best results")

    ensure_staging(conn)

    if step.startswith("1"):
        step_1_scope(conn)
    elif step.startswith("2"):
        step_2_scan(conn)
    elif step.startswith("3"):
        step_3_review(conn)
    elif step.startswith("4"):
        step_4_policies(conn)
    else:
        step_5_verify(conn)


if __name__ == "__main__":
    main()


