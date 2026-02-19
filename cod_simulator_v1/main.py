from cod_simulator.io.json_loader import load_heroes, load_artifacts, load_pets, load_talents
from cod_simulator.engine.models import Build, SimConfig
from cod_simulator.engine.simulation import CombatSimulator
import argparse

def main():
    ap = argparse.ArgumentParser(description="Call of Dragons Simulator V1")
    ap.add_argument("--heroes", default="data/heroes.json")
    ap.add_argument("--artifacts", default="data/artifacts.json")
    ap.add_argument("--pets", default="data/pets.json")
    ap.add_argument("--talents", default="data/talents.json")
    ap.add_argument("--duration", type=int, default=60)
    ap.add_argument("--deterministic", action="store_true", default=True)
    ap.add_argument("--montecarlo", action="store_true", default=False)
    ap.add_argument("--targets", type=int, default=1)
    ap.add_argument("--counter", action="store_true", default=True)
    ap.add_argument("--no-counter", action="store_true", default=False)
    ap.add_argument("--rage-normal", type=float, default=94)
    ap.add_argument("--rage-counter", type=float, default=16)
    ap.add_argument("--def-const", type=float, default=1400.0)
    args = ap.parse_args()

    deterministic = not args.montecarlo

    heroes = load_heroes(args.heroes)
    artifacts = load_artifacts(args.artifacts)
    pets = load_pets(args.pets)
    talents = load_talents(args.talents)

    # For V1 CLI, we use the demo builds unless you edit this section or add a build.json loader.
    attacker_build = Build(hero_id="attacker_demo", artifact_id="art_demo", pet_id="pet_demo", selected_talents={"t1":3,"t2":2})
    defender_build = Build(hero_id="defender_demo")

    counter_enabled = (not args.no_counter) and args.counter

    cfg = SimConfig(
        duration_s=args.duration,
        deterministic=deterministic,
        target_count=args.targets,
        counter_enabled=counter_enabled,
        rage_on_normal=args.rage_normal,
        rage_on_counter=args.rage_counter,
        defense_constant=args.def_const
    )

    sim = CombatSimulator(
        attacker_hero=heroes[attacker_build.hero_id],
        defender_hero=heroes[defender_build.hero_id],
        attacker_build=attacker_build,
        defender_build=defender_build,
        artifacts=artifacts,
        pets=pets,
        talent_nodes=talents,
        config=cfg
    )
    print(sim.run())

if __name__ == "__main__":
    main()
