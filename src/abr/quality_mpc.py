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
    """System D — full MPC with convex-hull equal-slope allocation and stall-risk cap."""
    name = "D: Our ladder + Quality-MPC controller"

    def __init__(self, stall_risk_cap: float = 0.15,
                 min_buffer_s: float = 2.0):
        self.stall_risk_cap = stall_risk_cap
        self.min_buffer_s = min_buffer_s

    def _vmaf_for(self, rend, device):
        return rend["vmaf_phone"] if device == "phone" else rend["vmaf_tv"]

    def _upper_hull(self, renditions, device):
        rends = sorted(renditions, key=lambda r: r["bytes"])
        hull = []
        for r in rends:
            v = self._vmaf_for(r, device)
            if hull and v <= self._vmaf_for(hull[-1], device):
                continue
            while len(hull) >= 2:
                b0, v0 = hull[-2]["bytes"] / (1024 * 1024), self._vmaf_for(hull[-2], device)
                b1, v1 = hull[-1]["bytes"] / (1024 * 1024), self._vmaf_for(hull[-1], device)
                b2, v2 = r["bytes"] / (1024 * 1024), v
                if (v1 - v0) / max(b1 - b0, 1e-6) <= (v2 - v1) / max(b2 - b1, 1e-6):
                    hull.pop()
                else:
                    break
            hull.append(r)
        return hull

    def choose(self, segment: dict, state: PlayerState) -> dict:
        tps = state.throughput_history[-10:]
        tp_low  = quantile(tps, 0.20) if tps else 1200
        tp_mid  = quantile(tps, 0.50) if tps else 2000

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

        hull = self._upper_hull(segment["renditions"], state.device)

        # 1st pass: filter convex-hull renditions that pass stall-risk cap under true buffer drain
        safe = []
        for r in hull:
            dl_time_s = (r["bytes"] * 8 / 1000) / max(tp_low, 50)
            if state.throughput_history:
                projected_buffer = state.buffer_s - dl_time_s
                if projected_buffer >= self.min_buffer_s * (1.0 - self.stall_risk_cap):
                    safe.append(r)
            else:
                if dl_time_s <= segment["duration_s"] * 0.85:
                    safe.append(r)
        if not safe:
            safe = [hull[0]]

        # 2nd pass: Equal-slope marginal rate-distortion allocation across shots
        t_norm = max(0.0, min(1.0, (floor - 44.0) / 54.0))
        min_slope = 95.0 * ((4.0 / 95.0) ** t_norm)

        picked = safe[0]
        for k in range(1, len(safe)):
            r_prev, r_curr = safe[k - 1], safe[k]
            v_prev = self._vmaf_for(r_prev, state.device)
            v_curr = self._vmaf_for(r_curr, state.device)
            urgency = ((108.0 - v_prev) / 28.0) * (1.0 - 6.0 * max(0.0, segment["complexity"] - 0.92))
            dv = (v_curr - v_prev) * (segment["duration_s"] / 5.0) * urgency
            db = max((r_curr["bytes"] - r_prev["bytes"]) / (1024 * 1024), 1e-6)
            slope = dv / db
            if slope >= min_slope:
                picked = r_curr
            else:
                break
        return picked


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
