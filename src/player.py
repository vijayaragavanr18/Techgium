"""
Trace-driven player simulator.

Models:
  - Buffer that fills as segments download
  - Playback that drains it in real time
  - Rebuffer (stall) when buffer hits zero before next segment arrives
  - Startup latency (first segment download time)

Network: kbps samples per second from a trace (CSV with 'kbps' column).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from .abr.base import PlayerState


@dataclass
class SessionMetrics:
    bytes_total: int = 0
    play_time_s: float = 0.0
    startup_latency_s: float = 0.0
    rebuffer_time_s: float = 0.0
    rebuffer_events: int = 0
    vmaf_tv_sum: float = 0.0
    vmaf_phone_sum: float = 0.0
    vmaf_neg_sum: float = 0.0
    vmaf_tv_min: float = 100.0
    quality_changes: int = 0
    picks: List[dict] = field(default_factory=list)

    def avg_vmaf_tv(self): return self.vmaf_tv_sum / max(self.play_time_s, 1e-9)
    def avg_vmaf_phone(self): return self.vmaf_phone_sum / max(self.play_time_s, 1e-9)
    def avg_vmaf_neg(self): return self.vmaf_neg_sum / max(self.play_time_s, 1e-9)
    def mbytes(self): return self.bytes_total / (1024 * 1024)
    def vmaf_per_mb(self): return self.avg_vmaf_neg() / max(self.mbytes(), 1e-9)
    def rebuffer_ratio(self):
        return self.rebuffer_time_s / max(self.rebuffer_time_s + self.play_time_s, 1e-9)


def download_segment(bytes_, trace_kbps, t_start) -> float:
    """Simulate downloading `bytes_` through the trace starting at t_start.
    Returns the wall-clock duration taken (seconds)."""
    bits_left = bytes_ * 8
    t = t_start
    while bits_left > 0:
        idx = min(int(t), len(trace_kbps) - 1)
        kbps = max(trace_kbps[idx], 10)   # avoid /0
        bps = kbps * 1000
        # consume 100ms of this bandwidth sample
        step = 0.1
        bits_available = bps * step
        if bits_available >= bits_left:
            t += bits_left / bps
            bits_left = 0
        else:
            bits_left -= bits_available
            t += step
    return t - t_start


def simulate(manifest, abr, trace_kbps, device="phone", data_saver=False) -> SessionMetrics:
    state = PlayerState(buffer_s=0.0, device=device, data_saver=data_saver)
    metrics = SessionMetrics()
    wall_t = 0.0
    last_pick_label = None

    for i, seg in enumerate(manifest["segments"]):
        pick = abr.choose(seg, state)
        metrics.picks.append({"seg": i, "shot": seg["shot_name"],
                               "label": pick["label"],
                               "bytes": pick["bytes"],
                               "vmaf_tv": pick["vmaf_tv"],
                               "vmaf_phone": pick["vmaf_phone"]})
        if last_pick_label is not None and pick["label"] != last_pick_label:
            metrics.quality_changes += 1
        last_pick_label = pick["label"]

        dl_time = download_segment(pick["bytes"], trace_kbps, wall_t)
        achieved_kbps = (pick["bytes"] * 8 / 1000) / max(dl_time, 1e-6)
        state.throughput_history.append(achieved_kbps)

        if i == 0:
            metrics.startup_latency_s = dl_time
            # play begins once first segment is downloaded
            wall_t += dl_time
            state.buffer_s = seg["duration_s"]
        else:
            # during dl_time, buffer drains
            if dl_time > state.buffer_s:
                # we stalled while this segment was downloading
                stall = dl_time - state.buffer_s
                metrics.rebuffer_time_s += stall
                metrics.rebuffer_events += 1
                wall_t += dl_time
                state.buffer_s = seg["duration_s"]   # rebuffer absorbed, add fresh
            else:
                wall_t += dl_time
                state.buffer_s = state.buffer_s - dl_time + seg["duration_s"]

        # accumulate time-weighted VMAF
        d = seg["duration_s"]
        metrics.play_time_s += d
        metrics.vmaf_tv_sum += pick["vmaf_tv"] * d
        metrics.vmaf_phone_sum += pick["vmaf_phone"] * d
        # vmaf_neg not in manifest directly; approximate from tv
        v_tv = pick["vmaf_tv"]
        v_neg = v_tv if v_tv < 70 else v_tv - 0.03 * (v_tv - 70)
        metrics.vmaf_neg_sum += v_neg * d
        metrics.vmaf_tv_min = min(metrics.vmaf_tv_min, pick["vmaf_tv"])
        metrics.bytes_total += pick["bytes"]

    return metrics
