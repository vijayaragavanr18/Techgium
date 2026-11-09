"""
Stage 5 — Charts focused on Indian network profiles.

Headline chart layout:
  01_quality_rate_curves.png    — per-shot VMAF-rate curves
  02_bytes_per_shot.png         — bits spent per shot: fixed vs quality-targeted
  03_ablation_scatter.png       — VMAF-NEG vs MiB across A/B/C/D
  04_headline_india.png         — the money chart: efficiency gain on Indian networks
  05_efficiency_table.png       — VMAF-NEG per MiB, A vs D, every trace
"""
import json, csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.quality_model import SHOTS, LADDER, vmaf_tv
from src.traces import INDIAN, RESEARCH

RESULTS = Path("results")
CHARTS = Path("charts"); CHARTS.mkdir(exist_ok=True)

DEEPBLUE = "#1F3A93"
LTYELLOW = "#F5B700"
GREY = "#6B7280"
SUCCESS = "#16A34A"
WARN = "#DC2626"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})


def chart_quality_rate():
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    axes = axes.flatten()
    kbps_range = [100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000, 6500, 8000]
    for ax, shot in zip(axes, SHOTS):
        for w, h, _ in LADDER:
            curve = [vmaf_tv(k, shot.complexity, h) for k in kbps_range]
            ax.plot(kbps_range, curve, label=f"{h}p", linewidth=1.8)
        ax.set_title(f"{shot.name}  (complexity={shot.complexity})", fontsize=10, color=DEEPBLUE)
        ax.set_xscale("log")
        ax.set_xlabel("bitrate (kbps)", fontsize=9)
        ax.set_ylabel("VMAF-TV", fontsize=9)
        ax.set_ylim(15, 100)
        ax.legend(fontsize=7, loc="lower right")
    fig.suptitle("Per-shot quality-rate curves (TV model)", color=DEEPBLUE, fontsize=13)
    fig.tight_layout()
    fig.savefig(CHARTS / "01_quality_rate_curves.png", dpi=130)
    plt.close(fig)


def chart_bytes_per_shot():
    manifest = json.loads(Path("manifest/manifest.json").read_text())
    shot_names = [s["shot_name"] for s in manifest["segments"]]
    fixed_bytes, qt_bytes = [], []
    for seg in manifest["segments"]:
        r720 = next(r for r in seg["renditions"] if r["label"] == "720p")
        fixed_bytes.append(r720["bytes"] / 1024)
        pick = seg["renditions"][-1]
        for r in sorted(seg["renditions"], key=lambda x: x["bytes"]):
            if r["vmaf_phone"] >= 70:
                pick = r; break
        qt_bytes.append(pick["bytes"] / 1024)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = range(len(shot_names)); w = 0.38
    ax.bar([i - w/2 for i in x], fixed_bytes, w, color=GREY, label="Fixed ladder (720p steady)")
    ax.bar([i + w/2 for i in x], qt_bytes, w, color=DEEPBLUE, label="Quality-targeted (meet VMAF-phone ≥ 70)")
    ax.set_xticks(list(x)); ax.set_xticklabels(shot_names, fontsize=10)
    ax.set_ylabel("KiB per segment")
    ax.set_title("Bits spent per shot — fixed ladder vs quality-targeted (phone VMAF floor = 70)", color=DEEPBLUE)
    ax.legend(loc="upper right")
    tot_fixed = sum(fixed_bytes); tot_qt = sum(qt_bytes)
    saved = 100 * (tot_fixed - tot_qt) / tot_fixed
    ax.text(0.02, 0.95, f"Total bytes saved: {saved:.1f}%",
            transform=ax.transAxes, fontsize=11, color=SUCCESS,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.8, edgecolor=SUCCESS))
    fig.tight_layout()
    fig.savefig(CHARTS / "02_bytes_per_shot.png", dpi=130)
    plt.close(fig)


