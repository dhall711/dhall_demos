WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_SF_OPPORTUNITIES') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY opportunity_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    opportunity_id,
    account_id,
    contact_id,
    opportunity_name,
    stage,
    amount,
    product_line,
    close_date,
    probability_pct,
    created_date,
    owner_name,
    DATEDIFF('day', created_date, COALESCE(close_date, CURRENT_DATE())) AS days_in_stage,
    CASE WHEN stage NOT IN ('Closed Won', 'Closed Lost') AND close_date < CURRENT_DATE() THEN TRUE ELSE FALSE END AS is_overdue,
    CASE
        WHEN probability_pct >= 70 THEN 'High'
        WHEN probability_pct >= 40 THEN 'Medium'
        ELSE 'Low'
    END AS win_probability_bucket,
    'Q' || CEIL(MONTH(close_date) / 3.0)::INT::STRING AS quarter,
    YEAR(close_date)::STRING AS fiscal_year,
    _fivetran_synced
FROM deduped
