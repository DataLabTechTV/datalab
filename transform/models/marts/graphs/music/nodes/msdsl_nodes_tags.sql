SELECT DISTINCT unnest(tags) AS genre
FROM {{ ref('msdsl_music_info') }}
JOIN {{ ref('dsn_nodes_genres') }}
USING (genre)
ORDER BY genre
