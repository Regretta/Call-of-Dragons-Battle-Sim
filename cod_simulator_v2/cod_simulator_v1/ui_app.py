import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from cod_simulator.io.json_loader import load_heroes, load_artifacts, load_pets, load_talents
from cod_simulator.io.excel_export import export_v1_json
from cod_simulator.engine.models import Build, SimConfig
from cod_simulator.engine.simulation import CombatSimulator
from cod_simulator.ui.talent_editor import TalentTreeEditor

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_EXCEL = BASE_DIR / "spreadsheets" / "Call of Dragons Database.xlsx"

def safe_float(s, default=0.0):
    try:
        return float(s)
    except Exception:
        return default

def safe_int(s, default=0):
    try:
        return int(float(s))
    except Exception:
        return default

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Call of Dragons Simulator V1")
        self.geometry("1020x700")

        self.att_selected_talents = {}
        self.def_selected_talents = {}

        self._load_data()
        self._ui()

    def _load_data(self):
        self.heroes = load_heroes(DATA_DIR / "heroes.json")
        self.artifacts = load_artifacts(DATA_DIR / "artifacts.json")
        self.pets = load_pets(DATA_DIR / "pets.json")
        self.talents = load_talents(DATA_DIR / "talents.json")
        self.hero_ids = list(self.heroes.keys())
        self.artifact_ids = ["(none)"] + list(self.artifacts.keys())
        self.pet_ids = ["(none)"] + list(self.pets.keys())

    def _ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        top = ttk.Frame(root)
        top.pack(fill="x")

        a = ttk.LabelFrame(top, text="Attacker", padding=10)
        a.pack(side="left", fill="both", expand=True, padx=(0, 8))
        d = ttk.LabelFrame(top, text="Defender", padding=10)
        d.pack(side="left", fill="both", expand=True)

        self.att_hero = tk.StringVar(value=self.hero_ids[0] if self.hero_ids else "")
        self.att_art = tk.StringVar(value="(none)")
        self.att_pet = tk.StringVar(value="(none)")
        self.att_extra = tk.StringVar(value="{}")
        self.att_points = tk.StringVar(value="Talents: 0 pts")

        self.def_hero = tk.StringVar(value=self.hero_ids[1] if len(self.hero_ids)>1 else (self.hero_ids[0] if self.hero_ids else ""))
        self.def_art = tk.StringVar(value="(none)")
        self.def_pet = tk.StringVar(value="(none)")
        self.def_extra = tk.StringVar(value="{}")
        self.def_points = tk.StringVar(value="Talents: 0 pts")

        def build_side(frame, hero_var, art_var, pet_var, extra_var, points_var, open_talents_fn):
            ttk.Label(frame, text="Hero").grid(row=0, column=0, sticky="w")
            ttk.Combobox(frame, textvariable=hero_var, values=self.hero_ids, state="readonly").grid(row=0, column=1, sticky="ew")
            ttk.Label(frame, text="Artifact").grid(row=1, column=0, sticky="w")
            ttk.Combobox(frame, textvariable=art_var, values=self.artifact_ids, state="readonly").grid(row=1, column=1, sticky="ew")
            ttk.Label(frame, text="Pet").grid(row=2, column=0, sticky="w")
            ttk.Combobox(frame, textvariable=pet_var, values=self.pet_ids, state="readonly").grid(row=2, column=1, sticky="ew")

            ttk.Button(frame, text="Edit Talents...", command=open_talents_fn).grid(row=3, column=0, sticky="w")
            ttk.Label(frame, textvariable=points_var).grid(row=3, column=1, sticky="w")

            ttk.Label(frame, text="Extra bonuses JSON").grid(row=4, column=0, sticky="w")
            ttk.Entry(frame, textvariable=extra_var).grid(row=4, column=1, sticky="ew")
            frame.columnconfigure(1, weight=1)

        build_side(a, self.att_hero, self.att_art, self.att_pet, self.att_extra, self.att_points, self.open_att_talents)
        build_side(d, self.def_hero, self.def_art, self.def_pet, self.def_extra, self.def_points, self.open_def_talents)

        cfg = ttk.LabelFrame(root, text="Simulation Settings", padding=10)
        cfg.pack(fill="x", pady=10)

        self.duration = tk.StringVar(value="60")
        self.targets = tk.StringVar(value="1")
        self.aoe = tk.StringVar(value="0.5")
        self.rn = tk.StringVar(value="94")
        self.rc = tk.StringVar(value="16")
        self.defc = tk.StringVar(value="1400")
        self.counter = tk.BooleanVar(value=True)
        self.det = tk.BooleanVar(value=True)

        ttk.Label(cfg, text="Duration").grid(row=0, column=0, sticky="w")
        ttk.Entry(cfg, textvariable=self.duration, width=8).grid(row=0, column=1, sticky="w", padx=(6,12))
        ttk.Label(cfg, text="Targets").grid(row=0, column=2, sticky="w")
        ttk.Entry(cfg, textvariable=self.targets, width=8).grid(row=0, column=3, sticky="w", padx=(6,12))
        ttk.Label(cfg, text="AOE split").grid(row=0, column=4, sticky="w")
        ttk.Entry(cfg, textvariable=self.aoe, width=8).grid(row=0, column=5, sticky="w", padx=(6,12))

        ttk.Label(cfg, text="Rage normal").grid(row=1, column=0, sticky="w")
        ttk.Entry(cfg, textvariable=self.rn, width=8).grid(row=1, column=1, sticky="w", padx=(6,12))
        ttk.Label(cfg, text="Rage counter").grid(row=1, column=2, sticky="w")
        ttk.Entry(cfg, textvariable=self.rc, width=8).grid(row=1, column=3, sticky="w", padx=(6,12))
        ttk.Label(cfg, text="Defense const").grid(row=1, column=4, sticky="w")
        ttk.Entry(cfg, textvariable=self.defc, width=8).grid(row=1, column=5, sticky="w", padx=(6,12))

        ttk.Checkbutton(cfg, text="Counter enabled", variable=self.counter).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(cfg, text="Deterministic (EV crit)", variable=self.det).grid(row=2, column=2, sticky="w")

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(0,10))
        ttk.Button(actions, text="Run Simulation", command=self.run_sim).pack(side="left")
        ttk.Button(actions, text="Import from Excel (Database)", command=self.import_excel).pack(side="left", padx=8)

        out = ttk.LabelFrame(root, text="Output", padding=10)
        out.pack(fill="both", expand=True)
        self.text = tk.Text(out, wrap="none")
        self.text.pack(fill="both", expand=True)
        self.text.insert("end", "Ready.\nTip: Talents UI uses x/y from talents.json (exported from Excel if those columns exist).\n")

    def _points_str(self, dct):
        return f"Talents: {sum(int(v) for v in dct.values())} pts"

    def open_att_talents(self):
        def apply(sel):
            self.att_selected_talents = sel
            self.att_points.set(self._points_str(sel))
        TalentTreeEditor(self, self.talents, self.att_selected_talents, on_apply=apply, title="Attacker Talents")

    def open_def_talents(self):
        def apply(sel):
            self.def_selected_talents = sel
            self.def_points.set(self._points_str(sel))
        TalentTreeEditor(self, self.talents, self.def_selected_talents, on_apply=apply, title="Defender Talents")

    def import_excel(self):
        path = filedialog.askopenfilename(
            title="Select Call of Dragons Database workbook",
            initialdir=str((BASE_DIR/"spreadsheets").resolve()),
            filetypes=[("Excel files","*.xlsx")],
            initialfile=str(DEFAULT_EXCEL.name) if DEFAULT_EXCEL.exists() else ""
        )
        if not path:
            return
        try:
            export_v1_json(path, DATA_DIR)
            self._load_data()
            messagebox.showinfo("Import complete", "Exported JSON to ./data. Restart the app to refresh dropdown lists.")
            self.text.insert("end", f"\nImported from: {path}\nUpdated JSON in: {DATA_DIR}\n")
        except Exception as e:
            messagebox.showerror("Import failed", str(e))

    def run_sim(self):
        try:
            att = Build(
                hero_id=self.att_hero.get(),
                artifact_id=None if self.att_art.get()=="(none)" else self.att_art.get(),
                pet_id=None if self.att_pet.get()=="(none)" else self.att_pet.get(),
                selected_talents=self.att_selected_talents,
                extra_bonuses=json.loads(self.att_extra.get() or "{}"),
            )
            deff = Build(
                hero_id=self.def_hero.get(),
                artifact_id=None if self.def_art.get()=="(none)" else self.def_art.get(),
                pet_id=None if self.def_pet.get()=="(none)" else self.def_pet.get(),
                selected_talents=self.def_selected_talents,
                extra_bonuses=json.loads(self.def_extra.get() or "{}"),
            )
            cfg = SimConfig(
                duration_s=safe_int(self.duration.get(), 60),
                deterministic=bool(self.det.get()),
                target_count=max(1, safe_int(self.targets.get(), 1)),
                aoe_split_ratio=max(0.0, safe_float(self.aoe.get(), 0.5)),
                counter_enabled=bool(self.counter.get()),
                rage_on_normal=safe_float(self.rn.get(), 94),
                rage_on_counter=safe_float(self.rc.get(), 16),
                defense_constant=safe_float(self.defc.get(), 1400),
            )
            sim = CombatSimulator(
                attacker_hero=self.heroes[att.hero_id],
                defender_hero=self.heroes[deff.hero_id],
                attacker_build=att,
                defender_build=deff,
                artifacts=self.artifacts,
                pets=self.pets,
                talent_nodes=self.talents,
                config=cfg,
            )
            res = sim.run()
            self.text.delete("1.0","end")
            self.text.insert("end", json.dumps(res, indent=2))
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__=="__main__":
    App().mainloop()
