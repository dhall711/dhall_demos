-- =============================================================
-- POSTGRES pg_lake SETUP (run in Snowsight Postgres worksheet)
-- Connect to: CERT_OLTP_DB instance via Snowsight
-- =============================================================

-- Step 1: Enable pg_lake extension
CREATE EXTENSION IF NOT EXISTS pg_lake CASCADE;

-- Step 2: Create Iceberg table that mirrors cert event data
-- This enables Snowflake to read this table via catalog integration
CREATE TABLE IF NOT EXISTS cert_events_iceberg (
    event_id TEXT PRIMARY KEY,
    cert_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    device_type TEXT,
    region TEXT,
    partner_name TEXT,
    key_algorithm TEXT,
    key_size INT,
    is_self_signed BOOLEAN DEFAULT FALSE,
    validity_end TIMESTAMP,
    signature_algorithm TEXT,
    compliance_status TEXT,
    created_at TIMESTAMP DEFAULT NOW()
) USING iceberg;

-- Step 3: Seed with recent cert events from existing OLTP tables
INSERT INTO cert_events_iceberg (event_id, cert_id, event_type, device_type, region, partner_name, key_algorithm, key_size, is_self_signed, validity_end, signature_algorithm, compliance_status, created_at)
SELECT
    gen_random_uuid()::TEXT,
    serial_number,
    CASE WHEN revoked THEN 'REVOCATION' ELSE 'ISSUANCE' END,
    device_type,
    region,
    issuer_org,
    key_algorithm,
    key_size,
    is_self_signed,
    validity_end,
    signature_algorithm,
    CASE
        WHEN is_self_signed THEN 'NON_COMPLIANT'
        WHEN key_algorithm = 'RSA' AND key_size < 2048 THEN 'NON_COMPLIANT'
        WHEN signature_algorithm LIKE 'sha1%' THEN 'NON_COMPLIANT'
        ELSE 'COMPLIANT'
    END,
    created_at
FROM active_certificates
LIMIT 100000;

-- Step 4: Verify
SELECT COUNT(*) FROM cert_events_iceberg;
