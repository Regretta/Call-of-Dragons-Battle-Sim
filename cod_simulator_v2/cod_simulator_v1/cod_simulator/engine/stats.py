from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from .models import Hero, Artifact, Pet, TalentNode, Build

DEFAULTS: Dict[str, float] = {
    "attack": 0.0,
    "defense": 0.0,
    "health": 0.0,
    "crit_chance": 0.0,
    "crit_damage": 1.5,
    "skill_damage_bonus": 0.0,
    "all_damage_bonus": 0.0,
    "damage_reduction": 0.0,
    "rage_bonus": 0.0,
    "shield": 0.0,
}

@dataclass
class StatBlock:
    stats: Dict[str, float]

    def get(self, k: str) -> float:
        return float(self.stats.get(k, DEFAULTS.get(k, 0.0)))

    def as_dict(self) -> Dict[str, float]:
        out = dict(DEFAULTS)
        out.update({k: float(v) for k, v in self.stats.items()})
        return out

def parse_talent_bonuses(talent_nodes: Dict[str, TalentNode], selected: Dict[str, int]) -> Dict[str, float]:
    bonuses: Dict[str, float] = {}
    for node_id, rank in selected.items():
        node = talent_nodes.get(node_id)
        if not node:
            continue
        r = max(0, min(int(rank), int(node.max_rank)))
        bonuses[node.stat] = bonuses.get(node.stat, 0.0) + (float(node.value_per_rank) * r)
    return bonuses

def build_final_stats(hero: Hero, *, artifact: Optional[Artifact], pet: Optional[Pet], talent_nodes: Dict[str, TalentNode], build: Build) -> StatBlock:
    s: Dict[str, float] = dict(DEFAULTS)
    s.update({k: float(v) for k, v in (hero.base_stats or {}).items()})
    if "crit_damage" not in s:
        s["crit_damage"] = DEFAULTS["crit_damage"]

    if pet:
        for stat, val in pet.bonuses.items():
            s[stat] = s.get(stat, 0.0) + float(val)

    if artifact:
        ms = artifact.main_stat or {}
        stat = ms.get("stat")
        val = float(ms.get("value", 0.0))
        if stat:
            s[stat] = s.get(stat, 0.0) + val
        for stat, val in (artifact.secondary_stats or {}).items():
            s[stat] = s.get(stat, 0.0) + float(val)

    tb = parse_talent_bonuses(talent_nodes, build.selected_talents or {})
    for stat, val in tb.items():
        s[stat] = s.get(stat, 0.0) + float(val)

    for stat, val in (build.extra_bonuses or {}).items():
        s[stat] = s.get(stat, 0.0) + float(val)

    return StatBlock(s)
