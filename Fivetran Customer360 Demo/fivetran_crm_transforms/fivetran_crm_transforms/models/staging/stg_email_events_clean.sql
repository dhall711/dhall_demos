WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_ELQ_EMAIL_EVENTS') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    event_id,
    campaign_id,
    contact_id,
    event_type,
    event_timestamp,
    email_subject,
    link_clicked,
    device_type,
    CASE WHEN HOUR(event_timestamp) BETWEEN 8 AND 18 AND DAYOFWEEK(event_timestamp) BETWEEN 1 AND 5 THEN TRUE ELSE FALSE END AS is_business_hours,
    CASE
        WHEN device_type IN ('Desktop', 'Tablet') THEN 'Desktop/Tablet'
        WHEN device_type = 'Mobile' THEN 'Mobile'
        ELSE 'Other'
    END AS device_category,
    CASE
        WHEN event_type IN ('Open', 'Click') THEN 'Positive'
        WHEN event_type = 'Send' THEN 'Neutral'
        ELSE 'Negative'
    END AS engagement_action,
    _fivetran_synced
FROM deduped
