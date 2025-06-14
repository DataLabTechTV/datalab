import os
import shutil
import tempfile
from string import Template

import kuzu
import pandas as pd
from loguru import logger as log

from shared.settings import LOCAL_DIR, env
from shared.storage import Storage


class KuzuOps:
    def __init__(self, schema: str, overwrite: bool = False):
        dbname = env.str(f"{schema.upper()}_GRAPH_DB")
        db_path = os.path.join(LOCAL_DIR, dbname)

        if os.path.exists(db_path):
            if overwrite:
                log.warning(f"Overwriting database: {db_path}")
                shutil.rmtree(db_path)

        db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(db)
        self.storage = Storage()

    def _create_music_graph_schema(self):
        # Nodes
        # =====

        log.info("Creating music_graph schema for User nodes")

        self.conn.execute(
            """
            CREATE NODE TABLE User (
                node_id INT64,
                user_id STRING,
                source STRING,
                country STRING,
                PRIMARY KEY (node_id)
            )
            """
        )

        log.info("Creating music_graph schema for Genre nodes")

        self.conn.execute(
            """
            CREATE NODE TABLE Genre (
                node_id INT64,
                genre STRING,
                PRIMARY KEY (node_id)
            )
            """
        )

        log.info("Creating music_graph schema for Track nodes")

        self.conn.execute(
            """
            CREATE NODE TABLE Track (
                node_id INT64,
                track_id STRING,
                name STRING,
                artist STRING,
                year INT16,
                PRIMARY KEY (node_id)
            )
            """
        )

        # Edges
        # =====

        log.info("Creating music_graph schema for Friend edges")
        self.conn.execute("CREATE REL TABLE Friend(FROM User TO User, MANY_MANY)")

        # log.info("Creating music_graph schema for Likes edges")
        # self.conn.execute("CREATE REL TABLE Likes(FROM User TO Genre, MANY_MANY)")

        # log.info("Creating music_graph schema for ListenedTo edges")
        # self.conn.execute(
        #     """
        #     CREATE REL TABLE ListenedTo(
        #         FROM User TO Track,
        #         play_count INT32,
        #         MANY_MANY
        #     )
        #     """
        # )

        log.info("Creating music_graph schema for Tagged edges")
        self.conn.execute("CREATE REL TABLE Tagged(FROM Track TO Genre, MANY_MANY)")

    def _copy_from_s3(self, s3_path: str, query: str, path_var="path"):
        with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
            self.storage.download_file(s3_path, tmp.name)
            query = Template(query).substitute({path_var: tmp.name})
            log.debug("Running query: {}", query)
            self.conn.execute(query)

    def _import_music_graph(self, s3_path: str):
        # Nodes
        # =====

        log.info("Importing music_graph DSN User nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/dsn_nodes_users.parquet",
            "COPY User(node_id, user_id, country, source) FROM '$path'",
        )

        # log.info("Importing music_graph MSDSL User nodes")

        # self._copy_from_s3(
        #     f"{s3_path}/nodes/msdsl_nodes_users.parquet",
        #     "COPY User(node_id, user_id, source) FROM '$path'",
        # )

        log.info("Importing music_graph MSDSL Track nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/msdsl_nodes_tracks.parquet",
            "COPY Track(node_id, track_id, name, artist, year) FROM '$path'",
        )

        log.info("Importing music_graph Genre nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/nodes_genres.parquet",
            "COPY Genre(node_id, genre) FROM '$path'",
        )

        # Edges
        # =====

        log.info("Importing music_graph DSN user-user friend edges")

        self._copy_from_s3(
            f"{s3_path}/edges/dsn_edges_friendships.parquet",
            "COPY Friend FROM '$path'",
        )

        # log.info("Importing music_graph DSN user-genre edges")

        # self._copy_from_s3(
        #     f"{s3_path}/edges/dsn_edges_user_genres.parquet",
        #     "COPY Likes FROM '$path'",
        # )

        # log.info("Importing music_graph MSDSL user-tracks edges")

        # self._copy_from_s3(
        #     f"{s3_path}/edges/msdsl_edges_user_tracks.parquet",
        #     "COPY ListenedTo FROM '$path'",
        # )

        log.info("Importing music_graph MSDSL track-genres edges")

        self._copy_from_s3(
            f"{s3_path}/edges/msdsl_edges_track_tags.parquet",
            "COPY Tagged FROM '$path'",
        )

    def load_music_graph(self, path: str):
        try:
            self._create_music_graph_schema()
        except Exception as e:
            log.error("Failed to create schema for music_graph: {}", e)
            return

        try:
            self._import_music_graph(path)
        except Exception as e:
            log.error("Failed to import nodes/edges for music_graph: {}", e)
            return

    @property
    def num_nodes(self):
        if not hasattr(self, "_num_nodes"):
            log.info("Computing and caching number of nodes")
            result = self.conn.execute("MATCH () RETURN COUNT(*) AS num_nodes")
            self._num_nodes = result.get_as_df().num_nodes.iloc[0]

        return self._num_nodes

    def query_node_batch(self, offset: int, limit: int) -> pd.DataFrame:
        if offset > self.num_nodes:
            log.info(
                "Offset reached a value higher than the number of nodes, "
                "returning an empty DataFrame"
            )
            return pd.DataFrame(columns=["node_id"])

        result = self.conn.execute(
            """
            MATCH (n)
            RETURN n.node_id AS node_id
            ORDER BY n.node_id
            SKIP $skip
            LIMIT $limit
            """,
            parameters=dict(skip=offset, limit=limit),
        )

        return result.get_as_df()

    def query_neighbors(self, nodes: pd.DataFrame):
        result = self.conn.execute(
            """
            MATCH (n)-->(m)
            WHERE n.node_id IN CAST($nodes AS INT64[])
            RETURN n.node_id AS source_id, m.node_id AS target_id
            ORDER BY source_id, target_id
            """,
            parameters=dict(nodes=nodes.node_id.to_list()),
        )

        return result.get_as_df()

    def update_embeddings(
        self,
        embeddings: dict[int, list[float]],
        batch_size: int = 1000,
    ):
        log.info("Updating graph DB node embeddings (batch_size = {})", batch_size)

        embeddings_lst = [[nid, e] for nid, e in embeddings.items()]

        for nr, start in enumerate(range(0, len(embeddings_lst), batch_size), 1):
            log.info("Updating embeddings: batch {}", nr)

            batch = embeddings_lst[start : start + batch_size]

            self.conn.execute(
                """
                UNWIND $batch AS batch
                MATCH (n {node_id: batch[0]})
                SET n.embedding = batch[1]
                """,
                parameters=dict(batch=batch),
            )
