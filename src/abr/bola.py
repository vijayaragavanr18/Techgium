"""System B — BOLA-style buffer-based ABR.

Simplified BOLA: maximises a utility U(r) - gamma * p(r) / buffer, where
U(r) = ln(bitrate_r / bitrate_min). This is the dash.js default for VoD.
We use it with the SAME fixed ladder as System A.
"""
import math
from .base import ABR, PlayerState


class BOLA(ABR):
    name = "B: Per-title ladder + BOLA ABR"

    def __init__(self, V: float = 0.93, gamma: float = 5.0):
        self.V = V
        self.gamma = gamma

    def choose(self, segment: dict, state: PlayerState) -> dict:
        rends = segment["renditions"]
        buf = max(state.buffer_s, 1.0)
        best = rends[0]
        best_score = -math.inf
        min_kbps = rends[0]["nominal_kbps"]
        for r in rends:
            utility = math.log(r["nominal_kbps"] / min_kbps + 1e-9)
            p = r["bytes"] * 8 / 1000 / segment["duration_s"]  # kbps
            score = (self.V * utility - self.gamma / buf) / (p / min_kbps)
            if score > best_score:
                best_score = score
                best = r
        return best
