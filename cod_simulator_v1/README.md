# Call of Dragons Simulator — V1 (Python)

This is a clean, refactored **V1 package** for a time-stepped Call of Dragons combat simulator.

## What V1 Includes
- **1-second time steps**
- Each second:
  - Attacker normal attacks (**gains 94 rage**)
  - If enabled, defender counterattacks (**attacker gains 16 rage**)
- **Cast active skill at 1000 rage**
- **Crit rate & crit damage**
  - Deterministic mode = expected value (default)
  - Monte Carlo mode = per-hit crit rolling
- **Stats aggregation** from:
  - Hero base stats
  - Artifact main/secondary stats
  - Pet bonuses
  - Talent nodes (node_id -> rank)
  - Extra bonuses (for testing)
- **Timed effects** after skill cast (e.g., +10% skill damage for 3 seconds)
- **Shield absorption** (defender shield absorbs damage before it counts)
- **AOE split** support (damage across multiple targets)

## Quick Start
1) Install Python 3.10+  
2) Install dependencies:
```bash
pip install -r requirements.txt
```

3) Run the demo:
```bash
python run_demo.py
```

## Running the CLI
```bash
python main.py --duration 60 --targets 1 --rage-normal 94 --rage-counter 16
```

To use Monte Carlo crit rolling:
```bash
python main.py --montecarlo
```

## Data Files (JSON)
The simulator reads from:
- `data/heroes.json`
- `data/artifacts.json`
- `data/pets.json`
- `data/talents.json`

### Hero schema (V1)
Each hero includes:
- base_stats: attack/defense/health + optional bonuses (crit_chance, crit_damage, etc.)
- skill_factor: e.g. 1400 means 1.4x attack
- skill_effects: list of timed effects applied after cast

Example skill_effect:
```json
{"type":"buff","target":"attacker","stat":"skill_damage_bonus","value":0.10,"duration_s":3}
```

## Exporting from your Excel database
This repo includes an exporter you can customize:

```bash
python tools/export_from_excel.py --excel "Call of Dragons Database.xlsx" --out data
```

### IMPORTANT:
Your workbook sheet/column names may differ.
Open `cod_simulator/io/excel_export.py` and adjust:
- sheet names (SHEET_HERO, SHEET_TALENT_NODE, ...)
- column names (COL_HERO_ID, COL_HERO_NAME, ...)

Then rerun the export.

## Uploading to GitHub (no copy/paste)
1) Unzip this project locally
2) Create a GitHub repo
3) Drag-and-drop the entire folder into GitHub **or** push via git:

```bash
git init
git add .
git commit -m "Initial V1 simulator"
git branch -M main
git remote add origin <your_repo_url>
git push -u origin main
```

## Notes / Future Expansion
This V1 is intentionally modular so you can add:
- troop count scaling
- bidirectional HP and troop loss over time
- multiple skills / rotations
- true counter damage / retaliation stats
- damage types (physical vs magic) and matching defenses
- behemoth / season modifiers
