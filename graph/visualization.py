from pathlib import Path
from typing import Optional

import geopandas as gpd
import kagglehub
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from shared.color import COLOR_PALETTE, get_palette


def set_labels(G: nx.Graph, label_props: dict[str, str]):
    """
    Set the display node "label" property to a specified property, based on the node
    type given by "_label".
    """

    for node, data in G.nodes(data=True):
        prop = label_props.get(data["_label"], node)
        data["label"] = data[prop]


def plot(
    G: nx.Graph,
    name_prop: str = "label",
    node_classes: Optional[dict[str, str]] = None,
    hide_edges: bool = False,
    show_edge_labels: bool = False,
    scale: float = 1.0,
    margin: float = 0.1,
    font_size: float = 8,
    font_family: Optional[str] = None,
    figsize: tuple[int, int] = (15, 10),
    dpi: int = 300,
    transparent: bool = True,
    seed: int = 1337,
):
    # TODO: refactor: split maybe into a class, while keeping this caller function

    # Node fill color map
    # ===================

    node_labels = list(set(nx.get_node_attributes(G, "_label").values()))
    node_palette = get_palette(len(node_labels))

    node_color_map_by_label = {
        label: node_palette[i] for i, label in enumerate(node_labels)
    }

    # Node stroke color map
    # =====================

    node_classes = node_classes or {}
    node_classes_idx = {ncls: i for i, ncls in enumerate(node_classes.keys())}
    node_edge_palette = get_palette(len(node_classes), reverse=True)

    node_edgecolor_map_by_id = {}

    for ncls, nids in node_classes.items():
        i = node_classes_idx[ncls]
        for nid in nids:
            node_edgecolor_map_by_id[nid] = node_edge_palette[i]

    # Build color maps
    # ================

    node_colors = []
    node_edgecolors = []
    node_linewidths = []

    for _, d in G.nodes(data=True):
        color = node_color_map_by_label.get(d["_label"], "gray")
        node_colors.append(color)

        edgecolor = node_edgecolor_map_by_id.get(d["node_id"], color)
        node_edgecolors.append(edgecolor)

        if d["node_id"] in node_edgecolor_map_by_id:
            node_linewidths.append(2)
        else:
            node_linewidths.append(1)

    # Visualization
    # =============

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if transparent:
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

    ax.set_axis_off()
    ax.margins(margin / scale)
    plt.tight_layout()

    pos = nx.spring_layout(G, method="energy", weight="vis_weight", seed=seed)

    nx.draw_networkx_nodes(
        G,
        pos=pos,
        ax=ax,
        node_color=node_colors,
        edgecolors=node_edgecolors,
        linewidths=node_linewidths,
        node_size=500 * scale,
        alpha=1,
    )

    node_names = {n: d[name_prop] for n, d in G.nodes(data=True)}

    node_label_color_map = {
        n: node_edgecolor_map_by_id.get(
            d["node_id"],
            node_color_map_by_label[d["_label"]],
        )
        for n, d in G.nodes(data=True)
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

    if not hide_edges:
        nx.draw_networkx_edges(
            G,
            pos=pos,
            ax=ax,
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            min_target_margin=15 * scale,
            edge_color=COLOR_PALETTE[1],
        )

    if show_edge_labels:
        edge_labels = {(s, t): d["_label"] for s, t, d in G.edges(data=True)}

        nx.draw_networkx_edge_labels(
            G,
            pos=pos,
            ax=ax,
            font_family=font_family,
            font_color=COLOR_PALETTE[1],
            font_size=font_size * np.sqrt(scale),
            edge_labels=edge_labels,
            bbox=dict(
                facecolor="black",
                edgecolor="#333333",
                boxstyle="round4,pad=0.5",
                alpha=0.75,
                linewidth=1.5,
            ),
        )

    plt.show()


def plot_map(
    data: pd.DataFrame,
    code_col: str,
    class_col: str,
    figsize: tuple[int, int] = (15, 15),
    dpi: int = 300,
    transparent: bool = True,
):
    geo_path = kagglehub.dataset_download("kopfstein/natural-earth")
    geo_path = Path(geo_path) / "110m_cultural/ne_110m_admin_0_countries.shx"

    world = gpd.read_file(geo_path)

    highlighted = world.merge(data, left_on="ISO_A3", right_on=code_col, how="inner")

    class_list = highlighted[class_col].drop_duplicates().to_list()
    palette = get_palette(len(class_list))
    class_color_map = {class_: palette[i] for i, class_ in enumerate(class_list)}

    highlighted["color"] = highlighted[class_col].map(
        lambda class_: class_color_map[class_]
    )

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    if transparent:
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")

    ax.set_axis_off()
    ax.margins(0)
    plt.tight_layout()

    world.plot(
        ax=ax,
        facecolor="lightgray",
        edgecolor="black",
    )

    highlighted.plot(
        ax=ax,
        color=highlighted["color"].fillna("lightgray"),
        edgecolor="black",
    )

    plt.show()
