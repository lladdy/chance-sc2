import sc2
from chance.strats.strat import Strat

from sc2.constants import *
from sc2.helpers import ControlGroup


class ProxyRax(Strat):
    def __init__(self, _bot: sc2.BotAI):
        super().__init__(_bot)
        self.attack_groups = set()

    async def on_step(self):
        cc = self._bot.townhalls(UnitTypeId.COMMANDCENTER)
        if not cc.exists:
            target = self._bot.enemy_structures.random_or(self._bot.enemy_start_locations[0]).position
            for unit in self._bot.workers | self._bot.units(UnitTypeId.MARINE):
                self._bot.do(unit.attack(target))
            return
        else:
            cc = cc.first

        if self._bot.units(UnitTypeId.MARINE).idle.amount > 15 and self._bot.iteration % 50 == 1:
            cg = ControlGroup(self._bot.units(UnitTypeId.MARINE).idle)
            self.attack_groups.add(cg)

        if self._bot.can_afford(UnitTypeId.SCV) and self._bot.workers.amount < 16 and cc.is_idle:
            self._bot.do(cc.train(UnitTypeId.SCV))

        elif self._bot.supply_left < (2 if self._bot.structures(UnitTypeId.BARRACKS).amount < 3 else 4):
            if self._bot.can_afford(UnitTypeId.SUPPLYDEPOT) and self._bot.already_pending(UnitTypeId.SUPPLYDEPOT) < 2:
                await self._bot.build(UnitTypeId.SUPPLYDEPOT,
                                      near=cc.position.towards(self._bot.game_info.map_center, 5))

        elif self._bot.structures(UnitTypeId.BARRACKS).amount < 3 or (
            self._bot.minerals > 400 and self._bot.structures(UnitTypeId.BARRACKS).amount < 5):
            if self._bot.can_afford(UnitTypeId.BARRACKS):
                p = self._bot.game_info.map_center.towards(self._bot.enemy_start_locations[0], 25)
                await self._bot.build(UnitTypeId.BARRACKS, near=p)

        for rax in self._bot.structures(UnitTypeId.BARRACKS).ready.idle:
            if not self._bot.can_afford(UnitTypeId.MARINE):
                break
            self._bot.do(rax.train(UnitTypeId.MARINE))

        for scv in self._bot.workers.idle:
            self._bot.do(scv.gather(self._bot.mineral_field.closest_to(cc)))

        for ac in list(self.attack_groups):
            alive_units = ac.select_units(self._bot.units)
            if alive_units.exists and alive_units.idle.exists:
                target = self._bot.enemy_structures.random_or(self._bot.enemy_start_locations[0]).position
                for marine in ac.select_units(self._bot.units):
                    self._bot.do(marine.attack(target))
            else:
                self.attack_groups.remove(ac)
