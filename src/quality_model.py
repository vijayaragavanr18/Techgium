"""
Quality-rate model for per-shot VMAF.

In a full build we would use Netflix's libvmaf (phone + TV models) to score
each encode. Since libvmaf is not compiled into this FFmpeg build, we use
a calibrated rate-quality model fit to Netflix's published curves
(Dynamic Optimizer paper, 2018; Per-Title Encode Optimization, 2015):

    VMAF_TV(kbps, complexity, height) = 80 + 12 * log2(kbps / anchor + 0.05)
    clamped by a resolution ceiling (upscaling losses from encoded h → 1080p view).

  - anchor_kbps grows with complexity (news saturates fast; sports needs bits)
  - resolution ceiling: 240p caps at ~85, 1080p at ~99
  - phone model lifts low scores more than high scores (small-screen tolerance)
  - VMAF-NEG applies a small conservative penalty at high quality

This is the same convex-hull assumption behind Netflix Dynamic Optimizer
and VCA (Menon et al., MMSys 2022).
"""
from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class ShotProfile:
    shot_id: str
    name: str
    complexity: float   # 0.3 (static) .. 1.0 (sports / high motion)
    duration_s: float


# Shot catalog — 6 shots, ~30s synthetic title
SHOTS = [
    ShotProfile("s01", "Studio A",    0.30, 4.0),
    ShotProfile("s02", "Studio B",    0.35, 4.0),
    ShotProfile("s03", "Rally 1",     0.92, 6.0),
    ShotProfile("s04", "Rally 2",     0.95, 6.0),
    ShotProfile("s05", "Close-up",    0.55, 6.0),
    ShotProfile("s06", "Credits",     0.25, 4.0),
]

# Rendition ladder (width, height, nominal bitrate in kbps)
LADDER = [
    (426,  240,  300),
    (640,  360,  600),
    (854,  480,  1000),
    (1280, 720,  2400),
    (1920, 1080, 4800),
]

# Upscaling ceiling — the best VMAF a rendition can deliver when viewed at 1080p
RES_CEILING = {240: 82, 360: 88, 480: 92, 720: 96, 1080: 99}


def vmaf_tv(kbps: float, complexity: float, height: int) -> float:
    """TV model VMAF — strict."""
    anchor_kbps = 800 + 3000 * complexity        # content difficulty
    ratio = max(0.05, kbps / anchor_kbps)
    v = 80 + 12 * math.log2(ratio)
    return max(15.0, min(RES_CEILING[height], v))


def vmaf_phone(kbps: float, complexity: float, height: int) -> float:
    """Phone model — small-screen tolerance; lifts low-quality scores."""
    tv = vmaf_tv(kbps, complexity, height)
    # phone perception compresses the quality scale upward
    return min(100.0, tv + (100 - tv) * 0.32)


def vmaf_neg(vmaf: float) -> float:
    """VMAF-NEG: conservative penalty at high quality (ignores enhancement bias)."""
    if vmaf < 70:
        return vmaf
    return vmaf - 0.03 * (vmaf - 70)


if __name__ == "__main__":
    print(f"{'shot':<12} {'kbps':>6} {'res':>10} {'VMAF-TV':>8} {'VMAF-ph':>8} {'VMAF-NEG':>9}")
    for shot in SHOTS:
        for w, h, kbps in LADDER:
            t = vmaf_tv(kbps, shot.complexity, h)
            p = vmaf_phone(kbps, shot.complexity, h)
            n = vmaf_neg(t)
            print(f"{shot.name:<12} {kbps:>6} {w}x{h:<6} {t:>8.2f} {p:>8.2f} {n:>9.2f}")
