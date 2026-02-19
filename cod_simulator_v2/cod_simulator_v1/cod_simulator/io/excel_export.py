from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import json
import pandas as pd

"""
Excel -> JSON export (V1 + Talent UI metadata)

This exporter is meant to pull real entities from your database workbook.

Talent nodes support OPTIONAL UI columns so the simulator can render a clickable tree:
- Name
- Description
- Tree (Magic/Control/etc.)
- X, Y (canvas coordinates)
- Prereq (comma-separated node IDs)

If your workbook doesn't have these columns yet, the export still works,
but the talent UI will show a simple list/tree without positioning.
"""

SHEET_HERO = "Hero"
SHEET_TALENT_NODE = "Talent Node"
SHEET_ARTIFACTS = "Artifacts"
SHEET_PETS = "War Pets"

COL_HERO_ID = "ID"
COL_HERO_NAME = "Hero"
COL_HERO_RARITY = "Quality"
COL_HERO_RAGE_COST = "Rage Cost"
COL_HERO_ATK = "Attack"
COL_HERO_DEF = "Defense"
COL_HERO_HP = "Health"
COL_HERO_SKILL_FACTOR = "Skill Factor"

COL_TALENT_ID = "Node ID"
COL_TALENT_STAT = "Stat"
COL_TALENT_VALUE_PER_RANK = "Value 1"
COL_TALENT_MAX_RANK = "Max Rank"
# Optional UI columns
COL_TALENT_NAME = "Name"
COL_TALENT_DESC = "Description"
COL_TALENT_TREE = "Tree"
COL_TALENT_X = "X"
COL_TALENT_Y = "Y"
COL_TALENT_PREREQ = "Prereq"   # comma-separated IDs

COL_ART_ID = "ID"
COL_ART_NAME = "Artifact"
COL_ART_RARITY = "Quality"
COL_ART_MAIN_STAT = "Main Stat"
COL_ART_MAIN_VALUE = "Main Max"

COL_PET_ID = "ID"
COL_PET_NAME = "Pet"
COL_PET_RARITY = "Quality"
COL_PET_ATK_BONUS = "Attack Bonus"
COL_PET_DEF_BONUS = "Defense Bonus"
COL_PET_HP_BONUS = "Health Bonus"

def _safe(v, default=None):
    if v is None:
        return default
    try:
        if pd.isna(v):
            return default
    except Exception:
        pass
    return v

def _read(excel_path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(excel_path, sheet_name=sheet)

def export_v1_json(excel_path: str | Path, out_dir: str | Path) -> Dict[str, Path]:
    excel_path = Path(excel_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    heroes: List[Dict[str, Any]] = []
    talents: List[Dict[str, Any]] = []
    artifacts: List[Dict[str, Any]] = []
    pets: List[Dict[str, Any]] = []

    # Heroes
    try:
        df = _read(excel_path, SHEET_HERO)
        for r in df.where(pd.notnull(df), None).to_dict(orient="records"):
            hid = _safe(r.get(COL_HERO_ID))
            name = _safe(r.get(COL_HERO_NAME))
            if hid is None or name is None:
                continue
            heroes.append({
                "id": str(hid),
                "name": str(name),
                "rarity": str(_safe(r.get(COL_HERO_RARITY), "Unknown")),
                "rage_cost": int(_safe(r.get(COL_HERO_RAGE_COST), 1000) or 1000),
                "base_stats": {
                    "attack": float(_safe(r.get(COL_HERO_ATK), 0) or 0),
                    "defense": float(_safe(r.get(COL_HERO_DEF), 0) or 0),
                    "health": float(_safe(r.get(COL_HERO_HP), 0) or 0),
                },
                "skill_factor": float(_safe(r.get(COL_HERO_SKILL_FACTOR), 0) or 0),
                "skill_effects": []
            })
    except Exception:
        pass

    # Talents (+ UI fields)
    try:
        df = _read(excel_path, SHEET_TALENT_NODE)
        for r in df.where(pd.notnull(df), None).to_dict(orient="records"):
            tid = _safe(r.get(COL_TALENT_ID))
            stat = _safe(r.get(COL_TALENT_STAT))
            if tid is None or stat is None:
                continue
            prereq_raw = str(_safe(r.get(COL_TALENT_PREREQ), "") or "")
            prereq = [p.strip() for p in prereq_raw.split(",") if p.strip()]
            talents.append({
                "id": str(tid),
                "stat": str(stat),
                "value_per_rank": float(_safe(r.get(COL_TALENT_VALUE_PER_RANK), 0) or 0),
                "max_rank": int(_safe(r.get(COL_TALENT_MAX_RANK), 1) or 1),
                "name": str(_safe(r.get(COL_TALENT_NAME), "") or ""),
                "description": str(_safe(r.get(COL_TALENT_DESC), "") or ""),
                "tree": str(_safe(r.get(COL_TALENT_TREE), "General") or "General"),
                "x": float(_safe(r.get(COL_TALENT_X), 0) or 0),
                "y": float(_safe(r.get(COL_TALENT_Y), 0) or 0),
                "prereq": prereq,
            })
    except Exception:
        pass

    # Artifacts
    try:
        df = _read(excel_path, SHEET_ARTIFACTS)
        for r in df.where(pd.notnull(df), None).to_dict(orient="records"):
            aid = _safe(r.get(COL_ART_ID))
            name = _safe(r.get(COL_ART_NAME))
            ms = _safe(r.get(COL_ART_MAIN_STAT))
            if aid is None or name is None or ms is None:
                continue
            artifacts.append({
                "id": str(aid),
                "name": str(name),
                "rarity": str(_safe(r.get(COL_ART_RARITY), "Unknown")),
                "main_stat": {"stat": str(ms), "value": float(_safe(r.get(COL_ART_MAIN_VALUE), 0) or 0)},
                "secondary_stats": {}
            })
    except Exception:
        pass

    # Pets
    try:
        df = _read(excel_path, SHEET_PETS)
        for r in df.where(pd.notnull(df), None).to_dict(orient="records"):
            pid = _safe(r.get(COL_PET_ID))
            name = _safe(r.get(COL_PET_NAME))
            if pid is None or name is None:
                continue
            bonuses: Dict[str, float] = {}
            for col, stat in [(COL_PET_ATK_BONUS,"attack"),(COL_PET_DEF_BONUS,"defense"),(COL_PET_HP_BONUS,"health")]:
                v = _safe(r.get(col))
                if v is not None:
                    bonuses[stat] = bonuses.get(stat, 0.0) + float(v or 0)
            pets.append({
                "id": str(pid),
                "name": str(name),
                "rarity": str(_safe(r.get(COL_PET_RARITY), "Unknown")),
                "bonuses": bonuses
            })
    except Exception:
        pass

    paths = {
        "heroes": out_dir/"heroes.json",
        "talents": out_dir/"talents.json",
        "artifacts": out_dir/"artifacts.json",
        "pets": out_dir/"pets.json",
    }
    paths["heroes"].write_text(json.dumps({"heroes": heroes}, indent=2), encoding="utf-8")
    paths["talents"].write_text(json.dumps({"talents": talents}, indent=2), encoding="utf-8")
    paths["artifacts"].write_text(json.dumps({"artifacts": artifacts}, indent=2), encoding="utf-8")
    paths["pets"].write_text(json.dumps({"pets": pets}, indent=2), encoding="utf-8")
    return paths
