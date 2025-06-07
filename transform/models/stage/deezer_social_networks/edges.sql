SELECT e.source, e.target, 'HR' AS country
FROM {{ ref('hr_edges') }} AS e

UNION

SELECT e.source, e.target, 'HU' AS country
FROM {{ ref('hu_edges') }} AS e

UNION

SELECT e.source, e.target, 'RO' AS country
FROM {{ ref('ro_edges') }} AS e

ORDER BY e.source, e.target
