WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_SF_CASES') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    case_id,
    account_id,
    contact_id,
    subject,
    description,
    status,
    priority,
    case_type,
    channel,
    created_date,
    resolved_date,
    CASE WHEN resolved_date IS NOT NULL THEN DATEDIFF('hour', created_date, resolved_date) ELSE NULL END AS resolution_time_hours,
    CASE
        WHEN status IN ('Resolved', 'Closed') AND resolution_time_hours <= 24 THEN 'Within SLA'
        WHEN status IN ('Resolved', 'Closed') AND resolution_time_hours <= 72 THEN 'At Risk'
        WHEN status IN ('Resolved', 'Closed') THEN 'Breached'
        WHEN status NOT IN ('Resolved', 'Closed') AND DATEDIFF('hour', created_date, CURRENT_TIMESTAMP()) > 72 THEN 'Breached'
        WHEN status NOT IN ('Resolved', 'Closed') AND DATEDIFF('hour', created_date, CURRENT_TIMESTAMP()) > 24 THEN 'At Risk'
        ELSE 'Within SLA'
    END AS sla_status,
    DATEDIFF('day', created_date, CURRENT_DATE()) AS case_age_days,
    CASE WHEN status = 'Escalated' OR priority = 'Critical' THEN TRUE ELSE FALSE END AS escalation_flag,
    _fivetran_synced
FROM deduped
