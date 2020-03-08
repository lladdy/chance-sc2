from sc2.units import Units

from general.extended_power import ExtendedPower
from plans.tactics import PlanZoneAttack


class PlanZoneAttackAllIn(PlanZoneAttack):
    def _start_attack(self, power: ExtendedPower, attackers: Units):
        self.retreat_multiplier = 0  # never retreat, never surrender
        return super()._start_attack(power, attackers)
