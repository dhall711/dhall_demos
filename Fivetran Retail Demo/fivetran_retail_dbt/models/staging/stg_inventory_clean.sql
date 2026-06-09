SELECT
    inventory_id,
    product_id,
    warehouse,
    snapshot_date,
    units_on_hand,
    units_reserved,
    units_incoming,
    units_on_hand - units_reserved AS available_units,
    reorder_point,
    max_stock_level,
    CASE
        WHEN units_on_hand <= 0 THEN 'Out of Stock'
        WHEN units_on_hand <= reorder_point THEN 'Low Stock'
        WHEN units_on_hand >= max_stock_level * 0.9 THEN 'Overstock'
        ELSE 'Healthy'
    END AS stock_status,
    CASE
        WHEN units_on_hand <= reorder_point AND units_incoming = 0 THEN TRUE
        ELSE FALSE
    END AS stockout_risk,
    TRUE AS is_valid_record,
    _fivetran_synced AS source_synced_at,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('bronze', 'RAW_INVENTORY') }}
WHERE _fivetran_deleted = FALSE
QUALIFY ROW_NUMBER() OVER (PARTITION BY inventory_id ORDER BY _fivetran_synced DESC) = 1
