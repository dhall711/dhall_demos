SELECT
    order_id,
    customer_id,
    product_id,
    order_date,
    order_timestamp,
    quantity,
    unit_price,
    discount_pct,
    total_amount,
    ROUND(total_amount * 0.85, 2) AS net_revenue,
    order_status,
    CASE
        WHEN order_status IN ('Delivered', 'Shipped') THEN 'Fulfilled'
        WHEN order_status = 'Processing' THEN 'In Progress'
        WHEN order_status = 'Cancelled' THEN 'Cancelled'
        WHEN order_status = 'Returned' THEN 'Returned'
        ELSE 'Unknown'
    END AS status_group,
    payment_method,
    shipping_method,
    shipping_zone,
    warehouse,
    DAYNAME(order_date) AS order_day_of_week,
    CASE WHEN DAYOFWEEK(order_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend_order,
    CASE
        WHEN MONTH(order_date) IN (3,4,5) THEN 'Spring'
        WHEN MONTH(order_date) IN (6,7,8) THEN 'Summer'
        WHEN MONTH(order_date) IN (9,10,11) THEN 'Autumn'
        ELSE 'Winter'
    END AS season,
    TRUE AS is_valid_record,
    _fivetran_synced AS source_synced_at,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('bronze', 'RAW_ORDERS') }}
WHERE _fivetran_deleted = FALSE
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _fivetran_synced DESC) = 1
