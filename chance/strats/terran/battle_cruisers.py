import random

from chance.strats import Strat
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.terran import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *
from sharpy.plans.tactics.terran import *
from sharpy.utils import select_build_index


class JumpIn(ActBase):
    def __init__(self):
        self.done = False
        super().__init__()

    async def execute(self) -> bool:
        if self.done:
            return True
        bcs = self.cache.own(UnitTypeId.BATTLECRUISER)
        if bcs.amount > 1:
            self.done = True
            for bc in bcs:
                self.knowledge.cooldown_manager.used_ability(bc.tag, AbilityId.EFFECT_TACTICALJUMP)

                bc(AbilityId.EFFECT_TACTICALJUMP, self.zone_manager.enemy_main_zone.behind_mineral_position_center)

        return True


class BattleCruisers(Strat):
    jump: int

    async def create_plan(self) -> BuildOrder:
        self.build_name = "default"

        attack_value = random.randint(50, 80)
        self.attack = Step(None, PlanZoneAttack(attack_value))
        empty = BuildOrder([])

        if self.build_name == "default":
            self.jump = select_build_index(self._bot.knowledge, "build.bc", 0, 1)
        else:
            self.jump = int(self.build_name)

        if self.jump == 0:
            self._bot.knowledge.print(f"Att at {attack_value}", "Build")
        else:
            self._bot.knowledge.print(f"Jump, att at {attack_value}", "Build")

        worker_scout = Step(None, WorkerScout(), skip_until=UnitExists(UnitTypeId.SUPPLYDEPOT, 1))
        self.distribute_workers = DistributeWorkers(4)
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
            Step(None, JumpIn(), RequireCustom(lambda k: self.jump == 0)),
            self.attack,
            PlanFinishEnemy(),
        ]

        return BuildOrder(
            empty.depots,
            Step(None, MorphOrbitals(), skip_until=UnitReady(UnitTypeId.BARRACKS, 1)),
            [Step(None, ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 34 + 12))],
            [
                Step(Supply(13), GridBuilding(UnitTypeId.SUPPLYDEPOT, 1)),
                Step(UnitReady(UnitTypeId.SUPPLYDEPOT, 0.95), GridBuilding(UnitTypeId.BARRACKS, 1)),
                BuildGas(1),
                Expand(2),
                Step(Supply(20), GridBuilding(UnitTypeId.SUPPLYDEPOT, 2)),
                BuildGas(2),
                Step(None, GridBuilding(UnitTypeId.FACTORY, 1), skip_until=UnitReady(UnitTypeId.BARRACKS, 1)),
                Step(UnitReady(UnitTypeId.FACTORY, 1), GridBuilding(UnitTypeId.STARPORT, 1)),
                DefensiveBuilding(UnitTypeId.BUNKER, DefensePosition.Entrance, 1),
                Step(None, GridBuilding(UnitTypeId.BARRACKS, 2)),
                BuildGas(3),
                Step(None, BuildAddon(UnitTypeId.FACTORYTECHLAB, UnitTypeId.FACTORY, 1)),
                Step(UnitReady(UnitTypeId.STARPORT, 1), GridBuilding(UnitTypeId.FUSIONCORE, 1)),
                Step(None, BuildAddon(UnitTypeId.STARPORTTECHLAB, UnitTypeId.STARPORT, 1)),
                StepBuildGas(
                    4, None, UnitExists(UnitTypeId.BATTLECRUISER, 1, include_killed=True, include_pending=True)
                ),
                Step(
                    UnitExists(UnitTypeId.BATTLECRUISER, 1, include_killed=True), GridBuilding(UnitTypeId.BARRACKS, 3),
                ),
                Step(None, BuildAddon(UnitTypeId.BARRACKSTECHLAB, UnitTypeId.BARRACKS, 1)),
                Step(None, BuildAddon(UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKS, 1)),
                Step(None, GridBuilding(UnitTypeId.STARPORT, 2)),
                Step(
                    UnitReady(UnitTypeId.STARPORT, 2), BuildAddon(UnitTypeId.STARPORTTECHLAB, UnitTypeId.STARPORT, 2),
                ),
                Step(None, Tech(UpgradeId.SHIELDWALL)),
                Step(Minerals(600), GridBuilding(UnitTypeId.BARRACKS, 5)),
                Expand(3),
            ],
            [
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
                Step(
                    UnitReady(UnitTypeId.STARPORT, 1), ActUnit(UnitTypeId.RAVEN, UnitTypeId.STARPORT, 2, priority=True),
                ),
            ],
            Step(
                None,
                SequentialList(ActUnit(UnitTypeId.BATTLECRUISER, UnitTypeId.STARPORT, 20, priority=True)),
                skip_until=UnitReady(UnitTypeId.FUSIONCORE, 1),
            ),
            ActUnit(UnitTypeId.SIEGETANK, UnitTypeId.FACTORY, 10),
            ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 50),
            SequentialList(tactics),
        )
