import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_hex

COLOR_PALETTE = [
    "#42b0f9",
    "#ff5c92",
    "#ffcc00",
    "#9900ff",
    "#92ff5c",
    "#f98242",
]


def darken_color(color, amount=0.5) -> tuple[float, float, float]:
    c = mpl.colors.to_rgb(color)
    return tuple(max(0, min(1, channel * (1 - amount))) for channel in c)


def get_palette(n_colors: int = 3, darken: bool = False, reverse: bool = False):
    color_palette = list(COLOR_PALETTE)

    if reverse:
        color_palette = reversed(color_palette)

    if darken:
        color_palette = [darken_color(c) for c in color_palette]
    else:
        color_palette = list(color_palette)

    if n_colors <= len(color_palette):
        return color_palette

    cmap = LinearSegmentedColormap.from_list("custom", color_palette)
    return [to_hex(cmap(i)) for i in np.linspace(0, 1, n_colors)]
