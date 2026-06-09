WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_SF_CONTACTS') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY contact_id ORDER BY _fivetran_synced DESC) = 1
),
last_touch AS (
    SELECT contact_id, MAX(note_date) AS last_touch_date
    FROM {{ source('bronze', 'RAW_FIN_ADVISOR_NOTES') }}
    GROUP BY contact_id
)
SELECT
    d.contact_id,
    d.account_id,
    d.first_name,
    d.last_name,
    d.email,
    d.phone,
    d.title,
    d.department,
    d.contact_role,
    d.preferred_channel,
    COALESCE(DATEDIFF('day', lt.last_touch_date, CURRENT_DATE()), 999) AS days_since_last_touch,
    CASE
        WHEN days_since_last_touch <= 30 THEN 'High'
        WHEN days_since_last_touch <= 90 THEN 'Medium'
        WHEN days_since_last_touch <= 180 THEN 'Low'
        ELSE 'Dormant'
    END AS engagement_level,
    CASE WHEN d.contact_role = 'Decision Maker' OR d.title IN ('CEO', 'CFO') THEN TRUE ELSE FALSE END AS primary_contact,
    d._fivetran_synced
FROM deduped d
LEFT JOIN last_touch lt ON d.contact_id = lt.contact_id
