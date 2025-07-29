from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx

COLOR_PALETTE = [
    "#42b0f9",
    "#ffcc00",
    "#ff5c92",
]


def plot(
    G: nx.Graph,
    label: str = "label",
    figsize: tuple[int, int] = (8, 5),
    margin: float = 0.2,
    font_family: Optional[str] = None,
):
    _, ax = plt.subplots(figsize=figsize)

    pos = nx.circular_layout(G)
    labels = {n: d[label] for n, d in G.nodes(data=True)}

    ax.set_axis_off()
    ax.margins(margin)
    plt.tight_layout()

    nx.draw_networkx_nodes(
        G,
        pos=pos,
        ax=ax,
        node_color=COLOR_PALETTE[0],
        node_size=1000,
    )

    nx.draw_networkx_edges(
        G,
        pos=pos,
        ax=ax,
        edge_color=COLOR_PALETTE[2],
    )

    nx.draw_networkx_labels(
        G,
        pos=pos,
        ax=ax,
        labels=labels,
        font_family=font_family,
        font_color=COLOR_PALETTE[2],
        font_size=10,
        bbox=dict(
            facecolor="white",
            edgecolor=COLOR_PALETTE[2],
            boxstyle="round,pad=0.4",
            alpha=0.85,
        ),
    )

    plt.show()
