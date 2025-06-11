SELECT
    'd_hr' || e.source_id AS source_id,
    'd_hr' || e.target_id AS target_id,
FROM {{ ref('dsn_hr_edges') }} AS e

UNION

SELECT
    'd_hu' || e.source_id AS source_id,
    'd_hu' || e.target_id AS target_id,
FROM {{ ref('dsn_hu_edges') }} AS e

UNION

SELECT
    'd_ro' || e.source_id AS source_id,
    'd_ro' || e.target_id AS target_id,
FROM {{ ref('dsn_ro_edges') }} AS e

ORDER BY source_id, target_id
