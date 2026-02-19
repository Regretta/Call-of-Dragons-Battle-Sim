from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from ..engine.models import Hero, Artifact, Pet, TalentNode

def _load_json(path: str | Path) -> Any:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))

def load_heroes(path: str | Path) -> Dict[str, Hero]:
    data = _load_json(path)
    out: Dict[str, Hero] = {}
    for h in data.get("heroes", []):
        hid = str(h.get("id"))
        out[hid] = Hero(
            id=hid,
            name=h.get("name", hid),
            rarity=h.get("rarity", "Unknown"),
            rage_cost=int(h.get("rage_cost", 1000)),
            base_stats=h.get("base_stats", {}) or {},
            skill_factor=float(h.get("skill_factor", 0.0)),
            skill_effects=h.get("skill_effects", []) or [],
        )
    return out

def load_artifacts(path: str | Path) -> Dict[str, Artifact]:
    data = _load_json(path)
    out: Dict[str, Artifact] = {}
    for a in data.get("artifacts", []):
        aid = str(a.get("id"))
        out[aid] = Artifact(
            id=aid,
            name=a.get("name", aid),
            rarity=a.get("rarity", "Unknown"),
            main_stat=a.get("main_stat", {}) or {},
            secondary_stats=a.get("secondary_stats", {}) or {},
        )
    return out

def load_pets(path: str | Path) -> Dict[str, Pet]:
    data = _load_json(path)
    out: Dict[str, Pet] = {}
    for p in data.get("pets", []):
        pid = str(p.get("id"))
        out[pid] = Pet(
            id=pid,
            name=p.get("name", pid),
            rarity=p.get("rarity", "Unknown"),
            bonuses=p.get("bonuses", {}) or {},
        )
    return out

def load_talents(path: str | Path) -> Dict[str, TalentNode]:
    data = _load_json(path)
    out: Dict[str, TalentNode] = {}
    for t in data.get("talents", []):
        tid = str(t.get("id"))
        out[tid] = TalentNode(
            id=tid,
            stat=t.get("stat",""),
            value_per_rank=float(t.get("value_per_rank", 0.0)),
            max_rank=int(t.get("max_rank", 1)),
            name=t.get("name","") or "",
            description=t.get("description","") or "",
            tree=t.get("tree","General") or "General",
            x=float(t.get("x", 0.0) or 0.0),
            y=float(t.get("y", 0.0) or 0.0),
            prereq=list(t.get("prereq", []) or []),
        )
    return out
