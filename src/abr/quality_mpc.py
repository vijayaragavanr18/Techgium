"""
Systems C & D — OUR Quality-Targeted MPC controller.

Differentiator vs A/B:
  1. Reads per-segment VMAF (phone or TV model) from the manifest.
  2. Sets a VMAF floor based on the device model and data-saver.
     → adaptive: floor drops when sustained throughput can't support it.
  3. Uses a quantile throughput forecast (20th / 50th / 80th percentile).
  4. For each candidate rendition, computes:
         download time under pessimistic throughput
         projected buffer and stall risk
  5. Picks the fewest-bytes rendition that meets:
         VMAF >= adaptive floor
         stall_risk <= cap
     and tie-breaks by VMAF/MB (perceptual bang-per-buck).

System C uses OUR per-shot ladder + standard throughput ABR (ablation).
System D uses OUR per-shot ladder + OUR MPC (full stack).
"""
from typing import List

from .base import ABR, PlayerState


def base_vmaf_floor(device: str, data_saver: bool) -> float:
    """Device-dependent quality floor (before network adaptation)."""
    if data_saver:
        return 55.0 if device == "phone" else 65.0
    return 68.0 if device == "phone" else 76.0


def quantile(xs, q):
    if not xs:
        return 0.0
    s = sorted(xs)
    i = min(len(s) - 1, int(q * len(s)))
    return s[i]


class QualityMPC(ABR):
    """System D — full MPC with adaptive quality floor and stall-risk cap."""
    name = "D: Our ladder + Quality-MPC controller"

    def __init__(self, stall_risk_cap: float = 0.15,
                 min_buffer_s: float = 2.0):
        self.stall_risk_cap = stall_risk_cap
        self.min_buffer_s = min_buffer_s

    def _vmaf_for(self, rend, device):
        return rend["vmaf_phone"] if device == "phone" else rend["vmaf_tv"]

    def choose(self, segment: dict, state: PlayerState) -> dict:
        tps = state.throughput_history[-10:]
        tp_low  = quantile(tps, 0.20) if tps else 500
        tp_mid  = quantile(tps, 0.50) if tps else 1000

        # Adaptive quality floor:
        #  - start from device base floor
        #  - lower it harder when sustained throughput is low
        #  - tie it to the PESSIMISTIC quantile, not the median, so we
        #    don't overshoot and rebuffer on jittery rural links.
        base_floor = base_vmaf_floor(state.device, state.data_saver)
        guard = tp_low if tp_low > 0 else tp_mid
        if guard < 2500:
            scale = max(0.2, (guard - 200) / 2300)
            floor = 38 + (base_floor - 38) * scale
        else:
            floor = base_floor

        candidates = sorted(segment["renditions"], key=lambda r: r["bytes"])

        # 1st pass: fewest bytes that meet floor AND pass stall-risk cap
        feasible = []
        for r in candidates:
            v = self._vmaf_for(r, state.device)
            if v < floor:
                continue
            dl_time_s = (r["bytes"] * 8 / 1000) / max(tp_low, 50)
            projected_buffer = state.buffer_s + segment["duration_s"] - dl_time_s
            stall_risk = max(0.0, (self.min_buffer_s - projected_buffer) / self.min_buffer_s)
            if stall_risk <= self.stall_risk_cap:
                feasible.append((r, v))

        if feasible:
            # among feasible, pick fewest bytes (already sorted)
            return feasible[0][0]

        # 2nd pass: no rendition meets floor without stall risk —
        # fall back to the one with best VMAF/MB that still fits buffer
        best = candidates[0]
        best_eff = -1
        for r in candidates:
            v = self._vmaf_for(r, state.device)
            mb = r["bytes"] / (1024 * 1024)
            eff = v / max(mb, 1e-6)
            dl_time_s = (r["bytes"] * 8 / 1000) / max(tp_mid, 50)
            projected_buffer = state.buffer_s + segment["duration_s"] - dl_time_s
            if projected_buffer >= self.min_buffer_s and eff > best_eff:
                best, best_eff = r, eff
        return best


class OurLadderThroughput(ABR):
    """System C — same ladder generator & manifest as D, but a standard
    throughput ABR (isolates the ladder-gain from the controller-gain)."""
    name = "C: Our ladder + throughput ABR"

    def __init__(self, safety: float = 0.85):
        self.safety = safety

    def choose(self, segment: dict, state: PlayerState) -> dict:
        tp = state.harmonic_throughput_kbps(5)
        if tp == 0:
            return segment["renditions"][0]
        target = self.safety * tp
        picked = segment["renditions"][0]
        for r in segment["renditions"]:
            actual_kbps = r["bytes"] * 8 / 1000 / segment["duration_s"]
            if actual_kbps <= target:
                picked = r
        return picked
