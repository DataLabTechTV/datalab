import os
import shutil

import kuzu
from loguru import logger as log

from shared.settings import LOCAL_DIR, env


class KuzuOpsException(Exception):
    pass


class KuzuOps:
    def __init__(self, dbname: str, overwrite: bool = False):
        db_path = os.path.join(LOCAL_DIR, dbname)

        if os.path.exists(db_path):
            if overwrite:
                log.warning(f"Overwriting database: {db_path}")
                shutil.rmtree(db_path)
            else:
                raise KuzuOpsException(f"Database exists: {db_path}")

        db = kuzu.Database(db_path)
        self.con = kuzu.Connection(db)

        env.str("S3_ENDPOINT")
        env.bool("S3_USE_SSL")
        env.str("S3_URL_STYLE")
        env.str("S3_ACCESS_KEY_ID")
        env.str("S3_SECRET_ACCESS_KEY")
        env.str("S3_REGION")

    def _create_music_graph_schema(self):
        log.info("Creating music_graph schema for User nodes")

        self.con.execute(
            """
            CREATE NODE TABLE User (
                node_id STRING,
                user_id STRING,
                source STRING,
                country STRING,
                PRIMARY KEY (node_id)
            )
            """
        )

        log.info("Creating music_graph schema for Genre nodes")

        self.con.execute(
            """
            CREATE NODE TABLE Genre (
                genre STRING,
                PRIMARY KEY (genre)
            )
            """
        )

        log.info("Creating music_graph schema for Track nodes")

        self.con.execute(
            """
            CREATE NODE TABLE Track (
                track_id STRING,
                name STRING,
                artist STRING,
                year INT16,
                PRIMARY KEY (track_id)
            )
            """
        )

        log.info("Creating music_graph schema for Friend edges")
        self.con.execute("CREATE REL TABLE Friend(FROM User TO User, MANY_MANY)")

        log.info("Creating music_graph schema for Likes edges")
        self.con.execute("CREATE REL TABLE Likes(FROM User TO Genre, MANY_MANY)")

        log.info("Creating music_graph schema for ListenedTo edges")
        self.con.execute("CREATE REL TABLE ListenedTo(FROM User TO Track, MANY_MANY)")

        log.info("Creating music_graph schema for Tagged edges")
        self.con.execute("CREATE REL TABLE Tagged(FROM Track TO Genre, MANY_MANY)")

    def _import_music_graph(self, path: str):
        log.info("Importing music_graph: nodes")

        self.con.execute(
            f"""
            COPY User(node_id, user_id, source, country)
            FROM '{path}/nodes/dsn_nodes_users.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY User(node_id, user_id, source)
            FROM '{path}/nodes/msdsl_nodes_users.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY Genre(genre)
            FROM '{path}/nodes/dsn_nodes_genres.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY Genre(genre)
            FROM '{path}/nodes/msdsl_nodes_tags.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY Track(track_id, name, artist, year)
            FROM '{path}/nodes/msdsl_nodes_tracks.parquet'
            """
        )

        log.info("Importing music_graph: edges")

        self.con.execute(
            f"""
            COPY Friend(source_id, target_id)
            FROM '{path}/edges/dsn_edges_friendships.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY Likes(source_id, target_id)
            FROM '{path}/edges/dsn_edges_user_genres.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY ListenedTo(source_id, target_id)
            FROM '{path}/edges/msdsl_edges_user_tracks.parquet'
            """
        )

        self.con.execute(
            f"""
            COPY Tagged(source_id, target_id)
            FROM '{path}/edges/msdsl_edges_track_tags.parquet'
            """
        )

    def load_music_graph(self, path: str):
        try:
            self._create_music_graph_schema()
        except:
            log.exception("Could not create schema for music_graph")
            return

        try:
            self._import_music_graph(path)
        except:
            log.exception("Could not import music_graph")
            return
