from chance.strats.strat import Strat
from sc2 import UnitTypeId
from sharpy.plans import BuildOrder, StepBuildGas, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, ZergUnit
from sharpy.plans.require import RequiredUnitExists
from sharpy.plans.tactics import *
from sharpy.plans.tactics.zerg import InjectLarva


class RoachRush(Strat):
    """ Build implementation of https://lotv.spawningtool.com/build/88835/"""

    async def create_plan(self) -> BuildOrder:
        flying_buildings = lambda k: self._bot.enemy_structures.flying.exists and self._bot.supply_used > 30
        in_case_of_air = [
            Step(flying_buildings, StepBuildGas(2)),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 20),
            MorphLair(),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 30),
            StepBuildGas(4),
            ActBuilding(UnitTypeId.SPIRE),
            ZergUnit(UnitTypeId.MUTALISK, 10, priority=True)
        ]
        return BuildOrder([
            SequentialList([
                ActBuilding(UnitTypeId.SPAWNINGPOOL, 1),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                StepBuildGas(1),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
                ActBuilding(UnitTypeId.ROACHWARREN, 1),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 1),
                ActUnit(UnitTypeId.ROACH, UnitTypeId.LARVA, 100),
            ]),
            in_case_of_air,
            SequentialList(
                [
                    PlanDistributeWorkers(),
                    PlanZoneDefense(),
                    AutoOverLord(),
                    InjectLarva(),
                    PlanZoneGather(),
                    Step(RequiredUnitExists(UnitTypeId.ROACH, 7), PlanZoneAttack(1)),
                    PlanFinishEnemy(),
                ])
        ])
