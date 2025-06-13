from dataclasses import dataclass
from typing import Optional

import pandas as pd

from graph.ops import KuzuOps


@dataclass
class NodeBatch:
    count: int
    nodes: pd.Series
    edges: Optional[pd.DataFrame] = None

    def reindex(self):
        if self.edges is None:
            return

        self.edges.source = self.edges.source.map(
            lambda n: self.nodes[self.nodes == n].index[0]
        )

        self.edges.target = self.edges.target.map(
            lambda n: self.nodes[self.nodes == n].index[0]
        )


class KuzuNodeBatcher:
    def __init__(
        self,
        schema: str,
        *,
        include_edges: bool = False,
        reindex: bool = False,
        batch_size: int = 1000,
    ):
        self.include_edges = include_edges
        self.reindex = reindex

        self.offset = 0
        self.limit = batch_size
        self.count = 0

        self.ops = KuzuOps(schema)

    def __iter__(self):
        return self

    def __next__(self):
        nodes = self.ops.query_node_batch(self.offset, self.limit)

        if len(nodes) == 0:
            raise StopIteration

        self.count += 1

        if self.include_edges:
            edges = self.ops.query_neighbors(nodes)
            nodes = (
                pd.concat((nodes, edges.source, edges.target))
                .drop_duplicates()
                .reset_index(drop=True)
            )
        else:
            edges = None

        batch = NodeBatch(count=self.count, nodes=nodes, edges=edges)

        if self.reindex:
            batch.reindex()

        return batch
