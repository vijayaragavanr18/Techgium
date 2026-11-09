"""
Stage 4 — Run the full A/B/C/D ablation.

For every (ABR system) x (network trace) x (device):
  - Simulate playback of the manifest
  - Record bytes used, average VMAF, rebuffering, startup latency
  - Compute VMAF-NEG per MB (the primary metric)

Outputs: results/results.csv  and  results/summary.json
"""
import csv
import json
from pathlib import Path

from src.player import simulate
from src.abr.fixed import ThroughputABR
from src.abr.bola import BOLA
from src.abr.quality_mpc import OurLadderThroughput, QualityMPC
from src.traces import TRACES, INDIAN, RESEARCH, save_all as save_traces

MANIFEST_P = Path("manifest/manifest.json")
RESULTS = Path("results"); RESULTS.mkdir(exist_ok=True)


def main():
    save_traces(Path("traces"))
    manifest = json.loads(MANIFEST_P.read_text())

    systems = [
        ThroughputABR(),           # A
        BOLA(),                    # B
        OurLadderThroughput(),     # C
        QualityMPC(),              # D
    ]

    rows = []
    for device in ["phone", "tv"]:
        for trace_name, trace in TRACES.items():
            for sys in systems:
                m = simulate(manifest, sys, trace, device=device)
                rows.append({
                    "system": sys.name,
                    "device": device,
                    "trace": trace_name,
                    "bytes": m.bytes_total,
                    "MiB": round(m.mbytes(), 3),
                    "vmaf_tv": round(m.avg_vmaf_tv(), 2),
                    "vmaf_phone": round(m.avg_vmaf_phone(), 2),
                    "vmaf_neg": round(m.avg_vmaf_neg(), 2),
                    "vmaf_per_MB": round(m.vmaf_per_mb(), 2),
                    "startup_s": round(m.startup_latency_s, 3),
                    "rebuffer_s": round(m.rebuffer_time_s, 3),
                    "rebuffer_events": m.rebuffer_events,
                    "rebuffer_ratio": round(m.rebuffer_ratio(), 4),
                    "quality_changes": m.quality_changes,
                })

    with open(RESULTS / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Aggregated "equal VMAF" style summary
    summary = {}
    for device in ["phone", "tv"]:
        for trace_name in TRACES:
            key = f"{device}/{trace_name}"
            group = [r for r in rows if r["device"] == device and r["trace"] == trace_name]
            base = next(r for r in group if r["system"].startswith("A"))
            ours = next(r for r in group if r["system"].startswith("D"))
            pct_saved = 100.0 * (base["MiB"] - ours["MiB"]) / base["MiB"]
            delta_vmaf = ours["vmaf_neg"] - base["vmaf_neg"]
            summary[key] = {
                "baseline_A_MiB": base["MiB"],
                "ours_D_MiB": ours["MiB"],
                "pct_bytes_saved": round(pct_saved, 2),
                "baseline_A_VMAF_NEG": base["vmaf_neg"],
                "ours_D_VMAF_NEG": ours["vmaf_neg"],
                "delta_VMAF_NEG": round(delta_vmaf, 2),
                "baseline_A_rebuffer_s": base["rebuffer_s"],
                "ours_D_rebuffer_s": ours["rebuffer_s"],
            }

    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2))

    # pretty print
    print(f"\n{'system':<45} {'device':<6} {'trace':<13} {'MiB':>6} {'VMAFneg':>7} {'reb_s':>6}")
    for r in rows:
        print(f"{r['system']:<45} {r['device']:<6} {r['trace']:<13} "
              f"{r['MiB']:>6.2f} {r['vmaf_neg']:>7.2f} {r['rebuffer_s']:>6.2f}")

    print(f"\n============ Summary: A (dash.js default) vs D (ours) ============")
    print(f"\n--- Indian network profiles ---")
    for k, v in summary.items():
        trace = k.split("/")[1]
        if trace in INDIAN:
            print(f"  {k:<28}  bytes saved: {v['pct_bytes_saved']:>6.1f}%   "
                  f"ΔVMAF-NEG: {v['delta_VMAF_NEG']:+6.2f}   "
                  f"rebuffer A/D: {v['baseline_A_rebuffer_s']:>5.2f}s / {v['ours_D_rebuffer_s']:>5.2f}s")
    print(f"\n--- Research benchmark traces ---")
    for k, v in summary.items():
        trace = k.split("/")[1]
        if trace in RESEARCH:
            print(f"  {k:<28}  bytes saved: {v['pct_bytes_saved']:>6.1f}%   "
                  f"ΔVMAF-NEG: {v['delta_VMAF_NEG']:+6.2f}   "
                  f"rebuffer A/D: {v['baseline_A_rebuffer_s']:>5.2f}s / {v['ours_D_rebuffer_s']:>5.2f}s")


if __name__ == "__main__":
    main()
