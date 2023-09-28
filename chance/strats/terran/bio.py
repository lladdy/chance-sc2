from typing import List, Optional

from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sharpy.interfaces import IZoneManager
from sharpy.knowledges import Knowledge
from sharpy.managers.extensions import BuildDetector, ChatManager
from sharpy.plans import BuildOrder, Step, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.terran import *
from sharpy.plans.require import *
from sharpy.plans.require.supply import SupplyType
from sharpy.plans.tactics import *
from sharpy.plans.tactics.terran import *


class BuildBio(BuildOrder):
    zone_manager: IZoneManager

    def __init__(self):
        self.worker_rushed = False
        self.rush_bunker = BuildPosition(UnitTypeId.BUNKER, Point2((0, 0)), exact=True)
        viking_counters = [
            UnitTypeId.COLOSSUS,
            UnitTypeId.MEDIVAC,
            UnitTypeId.RAVEN,
            UnitTypeId.VOIDRAY,
            UnitTypeId.CARRIER,
            UnitTypeId.TEMPEST,
            UnitTypeId.BROODLORD,
        ]

        warn = WarnBuildMacro(
            [
                (UnitTypeId.SUPPLYDEPOT, 1, 18),
                (UnitTypeId.BARRACKS, 1, 42),
                (UnitTypeId.REFINERY, 1, 44),
                (UnitTypeId.COMMANDCENTER, 2, 60 + 44),
                (UnitTypeId.BARRACKSREACTOR, 1, 120),
                (UnitTypeId.FACTORY, 1, 120 + 21),
            ],
            [],
        )

        scv = [
            Step(None, TerranUnit(UnitTypeId.MARINE, 2, priority=True), skip_until=lambda k: self.worker_rushed),
            Step(None, MorphOrbitals(), skip_until=UnitReady(UnitTypeId.BARRACKS, 1)),
            Step(
                None,
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 16 + 6),
                skip=UnitExists(UnitTypeId.COMMANDCENTER, 2),
            ),
            Step(None, ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 32 + 12)),
        ]

        dt_counter = [
            Step(
                Any(
                    [
                        EnemyBuildingExists(UnitTypeId.DARKSHRINE),
                        EnemyUnitExistsAfter(UnitTypeId.DARKTEMPLAR),
                        EnemyUnitExistsAfter(UnitTypeId.BANSHEE),
                    ]
                ),
                None,
            ),
            Step(None, GridBuilding(UnitTypeId.ENGINEERINGBAY, 1)),
            Step(None, DefensiveBuilding(UnitTypeId.MISSILETURRET, DefensePosition.Entrance, 2)),
            Step(None, DefensiveBuilding(UnitTypeId.MISSILETURRET, DefensePosition.CenterMineralLine, None)),
        ]
        dt_counter2 = [
            Step(
                Any(
                    [
                        EnemyBuildingExists(UnitTypeId.DARKSHRINE),
                        EnemyUnitExistsAfter(UnitTypeId.DARKTEMPLAR),
                        EnemyUnitExistsAfter(UnitTypeId.BANSHEE),
                    ]
                ),
                None,
            ),
            Step(None, GridBuilding(UnitTypeId.STARPORT, 2)),
            Step(None, BuildAddon(UnitTypeId.STARPORTTECHLAB, UnitTypeId.STARPORT, 1)),
            Step(UnitReady(UnitTypeId.STARPORT, 1), ActUnit(UnitTypeId.RAVEN, UnitTypeId.STARPORT, 2)),
        ]

        opener = [
            Step(Supply(13), GridBuilding(UnitTypeId.SUPPLYDEPOT, 1, priority=True)),
            GridBuilding(UnitTypeId.BARRACKS, 1, priority=True),
            StepBuildGas(1, Supply(15)),
            TerranUnit(UnitTypeId.REAPER, 1, only_once=True, priority=True),
            Step(
                None,
                Expand(2),
                skip_until=Any(
                    [
                        RequireCustom(lambda k: not self.rush_detected),
                        UnitExists(UnitTypeId.SIEGETANK, 2, include_killed=True),
                    ]
                ),
            ),
            Step(
                None,
                CancelBuilding(UnitTypeId.COMMANDCENTER, 1),
                skip=Any(
                    [
                        RequireCustom(lambda k: not self.rush_detected),
                        UnitExists(UnitTypeId.SIEGETANK, 2, include_killed=True),
                    ]
                ),
            ),
            Step(None, self.rush_bunker, skip_until=lambda k: self.rush_detected),
            Step(None, GridBuilding(UnitTypeId.BARRACKS, 2), skip_until=lambda k: self.rush_detected),
            GridBuilding(UnitTypeId.SUPPLYDEPOT, 2, priority=True),
            BuildAddon(UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKS, 1),
            GridBuilding(UnitTypeId.FACTORY, 1),
            BuildAddon(UnitTypeId.FACTORYTECHLAB, UnitTypeId.FACTORY, 1),
            AutoDepot(),
        ]

        buildings = [
            Step(None, GridBuilding(UnitTypeId.BARRACKS, 2)),
            Step(UnitReady(UnitTypeId.FACTORYTECHLAB), TerranUnit(UnitTypeId.SIEGETANK, 1)),
            BuildGas(2),
            # BuildStep(None, GridBuilding(UnitTypeId.ARMORY, 1)),
            Step(None, BuildAddon(UnitTypeId.BARRACKSTECHLAB, UnitTypeId.BARRACKS, 1)),
            Step(None, GridBuilding(UnitTypeId.STARPORT, 1)),
            Step(None, GridBuilding(UnitTypeId.BARRACKS, 3)),
            Step(None, BuildAddon(UnitTypeId.BARRACKSTECHLAB, UnitTypeId.BARRACKS, 2)),
            Step(Supply(40, SupplyType.Workers), Expand(3)),
            Step(None, GridBuilding(UnitTypeId.BARRACKS, 5)),
            Step(None, BuildAddon(UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKS, 3)),
            Step(None, BuildAddon(UnitTypeId.STARPORTREACTOR, UnitTypeId.STARPORT, 1)),
            BuildGas(4),
        ]

        tech = [
            Step(None, Tech(UpgradeId.PUNISHERGRENADES)),
            Step(None, Tech(UpgradeId.STIMPACK)),
            Step(None, Tech(UpgradeId.SHIELDWALL)),
        ]

        mech = [TerranUnit(UnitTypeId.SIEGETANK, 2, priority=True)]

        air = [
            Step(UnitReady(UnitTypeId.STARPORT, 1), TerranUnit(UnitTypeId.MEDIVAC, 2, priority=True)),
            Step(None, TerranUnit(UnitTypeId.VIKINGFIGHTER, 1, priority=True)),
            Step(
                None,
                TerranUnit(UnitTypeId.VIKINGFIGHTER, 3, priority=True),
                skip_until=self.RequireAnyEnemyUnits(viking_counters, 1),
            ),
            Step(UnitReady(UnitTypeId.STARPORT, 1), TerranUnit(UnitTypeId.MEDIVAC, 4, priority=True)),
            Step(
                None,
                TerranUnit(UnitTypeId.VIKINGFIGHTER, 10, priority=True),
                skip_until=self.RequireAnyEnemyUnits(viking_counters, 4),
            ),
            Step(UnitReady(UnitTypeId.STARPORT, 1), TerranUnit(UnitTypeId.MEDIVAC, 6, priority=True)),
        ]

        marines = [
            Step(UnitExists(UnitTypeId.REAPER, 1, include_killed=True), TerranUnit(UnitTypeId.MARINE, 2)),
            BuildOrder(
                [
                    TerranUnit(UnitTypeId.MARAUDER, 20, priority=True),
                    TerranUnit(UnitTypeId.MARINE, 20),
                    Step(Minerals(250), TerranUnit(UnitTypeId.MARINE, 100)),
                ]
            ),
        ]

        use_money = BuildOrder(
            [
                Step(Minerals(400), GridBuilding(UnitTypeId.BARRACKS, 8)),
                Step(Minerals(500), BuildAddon(UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKS, 6)),
            ]
        )

        super().__init__([warn, scv, opener, buildings, dt_counter, dt_counter2, tech, mech, air, marines, use_money])

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)
        self.zone_manager = knowledge.get_required_manager(IZoneManager)
        self.build_detector = knowledge.get_required_manager(BuildDetector)
        self.rush_bunker.position = self.zone_manager.expansion_zones[0].ramp.ramp.barracks_in_middle

    @property
    def rush_detected(self) -> bool:
        return self.build_detector.rush_detected

    async def execute(self) -> bool:
        if not self.worker_rushed and self.ai.time < 120:
            self.worker_rushed = self.cache.enemy_workers.filter(
                lambda u: u.distance_to(self.ai.start_location) < u.distance_to(self.zone_manager.enemy_start_location)
            )

        return await super().execute()


class Bio(Strat):

    def configure_managers(self) -> Optional[List["ManagerBase"]]:
        return [BuildDetector(), ChatManager()]

    async def create_plan(self) -> BuildOrder:
        worker_scout = Step(None, WorkerScout(), skip_until=UnitExists(UnitTypeId.SUPPLYDEPOT, 1))
        tactics = [
            MineOpenBlockedBase(),
            PlanCancelBuilding(),
            LowerDepots(),
            PlanZoneDefense(),
            worker_scout,
            Step(None, CallMule(50), skip=Time(5 * 60)),
            Step(None, CallMule(100), skip_until=Time(5 * 60)),
            Step(None, ScanEnemy(), skip_until=Time(5 * 60)),
            DistributeWorkers(),
            Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
            ManTheBunkers(),
            Repair(),
            ContinueBuilding(),
            PlanZoneGatherTerran(),
            PlanZoneAttack(26),
            PlanFinishEnemy(),
        ]

        return BuildOrder([BuildBio(), tactics])
