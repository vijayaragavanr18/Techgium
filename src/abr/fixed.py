"""System A — fixed-bitrate ladder, throughput-based ABR (dash.js-ish default)."""
from .base import ABR, PlayerState


class ThroughputABR(ABR):
    """Pick the highest rendition whose nominal_kbps <= safety * recent throughput.
    Classic dash.js default behavior."""
    name = "A: Fixed ladder + throughput ABR"

    def __init__(self, safety: float = 0.85):
        self.safety = safety

    def choose(self, segment: dict, state: PlayerState) -> dict:
        tp = state.harmonic_throughput_kbps(5)
        if tp == 0:
            # startup: pick lowest
            return segment["renditions"][0]
        target = self.safety * tp
        picked = segment["renditions"][0]
        for r in segment["renditions"]:
            if r["nominal_kbps"] <= target:
                picked = r
        return picked
