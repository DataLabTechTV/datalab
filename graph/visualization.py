from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from adjustText import adjust_text
from matplotlib.colors import LinearSegmentedColormap, to_hex

COLOR_PALETTE = [
    "#42b0f9",
    "#ff5c92",
    "#ffcc00",
]


def set_labels(G: nx.Graph, label_props: dict[str, str]):
    """
    Set the display node "label" property to a specified property, based on the node
    type given by "_label".
    """

    for node, data in G.nodes(data=True):
        prop = label_props.get(data["_label"], node)
        data["label"] = data[prop]


def get_palette(n_colors: int = 3):
    if n_colors <= len(COLOR_PALETTE):
        return COLOR_PALETTE

    cmap = LinearSegmentedColormap.from_list("custom", COLOR_PALETTE)
    return [to_hex(cmap(i)) for i in np.linspace(0, 1, n_colors)]


def darken_color(color, amount=0.5) -> tuple[float, float, float]:
    c = mpl.colors.to_rgb(color)
    return tuple(max(0, min(1, channel * (1 - amount))) for channel in c)


def plot(
    G: nx.Graph,
    name_prop: str = "label",
    scale: float = 1.0,
    margin: float = 0.1,
    font_size: float = 8,
    font_family: Optional[str] = None,
    figsize: tuple[int, int] = (15, 10),
    dpi: int = 300,
    transparent: bool = True,
    text_no_overlap: bool = False,
    seed: int = 1337,
):
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if transparent:
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

    node_names = {n: d[name_prop] for n, d in G.nodes(data=True)}

    node_labels = list(set(nx.get_node_attributes(G, "_label").values()))

    n_node_labels = len(node_labels)
    node_palette = get_palette(n_node_labels)

    node_color_map = {label: node_palette[i] for i, label in enumerate(node_labels)}

    node_colors = [
        node_color_map.get(d["_label"], "gray") for _, d in G.nodes(data=True)
    ]

    ax.set_axis_off()
    ax.margins(margin / scale)
    plt.tight_layout()

    pos = nx.spring_layout(G, method="energy", seed=seed)

    nx.draw_networkx_nodes(
        G,
        pos=pos,
        ax=ax,
        node_color=node_colors,
        node_size=500 * scale,
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

    if text_no_overlap:
        labels = []

        for n, (x, y) in pos.items():
            label = plt.text(
                x,
                y,
                node_names[n],
                fontsize=10,
                ha="center",
                va="center",
                bbox=dict(
                    facecolor="#dadada",
                    edgecolor="#666666",
                    boxstyle="round4,pad=0.5",
                    alpha=1,
                    linewidth=1.5,
                ),
            )

            labels.append(label)

        adjust_text(labels)

    else:
        node_label_color_map = {
            n: node_color_map[d["_label"]] for n, d in G.nodes(data=True)
        }

        nx.draw_networkx_labels(
            G,
            pos=pos,
            ax=ax,
            labels=node_names,
            font_family=font_family,
            font_color=node_label_color_map,
            font_size=font_size * np.sqrt(scale),
            bbox=dict(
                facecolor="black",
                edgecolor="#333333",
                boxstyle="round4,pad=0.5",
                alpha=0.75,
                linewidth=1.5,
            ),
        )

    plt.show()
