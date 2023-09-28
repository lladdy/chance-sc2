from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import *
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *


class DistruptorBuild(BuildOrder):
    def __init__(self):
        build = BuildOrder(
            Step(
                UnitReady(UnitTypeId.PYLON),
                ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS),
                skip=UnitExists(UnitTypeId.PROBE, 19),
            ),
            Step(
                None,
                ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY),
                skip=UnitExists(UnitTypeId.IMMORTAL, 1, include_killed=True),
            ),
            Step(
                None,
                ChronoUnit(UnitTypeId.OBSERVER, UnitTypeId.ROBOTICSFACILITY),
                skip=UnitExists(UnitTypeId.OBSERVER, 1, include_killed=True),
            ),
            Step(
                None,
                ChronoUnit(UnitTypeId.DISRUPTOR, UnitTypeId.ROBOTICSFACILITY),
                skip=UnitExists(UnitTypeId.DISRUPTOR, 1, include_killed=True),
            ),
            SequentialList(
                ProtossUnit(UnitTypeId.PROBE, 16 + 6),  # One base
                Step(UnitExists(UnitTypeId.NEXUS, 2), ProtossUnit(UnitTypeId.PROBE, 44)),
            ),
            Step(UnitReady(UnitTypeId.PYLON, 1), AutoPylon()),
            SequentialList(
                GridBuilding(UnitTypeId.PYLON, 1),
                GridBuilding(UnitTypeId.GATEWAY, 2, priority=True),
                BuildGas(2),
                GridBuilding(UnitTypeId.CYBERNETICSCORE, 1, priority=True),
                GridBuilding(UnitTypeId.ROBOTICSFACILITY, 1, priority=True),
                Tech(UpgradeId.WARPGATERESEARCH, UnitTypeId.CYBERNETICSCORE),
                GridBuilding(UnitTypeId.ROBOTICSBAY, 1, priority=True),
                Step(UnitExists(UnitTypeId.DISRUPTOR, 1, include_killed=True, include_not_ready=False), Expand(2), ),
                BuildGas(4),
            ),
            BuildOrder(
                ProtossUnit(UnitTypeId.IMMORTAL, 1, priority=True, only_once=True),
                ProtossUnit(UnitTypeId.OBSERVER, 1, priority=True),
                ProtossUnit(UnitTypeId.DISRUPTOR, 4, priority=True),
                ProtossUnit(UnitTypeId.STALKER),
                SequentialList(
                    Step(Minerals(300), GridBuilding(UnitTypeId.GATEWAY, 3, priority=True)),
                    Step(UnitReady(UnitTypeId.NEXUS, 2), GridBuilding(UnitTypeId.GATEWAY, 6, priority=True)),
                ),
            ),
        )

        tactics = [
            MineOpenBlockedBase(),
            PlanCancelBuilding(),
            WorkerRallyPoint(),
            RestorePower(),
            DistributeWorkers(),
            Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
            PlanWorkerOnlyDefense(),  # Counter worker rushes
            PlanZoneDefense(),
            PlanZoneGather(),
            Step(UnitExists(UnitTypeId.DISRUPTOR, include_killed=True), PlanZoneAttack()),
            PlanFinishEnemy(),
        ]

        super().__init__(build, tactics)


class Distruptors(Strat):
    async def create_plan(self) -> BuildOrder:
        return DistruptorBuild()
