SELECT
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    city,
    state,
    country,
    signup_date,
    customer_segment,
    lifetime_value,
    preferred_category,
    marketing_channel,
    DATEDIFF('day', signup_date, CURRENT_DATE()) AS tenure_days,
    CASE
        WHEN DATEDIFF('day', signup_date, CURRENT_DATE()) <= 90 THEN 'New'
        WHEN DATEDIFF('day', signup_date, CURRENT_DATE()) <= 365 THEN 'Established'
        ELSE 'Loyal'
    END AS tenure_bucket,
    DAYNAME(signup_date) AS signup_day_of_week,
    CASE WHEN DAYOFWEEK(signup_date) IN (0, 6) THEN TRUE ELSE FALSE END AS signed_up_on_weekend,
    TRUE AS is_valid_record,
    _fivetran_synced AS source_synced_at,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('bronze', 'RAW_CUSTOMERS') }}
WHERE _fivetran_deleted = FALSE
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY _fivetran_synced DESC) = 1
