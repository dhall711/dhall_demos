WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_ELQ_CAMPAIGN_MEMBERS') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    member_id,
    campaign_id,
    contact_id,
    status,
    responded_date,
    engagement_score,
    CASE
        WHEN status IN ('Converted') THEN 'Deep'
        WHEN status IN ('Responded', 'Clicked') THEN 'Moderate'
        WHEN status IN ('Opened') THEN 'Shallow'
        ELSE 'None'
    END AS engagement_depth,
    CASE WHEN responded_date IS NOT NULL THEN DATEDIFF('day', _fivetran_synced, responded_date) ELSE NULL END AS days_to_respond,
    CASE WHEN status = 'Converted' THEN TRUE ELSE FALSE END AS conversion_flag,
    _fivetran_synced
FROM deduped
