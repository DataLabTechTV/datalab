SELECT DISTINCT unnest(tags) AS genre
FROM {{ ref('msdsl_music_info') }}
ORDER BY genre
