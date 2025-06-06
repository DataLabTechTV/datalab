SELECT 'HR' AS country, *
FROM {{ ref('hr_genres') }}

UNION

SELECT 'HU' AS country, *
FROM {{ ref('hu_genres') }}

UNION

SELECT 'RO' AS country, *
FROM {{ ref('ro_genres') }}
