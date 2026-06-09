WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_ELQ_CAMPAIGNS') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id ORDER BY _fivetran_synced DESC) = 1
),
campaign_stats AS (
    SELECT
        campaign_id,
        COUNT(*) AS total_members,
        SUM(CASE WHEN status IN ('Responded', 'Converted') THEN 1 ELSE 0 END) AS responses
    FROM {{ source('bronze', 'RAW_ELQ_CAMPAIGN_MEMBERS') }}
    GROUP BY campaign_id
)
SELECT
    d.campaign_id,
    d.campaign_name,
    d.campaign_type,
    d.product_focus,
    d.start_date,
    d.end_date,
    d.budget,
    d.status,
    d.target_segment,
    COALESCE(cs.total_members, 0) AS total_members,
    COALESCE(cs.responses, 0) AS total_responses,
    CASE WHEN d.budget > 0 AND cs.responses > 0 THEN ROUND((cs.responses * 500.0 - d.budget) / d.budget * 100, 2) ELSE 0 END AS roi_pct,
    CASE WHEN cs.responses > 0 THEN ROUND(d.budget / cs.responses, 2) ELSE NULL END AS cost_per_response,
    CASE
        WHEN roi_pct > 100 THEN 'High'
        WHEN roi_pct > 0 THEN 'Medium'
        ELSE 'Low'
    END AS campaign_effectiveness,
    d._fivetran_synced
FROM deduped d
LEFT JOIN campaign_stats cs ON d.campaign_id = cs.campaign_id