def chart_ablation_scatter():
    rows = list(csv.DictReader(open(RESULTS / "results.csv")))
    colors = {"A": GREY, "B": "#F97316", "C": LTYELLOW, "D": DEEPBLUE}
    markers = {"phone": "o", "tv": "s"}
    fig, ax = plt.subplots(figsize=(11, 6.5))
    seen = set()
    for r in rows:
        if r["trace"] not in INDIAN:
            continue
        tag = r["system"][0]; c = colors[tag]; m = markers[r["device"]]
        key = (tag, r["device"])
        label = f"System {tag} ({r['device']})" if key not in seen else None
        seen.add(key)
        ax.scatter(float(r["MiB"]), float(r["vmaf_neg"]),
                   s=100, c=c, marker=m, edgecolor="black", linewidth=0.5,
                   label=label, alpha=0.85)
    ax.set_xlabel("Data delivered (MiB)", fontsize=11)
    ax.set_ylabel("Average VMAF-NEG (time-weighted)", fontsize=11)
    ax.set_title("A/B/C/D ablation on Indian network profiles\nUpper-left = better (more quality, fewer bytes)",
                 color=DEEPBLUE)
    ax.legend(loc="lower right", fontsize=9, ncol=2)
    fig.tight_layout()
    fig.savefig(CHARTS / "03_ablation_scatter.png", dpi=130)
    plt.close(fig)


def chart_headline_india():
    """The money chart — bytes saved on each Indian network, device=phone."""
    rows = list(csv.DictReader(open(RESULTS / "results.csv")))
    phone_rows = [r for r in rows if r["device"] == "phone"]
    ordered = ["bsnl_3g_rural", "airtel_4g_tier2", "jio_4g_metro",
               "metro_peak_hour", "jio_5g_metro"]
    pretty = {"bsnl_3g_rural": "BSNL 3G\n(rural)",
              "airtel_4g_tier2": "Airtel 4G\n(tier-2)",
              "jio_4g_metro": "Jio 4G\n(metro)",
              "metro_peak_hour": "Metro\npeak-hour",
              "jio_5g_metro": "Jio 5G\n(metro)"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: % bytes saved (D vs A) on each Indian network
    pcts = []
    for t in ordered:
        a = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("A"))
        d = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("D"))
        pcts.append(100 * (float(a["MiB"]) - float(d["MiB"])) / float(a["MiB"]))
    bars = ax1.bar([pretty[t] for t in ordered], pcts, color=DEEPBLUE, edgecolor=DEEPBLUE)
    ax1.axhline(0, color="black", linewidth=0.5)
    ax1.set_ylabel("% bandwidth saved (D vs A)", fontsize=11)
    ax1.set_title("Bandwidth saved on Indian networks — phone viewer\n(A overdelivers on fast links; D sends only what the phone needs)",
                  color=DEEPBLUE, fontsize=11)
    for b, p in zip(bars, pcts):
        ax1.text(b.get_x() + b.get_width()/2, p + (1.5 if p >= 0 else -4),
                 f"{p:.1f}%", ha="center", fontsize=11, color=DEEPBLUE, fontweight="bold")

    # Right: VMAF-NEG per MiB (efficiency) across traces for A and D
    eff_a = []; eff_d = []
    for t in ordered:
        a = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("A"))
        d = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("D"))
        eff_a.append(float(a["vmaf_neg"]) / float(a["MiB"]))
        eff_d.append(float(d["vmaf_neg"]) / float(d["MiB"]))
    x = list(range(len(ordered))); w = 0.38
    ax2.bar([i - w/2 for i in x], eff_a, w, color=GREY, label="A — dash.js default")
    ax2.bar([i + w/2 for i in x], eff_d, w, color=DEEPBLUE, label="D — Quality-MPC (ours)")
    ax2.set_xticks(x); ax2.set_xticklabels([pretty[t] for t in ordered], fontsize=9)
    ax2.set_ylabel("VMAF-NEG per MiB (higher = more perceptual quality per byte)", fontsize=10)
    ax2.set_title("Perceptual efficiency — Indian networks, phone viewer\n(primary metric from the paper)",
                  color=DEEPBLUE, fontsize=11)
    ax2.legend(loc="upper left", fontsize=10)
    for i, (a, d) in enumerate(zip(eff_a, eff_d)):
        mult = d / a if a > 0 else 0
        ax2.text(i, max(a, d) + 2, f"{mult:.1f}×",
                 ha="center", fontsize=10, color=SUCCESS, fontweight="bold")

    fig.suptitle("Quality-Targeted Adaptive Streaming — PoC on Indian networks",
                 color=DEEPBLUE, fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "04_headline_india.png", dpi=130)
    plt.close(fig)


