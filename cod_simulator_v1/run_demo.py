from cod_simulator.io.json_loader import load_heroes, load_artifacts, load_pets, load_talents
from cod_simulator.engine.models import Build, SimConfig
from cod_simulator.engine.simulation import CombatSimulator

def main():
    heroes = load_heroes("data/heroes.json")
    artifacts = load_artifacts("data/artifacts.json")
    pets = load_pets("data/pets.json")
    talents = load_talents("data/talents.json")

    attacker_build = Build(
        hero_id="attacker_demo",
        artifact_id="art_demo",
        pet_id="pet_demo",
        selected_talents={"t1": 3, "t2": 2},
        extra_bonuses={}
    )

    defender_build = Build(
        hero_id="defender_demo",
        artifact_id=None,
        pet_id=None,
        selected_talents={},
        extra_bonuses={}
    )

    cfg = SimConfig(
        duration_s=60,
        deterministic=True,
        target_count=1,
        counter_enabled=True,
        rage_on_normal=94,
        rage_on_counter=16,
        defense_constant=1400.0
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

    result = sim.run()
    print(result)

if __name__ == "__main__":
    main()
