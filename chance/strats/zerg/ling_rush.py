from chance.strats.strat import Strat
from sc2 import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units
from sharpy.general.extended_power import ExtendedPower
from sharpy.plans import BuildOrder, StepBuildGas, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, ZergUnit
from sharpy.plans.require import RequiredGas, RequireCustom, RequiredUnitExists, RequiredAny, RequiredTechReady
from sharpy.plans.tactics import *
from sharpy.plans.tactics.zerg import InjectLarva



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
        limit_gas = RequiredAny([RequiredGas(100), RequiredTechReady(UpgradeId.ZERGLINGMOVEMENTSPEED, 0.001)])
        return BuildOrder([
            SequentialList([
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActExpand(2),
                StepBuildGas(1),
                ActBuilding(UnitTypeId.SPAWNINGPOOL, 1),
                ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
                Step(None, ActTech(UpgradeId.ZERGLINGMOVEMENTSPEED, UnitTypeId.SPAWNINGPOOL),
                     skip_until=RequiredGas(100)),
                ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 1),
                ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 30),
                ActBuilding(UnitTypeId.BANELINGNEST, 1),
                BuildOrder([
                    Step(None, ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 200), skip=RequireCustom(lambda k: self._bot.vespene > 25 or flying_buildings)),
                    Step(None, ActUnit(UnitTypeId.BANELING, UnitTypeId.ZERGLING, 200), skip=RequireCustom(flying_buildings)),
                ])
            ]),
            SequentialList([
                Step(None, PlanDistributeWorkers(), skip=limit_gas),
                Step(limit_gas, PlanDistributeWorkers(1, 1), skip=RequireCustom(flying_buildings)),
                Step(RequireCustom(flying_buildings), PlanDistributeWorkers()),
            ]),
            in_case_of_air,
            SequentialList(
                [
                    PlanZoneDefense(),
                    AutoOverLord(),
                    InjectLarva(),
                    PlanZoneGather(),
                    Step(RequiredTechReady(UpgradeId.ZERGLINGMOVEMENTSPEED), PlanZoneAttack(10)),
                    PlanFinishEnemy(),
                ])
        ])
