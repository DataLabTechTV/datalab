SELECT g.user_id, g.genres, 'HR' AS country
FROM {{ ref('hr_genres') }} AS g

UNION

SELECT g.user_id, g.genres, 'HU' AS country
FROM {{ ref('hu_genres') }} AS g

UNION

SELECT g.user_id, g.genres, 'RO' AS country
FROM {{ ref('ro_genres') }} AS g

ORDER BY g.user_id
