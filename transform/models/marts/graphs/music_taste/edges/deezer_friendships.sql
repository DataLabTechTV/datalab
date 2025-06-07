SELECT
    e.source_id AS source_id,
    e.target_id AS target_id,
    'Deezer' AS source,
    'HR' AS country
FROM {{ ref('hr_edges') }} AS e

UNION

SELECT
    e.source_id AS source_id,
    e.target_id AS target_id,
    'Deezer' AS source,
    'HU' AS country
FROM {{ ref('hu_edges') }} AS e

UNION

SELECT
    e.source_id AS source_id,
    e.target_id AS target_id,
    'Deezer' AS source,
    'RO' AS country
FROM {{ ref('ro_edges') }} AS e

ORDER BY e.source_id, e.target_id
