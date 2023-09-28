from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId

from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *


class MacroStalkers(Strat):

    async def create_plan(self) -> BuildOrder:
        return BuildOrder(
            Step(
                None,
                ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS),
                skip=UnitExists(UnitTypeId.PROBE, 40, include_pending=True),
                skip_until=UnitExists(UnitTypeId.ASSIMILATOR, 1),
            ),
            SequentialList(
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 14),
                GridBuilding(UnitTypeId.PYLON, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 16),
                BuildGas(1),
                GridBuilding(UnitTypeId.GATEWAY, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 20),
                Expand(2),
                GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 21),
                BuildGas(2),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 22),
                GridBuilding(UnitTypeId.PYLON, 1),
                BuildOrder(
                    AutoPylon(),
                    Tech(UpgradeId.WARPGATERESEARCH),
                    [
                        ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 22),
                        Step(UnitExists(UnitTypeId.NEXUS, 2), ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 44)),
                        StepBuildGas(3, skip=Gas(300)),
                    ],
                    [ProtossUnit(UnitTypeId.STALKER, 100)],
                    [GridBuilding(UnitTypeId.GATEWAY, 7), StepBuildGas(4, skip=Gas(200))],
                ),
            ),
            SequentialList(
                MineOpenBlockedBase(),
                PlanZoneDefense(),
                RestorePower(),
                DistributeWorkers(),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                PlanZoneGather(),
                Step(UnitReady(UnitTypeId.GATEWAY, 4), PlanZoneAttack(4)),
                PlanFinishEnemy(),
            ),
        )
