from enum import Enum

import torch
from loguru import logger as log

from graph.batch import KuzuNodeBatcher
from graph.ops import KuzuOps


class NodeEmbeddingAlgo(Enum):
    FRP = 1


class NodeEmbedding:
    def __init__(
        self,
        schema: str,
        *,
        dim: int = 128,
        batch_size: int = 512,
        epochs: int = 1,
        algo: NodeEmbeddingAlgo = NodeEmbeddingAlgo.FRP,
    ):
        self.schema = schema
        self.dim = dim
        self.batch_size = batch_size
        self.epochs = epochs
        self.algo = algo

        self.ops = KuzuOps(schema)

        self.dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log.info("Using device: {}", self.dev)

    def _train_frp(self):
        log.info("Training FRP (Fast Random Projection)")

        mlp = torch.nn.Sequential(
            torch.nn.Linear(self.dim, self.dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.dim, self.dim),
        ).to(self.dev)

        global_embeddings = {}
        embeddings = {}

        for epoch in range(1, self.epochs + 1):
            node_batcher = KuzuNodeBatcher(
                self.schema,
                include_edges=True,
                reindex_edges=True,
                batch_size=self.batch_size,
            )

            for batch in node_batcher:
                log.info("Training FRP: batch {}, epoch {}", batch.nr, epoch)

                edge_index = torch.tensor(
                    [batch.edges.source_id, batch.edges.target_id],
                    dtype=torch.long,
                    device=self.dev,
                )

                # Get or initialize node features
                x = []

                for node_idx in batch.index.values():
                    if node_idx not in global_embeddings:
                        global_embeddings[node_idx] = torch.randn(
                            self.dim,
                            device=self.dev,
                        )
                    x.append(global_embeddings[node_idx])

                x = torch.stack(x).to(self.dev)

                # Manual FRP aggregation
                row, col = edge_index
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

                # Write back updated embeddings for batch.nodes only
                for node_idx in batch.index.values():
                    node_id = batch.index.inv[node_idx]
                    embeddings[node_id] = updated[node_idx].detach()

        node_ids = list(embeddings.keys())

        for nr, start in enumerate(range(0, len(node_ids), self.batch_size), 1):
            log.info("Updating embeddings batch {}", nr)

            batch = {}

            for node_id in node_ids[start : start + self.batch_size]:
                batch[node_id] = embeddings[node_id].cpu().tolist()

            self.ops.update_embeddings(batch, dim=self.dim)

        if torch.cuda.is_available():
            log.info("Emptying CUDA cache")
            torch.cuda.empty_cache()

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
        if not hasattr(self, "_embeddings"):
            return

        return self._embeddings
