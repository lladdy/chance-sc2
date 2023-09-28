from chance.strats.strat import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.plans import BuildOrder, StepBuildGas, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, ZergUnit
from sharpy.plans.require import UnitExists
from sharpy.plans.tactics import *
from sharpy.plans.tactics.zerg import InjectLarva
from sharpy.plans.tactics.zone_attack_all_in import PlanZoneAttackAllIn


class RavagerRush(Strat):
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
                StepBuildGas(2),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActBuilding(UnitTypeId.ROACHWARREN, 1),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActUnit(UnitTypeId.ROACH, UnitTypeId.LARVA, 3),
                ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 3),
                ActUnit(UnitTypeId.ROACH, UnitTypeId.LARVA, 4),
                ActUnit(UnitTypeId.RAVAGER, UnitTypeId.ROACH, 3),
                ActUnit(UnitTypeId.ROACH, UnitTypeId.LARVA, 100),
            ]),
            in_case_of_air,
            SequentialList(
                [
                    MineOpenBlockedBase(),
                    DistributeWorkers(4),
                    Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                    PlanZoneDefense(),
                    AutoOverLord(),
                    InjectLarva(),
                    PlanZoneGather(),
                    Step(UnitExists(UnitTypeId.RAVAGER), PlanZoneAttackAllIn(10)),
                    PlanFinishEnemy(),
                ])
        ])
