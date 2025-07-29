import matplotlib.pyplot as plt
import networkx as nx


def plot(
    G: nx.Graph,
    label: str = "label",
    figsize: tuple[int, int] = (8, 5),
    margin: float = 0.2,
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
        node_color="skyblue",
        node_size=1000,
    )
    nx.draw_networkx_edges(G, pos=pos, ax=ax)
    nx.draw_networkx_labels(G, pos=pos, ax=ax, labels=labels)

    plt.show()
