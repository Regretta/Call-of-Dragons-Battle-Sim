from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List

@dataclass(frozen=True)
class Hero:
    id: str
    name: str
    rarity: str = "Unknown"
    rage_cost: int = 1000
    base_stats: Dict[str, float] = field(default_factory=dict)
    skill_factor: float = 0.0
    skill_effects: List[Dict[str, Any]] = field(default_factory=list)

@dataclass(frozen=True)
class Artifact:
    id: str
    name: str
    rarity: str
    main_stat: Dict[str, float]
    secondary_stats: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class Pet:
    id: str
    name: str
    rarity: str
    bonuses: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class TalentNode:
    id: str
    stat: str
    value_per_rank: float
    max_rank: int
    # UI / metadata (optional but supported)
    name: str = ""
    description: str = ""
    tree: str = "General"   # e.g., "Magic", "Control", "PVP", "Foundation"
    x: float = 0.0          # canvas coordinates (0..1 normalized or pixels)
    y: float = 0.0
    prereq: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class Build:
    hero_id: str
    artifact_id: Optional[str] = None
    pet_id: Optional[str] = None
    selected_talents: Dict[str, int] = field(default_factory=dict)
    extra_bonuses: Dict[str, float] = field(default_factory=dict)

@dataclass(frozen=True)
class SimConfig:
    duration_s: int = 60
    deterministic: bool = True
    target_count: int = 1
    aoe_split_ratio: float = 0.5
    counter_enabled: bool = True
    rage_on_normal: float = 94
    rage_on_counter: float = 16
    defense_constant: float = 1400.0
