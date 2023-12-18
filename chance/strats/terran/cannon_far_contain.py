from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sharpy.managers.core.building_solver import WallType
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *


class CannonFarContain(Strat):
    """
    Contributed by Ratosh.
    """
    async def create_plan(self) -> BuildOrder:
        self._bot.building_solver.wall_type = WallType.NoWall
        rush_killed = RequireCustom(
            lambda k: self._bot.lost_units_manager.own_lost_type(UnitTypeId.PROBE) >= 3 or self._bot.time > 4 * 60
        )

        cannon_contain = self.cannon_contain()

        return BuildOrder(
            Step(
                None,
                ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS),
                skip=UnitExists(UnitTypeId.PROBE, 16),
                skip_until=UnitReady(UnitTypeId.PYLON, 1),
            ),
            ChronoAnyTech(0),
            SequentialList(
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 13),
                GridBuilding(UnitTypeId.PYLON, 1),
                Step(None, cannon_contain, skip=rush_killed),
                BuildOrder(
                    [
                        Expand(2),
                        ProtossUnit(UnitTypeId.PROBE, 30),
                        Step(UnitExists(UnitTypeId.NEXUS, 2), ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 44)),
                    ],
                    GridBuilding(UnitTypeId.GATEWAY, 2),
                    GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                    BuildGas(2),
                    AutoPylon(),
                    ProtossUnit(UnitTypeId.STALKER, 4, priority=True),
                    StepBuildGas(3, skip=Gas(300)),
                    Tech(UpgradeId.WARPGATERESEARCH),
                    BuildOrder([]).forge_upgrades_all,
                    Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL, 1), Tech(UpgradeId.BLINKTECH)),
                    [
                        ProtossUnit(UnitTypeId.PROBE, 22),
                        Step(UnitExists(UnitTypeId.NEXUS, 2), ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 44)),
                        StepBuildGas(3, skip=Gas(300)),
                    ],
                    [ProtossUnit(UnitTypeId.STALKER, 100)],
                    [
                        Step(UnitReady(UnitTypeId.CYBERNETICSCORE, 1), GridBuilding(UnitTypeId.TWILIGHTCOUNCIL, 1), ),
                        Step(UnitReady(UnitTypeId.CYBERNETICSCORE, 1), GridBuilding(UnitTypeId.GATEWAY, 7)),
                        StepBuildGas(4, skip=Gas(200)),
                    ],
                ),
            ),
            SequentialList(
                PlanCancelBuilding(),
                PlanZoneDefense(),
                DistributeWorkers(),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                PlanZoneGather(),
                PlanZoneAttack(6),
                PlanFinishEnemy(),
            ),
        )

    def cannon_contain(self) -> ActBase:
        enemy_natural: Point2 = self._bot.zone_manager.expansion_zones[-2].center_location
        contain_center: Point2 = enemy_natural.towards(self._bot.game_info.map_center, 25)

        return Step(
            None,
            BuildOrder(
                [
                    [
                        ActUnitOnce(UnitTypeId.PROBE, UnitTypeId.NEXUS, 14),
                        GridBuilding(UnitTypeId.FORGE, 1),
                        ActUnitOnce(UnitTypeId.PROBE, UnitTypeId.NEXUS, 18),
                    ],
                    [
                        BuildPosition(UnitTypeId.PYLON, contain_center),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 2),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 4),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PYLON,
                            contain_center.towards(enemy_natural, 6),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 8),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 10),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 12),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PYLON,
                            contain_center.towards(enemy_natural, 14),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 16),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 18),
                            exact=False,
                            only_once=True,
                        ),
                        BuildPosition(
                            UnitTypeId.PHOTONCANNON,
                            contain_center.towards(enemy_natural, 20),
                            exact=False,
                            only_once=True,
                        ),
                    ],
                    ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 16),
                ]
            ),
            # Skip cannon rushing until our natural is ready, or have over 750 minerals, the build is probably stuck
            skip=Any([UnitReady(UnitTypeId.NEXUS, 2), Minerals(750)]),
        )
