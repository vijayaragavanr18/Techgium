"""Abstract ABR controller interface."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class PlayerState:
    buffer_s: float = 0.0           # buffered seconds of playback
    throughput_history: List[float] = field(default_factory=list)   # recent kbps estimates
    device: str = "phone"           # 'phone' or 'tv'
    data_saver: bool = False

    def recent_throughput_kbps(self, n: int = 5) -> float:
        if not self.throughput_history:
            return 0.0
        tail = self.throughput_history[-n:]
        return sum(tail) / len(tail)

    def harmonic_throughput_kbps(self, n: int = 5) -> float:
        """Harmonic mean is more pessimistic — standard ABR literature."""
        tail = [t for t in self.throughput_history[-n:] if t > 0]
        if not tail:
            return 0.0
        return len(tail) / sum(1.0/t for t in tail)


class ABR:
    name: str = "base"

    def choose(self, segment: dict, state: PlayerState) -> dict:
        """Given a manifest segment entry, choose one rendition dict."""
        raise NotImplementedError
