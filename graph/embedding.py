from enum import Enum

import torch
from loguru import logger as log
from torch.sparse import SparseSemiStructuredTensorCUSPARSELT
from torch_geometric.data import Data
from torch_sparse import SparseTensor

from graph.batch import KuzuNodeBatcher


class NodeEmbeddingAlgo(Enum):
    FRP = 1


class NodeEmbedding:
    def __init__(
        self,
        schema: str,
        *,
        dim: int = 128,
        batch_size: int = 512,
        epochs: int = 10,
        algo: NodeEmbeddingAlgo = NodeEmbeddingAlgo.FRP,
    ):
        self.schema = schema
        self.dim = dim
        self.batch_size = batch_size
        self.epochs = epochs
        self.algo = algo

        self.dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log.info("Using device: {}", self.dev)

        self._embeddings = None

    def _train_frp(self):
        log.info("Training Fast Random Projection (FRP)")

        mlp = torch.nn.Sequential(
            torch.nn.Linear(self.dim, self.dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.dim, self.dim),
        ).to(self.dev)

        embeddings = {}

        node_batcher = KuzuNodeBatcher(
            self.schema,
            include_edges=True,
            reindex=True,
            batch_size=self.batch_size,
        )

        for epoch in range(1, self.epochs + 1):
            log.info("Training epoch {}", epoch)

            for batch in node_batcher:
                log.info("Training batch {}", batch.count)

                edge_index = torch.tensor(
                    [batch.edges.source, batch.edges.target],
                    dtype=torch.long,
                    device=self.dev,
                )

                # Get or initialize node features
                x = []

                for idx in batch.nodes.index:
                    if idx not in embeddings:
                        embeddings[idx] = torch.randn(self.dim, device=self.dev)
                    x.append(embeddings[idx])

                x = torch.stack(x).to(self.dev)

                # Manual FRP aggregation
                row, col = edge_index  # row: target, col: source
                agg = torch.zeros_like(x, device=self.dev)
                agg.index_add_(0, row, x[col])

                deg = (
                    torch.bincount(row, minlength=x.size(0))
                    .clamp(min=1)
                    .unsqueeze(1)
                    .to(self.dev)
                )

                agg = agg / deg

                # Optionally apply non-linear update
                updated = mlp(agg)

                # Write back updated embeddings for batch_nodes only
                for idx, node in batch.nodes.items():
                    embeddings[node] = updated[idx].detach()

        self._embeddings = embeddings

    def train(self):
        match self.algo:
            case NodeEmbeddingAlgo.FRP:
                self._train_frp()
            case _:
                log.error(
                    "Unsupported algorithm: options include {}",
                    ", ".join(algo.name for algo in NodeEmbeddingAlgo),
                )
                return

    @property
    def embeddings(self):
        # TODO: make sure no torch tensors are returned here
        return self._embeddings
