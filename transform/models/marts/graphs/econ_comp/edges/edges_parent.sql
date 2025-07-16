SELECT
    sn.node_id AS source_id,
    tn.node_id AS target_id
FROM
    {{ ref('taoec_hs92_products') }} AS p
JOIN
    {{ ref('nodes_products') }} AS sn
    ON p.product_id = sn.product_id
JOIN
    {{ ref('nodes_products') }} AS tn
    ON p.product_parent_id = tn.product_id
