import os
import shutil
import tempfile
from string import Template

import kuzu
from loguru import logger as log

from shared.settings import LOCAL_DIR
from shared.storage import Storage


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
        self.storage = Storage()

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

        log.info("Installing httpfs extension")
        self.con.execute("INSTALL httpfs")
        self.con.execute("LOAD httpfs")

    def _copy_from_s3(self, s3_path: str, query: str, path_var="path"):
        with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
            self.storage.download_file(s3_path, tmp.name)
            self.con.execute(Template(query).substitute({path_var: tmp.name}))

    def _import_music_graph(self, s3_path: str):
        log.info("Importing music_graph DSN User nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/dsn_nodes_users.parquet",
            "COPY User(node_id, user_id, source, country) FROM '$path'",
        )

        log.info("Importing music_graph MSDSL User nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/msdsl_nodes_users.parquet",
            "COPY User(node_id, user_id, source) FROM '$path'",
        )

        log.info("Importing music_graph MSDSL Track nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/msdsl_nodes_tracks.parquet",
            "COPY Track(track_id, name, artist, year) FROM '$path'",
        )

        log.info("Importing music_graph Genre nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/nodes_genres.parquet",
            "COPY Genre(genre) FROM '$path'",
        )

        log.info("Importing music_graph DSN user-user friend edges")

        self._copy_from_s3(
            f"{s3_path}/edges/dsn_edges_friendships.parquet",
            "COPY Friend FROM '$path'",
        )

        log.info("Importing music_graph DSN user-genre edges")

        self._copy_from_s3(
            f"{s3_path}/edges/dsn_edges_user_genres.parquet",
            "COPY Likes FROM '$path'",
        )

        log.info("Importing music_graph MSDSL user-tracks edges")

        self._copy_from_s3(
            f"{s3_path}/edges/msdsl_edges_user_tracks.parquet",
            "COPY ListenedTo FROM '$path'",
        )

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
