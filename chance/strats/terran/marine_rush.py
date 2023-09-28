# import sc2
import random

from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sharpy.combat import MoveType
from sharpy.plans import BuildOrder, Step, SequentialList
from sharpy.plans.acts import *
from sharpy.plans.acts.terran import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *
from sharpy.plans.tactics.terran import *
from sharpy.utils import select_build_index


class DodgeRampAttack(PlanZoneAttack):
    async def execute(self) -> bool:
        base_ramp = self.zone_manager.expansion_zones[-1].ramp
        for effect in self.ai.state.effects:
            if effect.id != "FORCEFIELD":
                continue
            pos: Point2 = base_ramp.bottom_center
            for epos in effect.positions:
                if pos.distance_to_point2(epos) < 5:
                    return await self.small_retreat()

        return await super().execute()

    async def small_retreat(self):
        attacking_units = self.roles.attacking_units
        natural = self.zone_manager.expansion_zones[-2]

        for unit in attacking_units:
            self.combat.add_unit(unit)

        self.combat.execute(natural.gather_point, MoveType.DefensiveRetreat)
        return False


class MarineRush(Strat):
    tactic_index: int

    build_name = "default"

    async def pre_step_execute(self):
        if self.tactic_index != 1 and self._bot.time < 5 * 60:
            self._bot.knowledge.gather_point = self._bot.zone_manager.expansion_zones[-2].gather_point

    async def create_plan(self) -> BuildOrder:
        if self.build_name == "default":
            self.tactic_index = select_build_index(self._bot.knowledge, "build.marine", 0, 2)
        else:
            self.tactic_index = int(self.build_name)

        if self.tactic_index == 0:
            self._bot.knowledge.print("Proxy 2 rax bunker rush", "Build")
            self.attack = DodgeRampAttack(3)
            zone = self._bot.zone_manager.expansion_zones[-random.randint(3, 5)]
            natural = self._bot.zone_manager.expansion_zones[-2]
            chunk = [
                Step(Supply(12), GridBuilding(UnitTypeId.SUPPLYDEPOT, 1)),
                BuildPosition(UnitTypeId.BARRACKS, zone.center_location, exact=False, only_once=True),
                BuildPosition(
                    UnitTypeId.BARRACKS,
                    zone.center_location.towards(self._bot.zone_manager.enemy_expansion_zones[0].ramp.bottom_center, 5),
                    exact=False,
                    only_once=True,
                ),
                BuildPosition(
                    UnitTypeId.BARRACKS,
                    zone.center_location.towards(self._bot.game_info.map_center, 5),
                    exact=False,
                    only_once=True,
                ),
                Step(None, GridBuilding(UnitTypeId.SUPPLYDEPOT, 2)),
                Step(
                    UnitReady(UnitTypeId.MARINE, 1),
                    BuildPosition(
                        UnitTypeId.BUNKER,
                        natural.center_location.towards(self._bot.game_info.map_center, 4),
                        exact=False,
                        only_once=True,
                    ),
                ),
                Step(Minerals(225), GridBuilding(UnitTypeId.BARRACKS, 6)),
            ]
        elif self.tactic_index == 1:
            self._bot.knowledge.print("20 marine all in", "Build")
            self.attack = DodgeRampAttack(20)
            chunk = [
                Step(Supply(14), GridBuilding(UnitTypeId.SUPPLYDEPOT, 1)),
                Step(UnitReady(UnitTypeId.SUPPLYDEPOT, 1), GridBuilding(UnitTypeId.BARRACKS, 1)),
                Step(None, GridBuilding(UnitTypeId.SUPPLYDEPOT, 2)),
                GridBuilding(UnitTypeId.BARRACKS, 6),
            ]
        else:
            self._bot.knowledge.print("10 marine proxy rax", "Build")
            self.attack = DodgeRampAttack(10)
            zone = self._bot.zone_manager.expansion_zones[-random.randint(3, 5)]
            chunk = [
                Step(Supply(14), GridBuilding(UnitTypeId.SUPPLYDEPOT, 1)),
                Step(UnitReady(UnitTypeId.SUPPLYDEPOT, 1), GridBuilding(UnitTypeId.BARRACKS, 1)),
                Step(None, GridBuilding(UnitTypeId.SUPPLYDEPOT, 2)),
                BuildPosition(UnitTypeId.BARRACKS, zone.center_location, exact=False, only_once=True),
                BuildPosition(
                    UnitTypeId.BARRACKS,
                    zone.center_location.towards(self._bot.zone_manager.expansion_zones[-1].ramp.bottom_center, 5),
                    exact=False,
                    only_once=True,
                ),
                Step(Minerals(225), GridBuilding(UnitTypeId.BARRACKS, 6)),
            ]

        empty = BuildOrder([])

        worker_scout = Step(None, WorkerScout(), skip_until=UnitExists(UnitTypeId.SUPPLYDEPOT, 1))
        self.distribute_workers = DistributeWorkers()

        tactics = [
            MineOpenBlockedBase(),
            PlanCancelBuilding(),
            LowerDepots(),
            PlanZoneDefense(),
            worker_scout,
            Step(None, CallMule(50), skip=Time(5 * 60)),
            Step(None, CallMule(100), skip_until=Time(5 * 60)),
            Step(None, ScanEnemy(), skip_until=Time(5 * 60)),
            self.distribute_workers,
            Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
            ManTheBunkers(),
            Repair(),
            ContinueBuilding(),
            PlanZoneGatherTerran(),
            Step(None, self.attack),
            PlanFinishEnemy(),
        ]

        return BuildOrder(
            empty.depots,
            Step(None, MorphOrbitals(), skip_until=UnitReady(UnitTypeId.BARRACKS, 1)),
            [Step(None, ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 20))],
            chunk,
            ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 200),
            SequentialList(tactics),
        )
