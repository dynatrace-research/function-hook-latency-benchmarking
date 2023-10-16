from typing import Dict, List

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import PathPatch

RC_CONTEXT = {
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": "Palatino",
    "font.size": 11,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.0,
    "savefig.dpi": 300,
    "figure.dpi": 300,
}


@matplotlib.rc_context(RC_CONTEXT)
def plot_boxplots(
    df: pd.DataFrame,
    condition_names: Dict[str, str],
    hook_names: Dict[bool, str],
    filename: str = "boxplots.pdf",
):
    fig = plt.figure(figsize=(5.5, 2.5))

    df = df.copy(deep=True)
    df["hook"] = df["hook"].map(hook_names)
    df["condition"] = df["condition"].map(condition_names)

    ax = sns.boxplot(
        data=df,
        x="condition",
        y="time",
        hue="hook",
        hue_order=[hook_names[False], hook_names[True]],
        palette=["#b2df8a", "#a6cee3"],
        width=0.75,
        showcaps=True,
        showfliers=False,
        linewidth=0.5,
    )

    sns.despine(offset=10, trim=False)
    ax.set_xlabel("")
    ax.set_ylabel("RTT (ms)")
    ax.set_ylim(0, 5)
    ax.legend(loc="lower left", frameon=False, fancybox=False, ncol=2)
    ax.legend_.set_bbox_to_anchor((0, -0.1, 1, 1))
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    ax.yaxis.grid(
        True,
        ls=(0, (1, 3)),
        which="major",
        color="grey",
        alpha=0.25,
        lw=1,
    )

    _adjust_box_widths(fig, 0.8)

    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


@matplotlib.rc_context(RC_CONTEXT)
def plot_lagplots(
    df: pd.DataFrame,
    conditions: List[List[str]],
    condition_names: Dict[str, str],
    hook_names: Dict[bool, str],
    cutoff: int,
    filename: str = "lagplots.pdf",
):
    colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3"]
    fig, axes = plt.subplots(
        len(conditions),
        1,
        figsize=(5.5, 2.5),
        sharex=True,
    )

    print(f"\\newcommand{{\\TestLagplotCutoff}}{{{cutoff:,d}}}")

    df = df.query("hook == False and iteration < @cutoff").copy(deep=True)
    df["hook"] = df["hook"].map(hook_names)
    df["condition"] = df["condition"].map(condition_names)

    for condition, ax in zip(conditions, axes):
        sns.lineplot(
            ax=ax,
            data=df,
            y="time",
            x="iteration",
            hue="condition",
            hue_order=[condition_names[e] for e in condition],
            linewidth=0.25,
            alpha=0.75,
            palette=colors[1:3],
            rasterized=True,
        )

        legend = ax.legend(
            loc="lower left",
            frameon=False,
            fancybox=False,
            ncol=2,
            fontsize=10,
        )
        for lh in legend.legendHandles:
            lh.set_linewidth(2)
            lh.set_alpha(1)

        sns.despine(ax=ax, offset=10, trim=False)
        ax.legend_.set_bbox_to_anchor((0, -0.4, 1, 1))
        ax.set_xlabel("Iterations")
        ax.set_ylabel("RTT (ms)", fontsize=9)
        ax.set_yscale("log")
        ax.set_ylim(1, 20)
        ax.xaxis.grid(False)
        ax.yaxis.grid(
            True,
            ls=(0, (1, 3)),
            which="both",
            color="grey",
            alpha=0.25,
            lw=1,
        )

        tickform = matplotlib.ticker.FuncFormatter(
            lambda x, _: format(int(x), ","),
        )
        ax.xaxis.set_major_formatter(tickform)
        ax.yaxis.set_major_formatter(tickform)

    fig.tight_layout()
    fig.savefig(filename)
    plt.show()


def _adjust_box_widths(fig, factor):
    """
    Adjust the widths of a seaborn-generated boxplot.

    (c) 2019-07-09, by Eric (https://stackoverflow.com/a/56955897/927377)
    Dynatrace has not made any changes to this code. This code is supplied
    without warranty, and is available under Creative Commons BY-SA 4.0.

    :param fig: The figure object containing the boxplot
    :param factor: The factor by which to adjust the width
    """

    # iterating through Axes instances
    for ax in fig.axes:
        # iterating through axes artists:
        for c in ax.get_children():
            # searching for PathPatches
            if isinstance(c, PathPatch):
                # getting current width of box:
                p = c.get_path()
                verts = p.vertices
                verts_sub = verts[:-1]
                xmin = np.min(verts_sub[:, 0])
                xmax = np.max(verts_sub[:, 0])
                xmid = 0.5 * (xmin + xmax)
                xhalf = 0.5 * (xmax - xmin)

                # setting new width of box
                xmin_new = xmid - factor * xhalf
                xmax_new = xmid + factor * xhalf
                verts_sub[verts_sub[:, 0] == xmin, 0] = xmin_new
                verts_sub[verts_sub[:, 0] == xmax, 0] = xmax_new

                # setting new width of median line
                for line in ax.lines:
                    if np.all(line.get_xdata() == [xmin, xmax]):
                        line.set_xdata([xmin_new, xmax_new])
