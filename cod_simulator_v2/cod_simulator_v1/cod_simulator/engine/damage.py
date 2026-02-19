from __future__ import annotations
import random

def defense_reduction(defense: float, constant: float) -> float:
    defense = max(0.0, float(defense))
    constant = max(1e-6, float(constant))
    return defense / (defense + constant)

def expected_crit_multiplier(crit_chance: float, crit_damage: float) -> float:
    c = min(max(float(crit_chance), 0.0), 1.0)
    cd = max(float(crit_damage), 1.0)
    return (1.0 - c) + (c * cd)

def roll_is_crit(crit_chance: float) -> bool:
    c = min(max(float(crit_chance), 0.0), 1.0)
    return random.random() < c

def calculate_damage(attacker: dict, defender: dict, base_multiplier: float, *, defense_constant: float, deterministic: bool) -> float:
    atk = float(attacker.get("attack", 0.0))
    base = atk * float(base_multiplier)

    skill_bonus = float(attacker.get("skill_damage_bonus", 0.0))
    all_bonus = float(attacker.get("all_damage_bonus", 0.0))
    dmg = base * (1.0 + skill_bonus) * (1.0 + all_bonus)

    dmg_reduction = float(defender.get("damage_reduction", 0.0))
    dmg *= (1.0 - min(max(dmg_reduction, 0.0), 0.95))

    defense = float(defender.get("defense", 0.0))
    dmg *= (1.0 - defense_reduction(defense, defense_constant))

    crit_chance = float(attacker.get("crit_chance", 0.0))
    crit_damage = float(attacker.get("crit_damage", 1.5))
    if deterministic:
        dmg *= expected_crit_multiplier(crit_chance, crit_damage)
    else:
        if roll_is_crit(crit_chance):
            dmg *= max(1.0, crit_damage)

    return max(0.0, dmg)
