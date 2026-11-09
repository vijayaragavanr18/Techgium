"""
Stage 6 — Visualize the network traces used in the ablation.

Produces charts/06_traces_india.png — a two-panel view:
  left:  the 5 Indian profiles (TRAI/Ookla-modeled)
  right: the 3 research benchmarks (Belgium, Norway, sudden_drop) for reference
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.traces import TRACES, INDIAN, RESEARCH

CHARTS = Path("charts")

DEEPBLUE = "#1F3A93"
LTYELLOW = "#F5B700"
GREY = "#6B7280"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})

COLORS = {
    "bsnl_3g_rural":   "#DC2626",
    "airtel_4g_tier2": "#F97316",
    "jio_4g_metro":    "#2563EB",
    "metro_peak_hour": "#7C3AED",
    "jio_5g_metro":    "#16A34A",
    "belgium_4g":      GREY,
    "norway_3g":       "#64748B",
    "sudden_drop":     "#9CA3AF",
}
PRETTY = {
    "bsnl_3g_rural":   "BSNL 3G (rural)",
    "airtel_4g_tier2": "Airtel 4G (tier-2)",
    "jio_4g_metro":    "Jio 4G (metro)",
    "metro_peak_hour": "Metro peak-hour",
    "jio_5g_metro":    "Jio 5G (metro)",
    "belgium_4g":      "Belgium 4G",
    "norway_3g":       "Norway 3G",
    "sudden_drop":     "Sudden drop",
}


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for name in INDIAN:
        series = [v / 1000 for v in TRACES[name]]   # Mbps
        ax1.plot(series, label=PRETTY[name], color=COLORS[name], linewidth=1.8, alpha=0.9)
    ax1.set_title("Indian network profiles (modeled from TRAI MySpeed + Ookla India)",
                  color=DEEPBLUE, fontsize=12, fontweight="bold")
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Throughput (Mbps, log scale)")
    ax1.set_yscale("log")
    ax1.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax1.set_ylim(0.1, 200)

    for name in RESEARCH:
        series = [v / 1000 for v in TRACES[name]]
        ax2.plot(series, label=PRETTY[name], color=COLORS[name], linewidth=1.8, alpha=0.9)
    ax2.set_title("Research benchmarks (kept for academic comparability)",
                  color=DEEPBLUE, fontsize=12, fontweight="bold")
    ax2.set_xlabel("Time (seconds)")
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.95)

    fig.suptitle("Network traces used in the A/B/C/D ablation",
                 color=DEEPBLUE, fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(CHARTS / "06_traces_india.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("Wrote", CHARTS / "06_traces_india.png")


if __name__ == "__main__":
    main()
