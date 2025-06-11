SELECT
    'd_hr_' || e.source_id AS source_id,
    'd_hr_' || e.target_id AS target_id,
FROM {{ ref('dsn_hr_edges') }} AS e

UNION

SELECT
    'd_hu_' || e.source_id AS source_id,
    'd_hu_' || e.target_id AS target_id,
FROM {{ ref('dsn_hu_edges') }} AS e

UNION

SELECT
    'd_ro_' || e.source_id AS source_id,
    'd_ro_' || e.target_id AS target_id,
FROM {{ ref('dsn_ro_edges') }} AS e

ORDER BY source_id, target_id
