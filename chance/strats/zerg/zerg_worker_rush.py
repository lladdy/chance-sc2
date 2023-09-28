from typing import List

from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.combat import MoveType
from sharpy.interfaces import ICombatManager, IZoneManager, ILostUnitsManager
from sharpy.knowledges import Knowledge
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *
from sharpy.plans.tactics.zerg import *


class DummyZergAttack(ActBase):
    combat: ICombatManager

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)
        self.all_out_started = False
        self.unit_values = knowledge.unit_values
        self.combat: ICombatManager = self.knowledge.get_required_manager(ICombatManager)
        self.zone_manager: IZoneManager = self.knowledge.get_required_manager(IZoneManager)

    async def execute(self) -> bool:
        target = self.zone_manager.enemy_start_location
        defend = False
        for zone in self.zone_manager.expansion_zones:
            if zone.is_ours and zone.is_under_attack:
                ground_units = zone.known_enemy_units.not_flying
                if zone.known_enemy_power.ground_presence > 0 and ground_units:
                    defend = True
                    for zl in self.ai.units.of_type(
                        [UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.QUEEN, UnitTypeId.MUTALISK]
                    ):
                        target = ground_units.closest_to(zone.center_location).position
                        self.combat.add_unit(zl)
                elif zone.known_enemy_units:
                    for zl in self.cache.own(UnitTypeId.QUEEN):
                        target = zone.known_enemy_units.closest_to(zone.center_location).position
                        self.combat.add_unit(zl)
                break  # defend the most important zone first

        if not defend:
            target = await self.select_attack_target()

            if self.all_out_started and len(self.cache.own(UnitTypeId.ZERGLING)) == 0:
                await self.ai.chat_send("attack end!")
                self.all_out_started = False

            if self.ai.time < 9 * 60:
                limit = 6
            elif self.ai.time < 13 * 60:
                limit = 12
            elif self.ai.time < 17 * 60:
                limit = 20
            else:
                limit = 25

            if not self.all_out_started and len(self.cache.own(UnitTypeId.ZERGLING).idle) >= limit:
                await self.ai.chat_send("attack start!")
                self.all_out_started = True

            if self.all_out_started:
                for zl in self.ai.units.of_type([UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.MUTALISK]):
                    self.combat.add_unit(zl)

        self.combat.execute(target, MoveType.Assault)
        return True

    async def select_attack_target(self):
        if self.ai.enemy_structures.exists:
            target = self.ai.enemy_structures.closest_to(self.ai.start_location).position
        else:
            target = self.ai.enemy_start_locations[0]

            last_scout = 0
            for zone in self.zone_manager.enemy_expansion_zones:
                if zone.is_enemys:
                    target = zone.center_location
                    break
                if last_scout > zone.last_scouted_center:
                    target = zone.center_location
                    last_scout = zone.last_scouted_center
                    if last_scout + 2 * 60 < self.ai.time:
                        break
        return target


class LingFloodBuild(BuildOrder):
    def __init__(self):
        gas_related = [
            StepBuildGas(1, UnitExists(UnitTypeId.HATCHERY, 2)),
            Step(None, Tech(UpgradeId.ZERGLINGMOVEMENTSPEED), skip_until=Gas(100)),
        ]
        buildings = [
            # 12 Pool
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL, 1)),
            Step(UnitExists(UnitTypeId.ZERGLING, 4, include_killed=True), Expand(2)),
            Step(None, ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 2)),
            Step(UnitExists(UnitTypeId.DRONE, 24, include_killed=True), Expand(3)),
            Step(None, ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 3)),
            Step(UnitExists(UnitTypeId.DRONE, 30, include_killed=True), Expand(4)),
            Step(None, ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 4)),
        ]

        spire_end_game = [
            Step(Any([Supply(70), UnitExists(UnitTypeId.LAIR, 1)]), None),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 35),
            MorphLair(),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 40),
            StepBuildGas(3, None),
            ActBuilding(UnitTypeId.SPIRE, 1),
            ActUnit(UnitTypeId.MUTALISK, UnitTypeId.LARVA, 10, priority=True),
        ]

        units = [
            Step(None, None, UnitExists(UnitTypeId.HATCHERY, 1)),
            # 12 Pool followed by overlord
            Step(
                UnitExists(UnitTypeId.SPAWNINGPOOL, 1),
                ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
                UnitExists(UnitTypeId.OVERLORD, 2),
            ),
            # TheMusZero
            Step(
                UnitExists(UnitTypeId.SPAWNINGPOOL, 1),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                UnitExists(UnitTypeId.DRONE, 14),
            ),
            # Early zerglings
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 4), None),
            # Queen for more larvae
            Step(
                UnitExists(UnitTypeId.SPAWNINGPOOL, 1),
                ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 1),
                UnitExists(UnitTypeId.QUEEN, 1),
            ),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 20), None),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), ActUnitOnce(UnitTypeId.ZERGLING, UnitTypeId.LARVA, 12),
                 None, ),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 30), None),
            # Endless zerglings
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA), None),
        ]

        super().__init__([self.overlords, buildings, spire_end_game, gas_related, units])


