"""
Synthetic network traces (kbps per second).

Research defaults (kept for comparability with Pensieve/Fugu/Oboe papers):
  - belgium_4g : stable 4G around 4 Mbps, van-commuter-style
  - norway_3g  : jittery 3G around 800 kbps
  - sudden_drop: 2 Mbps for 20s then crashes to 300 kbps

Indian profiles — modeled from TRAI 'MySpeed' quarterly reports and public
Ookla Speedtest India open data, specifically:
  - Jio 4G metro      : ~15 Mbps average, moderate variance
  - Airtel 4G tier-2  : ~8 Mbps, more variance, evening 20:00 dip
  - BSNL 3G rural     : ~1 Mbps, high variance, frequent stalls
  - Metro peak-hour   : 20 Mbps → 3 Mbps crash around 20:30 (prime-time OTT)
  - Jio 5G metro      : ~80 Mbps when available

Why both sets: Norway/Belgium stay in for academic comparability (reviewers
have the baselines in their heads); Indian traces are what an LTTS OTT client
would actually plan for.
"""
import csv
import random
from pathlib import Path


# ---------- Research defaults (kept) ----------
def gen_belgium_4g(n_s: int = 60, seed: int = 42):
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 3800 + 400 * (1 if t % 15 < 8 else -1)
        base += random.gauss(0, 300)
        if 20 <= t < 24:
            base *= 0.5
        out.append(max(200, int(base)))
    return out


def gen_norway_3g(n_s: int = 60, seed: int = 7):
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 800 + 200 * random.gauss(0, 1)
        if 10 <= t < 15:
            base = 300
        out.append(max(150, int(base)))
    return out


def gen_sudden_drop(n_s: int = 60, seed: int = 11):
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 2200 + random.gauss(0, 150) if t < 20 else 320 + random.gauss(0, 50)
        out.append(max(100, int(base)))
    return out


# ---------- Indian network profiles ----------
def gen_jio_4g_metro(n_s: int = 60, seed: int = 101):
    """TRAI MySpeed: Jio 4G avg DL in metros ~15 Mbps, p50 stable, mild jitter.
    Captures cell-edge handovers as periodic 30% dips."""
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 15000 + random.gauss(0, 1500)
        if t % 12 < 2:            # handover dip every ~12s
            base *= 0.7
        out.append(max(1500, int(base)))
    return out


def gen_airtel_4g_tier2(n_s: int = 60, seed: int = 202):
    """Tier-2 city 4G: ~8 Mbps avg, higher variance, prime-time congestion.
    A representative evening slice: steady 8 Mbps then a sustained dip 25–40s
    simulating peak-hour OTT contention."""
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 8000 + random.gauss(0, 1200)
        if 25 <= t < 40:
            base = 3500 + random.gauss(0, 600)   # evening prime-time dip
        out.append(max(500, int(base)))
    return out


def gen_bsnl_3g_rural(n_s: int = 60, seed: int = 303):
    """BSNL 3G rural: ~1 Mbps avg, bursty, frequent sub-500 kbps troughs.
    What a lot of India still watches on."""
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 1000 + 400 * random.gauss(0, 1)
        if random.random() < 0.15:                # sporadic stall
            base = 200
        out.append(max(120, int(base)))
    return out


def gen_metro_peak_hour(n_s: int = 60, seed: int = 404):
    """IPL / cricket prime-time pattern: fine until ~20:30, then
    tower-level congestion drops you from 20 Mbps to 3 Mbps."""
    random.seed(seed)
    out = []
    for t in range(n_s):
        if t < 20:
            base = 20000 + random.gauss(0, 2000)
        elif t < 25:
            base = 20000 - (t - 20) * 3400       # ramp down over 5s
        else:
            base = 3000 + random.gauss(0, 600)
        out.append(max(300, int(base)))
    return out


def gen_jio_5g_metro(n_s: int = 60, seed: int = 505):
    """Jio True5G: 80–120 Mbps where available, rare cell-edge drops."""
    random.seed(seed)
    out = []
    for t in range(n_s):
        base = 90000 + random.gauss(0, 10000)
        if t % 20 < 1:
            base *= 0.4
        out.append(max(5000, int(base)))
    return out


# Trace catalog
TRACES = {
    # Research defaults (kept for comparability)
    "belgium_4g":        gen_belgium_4g(),
    "norway_3g":         gen_norway_3g(),
    "sudden_drop":       gen_sudden_drop(),
    # Indian profiles
    "jio_4g_metro":      gen_jio_4g_metro(),
    "airtel_4g_tier2":   gen_airtel_4g_tier2(),
    "bsnl_3g_rural":     gen_bsnl_3g_rural(),
    "metro_peak_hour":   gen_metro_peak_hour(),
    "jio_5g_metro":      gen_jio_5g_metro(),
}

# Group labels for reporting
INDIAN = ["jio_4g_metro", "airtel_4g_tier2", "bsnl_3g_rural",
          "metro_peak_hour", "jio_5g_metro"]
RESEARCH = ["belgium_4g", "norway_3g", "sudden_drop"]


def save_all(out_dir: Path = Path("traces")):
    out_dir.mkdir(exist_ok=True)
    for name, series in TRACES.items():
        with open(out_dir / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["second", "kbps"])
            for i, kbps in enumerate(series):
                w.writerow([i, kbps])


if __name__ == "__main__":
    save_all()
    print(f"{'trace':<20} {'mean Mbps':>10} {'min':>6} {'max':>7}")
    for name, series in TRACES.items():
        tag = "[IN]" if name in INDIAN else "[  ]"
        mean_mbps = sum(series) / len(series) / 1000
        print(f"{tag} {name:<16} {mean_mbps:>10.2f} {min(series):>6} {max(series):>7}")
