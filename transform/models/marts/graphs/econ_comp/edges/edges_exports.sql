SELECT
    sn.node_id AS source_id,
    tn.node_id AS target_id,
    sum(export_value) AS amount_usd
FROM
    {{ ref('taoec_hs92_ccp_trade_3y_latest') }} AS t
JOIN
    {{ ref('nodes_countries') }} AS sn
    ON t.country_id = sn.country_id
JOIN
    {{ ref('nodes_products') }} AS tn
    ON t.product_id = tn.product_id
WHERE
    export_value > 0
GROUP BY
    source_id,
    target_id
