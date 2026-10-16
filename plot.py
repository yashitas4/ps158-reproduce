"""Plot the wealth gap between families headed by college graduates and by
people with a high school education or less, SCF 1989-2025, styled after
The Economist's charts.

Reads data/scf_networth_by_education.csv (made by get_data.py) and writes
figures/networth_by_education.png (means) and
figures/networth_by_education_median.png (medians).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.ticker import StrMethodFormatter

IN_FILE = Path("data/scf_networth_by_education.csv")

# Which families to plot (see get_data.py for the options)
FAMILIES = "With children"

# One figure per statistic; the ratio panels share a scale so they compare directly
STATS = {
    "mean_networth": {"word": "mean", "ymax": 2500, "ystep": 500,
                      "out": Path("figures/networth_by_education.png")},
    "median_networth": {"word": "median", "ymax": 700, "ystep": 100,
                        "out": Path("figures/networth_by_education_median.png")},
}
RATIO_YMAX = 14

COLLEGE = "College degree"
HS_OR_LESS = "High school or less"

DARK_BLUE = "#006ba2"
LIGHT_BLUE = "#3ebcd2"
RED = "#e3120b"
INK = "#0c0c0c"
INK_SECONDARY = "#595959"
GRID = "#b7c6cf"

plt.rcParams["font.family"] = ["Arial", "Helvetica", "sans-serif"]


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=10, fontweight="bold", color=INK, pad=22)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.1)
    ax.yaxis.tick_right()
    ax.tick_params(axis="y", length=0, labelsize=9, colors=INK, pad=2)
    ax.tick_params(axis="x", length=4, labelsize=9, colors=INK, color=INK)
    ax.set_xticks([1989, 1995, 2001, 2007, 2013, 2019, 2025])
    ax.set_xlim(1988, 2026)
    for label in ax.get_yticklabels():
        label.set_verticalalignment("bottom")


def end_label(ax, x, y, text, dy=7):
    ax.annotate(text, (x, y), xytext=(0, dy), textcoords="offset points",
                ha="center", fontsize=8.5, color=INK)


def plot(df, stat, word, ymax, ystep, out):
    values = df.pivot(index="year", columns="group", values=stat) / 1e3
    ratio = values[COLLEGE] / values[HS_OR_LESS]
    years = values.index
    first, last = years[0], years[-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 5), gridspec_kw={"wspace": 0.22})
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(top=0.74, bottom=0.17, left=0.04, right=0.95)

    # Red tag, headline and subtitle
    fig.add_artist(Rectangle((0.04, 0.965), 0.035, 0.012, transform=fig.transFigure,
                             facecolor=RED, edgecolor="none"))
    fig.text(0.04, 0.93, "Degrees of wealth", fontsize=15, fontweight="bold",
             color=INK, va="top")
    fig.text(0.04, 0.87,
             f"United States, {word} net worth of families with children, by education of "
             "head of household*, 2025 prices",
             fontsize=10.5, color=INK, va="top")

    # Panel 1: the two groups
    for group, color, label in [(COLLEGE, DARK_BLUE, "College degree"),
                                (HS_OR_LESS, LIGHT_BLUE, "High school or less")]:
        ax1.plot(years, values[group], color=color, linewidth=2.2, label=label,
                 solid_capstyle="round")
        for year in (first, last):
            end_label(ax1, year, values.loc[year, group], f"{values.loc[year, group]:,.0f}")
    style(ax1, "$'000")
    ax1.set_ylim(0, ymax)
    ax1.set_yticks(range(0, ymax + 1, ystep))
    ax1.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax1.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False,
               fontsize=9, labelcolor=INK, handlelength=1.4, borderaxespad=0.2,
               columnspacing=1.2, handletextpad=0.5)

    # Panel 2: the gap as a ratio
    ax2.plot(years, ratio, color=DARK_BLUE, linewidth=2.2, solid_capstyle="round")
    for year in (first, ratio.idxmax(), last):
        end_label(ax2, year, ratio[year], f"{ratio[year]:.1f}")
    style(ax2, f"College {word} ÷ high-school-or-less {word}")
    ax2.set_ylim(0, RATIO_YMAX)
    ax2.set_yticks(range(0, RATIO_YMAX + 1, 2))

    fig.text(0.04, 0.06,
             "Sources: Federal Reserve Board, Survey of Consumer Finances, 1989–2025; "
             "own calculations",
             fontsize=8, color=INK_SECONDARY, va="top")
    fig.text(0.04, 0.025,
             "*SCF reference person. Families with a child of the reference person living at "
             f"home. High school or less includes no diploma. Weighted {word}s, five implicates pooled",
             fontsize=8, color=INK_SECONDARY, va="top")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print(f"Wrote {out}")


def main():
    df = pd.read_csv(IN_FILE)
    df = df[df["families"] == FAMILIES]
    for stat, opts in STATS.items():
        plot(df, stat, **opts)


if __name__ == "__main__":
    main()
