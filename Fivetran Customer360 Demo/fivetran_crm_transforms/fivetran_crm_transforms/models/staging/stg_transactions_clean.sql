WITH deduped AS (
    SELECT *
    FROM {{ source('bronze', 'RAW_FIN_TRANSACTIONS') }}
    WHERE _fivetran_deleted = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY _fivetran_synced DESC) = 1
)
SELECT
    transaction_id,
    account_id,
    transaction_type,
    amount,
    transaction_date,
    product_code,
    channel,
    CASE
        WHEN transaction_type IN ('Deposit', 'Interest') THEN 'Revenue'
        WHEN transaction_type IN ('Withdrawal', 'Fee') THEN 'Cost'
        ELSE 'Neutral'
    END AS transaction_category,
    TO_CHAR(transaction_date, 'YYYY-MM') AS month,
    'Q' || CEIL(MONTH(transaction_date) / 3.0)::INT::STRING || ' ' || YEAR(transaction_date)::STRING AS quarter,
    _fivetran_synced
FROM deduped
