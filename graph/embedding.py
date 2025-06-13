from enum import Enum

import torch
from loguru import logger as log
from torch_geometric.data import Data
from torch_sparse import SparseTensor


class NodeEmbeddingAlgo(Enum):
    FRP = 1


class NodeEmbedding:
    def __init__(self, algo: NodeEmbeddingAlgo = NodeEmbeddingAlgo.FRP):
        self.algo = algo

    def _train_frp(self):
        log.info("Training Fast Random Projection (FRP)")

        edge_index = torch.tensor([source_ids, target_ids], dtype=torch.long)
        data = Data(edge_index=edge_index)
        num_nodes = ...  # total nodes or batch nodes
        embedding_dim = 128
        R = (
            torch.randint(0, 2, (num_nodes, embedding_dim), dtype=torch.float32) * 2 - 1
        )  # ±1 matrix

        adj = SparseTensor(
            row=edge_index[0], col=edge_index[1], sparse_sizes=(num_nodes, num_nodes)
        )

        # Compute embedding: E = A * R
        embeddings = adj.matmul(R)

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
