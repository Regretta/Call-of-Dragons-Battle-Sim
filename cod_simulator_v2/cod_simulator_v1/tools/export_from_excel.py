from __future__ import annotations
import argparse
from pathlib import Path
from cod_simulator.io.excel_export import export_v1_json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True, help="Path to Excel workbook")
    ap.add_argument("--out", default="data", help="Output folder for JSON")
    args = ap.parse_args()
    out = export_v1_json(Path(args.excel), Path(args.out))
    print("Exported:")
    for k,v in out.items():
        print(f" - {k}: {v}")

if __name__ == "__main__":
    main()
