import pytest
from fixtures import graph_db_schema
from more_itertools import interleave_longest

from graph.ops import KuzuOps


@pytest.fixture(scope="module")
def ops(graph_db_schema):
    ops = KuzuOps(graph_db_schema)
    return ops


@pytest.fixture(scope="module")
def paths_df(ops):
    result = ops.conn.execute(
        """
        MATCH p = (t:Track)-[*1..2]-(m)
        WITH p AS p
        LIMIT 10
        RETURN
            list_transform(nodes(p), n -> n.node_id) AS nodes,
            list_transform(rels(p), r -> label(r)) AS rels;
        """
    )

    paths_df = result.get_as_df()

    paths_df = (
        paths_df.apply(lambda row: list(interleave_longest(*row)), axis=1)
        .rename("paths")
        .to_frame()
    )

    return paths_df


def test_paths_descriptions(ops, paths_df):
    print(ops.path_descriptions(paths_df, exclude_props=["embedding"]))
