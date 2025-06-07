SELECT e.source_id, e.target_id, 'HR' AS country
FROM {{ ref('hr_edges') }} AS e

UNION

SELECT e.source_id, e.target_id, 'HU' AS country
FROM {{ ref('hu_edges') }} AS e

UNION

SELECT e.source_id, e.target_id, 'RO' AS country
FROM {{ ref('ro_edges') }} AS e

ORDER BY e.source_id, e.target_id
