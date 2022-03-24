from typing import Optional, List

from chance.sharpy.set_game_step_size_act import SetGameStepSize
from chance.strats.protoss import MacroStalkers
from chance.strats.strat import Strat
from sharpy.interfaces import ICombatManager, IZoneManager, ILostUnitsManager
from sharpy.interfaces.combat_manager import MoveType
from sharpy.knowledges import KnowledgeBot, Knowledge
from sharpy.plans import BuildOrder, Step, SequentialList
from sharpy.plans.acts import ActBase
from sharpy.plans.require import RequireCustom


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
            if fighter.shield > 5 and fighter.distance_to(attack_zone.center_location) > 20:
                fighter.move(attack_zone.center_location)
            elif fighter.shield < 6 and enemy_natural.mineral_fields.exists:
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


class ProtossWorkerRush(Strat):
    async def on_start(self, bot: KnowledgeBot):
        await super().on_start(bot)
        self.cleanup = MacroStalkers()
        await self.cleanup.on_start(bot)

    def configure_managers(self) -> Optional[List["ManagerBase"]]:
        return self.cleanup.configure_managers()

    async def create_plan(self) -> BuildOrder:
        perform_cleanup = RequireCustom(lambda
                                            k: self._bot.zone_manager.enemy_main_zone.is_scouted_at_least_once and not self._bot.zone_manager.enemy_main_zone.is_enemys)
        return BuildOrder([
            Step(None, SequentialList(
                SetGameStepSize(1),  # improve our worker micro
                WorkerAttack()
            ), skip=perform_cleanup),
            Step(None, SequentialList(
                SetGameStepSize(self._bot.client.game_step),  # back to the original step size
                await self.cleanup.create_plan()
            ), skip=perform_cleanup),
        ])
