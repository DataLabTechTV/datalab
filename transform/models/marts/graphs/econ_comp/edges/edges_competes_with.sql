SELECT
    sn.node_id AS source_id,
    tn.node_id AS target_id,
    m.esi AS esi

FROM {{ ref('taoec_cc_metrics') }} AS m

JOIN {{ ref('nodes_countries') }} AS sn
ON m.country_id_1 = sn.country_id

JOIN {{ ref('nodes_countries') }} AS tn
ON m.country_id_2 = tn.country_id

WHERE m.esi > 0

ORDER BY m.esi DESC
