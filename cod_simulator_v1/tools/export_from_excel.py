from __future__ import annotations
import argparse
from pathlib import Path
from cod_simulator.io.excel_export import export_v1_json

def main():
    ap = argparse.ArgumentParser(description="Export CoD V1 simulator JSON from an Excel workbook.")
    ap.add_argument("--excel", required=True, help="Path to Excel workbook (e.g., 'Call of Dragons Database.xlsx').")
    ap.add_argument("--out", default="data", help="Output directory for JSON files (default: data).")
    args = ap.parse_args()

    out = export_v1_json(Path(args.excel), Path(args.out))
    print("Exported:")
    for k, p in out.items():
        print(f" - {k}: {p}")

if __name__ == "__main__":
    main()
