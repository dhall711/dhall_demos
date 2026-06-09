WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_FIN_ADVISOR_NOTES') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY note_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    note_id,
    account_id,
    contact_id,
    advisor_name,
    note_date,
    note_text,
    note_type,
    sentiment_flag,
    CASE
        WHEN LENGTH(note_text) > 150 THEN 'Detailed'
        WHEN LENGTH(note_text) > 80 THEN 'Standard'
        ELSE 'Brief'
    END AS note_depth,
    CASE
        WHEN sentiment_flag = 'Positive' THEN 'Positive'
        WHEN sentiment_flag = 'Neutral' THEN 'Neutral'
        WHEN sentiment_flag = 'Negative' THEN 'Negative'
        ELSE 'Concerned'
    END AS sentiment,
    _fivetran_synced
FROM deduped
