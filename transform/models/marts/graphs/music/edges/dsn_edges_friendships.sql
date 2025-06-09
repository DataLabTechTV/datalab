SELECT
    e.source_id AS source_id,
    e.target_id AS target_id,
    'Deezer' AS source,
    'HR' AS country
FROM {{ ref('dsn_hr_edges') }} AS e

UNION

SELECT
    e.source_id AS source_id,
    e.target_id AS target_id,
    'Deezer' AS source,
    'HU' AS country
FROM {{ ref('dsn_hu_edges') }} AS e

UNION

SELECT
    e.source_id AS source_id,
    e.target_id AS target_id,
    'Deezer' AS source,
    'RO' AS country
FROM {{ ref('dsn_ro_edges') }} AS e

ORDER BY e.source_id, e.target_id
