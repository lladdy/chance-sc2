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


class NoRetreatAttack(PlanZoneAttack):
    def _start_attack(self, power: ExtendedPower, attackers: Units):
        self.retreat_multiplier = 0  # don't retreat
        return super()._start_attack(power, attackers)


class LingRush(Strat):

    async def create_plan(self) -> BuildOrder:
        in_case_of_air = [
            Step(RequireCustom(lambda k: self._bot.enemy_structures.flying.exists and self._bot.supply_used > 30),
                 StepBuildGas(2)),
            RequiredUnitExists(UnitTypeId.DRONE, 20),
            MorphLair(),
            RequiredUnitExists(UnitTypeId.DRONE, 30),
            StepBuildGas(4),
            ActBuilding(UnitTypeId.SPIRE),
            ZergUnit(UnitTypeId.MUTALISK, 10, priority=True)
        ]
        stop_gas = RequiredAny([RequiredGas(100), RequiredTechReady(UpgradeId.ZERGLINGMOVEMENTSPEED, 0.001)])
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
                ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 200),
            ]),
            in_case_of_air,
            SequentialList([
                Step(None, PlanDistributeWorkers(), skip=stop_gas),
                Step(None, PlanDistributeWorkers(0, 0), skip_until=stop_gas),
            ]),
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
