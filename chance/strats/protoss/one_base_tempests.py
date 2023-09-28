from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.managers.core.building_solver import WallType
from sharpy.plans import BuildOrder, Step, SequentialList
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *


class OneBaseTempests(Strat):
    async def create_plan(self) -> BuildOrder:
        self._bot.building_solver.wall_type = WallType.ProtossMainZerg
        attack = PlanZoneAttack(4)
        return BuildOrder(
            [
                ChronoUnit(UnitTypeId.TEMPEST, UnitTypeId.STARGATE),
                SequentialList(
                    ProtossUnit(UnitTypeId.PROBE, 14),
                    GridBuilding(UnitTypeId.PYLON, 1),
                    ProtossUnit(UnitTypeId.PROBE, 15),
                    GridBuilding(UnitTypeId.GATEWAY, 1),
                    GridBuilding(UnitTypeId.FORGE, 1),
                    BuildGas(2),
                    ProtossUnit(UnitTypeId.PROBE, 18),
                    GridBuilding(UnitTypeId.PYLON, 2),
                    GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                    ProtossUnit(UnitTypeId.PROBE, 22),
                    BuildOrder(
                        AutoPylon(),
                        SequentialList(
                            GridBuilding(UnitTypeId.STARGATE, 1),
                            Step(UnitReady(UnitTypeId.STARGATE, 1), GridBuilding(UnitTypeId.FLEETBEACON, 1)),
                        ),
                        [ProtossUnit(UnitTypeId.TEMPEST, 100, priority=True)],
                        [Step(UnitExists(UnitTypeId.FLEETBEACON, 1), GridBuilding(UnitTypeId.STARGATE, 2))],
                    ),
                ),
                DefensiveCannons(4, 2, 0),
                SequentialList(
                    MineOpenBlockedBase(),
                    PlanZoneDefense(),
                    RestorePower(),
                    DistributeWorkers(),
                    Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                    PlanZoneGather(),
                    Step(UnitExists(UnitTypeId.TEMPEST, 1, include_killed=True), attack),
                    PlanFinishEnemy(),
                ),
            ]
        )
