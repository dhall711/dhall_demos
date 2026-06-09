WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_SF_ACCOUNTS') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    account_id,
    account_name,
    industry_segment,
    account_tier,
    annual_revenue,
    employee_count,
    relationship_start_date,
    assigned_advisor,
    region,
    DATEDIFF('year', relationship_start_date, CURRENT_DATE()) AS tenure_years,
    CASE
        WHEN tenure_years <= 2 THEN 'New'
        WHEN tenure_years <= 5 THEN 'Established'
        ELSE 'Long-Term'
    END AS tenure_bucket,
    CASE
        WHEN annual_revenue >= 10000000 THEN 'Enterprise'
        WHEN annual_revenue >= 2000000 THEN 'Mid-Market'
        ELSE 'SMB'
    END AS revenue_tier,
    LEAST(100, GREATEST(0,
        (CASE WHEN annual_revenue > 5000000 THEN 30 WHEN annual_revenue > 1000000 THEN 20 ELSE 10 END) +
        (CASE WHEN tenure_years > 5 THEN 30 WHEN tenure_years > 2 THEN 20 ELSE 10 END) +
        (CASE WHEN account_tier = 'Platinum' THEN 30 WHEN account_tier = 'Gold' THEN 20 WHEN account_tier = 'Silver' THEN 15 ELSE 10 END) +
        UNIFORM(0, 10, RANDOM())
    )) AS health_score,
    _fivetran_synced
FROM deduped
