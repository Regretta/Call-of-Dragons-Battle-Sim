from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import pandas as pd

"""
Excel -> JSON export helpers (V1)

This module is designed to help you take your existing Excel "database" workbook and export
the subset of data needed for V1 of the simulator.

Because sheet layouts can vary, this exporter is intentionally:
- explicit (you choose which columns map to which fields)
- fail-soft (skips rows that don't have required fields)
- easy to tweak (edit the SHEET + COLUMN constants below)

Expected JSON files produced:
- heroes.json
- talents.json
- artifacts.json
- pets.json

Workflow:
1) Put your Excel workbook in /data or point to it by path.
2) Run:
   python tools/export_from_excel.py --excel "Call of Dragons Database.xlsx" --out data
3) Confirm the JSON looks right, then run the simulator using those JSON files.
"""

# ---- Configure these to match your workbook ----
SHEET_HERO = "Hero"
SHEET_TALENT_NODE = "Talent Node"
SHEET_ARTIFACTS = "Artifacts"
SHEET_PETS = "War Pets"

# HERO column mapping (edit as needed)
COL_HERO_ID = "ID"
COL_HERO_NAME = "Hero"
COL_HERO_RARITY = "Quality"
COL_HERO_RAGE_COST = "Rage Cost"   # if missing, default 1000
COL_HERO_ATK = "Attack"
COL_HERO_DEF = "Defense"
COL_HERO_HP = "Health"
COL_HERO_SKILL_FACTOR = "Skill Factor"  # optional; if missing, set manually in JSON

# TALENT NODE mapping
COL_TALENT_ID = "Node ID"
COL_TALENT_STAT = "Stat"  # you may need to add this to your sheet or map from "Name"
COL_TALENT_VALUE_PER_RANK = "Value 1"
COL_TALENT_MAX_RANK = "Max Rank"

# ARTIFACT mapping
COL_ART_ID = "ID"
COL_ART_NAME = "Artifact"
COL_ART_RARITY = "Quality"
COL_ART_MAIN_STAT = "Main Stat"     # e.g. "attack_percent"
COL_ART_MAIN_VALUE = "Main Max"     # choose Max for V1; you can add min-roll later

# PET mapping
COL_PET_ID = "ID"
COL_PET_NAME = "Pet"
COL_PET_RARITY = "Quality"
# Example bonus column names:
COL_PET_ATK_BONUS = "Attack Bonus"
COL_PET_DEF_BONUS = "Defense Bonus"
COL_PET_HP_BONUS = "Health Bonus"

def _read_sheet(excel_path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(excel_path, sheet_name=sheet)

def _safe_get(row: Dict[str, Any], col: str, default=None):
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return val

def export_v1_json(excel_path: str | Path, out_dir: str | Path) -> Dict[str, Path]:
    excel_path = Path(excel_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Heroes ---
    heroes: List[Dict[str, Any]] = []
    try:
        df = _read_sheet(excel_path, SHEET_HERO)
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        for r in records:
            hero_id = _safe_get(r, COL_HERO_ID)
            name = _safe_get(r, COL_HERO_NAME)
            if hero_id is None or name is None:
                continue
            heroes.append({
                "id": str(hero_id),
                "name": str(name),
                "rarity": str(_safe_get(r, COL_HERO_RARITY, "Unknown")),
                "rage_cost": int(_safe_get(r, COL_HERO_RAGE_COST, 1000) or 1000),
                "base_stats": {
                    "attack": float(_safe_get(r, COL_HERO_ATK, 0) or 0),
                    "defense": float(_safe_get(r, COL_HERO_DEF, 0) or 0),
                    "health": float(_safe_get(r, COL_HERO_HP, 0) or 0),
                },
                "skill_factor": float(_safe_get(r, COL_HERO_SKILL_FACTOR, 0) or 0),
                # Optional, can be filled later per-hero
                "skill_effects": []
            })
    except Exception as e:
        # If sheet names/columns don't match, you can still hand-edit JSON.
        pass

    heroes_path = out_dir / "heroes.json"
    heroes_path.write_text(json.dumps({"heroes": heroes}, indent=2), encoding="utf-8")

    # --- Talents ---
    talents: List[Dict[str, Any]] = []
    try:
        df = _read_sheet(excel_path, SHEET_TALENT_NODE)
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        for r in records:
            node_id = _safe_get(r, COL_TALENT_ID)
            stat = _safe_get(r, COL_TALENT_STAT)
            if node_id is None or stat is None:
                continue
            talents.append({
                "id": str(node_id),
                "stat": str(stat),
                "value_per_rank": float(_safe_get(r, COL_TALENT_VALUE_PER_RANK, 0) or 0),
                "max_rank": int(_safe_get(r, COL_TALENT_MAX_RANK, 1) or 1),
            })
    except Exception:
        pass

    talents_path = out_dir / "talents.json"
    talents_path.write_text(json.dumps({"talents": talents}, indent=2), encoding="utf-8")

    # --- Artifacts ---
    artifacts: List[Dict[str, Any]] = []
    try:
        df = _read_sheet(excel_path, SHEET_ARTIFACTS)
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        for r in records:
            art_id = _safe_get(r, COL_ART_ID)
            name = _safe_get(r, COL_ART_NAME)
            if art_id is None or name is None:
                continue
            main_stat = _safe_get(r, COL_ART_MAIN_STAT)
            main_val = _safe_get(r, COL_ART_MAIN_VALUE, 0)
            if main_stat is None:
                continue
            artifacts.append({
                "id": str(art_id),
                "name": str(name),
                "rarity": str(_safe_get(r, COL_ART_RARITY, "Unknown")),
                "main_stat": {"stat": str(main_stat), "value": float(main_val or 0)},
                "secondary_stats": {}
            })
    except Exception:
        pass

    artifacts_path = out_dir / "artifacts.json"
    artifacts_path.write_text(json.dumps({"artifacts": artifacts}, indent=2), encoding="utf-8")

    # --- Pets ---
    pets: List[Dict[str, Any]] = []
    try:
        df = _read_sheet(excel_path, SHEET_PETS)
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        for r in records:
            pid = _safe_get(r, COL_PET_ID)
            name = _safe_get(r, COL_PET_NAME)
            if pid is None or name is None:
                continue
            bonuses: Dict[str, float] = {}
            for col, stat in [
                (COL_PET_ATK_BONUS, "attack"),
                (COL_PET_DEF_BONUS, "defense"),
                (COL_PET_HP_BONUS, "health"),
            ]:
                val = _safe_get(r, col)
                if val is not None:
                    bonuses[stat] = bonuses.get(stat, 0.0) + float(val or 0)

            pets.append({
                "id": str(pid),
                "name": str(name),
                "rarity": str(_safe_get(r, COL_PET_RARITY, "Unknown")),
                "bonuses": bonuses
            })
    except Exception:
        pass

    pets_path = out_dir / "pets.json"
    pets_path.write_text(json.dumps({"pets": pets}, indent=2), encoding="utf-8")

    return {
        "heroes": heroes_path,
        "talents": talents_path,
        "artifacts": artifacts_path,
        "pets": pets_path,
    }
