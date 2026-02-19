from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TimedModifier:
    stat: str
    value: float
    remaining_s: int

class ModifierManager:
    def __init__(self) -> None:
        self._mods: List[TimedModifier] = []

    def add(self, stat: str, value: float, duration_s: int) -> None:
        if duration_s <= 0:
            return
        self._mods.append(TimedModifier(stat=stat, value=float(value), remaining_s=int(duration_s)))

    def tick(self) -> None:
        for m in list(self._mods):
            m.remaining_s -= 1
            if m.remaining_s <= 0:
                self._mods.remove(m)

    def snapshot(self) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for m in self._mods:
            out[m.stat] = out.get(m.stat, 0.0) + m.value
        return out
