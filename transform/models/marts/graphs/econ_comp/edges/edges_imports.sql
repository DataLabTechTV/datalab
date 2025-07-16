SELECT
    product_id,
    country_id,
    sum(import_value) AS amount_usd
FROM
    {{ ref('taoec_hs92_ccp_trade_3y_latest') }}
WHERE
    import_value > 0
GROUP BY
    country_id,
    product_id
