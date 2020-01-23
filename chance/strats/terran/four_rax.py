from chance.strats.strat import Strat
from sc2 import UnitTypeId
from sc2.units import Units
from sharpy.general.extended_power import ExtendedPower
from sharpy.managers.roles import UnitTask
from sharpy.plans import BuildOrder, SequentialList
from sharpy.plans.acts import *
from sharpy.plans.acts.terran import AutoDepot
from sharpy.plans.tactics import *
from sharpy.plans.tactics.terran import LowerDepots, ManTheBunkers, Repair, ContinueBuilding, PlanZoneGatherTerran


class AllInPlanZoneAttack(PlanZoneAttack):

    def _start_attack(self, power: ExtendedPower, attackers: Units):
        self.retreat_multiplier = 0  # never retreat, never surrender

        for unit in self.cache.own(UnitTypeId.SCV).closest_n_units(self.knowledge.enemy_start_location, 5):
            self.knowledge.roles.set_task(UnitTask.Attacking, unit)

        return super()._start_attack(power, attackers)


class FourRax(Strat):
    async def create_plan(self) -> BuildOrder:
        return BuildOrder([
            SequentialList([
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 13),
                GridBuilding(UnitTypeId.SUPPLYDEPOT, 1),
                GridBuilding(UnitTypeId.BARRACKS, 3),
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 14),
                ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 1),
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 15),
                GridBuilding(UnitTypeId.BARRACKS, 4),
                BuildOrder([
                    AutoDepot(),
                    ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 200),
                ])

            ]),
            SequentialList(
                [
                    PlanCancelBuilding(),
                    LowerDepots(),
                    PlanZoneDefense(),
                    PlanDistributeWorkers(),
                    ManTheBunkers(),
                    Repair(),
                    ContinueBuilding(),
                    PlanZoneGatherTerran(),
                    AllInPlanZoneAttack(10),
                    PlanFinishEnemy(),
                ])
        ])