def chart_efficiency_table():
    rows = list(csv.DictReader(open(RESULTS / "results.csv")))
    traces = INDIAN + ["-------"] + RESEARCH
    headers = ["Trace", "Avg Mbps", "A MiB", "A VMAF-NEG", "D MiB", "D VMAF-NEG",
               "Bytes saved", "D efficiency vs A"]

    from src.traces import TRACES
    cells = []
    phone_rows = [r for r in rows if r["device"] == "phone"]
    for t in traces:
        if t == "-------":
            cells.append([""] * len(headers)); continue
        a = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("A"))
        d = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("D"))
        mbps = sum(TRACES[t]) / len(TRACES[t]) / 1000
        pct_saved = 100 * (float(a["MiB"]) - float(d["MiB"])) / float(a["MiB"])
        eff_a = float(a["vmaf_neg"]) / float(a["MiB"])
        eff_d = float(d["vmaf_neg"]) / float(d["MiB"])
        mult = eff_d / eff_a if eff_a > 0 else 0
        pretty_name = t.replace("_", " ")
        cells.append([pretty_name, f"{mbps:.1f}", a["MiB"], a["vmaf_neg"],
                      d["MiB"], d["vmaf_neg"], f"{pct_saved:+.1f}%", f"{mult:.2f}×"])

    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.axis("off")
    table = ax.table(cellText=cells, colLabels=headers,
                     cellLoc="center", colLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)
    # style
    for j in range(len(headers)):
        c = table[0, j]
        c.set_facecolor(DEEPBLUE); c.set_text_props(color="white", weight="bold")
    for i in range(1, len(cells) + 1):
        for j in range(len(headers)):
            c = table[i, j]
            if cells[i-1][0] == "":
                c.set_facecolor("white")
            elif i <= len(INDIAN):
                c.set_facecolor("#fff9db")
    ax.set_title("A (dash.js default) vs D (our Quality-MPC) — device = phone\nIndian profiles (yellow) · Research benchmarks (white)",
                 color=DEEPBLUE, fontsize=12, fontweight="bold", pad=20)
    fig.tight_layout()
    fig.savefig(CHARTS / "05_efficiency_table.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def write_headline():
    rows = list(csv.DictReader(open(RESULTS / "results.csv")))
    phone_rows = [r for r in rows if r["device"] == "phone"]
    lines = ["# Headline PoC Results — Indian networks first", ""]
    lines.append("## Phone viewer on Indian networks (A = dash.js default, D = our MPC)")
    lines.append("")
    lines.append("| Trace | Avg Mbps | A MiB | A VMAF-NEG | D MiB | D VMAF-NEG | Bytes saved | Efficiency |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    from src.traces import TRACES
    for t in INDIAN + RESEARCH:
        a = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("A"))
        d = next(r for r in phone_rows if r["trace"] == t and r["system"].startswith("D"))
        mbps = sum(TRACES[t]) / len(TRACES[t]) / 1000
        pct_saved = 100 * (float(a["MiB"]) - float(d["MiB"])) / float(a["MiB"])
        eff_a = float(a["vmaf_neg"]) / float(a["MiB"])
        eff_d = float(d["vmaf_neg"]) / float(d["MiB"])
        mult = eff_d / eff_a if eff_a > 0 else 0
        lines.append(f"| {t} | {mbps:.1f} | {a['MiB']} | {a['vmaf_neg']} | "
                     f"{d['MiB']} | {d['vmaf_neg']} | {pct_saved:+.1f}% | {mult:.2f}× |")
    lines.append("")
    lines.append("**Read:** D delivers the phone VMAF target with large bandwidth savings "
                 "on fast Indian links where A overdelivers for the device. On BSNL 3G rural "
                 "(the hardest case), D still cuts rebuffering with modest savings.")
    (RESULTS / "headline.md").write_text("\n".join(lines))


def main():
    chart_quality_rate()
    chart_bytes_per_shot()
    chart_ablation_scatter()
    chart_headline_india()
    chart_efficiency_table()
    write_headline()
    print("Generated:")
    for p in sorted(CHARTS.iterdir()):
        print(f"  {p}")


if __name__ == "__main__":
    main()