class WorkerAttack(ActBase):
    combat: ICombatManager
    zone_manager: IZoneManager
    lost_units_manager: ILostUnitsManager

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)
        self.all_out_started = False
        self.unit_values = knowledge.unit_values
        self.combat = self.knowledge.get_required_manager(ICombatManager)
        self.zone_manager = self.knowledge.get_required_manager(IZoneManager)
        self.lost_units_manager = self.knowledge.get_required_manager(ILostUnitsManager)
        self.tags: List[int] = []

    async def execute(self) -> bool:
        if self.knowledge.iteration == 0:
            for worker in self.ai.workers:
                self.tags.append(worker.tag)

        if len(self.tags) == 0:
            return True

        attack_zone = self.zone_manager.enemy_main_zone
        enemy_natural = self.zone_manager.expansion_zones[-2]

        target = self.zone_manager.enemy_start_location
        fighters = self.ai.workers.tags_in(self.tags)
        self.tags.clear()
        move_type = MoveType.Assault
        if self.lost_units_manager.calculate_enemy_lost_resources()[0] < 50:
            target = attack_zone.behind_mineral_position_center
            move_type = MoveType.PanicRetreat
        else:
            target = self.ai.structures.closest_to(attack_zone.behind_mineral_position_center)
            move_type = MoveType.Assault

        for fighter in fighters:  # type: Unit
            self.tags.append(fighter.tag)
            if fighter.health > 5 and fighter.distance_to(attack_zone.center_location) > 20:
                fighter.move(attack_zone.center_location)
            elif fighter.health < 6 and enemy_natural.mineral_fields.exists:
                mf = enemy_natural.mineral_fields.closest_to(fighter)
                fighter.gather(mf)
            else:
                if attack_zone.known_enemy_units.not_structure.closer_than(4, fighter).exists:
                    target = attack_zone.known_enemy_units.not_structure.closest_to(fighter).position
                    move_type = MoveType.Assault
                self.combat.add_unit(fighter)

        self.combat.execute(target, move_type)
        return True

    async def select_attack_target(self):
        if self.ai.enemy_structures.exists:
            target = self.ai.enemy_structures.closest_to(self.ai.start_location).position
        else:
            target = self.ai.enemy_start_locations[0]

            last_scout = 0
            for zone in self.zone_manager.enemy_expansion_zones:
                if zone.is_enemys:
                    target = zone.center_location
                    break
                if last_scout > zone.last_scouted_center:
                    target = zone.center_location
                    last_scout = zone.last_scouted_center
                    if last_scout + 2 * 60 < self.ai.time:
                        break
        return target


class ZergWorkerRush(Strat):
    """Zerg super worker rush"""

    async def create_plan(self) -> BuildOrder:
        stop_gas = Any([Gas(100), TechReady(UpgradeId.ZERGLINGMOVEMENTSPEED, 0.001)])
        end_game = Any([Supply(70), UnitExists(UnitTypeId.LAIR, 1)])

        return BuildOrder(
            ActUnitOnce(UnitTypeId.DRONE, UnitTypeId.LARVA, 24),
            LingFloodBuild(),
            SequentialList(
                MineOpenBlockedBase(),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                InjectLarva(),
                Step(None, DistributeWorkers(3, 3), skip=Any([stop_gas, end_game])),
                Step(None, DistributeWorkers(0, 0), skip_until=stop_gas, skip=end_game),
                Step(None, DistributeWorkers(None, None), skip_until=end_game),
                WorkerAttack(),
                DummyZergAttack(),
            ),
        )
