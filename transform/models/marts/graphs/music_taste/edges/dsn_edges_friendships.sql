WITH all_edges AS (
    SELECT
        source_id,
        target_id,
        'HR' AS country
    FROM {{ ref('dsn_hr_edges') }}

    UNION

    SELECT
        source_id,
        target_id,
        'HU' AS country
    FROM {{ ref('dsn_hu_edges') }}

    UNION

    SELECT
        source_id,
        target_id,
        'RO' AS country
    FROM {{ ref('dsn_ro_edges') }}
)
SELECT sn.node_id AS source_id, tn.node_id AS target_id,
FROM all_edges e

JOIN {{ ref('dsn_nodes_users') }} AS sn
ON e.source_id = sn.user_id AND e.country = sn.country

JOIN {{ ref('dsn_nodes_users') }} AS tn
ON e.target_id = tn.user_id AND e.country = tn.country

ORDER BY source_id, target_id
