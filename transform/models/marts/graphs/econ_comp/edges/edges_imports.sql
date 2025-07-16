SELECT
    sn.node_id AS source_id,
    tn.node_id AS target_id,
    sum(import_value) AS amount_usd
FROM
    {{ ref('taoec_hs92_ccp_trade_3y_latest') }} AS t
JOIN
    {{ ref('nodes_products') }} AS sn
    ON t.product_id = sn.product_id
JOIN
    {{ ref('nodes_countries') }} AS tn
    ON t.country_id = tn.country_id
WHERE
    import_value > 0
GROUP BY
    source_id,
    target_id
