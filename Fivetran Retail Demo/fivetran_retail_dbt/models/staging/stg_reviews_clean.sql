SELECT
    review_id,
    product_id,
    customer_id,
    rating,
    review_title,
    review_text,
    review_date,
    verified_purchase,
    helpful_votes,
    CASE
        WHEN rating >= 4 THEN 'Positive'
        WHEN rating = 3 THEN 'Neutral'
        ELSE 'Negative'
    END AS sentiment,
    LENGTH(review_text) AS review_length,
    CASE
        WHEN LENGTH(review_text) >= 200 THEN 'Detailed'
        WHEN LENGTH(review_text) >= 100 THEN 'Standard'
        ELSE 'Brief'
    END AS review_depth,
    TRUE AS is_valid_record,
    _fivetran_synced AS source_synced_at,
    CURRENT_TIMESTAMP() AS processed_at
FROM {{ source('bronze', 'RAW_REVIEWS') }}
WHERE _fivetran_deleted = FALSE
QUALIFY ROW_NUMBER() OVER (PARTITION BY review_id ORDER BY _fivetran_synced DESC) = 1
