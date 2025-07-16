SELECT
    country_id,
    product_id,
    sum(export_value) AS amount_usd
FROM
    {{ ref('taoec_hs92_ccp_trade_3y_latest') }}
WHERE
    export_value > 0
GROUP BY
    country_id,
    product_id
