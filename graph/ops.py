import os
import shutil
import tempfile
from enum import Enum
from string import Template
from typing import Any, Optional

import kuzu
import numpy as np
import pandas as pd
from loguru import logger as log
from more_itertools import interleave_longest

from shared.settings import LOCAL_DIR, env
from shared.storage import Storage, StoragePrefix


class KuzuTableType(Enum):
    NODE = "NODE"
    REL = "REL"


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
        self.storage = Storage(prefix=StoragePrefix.EXPORTS)

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

        log.info("Creating music_graph schema for Likes edges")
        self.conn.execute("CREATE REL TABLE Likes(FROM User TO Genre, MANY_MANY)")

        log.info("Creating music_graph schema for ListenedTo edges")
        self.conn.execute(
            """
            CREATE REL TABLE ListenedTo(
                FROM User TO Track,
                play_count INT32,
                MANY_MANY
            )
            """
        )

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

        log.info("Importing music_graph MSDSL User nodes")

        self._copy_from_s3(
            f"{s3_path}/nodes/msdsl_nodes_users.parquet",
            "COPY User(node_id, user_id, source) FROM '$path'",
        )

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

    def get_table_names(self, type_: KuzuTableType = KuzuTableType.NODE) -> list[str]:
        result = self.conn.execute(
            """
            CALL show_tables()
            WHERE type = $type
            RETURN name AS table_name;
            """,
            {"type": type_.value},
        )

        table_names = result.get_as_df()["table_name"].to_list()

        return table_names

    def update_embeddings(
        self,
        embeddings: dict[int, list[float]],
        dim: int,
        column_name: str = "embedding",
    ):
        node_tables = self.get_table_names(KuzuTableType.NODE)

        for node_table in node_tables:
            self.conn.execute(
                f"""
                ALTER TABLE {node_table}
                ADD IF NOT EXISTS {column_name} DOUBLE[{dim}]
                """
            )

        batch = [dict(nid=nid, e=e) for nid, e in embeddings.items()]

        self.conn.execute(
            """
            UNWIND $batch AS batch
            MATCH (n {node_id: batch.nid})
            SET n.embedding = batch.e
            """,
            parameters=dict(batch=batch),
        )

    def reindex_embeddings(self, column_name: str = "embedding"):
        log.info("Re-indexing embeddings")

        node_tables = self.get_table_names(KuzuTableType.NODE)

        embedding_tables = []

        for node_table in node_tables:
            result = self.conn.execute(
                f"""
                CALL table_info("{node_table}")
                WHERE name = $column_name
                RETURN count(*) > 0 AS has_embedding
                """,
                dict(column_name=column_name),
            )

            has_embedding = result.get_as_df()["has_embedding"].iloc[0]

            if has_embedding:
                embedding_tables.append(node_table)

        log.info(
            "Node tables with {} column: {}", column_name, ", ".join(embedding_tables)
        )

        self.conn.execute(
            """
            INSTALL vector;
            LOAD vector;
            """
        )

        for node_table in sorted(embedding_tables):
            index_name = f"{node_table}_{column_name}_idx".lower()

            result = self.conn.execute(
                f"""
                CALL show_indexes()
                WHERE `index name` = $index_name
                RETURN count(*) > 0 AS index_exists
                """,
                dict(index_name=index_name),
            )

            index_exists = result.get_as_df()["index_exists"].iloc[0]

            if index_exists:
                log.warning("Dropping existing index {}", index_name)

                self.conn.execute(
                    f"""
                    CALL drop_vector_index(
                        "{node_table}",
                        "{index_name}"
                    )
                    """
                )

            log.info("Creating index {}", index_name)

            self.conn.execute(
                f"""
                CALL create_vector_index(
                    "{node_table}",
                    "{index_name}",
                    "{column_name}"
                );
                """
            )

    def knn(
        self,
        node_id: int,
        column_name: str = "embedding",
        max_k: int = 10,
        max_distance: float = 1.0,
        exclude: Optional[list[int]] = None,
    ) -> pd.DataFrame:
        """
        Compute k-nearest neighbors, within the given constraints.

        Args:
            node_id: Source node ID for which the k-NN to be computed.
            column_name: Column name of the node property containing the embeddings.
                These should be indexed by `reindex_embeddings()`.
            max_k: Target number of neighbors to retrieve.
            max_distance: Neighbors above this threshold won't be returned. Since we're
                using the cosine distance, which ranges between 0 and 2, a value of 1.0
                here is equivalent to a 50% threshold.
            exclude: Optional list with node IDs to exclude.

        Returns:
            Pandas DataFrame with columns table, node_id and distance.
        """

        log.info(
            "Retrieving {}-nearest neighbors for node_id={} at a maximum distance of "
            "{} ∈ [0, 2] and excluding {} nodes",
            max_k,
            node_id,
            max_distance,
            len(exclude or []),
        )

        self.conn.execute("LOAD vector")

        node_tables = self.get_table_names(KuzuTableType.NODE)

        result = self.conn.execute(
            """
            MATCH (n)
            WHERE n.node_id = $node_id
            RETURN n.embedding AS embedding
            LIMIT 1
            """,
            dict(node_id=node_id),
        )

        node_embedding = result.get_as_df()["embedding"].iloc[0]

        nn_dfs = []

        exclude = exclude or []
        adj_k = max_k + len(exclude)

        for node_table in node_tables:
            index_name = f"{node_table}_{column_name}_idx".lower()

            result = self.conn.execute(
                f"""
                CALL query_vector_index(
                    '{node_table}',
                    '{index_name}',
                    $node_embedding,
                    {adj_k}
                )
                WHERE distance <= $max_distance
                    AND NOT node.node_id IN $exclude
                RETURN node.node_id AS node_id, distance
                ORDER BY distance
                LIMIT {max_k};
                """,
                dict(
                    node_embedding=node_embedding,
                    max_distance=max_distance,
                    exclude=exclude,
                ),
            )

            nn_df = result.get_as_df()
            nn_df["table"] = node_table

            log.debug(
                "Found {} nearest neighbor {} nodes for node_id={}",
                len(nn_df),
                node_table,
                node_id,
            )

            nn_dfs.append(nn_df)

        return pd.concat(nn_dfs)

    def sample_shortest_paths(
        self,
        source_node_ids: list[int],
        target_node_ids: list[int],
        n: int,
        min_length: int,
        max_length: int,
    ) -> pd.DataFrame:
        log.info(
            "Computing a sample of size {} of shortest paths between "
            "{} source nodes and {} target nodes, at distances ranging between "
            "{} and {} hops",
            n,
            len(source_node_ids),
            len(target_node_ids),
            min_length,
            max_length,
        )

        result = self.conn.execute(
            f"""
            MATCH p = (a)-[* SHORTEST {min_length}..{max_length}]-(b)
            WHERE a.node_id IN $source_node_ids
                AND b.node_id IN $target_node_ids
            RETURN
                list_transform(nodes(p), n -> n.node_id) AS nodes,
                list_transform(rels(p), r -> label(r)) AS rels;
            """,
            dict(
                source_node_ids=source_node_ids,
                target_node_ids=target_node_ids,
            ),
        )

        paths_df = result.get_as_df()
        paths_df = paths_df.sample(n)

        paths_df = (
            paths_df.apply(lambda row: list(interleave_longest(*row)), axis=1)
            .rename("paths")
            .to_frame()
        )

        return paths_df

    def random_walk(
        self,
        source_node_id: int,
        n: int,
        min_length: int,
        max_length: int,
    ) -> list[int]:
        log.info(
            "Computing {} random walks starting from node_id={} and ranging between "
            "{} and {} hops",
            n,
            source_node_id,
            min_length,
            max_length,
        )

        def sample_neighbor(
            source_node_id: int,
            prev_node_id: Optional[int] = None,
        ) -> Optional[tuple[str, int]]:
            result = self.conn.execute(
                f"""
                MATCH p = (n)-[r]-(m)
                WHERE n.node_id = $source_node_id
                    AND m.node_id <> $prev_node_id
                RETURN label(r) AS rel, m.node_id AS node;
                """,
                dict(
                    source_node_id=source_node_id,
                    prev_node_id=prev_node_id or -1,
                ),
            )

            neighbors = result.get_as_df()

            if len(neighbors) == 0:
                return

            next_in_path = neighbors.sample(1).iloc[0]

            return next_in_path.rel, next_in_path.node.item()

        paths = []

        for _ in range(n):
            path = [source_node_id]

            rand_len = np.random.randint(min_length, max_length + 1)

            for i in range(rand_len):
                next_in_path = sample_neighbor(
                    path[i * 2],
                    None if i == 0 else path[i * 2 - 2],
                )

                if next_in_path is None:
                    break

                rel_type, node_id = next_in_path
                path.append(rel_type)
                path.append(node_id)

            paths.append(path)

        paths_df = pd.DataFrame(dict(source_node_id=source_node_id, paths=paths))

        return paths_df

    def node_properties(self, nodes: list[dict[str, Any]]) -> dict[str, Any]:
        node_tables = self.get_table_names(KuzuTableType.NODE)

        node_props_schema = {}

        for node_table in node_tables:
            result = self.conn.execute(
                f"""
                CALL table_info("{node_table}")
                RETURN name;
                """
            )

            node_props_schema[node_table] = result.get_as_df()["name"].to_list()

        node_props = []

        for node in nodes:
            node_props.append(
                {
                    k: v
                    for k, v in node.items()
                    if k in node_props_schema[node["_label"]] + ["_label"]
                }
            )

        return node_props

    def rel_properties(self, rels: list[dict[str, Any]]) -> dict[str, Any]:
        rel_tables = self.get_table_names(KuzuTableType.REL)

        rel_props_schema = {}

        for rel_table in rel_tables:
            result = self.conn.execute(
                f"""
                CALL table_info("{rel_table}")
                RETURN name;
                """
            )

            rel_props_schema[rel_table] = result.get_as_df()["name"].to_list()

        rel_props = []

        for rel in rels:
            rel_props.append(
                {
                    k: v
                    for k, v in rel.items()
                    if k in rel_props_schema[rel["_label"]] + ["_label"]
                }
            )

        return rel_props

    def node_description(
        self,
        node: dict[str, Any],
        exclude_props: Optional[list[str]] = None,
    ) -> str:
        exclude_props = exclude_props or []
        exclude_props = exclude_props + ["_label", "node_id"]

        label = node["_label"]
        node_id = node["node_id"]

        props = [f"{k}={v}" for k, v in node.items() if k not in exclude_props]
        props = "" if len(props) == 0 else ", " + ", ".join(props)

        description = f"{label}(node_id={node_id}{props})"

        return description

    def rel_description(
        self,
        source_node: dict[str, Any],
        rel: dict[str, Any],
        target_node: dict[str, Any],
        exclude_props: Optional[list[str]] = None,
    ) -> str:
        exclude_props = exclude_props or []
        exclude_props += ["_label"]

        label = rel["_label"]

        props = [f"{k}={v}" for k, v in rel.items() if k not in exclude_props]
        props = "" if len(props) == 0 else " {%s}" % ", ".join(props)

        description = (
            f"({{ node_id: {source_node['node_id']} }})"
            f"-[:{label}{props}]-"
            f"({{ node_id: {target_node['node_id']} }})"
        )

        return description

    def hydrate_path(
        self,
        path: list[int | str],
        exclude_props: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        exclude_props = exclude_props or []

        stmt = []

        for i in range(0, len(path), 2):
            stmt.append("({ node_id: %d })" % path[i])

            if i + 1 < len(path):
                stmt.append("[:%s]" % path[i + 1])

        result = self.conn.execute(
            """
            MATCH p = %s
            RETURN nodes(p) AS nodes, rels(p) AS rels
            """
            % "-".join(stmt)
        )

        hydrate_df = result.get_as_df()

        if len(hydrate_df) == 0:
            log.warning("Could not match path: {}", path)
            return

        return hydrate_df.iloc[0]

    def path_descriptions(
        self,
        paths_df: pd.DataFrame,
        exclude_props: Optional[list[str]] = None,
    ) -> str:
        log.info("Computing node and rel descriptions for {} paths", len(paths_df))

        exclude_props = exclude_props or []
        hydrate_df = paths_df.apply(lambda row: self.hydrate_path(row.item()), axis=1)
        hydrate_df = hydrate_df.dropna()

        if len(hydrate_df) == 0:
            return ""

        hydrate_df.nodes = hydrate_df.nodes.apply(self.node_properties)
        hydrate_df.rels = hydrate_df.rels.apply(self.rel_properties)

        node_descriptions = set()

        for nodes in hydrate_df.nodes:
            node_descriptions |= set(
                self.node_description(node, exclude_props=exclude_props)
                for node in nodes
            )

        node_descriptions = "\n".join(node_descriptions)

        rel_descriptions = set()

        for _, row in hydrate_df.iterrows():
            path = list(interleave_longest(row.nodes, row.rels))

            for i in range(0, len(path) - 1, 2):
                source_node = path[i]
                rel = path[i + 1]
                target_node = path[i + 2]

                description = self.rel_description(
                    source_node,
                    rel,
                    target_node,
                    exclude_props=exclude_props,
                )

                rel_descriptions.add(description)

        rel_descriptions = "\n".join(rel_descriptions)

        description = (
            f"Nodes:\n{node_descriptions}\n\nRelationships:\n{rel_descriptions}"
        )

        return description
