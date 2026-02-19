# CoD Simulator V1 — Talent Tree UI

## Run
```bat
py -m pip install -r requirements.txt
python ui_app.py
```

## Talent Tree UI
- Click **Edit Talents...** under Attacker/Defender
- Hover nodes for tooltip
- Left click cycles rank (0 → 1 → ... → max → 0)
- Prereqs enforced (basic): you cannot rank a node unless its prereq nodes have rank > 0

## Pull talents from Excel database
In the UI click **Import from Excel (Database)** and select your workbook.

Talent nodes support OPTIONAL columns on the "Talent Node" sheet:
- Name
- Description
- Tree
- X
- Y
- Prereq (comma-separated node IDs)

If those columns are not present, export still works but nodes will stack at (0,0).
Add the columns (or update the COL_* constants in `cod_simulator/io/excel_export.py`).

## Build EXE
Run `build_windows_exe.bat` and use `dist\CoD_Sim_V1.exe`.
