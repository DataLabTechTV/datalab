from dataclasses import dataclass
from typing import Optional

import pandas as pd
from bidict import bidict
from loguru import logger as log

from graph.ops import KuzuOps


@dataclass
class NodeBatch:
    nr: int
    nodes: pd.DataFrame
    edges: Optional[pd.DataFrame] = None
    index: bidict = None  # original node_id -> local node index

    def __post_init__(self):
        involved_nodes = set(self.nodes.node_id)

        if self.edges is not None and len(self.edges) > 0:
            involved_nodes |= set(self.edges.source_id)
            involved_nodes |= set(self.edges.target_id)

        involved_nodes = sorted(involved_nodes)

        self.index = bidict()

        for idx, node_id in enumerate(involved_nodes):
            self.index[node_id] = idx

    def reindex(self):
        if self.edges is None or len(self.edges) == 0:
            return

        self.edges.source_id = self.edges.source_id.map(lambda sid: self.index[sid])
        self.edges.target_id = self.edges.target_id.map(lambda tid: self.index[tid])


class KuzuNodeBatcher:
    def __init__(
        self,
        schema: str,
        *,
        include_edges: bool = False,
        reindex_edges: bool = False,
        batch_size: int = 1000,
    ):
        self.include_edges = include_edges
        self.reindex_edges = reindex_edges

        self.offset = 0
        self.limit = batch_size
        self.count = 0

        self.ops = KuzuOps(schema)

    def __iter__(self):
        return self

    def __next__(self):
        log.info("Querying graph DB for node batch {}", self.count + 1)
        nodes = self.ops.query_node_batch(self.offset, self.limit)

        if len(nodes) == 0:
            raise StopIteration

        self.count += 1

        log.info(
            "Batch {} contains {} nodes, from node_id={} to node_id={}",
            len(nodes),
            nodes.node_id.min(),
            nodes.node_id.max(),
            self.count,
        )

        if self.include_edges:
            log.info("Retrieving incident edges for batch {}", self.count)
            edges = self.ops.query_neighbors(nodes)
        else:
            edges = None

        batch = NodeBatch(nr=self.count, nodes=nodes, edges=edges)

        if self.reindex_edges:
            log.info("Re-indexing edges in batch {}", self.count)
            batch.reindex()

        self.offset += self.limit

        return batch
