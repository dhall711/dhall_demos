SELECT
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    unit_cost,
    ROUND(unit_price - unit_cost, 2) AS unit_margin,
    ROUND((unit_price - unit_cost) / NULLIF(unit_price, 0) * 100, 1) AS margin_pct,
    weight_lbs,
    description,
    is_active,
    launch_date,
    CASE
        WHEN unit_price >= 500 THEN 'Premium'
        WHEN unit_price >= 100 THEN 'Mid-Range'
        ELSE 'Budget'
    END AS price_tier,
    TRUE AS is_valid_record,
    _fivetran_synced AS source_synced_at,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('bronze', 'RAW_PRODUCTS') }}
WHERE _fivetran_deleted = FALSE
QUALIFY ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY _fivetran_synced DESC) = 1
