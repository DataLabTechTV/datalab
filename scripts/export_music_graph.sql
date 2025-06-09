-- NODES

COPY marts.music_graph.dsn_nodes_genres
TO 's3://lakehouse/exports/music_graph/nodes/dsn_nodes_genres.parquet'
(FORMAT parquet);

COPY marts.music_graph.dsn_nodes_users
TO 's3://lakehouse/exports/music_graph/nodes/dsn_nodes_users.parquet'
(FORMAT parquet);

COPY marts.music_graph.msdsl_nodes_tags
TO 's3://lakehouse/exports/music_graph/nodes/msdsl_nodes_tags.parquet'
(FORMAT parquet);

COPY marts.music_graph.msdsl_nodes_tracks
TO 's3://lakehouse/exports/music_graph/nodes/msdsl_nodes_tracks.parquet'
(FORMAT parquet);

COPY marts.music_graph.msdsl_nodes_users
TO 's3://lakehouse/exports/music_graph/nodes/msdsl_nodes_users.parquet'
(FORMAT parquet);

-- EDGES

COPY marts.music_graph.dsn_edges_friendships
TO 's3://lakehouse/exports/music_graph/edges/dsn_edges_friendships.parquet'
(FORMAT parquet);

COPY marts.music_graph.dsn_edges_user_genres
TO 's3://lakehouse/exports/music_graph/edges/dsn_edges_user_genres.parquet'
(FORMAT parquet);

COPY marts.music_graph.msdsl_edges_track_tags
TO 's3://lakehouse/exports/music_graph/edges/msdsl_edges_track_tags.parquet'
(FORMAT parquet);

COPY marts.music_graph.msdsl_edges_user_tracks
TO 's3://lakehouse/exports/music_graph/edges/msdsl_edges_user_tracks.parquet'
(FORMAT parquet);
