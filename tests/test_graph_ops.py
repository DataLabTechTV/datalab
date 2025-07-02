import pytest
from fixtures import graph_db_schema

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
        RETURN nodes(p) AS nodes, rels(p) AS rels
        """
    )

    return result.get_as_df()


def test_paths_descriptions(ops, paths_df):
    print(ops.path_descriptions(paths_df))
