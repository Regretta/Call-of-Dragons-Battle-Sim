from __future__ import annotations
from typing import Dict, Any
from .models import Hero, Artifact, Pet, TalentNode, Build, SimConfig
from .stats import build_final_stats, StatBlock
from .rage import RageSystem
from .damage import calculate_damage
from .modifiers import ModifierManager

class CombatSimulator:
    def __init__(
        self,
        *,
        attacker_hero: Hero,
        defender_hero: Hero,
        attacker_build: Build,
        defender_build: Build,
        artifacts: Dict[str, Artifact],
        pets: Dict[str, Pet],
        talent_nodes: Dict[str, TalentNode],
        config: SimConfig,
    ) -> None:
        self.cfg = config
        self.time_s = 0

        self.attacker_base: StatBlock = build_final_stats(
            attacker_hero,
            artifact=artifacts.get(attacker_build.artifact_id) if attacker_build.artifact_id else None,
            pet=pets.get(attacker_build.pet_id) if attacker_build.pet_id else None,
            talent_nodes=talent_nodes,
            build=attacker_build,
        )
        self.defender_base: StatBlock = build_final_stats(
            defender_hero,
            artifact=artifacts.get(defender_build.artifact_id) if defender_build.artifact_id else None,
            pet=pets.get(defender_build.pet_id) if defender_build.pet_id else None,
            talent_nodes=talent_nodes,
            build=defender_build,
        )

        self.attacker_hero = attacker_hero
        self.mod_att = ModifierManager()
        self.mod_def = ModifierManager()

        self.rage = RageSystem(
            rage_cost=attacker_hero.rage_cost,
            rage_bonus=self.attacker_base.get("rage_bonus"),
        )

        self.def_shield = self.defender_base.get("shield")

        self.total_damage = 0.0
        self.breakdown = {"normal": 0.0, "skill": 0.0, "aoe_extra": 0.0}

    def _eff_att(self) -> Dict[str, float]:
        s = self.attacker_base.as_dict()
        for k, v in self.mod_att.snapshot().items():
            s[k] = s.get(k, 0.0) + float(v)
        return s

    def _eff_def(self) -> Dict[str, float]:
        s = self.defender_base.as_dict()
        for k, v in self.mod_def.snapshot().items():
            s[k] = s.get(k, 0.0) + float(v)
        s["shield"] = self.def_shield
        return s

    def _apply_to_def(self, dmg: float) -> float:
        dmg = max(0.0, float(dmg))
        if self.def_shield > 0:
            absorbed = min(self.def_shield, dmg)
            self.def_shield -= absorbed
            dmg -= absorbed
        self.total_damage += dmg
        return dmg

    def _normal_attack(self) -> None:
        dmg = calculate_damage(self._eff_att(), self._eff_def(), 0.5, defense_constant=self.cfg.defense_constant, deterministic=self.cfg.deterministic)
        dealt = self._apply_to_def(dmg)
        self.breakdown["normal"] += dealt
        self.rage.gain(self.cfg.rage_on_normal)

    def _counter(self) -> None:
        self.rage.gain(self.cfg.rage_on_counter)

    def _cast_skill(self) -> None:
        mult = float(self.attacker_hero.skill_factor) / 1000.0
        dmg_primary = calculate_damage(self._eff_att(), self._eff_def(), mult, defense_constant=self.cfg.defense_constant, deterministic=self.cfg.deterministic)

        if self.cfg.target_count <= 1:
            dealt = self._apply_to_def(dmg_primary)
            self.breakdown["skill"] += dealt
        else:
            extra_targets = self.cfg.target_count - 1
            total = dmg_primary + (dmg_primary * float(self.cfg.aoe_split_ratio) * extra_targets)
            dealt = self._apply_to_def(total)
            self.breakdown["skill"] += dmg_primary
            self.breakdown["aoe_extra"] += max(0.0, dealt - dmg_primary)

        self.rage.cast()

        # Post-cast timed effects
        for eff in (self.attacker_hero.skill_effects or []):
            if eff.get("type") != "buff":
                continue
            target = eff.get("target", "attacker")
            stat = eff.get("stat")
            value = float(eff.get("value", 0.0))
            duration = int(eff.get("duration_s", 0))
            if not stat or duration <= 0:
                continue
            if target == "attacker":
                self.mod_att.add(stat, value, duration)
            else:
                self.mod_def.add(stat, value, duration)

    def step(self) -> None:
        self._normal_attack()
        if self.cfg.counter_enabled:
            self._counter()
        if self.rage.can_cast():
            self._cast_skill()
        self.mod_att.tick()
        self.mod_def.tick()
        self.time_s += 1

    def run(self) -> Dict[str, Any]:
        while self.time_s < self.cfg.duration_s:
            self.step()
        return {
            "duration_s": self.cfg.duration_s,
            "total_damage": self.total_damage,
            "dps": self.total_damage / max(1, self.cfg.duration_s),
            "breakdown": self.breakdown,
            "final_rage": self.rage.rage,
        }
