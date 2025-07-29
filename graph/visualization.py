from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_hex

COLOR_PALETTE = [
    "#42b0f9",
    "#ff5c92",
    "#ffcc00",
]


def get_palette(n_colors: int = 3):
    if n_colors <= len(COLOR_PALETTE):
        return COLOR_PALETTE

    cmap = LinearSegmentedColormap.from_list("custom", COLOR_PALETTE)
    return [to_hex(cmap(i)) for i in np.linspace(0, 1, n_colors)]


def plot(
    G: nx.Graph,
    name_prop: str = "label",
    figsize: tuple[int, int] = (8, 5),
    margin: float = 0.2,
    font_family: Optional[str] = None,
    transparent: bool = True,
):
    fig, ax = plt.subplots(figsize=figsize)

    if transparent:
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

    node_names = {n: d[name_prop] for n, d in G.nodes(data=True)}

    node_labels = list(set(nx.get_node_attributes(G, "_label").values()))

    n_node_labels = len(node_labels)
    node_palette = get_palette(n_node_labels)

    node_label_color_map = {
        label: node_palette[i] for i, label in enumerate(node_labels)
    }

    node_colors = [
        node_label_color_map.get(d["_label"], "gray") for _, d in G.nodes(data=True)
    ]

    ax.set_axis_off()
    ax.margins(margin)
    plt.tight_layout()

    pos = nx.circular_layout(G)

    nx.draw_networkx_nodes(
        G,
        pos=pos,
        ax=ax,
        node_color=node_colors,
        node_size=1000,
        alpha=1,
    )

    nx.draw_networkx_edges(
        G,
        pos=pos,
        ax=ax,
        arrows=True,
        arrowsize=20,
        arrowstyle="->",
        min_target_margin=15,
        edge_color=COLOR_PALETTE[1],
    )

    nx.draw_networkx_labels(
        G,
        pos=pos,
        ax=ax,
        labels=node_names,
        font_family=font_family,
        font_color="#222222",
        font_size=10,
        bbox=dict(
            facecolor="#dadada",
            edgecolor="#666666",
            boxstyle="round4,pad=0.5",
            alpha=1,
            linewidth=1.5,
        ),
    )

    plt.show()
