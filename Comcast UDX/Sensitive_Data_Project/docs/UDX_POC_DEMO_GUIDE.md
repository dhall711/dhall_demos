### UDX POC Demo Guide (Streamlit in Snowflake)

#### What this POC shows
- Schema/table scanning in Snowflake
- Rules-based sensitive data detection with optional Cortex AI assist
- Domain- and tier-aware recommendations staged for review
- Bulk approve/reject and DDL generation for masking policies
- Manager and usage dashboards (credits, counts, distributions)
- UDX-specific sample datasets and tags

#### Launch
1. Ensure Snowflake connection is configured in `.streamlit/secrets.toml` (when running outside Snowsight).
2. In Snowsight, open Streamlit and point to `app/udx_poc.py`.

#### Steps to demo
1) Setup tab
   - Click "Create UDX sample data (idempotent)" to create database `UDX_POC` with schemas:
     - `RAW_CONSUMER`, `HR_TEAM_MEMBER`, `VENDOR_MGMT`, `OPS_GUEST_EXPERIENCE`, `PAYMENTS`
   - Populates example data and tags (e.g., `DATA_DOMAIN`).

2) Scan & Classify
   - Pick `UDX_POC` and a schema (e.g., `RAW_CONSUMER`, `PAYMENTS`).
   - Select a few tables (defaults to first two) and a sample size.
   - Optionally enable "Enable Cortex AI" for semantic hints (if allowed).
   - Configure thresholds: Auto-apply (not applied directly in POC; staged), Review min.
   - Run "Scan selected tables" to stage recommendations in `DATA_DISCOVERY_APP.RECOMMENDATIONS`.

3) Review & Generate
   - Filter by Status/Domain/Min confidence; inspect the staged rows.
   - Select IDs; set Status (APPROVED/REJECTED) and apply bulk.
   - Generate DDL for approved items to create/apply policies in the chosen DB/Schema.

4) Manager Dashboard
   - Shows last-24h warehouse credits and queries, and recommendation status counts.

5) Usage Dashboard
   - Domain distribution and confidence-band distribution of recommendations.

#### Notes
- This is a POC: no production hardening, minimal error handling.
- Cortex AI is optional and gated by the toggle; otherwise the app runs rules-only.
- Policies generated are simple CASE expressions and reuse per sensitive type.
- Composite sensitivity is illustrated by elevating tier when SSO and Name co-exist in HR.


