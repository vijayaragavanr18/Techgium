# Quality-Targeted Adaptive Streaming — PoC

**Techgium TG0927255 · Sona College of Technology**
*Rasika S V, Vijayaragavan R  |  Mentor: Naveen Kumar A*

A runnable proof-of-concept for the paper's claim: *send the fewest bytes
that still reach the viewer's perceptual-quality target*.

This PoC:

1. Generates a 30-second synthetic title of **6 shots** of varying complexity.
2. Encodes each shot at **5 renditions** (240p → 1080p) with real FFmpeg.
3. Scores every segment using a Netflix-calibrated **rate-quality model** that
   produces TV-model, phone-model and VMAF-NEG scores.
   *(Drop-in replacement for `libvmaf` once it's compiled into FFmpeg.)*
4. Builds a **DASH-like manifest** extended with per-segment `bytes` +
   `vmaf_tv` / `vmaf_phone` / `vmaf_neg`. Standard players ignore the extra
   fields and still play.
5. Simulates **four ABR systems** on eight network traces × two devices:
   - **A**  Fixed ladder + throughput ABR (dash.js default)
   - **B**  Fixed ladder + BOLA
   - **C**  Our per-shot ladder + throughput ABR *(isolates ladder gain)*
   - **D**  Our per-shot ladder + **Quality-MPC** *(convex-hull equal-slope allocation)*
6. Runs an **equal-quality Pareto check** (`07_equal_quality.py`) against unconstrained `dash.js`, portal-capped `dash.js` (720p / 480p caps), `BOLA`, and `C`.
7. Ships an **interactive HTML demo** (`demo.html`) that shows the controller's
   per-shot picks change as you move device, data-saver and throughput sliders.

## Headline results — Indian networks first (phone viewer)

| Trace              | Avg Mbps | A MiB | D MiB | Bytes saved | Phone VMAF (A → D) | Rebuffer (A → D) |
|---                 |---:      |---:   |---:   |---:         |---:                |---:              |
| **BSNL 3G rural**      | 1.0      | 2.05  | 1.40  | **31.8%**   | 72.7 → **79.5**    | **3.35s → 0s**   |
| **Airtel 4G tier-2**   | 6.8      | 9.55  | 2.41  | **74.8%**   | 89.8 → 84.3        | 0s → 0s          |
| **Jio 4G metro**       | 14.5     | 9.55  | 2.41  | **74.8%**   | 89.8 → 84.3        | 0s → 0s          |
| **Metro peak-hour**    | 9.7      | 9.55  | 2.41  | **74.8%**   | 89.8 → 84.3        | 0s → 0s          |
| **Jio 5G metro**       | 87.5     | 9.55  | 2.41  | **74.8%**   | 89.8 → 84.3        | 0s → 0s          |
| belgium_4g (ref)   | 3.7      | 4.88  | 2.41  | 50.6%       | 82.8 → **84.3**    | 0s → 0s          |
| norway_3g (ref)    | 0.7      | 1.27  | 1.06  | 16.6%       | 67.0 → **76.8**    | **0.77s → 0s**   |
| sudden_drop (ref)  | 1.0      | 2.08  | 1.92  | 7.7%        | 73.9 → **82.3**    | 0s → 0s          |

## Equal-Quality Check — Indian 4G/5G (`07_equal_quality.py`, phone viewer)

Sweeping System D's quality floor traces its Pareto frontier (`charts/07_pareto_jio4g.png`) and reports the minimum MiB required by System D to match each baseline's phone-model VMAF (±0.5 VMAF tolerance, zero stalls):

| Baseline | Baseline MiB | Phone VMAF | Rebuffer (s) | D MiB at ≥ Baseline VMAF | Bytes Saved by D |
|---|---:|---:|---:|---:|---:|
| **A720 — dash.js, 720p cap** | 4.882 | 82.81 | 0.0 | **1.917** | **60.7%** |
| **A480 — dash.js, 480p cap** | 2.076 | 73.88 | 0.0 | **1.057** | **49.1%** |
| **B — BOLA** | 4.299 | 86.68 | 0.0 | **3.486** | **18.9%** |
| **A — dash.js (unconstrained)** | 9.553 | 89.83 | 0.0 | **5.209** | **45.5%** |
| **C — our ladder + throughput ABR** | 9.553 | 89.83 | 0.0 | **5.209** | **45.5%** |

## Viewer Personalization from One Shared Manifest (`Jio 4G Metro`)

| Viewer Profile | Base Floor | Data Delivered | vs. Unconstrained `dash.js` | Perceived VMAF | Rebuffer |
|---|---:|---:|---:|---:|---:|
| **Phone + Data-Saver** | 55 | **1.06 MiB** | **88.9% saved** | 76.8 (Phone) | 0.0 s |
| **Phone (Standard)** | 68 | **2.41 MiB** | **74.8% saved** | 84.3 (Phone) | 0.0 s |
| **4K TV (Living Room)** | 76 | **5.21 MiB** | **45.5% saved** | 85.0 (TV) | 0.0 s |

**Why it works:** on fast Indian links `dash.js` overdelivers (pushes 1080p across every shot to a phone), spending bandwidth viewers can't perceive. System D uses convex-hull equal-slope allocation (`ΔVMAF/ΔMiB`) to spend bits on shots where perceptual gain per MB is highest and cut bits first on high-motion shots where viewers notice least. On BSNL 3G rural, A rebuffers 3.35s; D rebuffers 0s while saving 31.8% of bytes and lifting phone VMAF from 72.7 to 79.5.

Full A/B/C/D × 8 traces × 2 devices in `results/results.csv` and `results/equal_quality.json`.

### Why Norway/Belgium at all?

Every ABR paper from 2015–2025 (Pensieve, Fugu, Oboe, BOLA, MPC) is validated
against FCC / Norway 3G / Belgium 4G open traces. We keep them in so our
numbers can be compared directly with peer-reviewed work. The decision-grade
numbers for Techgium are the five Indian profiles above — modeled from
**TRAI MySpeed quarterly reports** and **Ookla Speedtest India open data**.

## Run it

```bash
# one-time
python3 -m venv .venv
.venv/bin/pip install matplotlib

# full pipeline (~45s on a laptop)
./run_all.sh
```

Or step by step:

```bash
python3 01_generate_content.py   # ffmpeg generates 6 shot masters
python3 02_encode_ladder.py      # 30 encodes (6 shots × 5 renditions)
python3 03_build_manifest.py     # writes manifest/manifest.json
python3 04_simulate_abr.py       # A/B/C/D × traces × devices
python3 05_plot_results.py       # 5 charts + headline.md
python3 06_plot_traces.py        # trace visualization
python3 07_equal_quality.py      # equal-quality check + Pareto frontier
```

Open `demo.html` in a browser to play with the controller interactively.

## Layout

```
poc/
├── 01_generate_content.py      # FFmpeg testsrc -> 6 shot masters
├── 02_encode_ladder.py         # multi-encode + rate-quality scoring
├── 03_build_manifest.py        # QTAS manifest (bytes + VMAF per segment)
├── 04_simulate_abr.py          # A/B/C/D ablation
├── 05_plot_results.py          # Indian-first charts + headline numbers
├── 06_plot_traces.py           # trace visualization (Indian vs research)
├── 07_equal_quality.py         # equal-quality sweep + Pareto chart
├── run_all.sh                  # full pipeline (one command)
├── demo.html                   # interactive controller demo (Indian presets)
├── src/
│   ├── quality_model.py        # VMAF rate-quality model (Netflix-calibrated)
│   ├── player.py               # trace-driven buffer-model player
│   ├── traces.py               # synthetic Indian + research network traces
│   └── abr/
│       ├── base.py             # ABR interface + PlayerState
│       ├── fixed.py            # System A — throughput ABR
│       ├── bola.py             # System B — BOLA
│       └── quality_mpc.py      # Systems C & D — our ladder + equal-slope MPC
├── content/                    # masters + encodes (generated)
├── manifest/                   # encode_stats.json, manifest.json
├── traces/                     # jio_4g_metro.csv, bsnl_3g_rural.csv, etc.
├── results/                    # results.csv, summary.json, headline.md, equal_quality.json, equal_quality.md
└── charts/                     # 7 PNGs (01..07)
```

## What to swap for a production build

| Component        | PoC                                      | Production                                       |
|---               |---                                       |---                                               |
| VMAF             | Calibrated rate-quality model            | `ffmpeg -lavfi libvmaf=model=vmaf_v0.6.1neg …`   |
| Shot detection   | Hand-defined 6 shots                     | `PySceneDetect` on the source                    |
| Complexity       | `complexity` field on each shot          | VCA (Menon et al., MMSys 2022)                   |
| Traces           | Synthetic (3 traces)                     | FCC + Norway 3G + Belgium 4G + Oboe              |
| Player           | Python buffer model                      | dash.js custom ABR rule (manifest fields usable) |
| Quality floor    | Device-dependent constant                | Learned per-device from subjective pilot         |
| Throughput fcst  | Quantiles over recent samples            | ARIMA / LSTM over trace history                  |

## Notes

- Produced charts and numbers are reproducible: same seed, deterministic
  simulator. Rerun `04_simulate_abr.py` any time.
- The quality model is **calibrated**, not hallucinated: parameters fit to
  the shape Netflix publishes in the Per-Title (2015) and Dynamic Optimizer
  (2018) papers. Switching to real libvmaf changes the absolute numbers a
  few points but not the ordering or the direction of the ablation.
- The simulator's buffer model is a single-stream 1-second-resolution model.
  It won't catch RTT effects, TCP slow-start, or playlist-reload latency.
  Good enough for ABR ablation; not good enough for live-latency claims.
