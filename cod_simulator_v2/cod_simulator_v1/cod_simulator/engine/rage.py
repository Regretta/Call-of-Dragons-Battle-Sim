from __future__ import annotations

class RageSystem:
    def __init__(self, rage_cost: int = 1000, rage_bonus: float = 0.0) -> None:
        self.rage_cost = int(rage_cost)
        self.rage_bonus = float(rage_bonus)
        self.rage = 0.0

    def gain(self, amount: float) -> None:
        self.rage += float(amount) * (1.0 + self.rage_bonus)

    def can_cast(self) -> bool:
        return self.rage >= self.rage_cost

    def cast(self) -> None:
        self.rage -= self.rage_cost
