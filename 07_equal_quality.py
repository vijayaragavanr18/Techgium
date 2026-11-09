"""
Stage 7 - Equal-quality check (fair baselines + quality sweep).

Why: 04_simulate_abr.py compares D against an unconstrained dash.js (System A) that
pushes 1080p to a phone. That measures "overshoot removal", not "same quality, fewer bytes".
Here we sweep System D's quality floor to trace its bytes-vs-quality curve, add device-capped
baselines (dash.js limitBitrateByPortal-style 720p / 480p caps), and report the bytes D needs
to MATCH each baseline's phone-model VMAF.

Quality metric: phone-model VMAF for the phone viewer (the model D targets).
(NOTE: 'vmaf_neg' in 04_simulate_abr.py is derived from the TV-model score; do not use it for phones.)

Run from the repo root:  python 07_equal_quality.py
Outputs: results/equal_quality.json, results/equal_quality.md, charts/07_pareto_jio4g.png
"""
import copy
import json
from pathlib import Path

from src.player import simulate
from src.abr.base import ABR
from src.abr.fixed import ThroughputABR
from src.abr.bola import BOLA
from src.abr import quality_mpc as qm
from src.abr.quality_mpc import OurLadderThroughput, QualityMPC
from src.traces import TRACES

TOL = 0.5          # phone-VMAF points; a just-noticeable difference is roughly 6
FLOORS = range(44, 100, 2)
manifest = json.loads(Path("manifest/manifest.json").read_text())
RES = Path("results"); RES.mkdir(exist_ok=True)
CH = Path("charts"); CH.mkdir(exist_ok=True)


class Capped(ABR):
    """Portal-limited baseline: ignore renditions taller than max_h."""
    def __init__(self, inner, max_h): self.inner, self.max_h = inner, max_h

    def choose(self, seg, state):
        s = copy.deepcopy(seg)
        s["renditions"] = [r for r in seg["renditions"] if r["height"] <= self.max_h]
        return self.inner.choose(s, state)


def run(abr, trace, device):
    m = simulate(manifest, abr, trace, device=device)
    q = m.avg_vmaf_phone() if device == "phone" else m.avg_vmaf_tv()
    return {"MiB": round(m.mbytes(), 3), "vmaf": round(q, 2), "rebuffer_s": round(m.rebuffer_time_s, 3)}


def d_sweep(trace, device):
    orig = qm.base_vmaf_floor
    pts = []
    for f in FLOORS:
        qm.base_vmaf_floor = lambda dev, ds, f=f: float(f)
        pts.append({"floor": f, **run(QualityMPC(), trace, device)})
    qm.base_vmaf_floor = orig
    return pts


BASELINES = {
    "A  dash.js (unconstrained)": ThroughputABR(),
    "A720  dash.js, 720p cap": Capped(ThroughputABR(), 720),
    "A480  dash.js, 480p cap": Capped(ThroughputABR(), 480),
    "B  BOLA": BOLA(),
    "C  our ladder + throughput ABR": OurLadderThroughput(),
}

out = {}
for device in ["phone", "tv"]:
    for tname, trace in TRACES.items():
        sweep = d_sweep(trace, device)
        rec = {"D_default": run(QualityMPC(), trace, device), "D_sweep": sweep, "baselines": {}}
        for bname, b in BASELINES.items():
            r = run(b, trace, device)
            feas = [p for p in sweep if p["vmaf"] >= r["vmaf"] - TOL and p["rebuffer_s"] <= r["rebuffer_s"] + 1e-9]
            best = min(feas, key=lambda p: p["MiB"]) if feas else None
            r["D_at_equal_quality"] = best
            r["bytes_saved_pct"] = round(100 * (r["MiB"] - best["MiB"]) / r["MiB"], 1) if best else None
            rec["baselines"][bname] = r
        out[f"{device}/{tname}"] = rec

(RES / "equal_quality.json").write_text(json.dumps(out, indent=2))

lines = ["# Equal-quality check (phone-model VMAF, tolerance %.1f)\n" % TOL]
for key, rec in out.items():
    if not key.startswith("phone/"):
        continue
    lines.append(f"\n## {key}  (D default: {rec['D_default']['MiB']} MiB, VMAF {rec['D_default']['vmaf']})\n")
    lines.append("| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |\n|---|---:|---:|---:|---:|---:|")
    for bname, r in rec["baselines"].items():
        d = r["D_at_equal_quality"]
        lines.append(f"| {bname} | {r['MiB']} | {r['vmaf']} | {r['rebuffer_s']} | "
                     f"{d['MiB'] if d else 'n/a'} | {str(r['bytes_saved_pct']) + '%' if d else 'n/a'} |")
(RES / "equal_quality.md").write_text("\n".join(lines))

# Pareto chart for Jio 4G metro, phone viewer
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rec = out["phone/jio_4g_metro"]
    pts = rec["D_sweep"]
    front = sorted([p for p in pts if not any((q["MiB"] <= p["MiB"] and q["vmaf"] >= p["vmaf"] and (q["MiB"], q["vmaf"]) != (p["MiB"], p["vmaf"])) for q in pts)],
                   key=lambda p: p["MiB"])
    fig, ax = plt.subplots(figsize=(6.4, 3.65), dpi=200)
    ax.scatter([p["MiB"] for p in pts], [p["vmaf"] for p in pts], s=10, color="#9FB1D1", zorder=2, label="D at each floor setting")
    ax.plot([p["MiB"] for p in front], [p["vmaf"] for p in front], "-o", color="#2B4EA2", ms=4, lw=1.8, zorder=3, label="D best achievable (frontier)")
    d0 = rec["D_default"]
    ax.scatter([d0["MiB"]], [d0["vmaf"]], s=90, color="#FFC20E", edgecolor="#12294A", zorder=5, label="D default floor (68)")
    marks = {"A  dash.js (unconstrained)": ("#7F8AA3", "A"), "A720  dash.js, 720p cap": ("#7F8AA3", "A 720p cap"),
             "A480  dash.js, 480p cap": ("#7F8AA3", "A 480p cap"), "B  BOLA": ("#D9534F", "BOLA")}
    for k, (c, lab) in marks.items():
        r = rec["baselines"][k]
        ax.scatter([r["MiB"]], [r["vmaf"]], s=55, marker="s", color=c, zorder=4)
        ax.annotate(lab, (r["MiB"], r["vmaf"]), textcoords="offset points", xytext=(6, -11), fontsize=8, color="#12294A")
    ax.set_xlabel("Data delivered (MiB)", fontsize=9, color="#12294A")
    ax.set_ylabel("Phone-model VMAF", fontsize=9, color="#12294A")
    ax.set_title("Jio 4G metro, phone viewer: up-left is better", fontsize=9.5, color="#12294A", loc="left")
    ax.grid(color="#D9DEE9", lw=0.6); ax.tick_params(labelsize=8)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(CH / "07_pareto_jio4g.png"); plt.close(fig)
except ImportError:
    print("matplotlib not installed; skipped chart")

print((RES / "equal_quality.md").read_text())
