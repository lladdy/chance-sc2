from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *


class ProxyVoidray(Strat):
    async def create_plan(self) -> BuildOrder:
        return BuildOrder(
            # ChronoUnit(UnitTypeId.VOIDRAY, UnitTypeId.STARGATE),
            SequentialList(
                GridBuilding(UnitTypeId.PYLON, 1),
                ProtossUnit(UnitTypeId.PROBE, 15),
                GridBuilding(UnitTypeId.GATEWAY, 1),
                ProtossUnit(UnitTypeId.PROBE, 14),
                BuildGas(1),
                ProtossUnit(UnitTypeId.PROBE, 16),
                BuildGas(1),
                ProtossUnit(UnitTypeId.PROBE, 18),
                GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                ProtossUnit(UnitTypeId.PROBE, 19),
                GridBuilding(UnitTypeId.PYLON, 2),
                ProtossUnit(UnitTypeId.PROBE, 21),
                GridBuilding(UnitTypeId.STARGATE, 2),  # todo: proxy
                ProtossUnit(UnitTypeId.ADEPT, 1),
                Tech(UpgradeId.WARPGATERESEARCH),
                ProtossUnit(UnitTypeId.PROBE, 23),
                GridBuilding(UnitTypeId.PYLON, 3),
                ProtossUnit(UnitTypeId.STALKER, 1),
                ProtossUnit(UnitTypeId.PROBE, 25),
                ProtossUnit(UnitTypeId.VOIDRAY, 1),
                ProtossUnit(UnitTypeId.PROBE, 30),
                BuildOrder(
                    AutoPylon(),
                    ProtossUnit(UnitTypeId.VOIDRAY, 1),
                ),
            ),
            # SequentialList(
            #     PlanZoneDefense(),
            #     RestorePower(),
            #     DistributeWorkers(),
            #     Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
            #     PlanZoneGather(),
            #     Step(UnitReady(UnitTypeId.VOIDRAY, 3), PlanZoneAttack(4)),
            #     PlanFinishEnemy(),
            # ),
        )
