from chance.strats.strat import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import BuildOrder, StepBuildGas, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, ZergUnit
from sharpy.plans.require import RequireCustom, Any, Gas, TechReady
from sharpy.plans.tactics import *
from sharpy.plans.tactics.zerg import InjectLarva
from sharpy.plans.tactics.zone_attack_all_in import PlanZoneAttackAllIn


class LingRush(Strat):

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
        limit_gas = Any([Gas(100), TechReady(UpgradeId.ZERGLINGMOVEMENTSPEED, 0.001)])
        return BuildOrder([
            SequentialList([
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                Expand(2),
                StepBuildGas(1),
                ActBuilding(UnitTypeId.SPAWNINGPOOL, 1),
                ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
                Step(None, Tech(UpgradeId.ZERGLINGMOVEMENTSPEED, UnitTypeId.SPAWNINGPOOL),
                     skip_until=Gas(100)),
                ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 1),
                ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 30),
                ActBuilding(UnitTypeId.BANELINGNEST, 1),
                BuildOrder([
                    Step(None, ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 200),
                         skip=RequireCustom(lambda k: self._bot.vespene > 25 or flying_buildings)),
                    Step(None, ActUnit(UnitTypeId.BANELING, UnitTypeId.ZERGLING, 200),
                         skip=RequireCustom(flying_buildings)),
                ])
            ]),
            SequentialList([
                Step(None, DistributeWorkers(), skip=limit_gas),
                Step(limit_gas, DistributeWorkers(1, 1), skip=RequireCustom(flying_buildings)),
                Step(RequireCustom(flying_buildings), DistributeWorkers()),
            ]),
            in_case_of_air,
            SequentialList(
                [
                    MineOpenBlockedBase(),
                    Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                    PlanZoneDefense(),
                    AutoOverLord(),
                    InjectLarva(),
                    PlanZoneGather(),
                    Step(TechReady(UpgradeId.ZERGLINGMOVEMENTSPEED), PlanZoneAttackAllIn(10)),
                    PlanFinishEnemy(),
                ])
        ])
