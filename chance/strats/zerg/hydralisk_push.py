import random

from chance.strats.strat import Strat
from sc2.constants import *


class HydraliskPush(Strat):
    """
    Adapted from https://github.com/BurnySc2/python-sc2/blob/develop/examples/zerg/hydralisk_push.py
    """
    def select_target(self):
        if self._bot.enemy_structures.exists:
            return random.choice(self._bot.enemy_structures).position

        return self._bot.enemy_start_locations[0]

    async def on_step(self):
        larvae = self._bot.units(UnitTypeId.LARVA)
        forces = self._bot.units(UnitTypeId.ZERGLING) | self._bot.units(UnitTypeId.HYDRALISK)

        if self._bot.units(UnitTypeId.HYDRALISK).amount > 10 and self._bot.iteration % 50 == 0:
            for unit in forces.idle:
                self._bot.do(unit.attack(self.select_target()))

        if self._bot.supply_left < 2:
            if self._bot.can_afford(UnitTypeId.OVERLORD) and larvae.exists:
                self._bot.do(larvae.random.train(UnitTypeId.OVERLORD))
                return

        if self._bot.structures(UnitTypeId.HYDRALISKDEN).ready.exists:
            if self._bot.can_afford(UnitTypeId.HYDRALISK) and larvae.exists:
                self._bot.do(larvae.random.train(UnitTypeId.HYDRALISK))
                return

        if not self._bot.townhalls.exists:
            for unit in self._bot.units(UnitTypeId.DRONE) | self._bot.units(QUEEN) | forces:
                self._bot.do(unit.attack(self._bot.enemy_start_locations[0]))
            return
        else:
            hq = self._bot.townhalls.first

        for queen in self._bot.units(UnitTypeId.QUEEN).idle:
            abilities = await self._bot.get_available_abilities(queen)
            if AbilityId.EFFECT_INJECTLARVA in abilities:
                self._bot.do(queen(AbilityId.EFFECT_INJECTLARVA, hq))

        if not (
            self._bot.structures(UnitTypeId.SPAWNINGPOOL).exists or self._bot.already_pending(UnitTypeId.SPAWNINGPOOL)):
            if self._bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self._bot.build(UnitTypeId.SPAWNINGPOOL, near=hq)

        if self._bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if not self._bot.townhalls(UnitTypeId.LAIR).exists and hq.is_idle:
                if self._bot.can_afford(UnitTypeId.LAIR):
                    self._bot.do(hq.build(UnitTypeId.LAIR))

        if self._bot.townhalls(UnitTypeId.LAIR).ready.exists:
            if not (self._bot.structures(UnitTypeId.HYDRALISKDEN).exists or self._bot.already_pending(
                UnitTypeId.HYDRALISKDEN)):
                if self._bot.can_afford(UnitTypeId.HYDRALISKDEN):
                    await self._bot.build(UnitTypeId.HYDRALISKDEN, near=hq)

        if self._bot.gas_buildings.amount < 2 and not self._bot.already_pending(UnitTypeId.EXTRACTOR):
            if self._bot.can_afford(UnitTypeId.EXTRACTOR):
                drone = self._bot.workers.random
                target = self._bot.vespene_geyser.closest_to(drone.position)
                err = self._bot.do(drone.build(UnitTypeId.EXTRACTOR, target))

        if hq.assigned_harvesters < hq.ideal_harvesters:
            if self._bot.can_afford(UnitTypeId.DRONE) and larvae.exists:
                larva = larvae.random
                self._bot.do(larva.train(UnitTypeId.DRONE))
                return

        for a in self._bot.gas_buildings:
            if a.assigned_harvesters < a.ideal_harvesters:
                w = self._bot.workers.closer_than(20, a)
                if w.exists:
                    self._bot.do(w.random.gather(a))

        if self._bot.structures(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if not self._bot.units(UnitTypeId.QUEEN).exists and hq.is_ready and hq.is_idle:
                if self._bot.can_afford(UnitTypeId.QUEEN):
                    self._bot.do(hq.train(UnitTypeId.QUEEN))

        if self._bot.units(UnitTypeId.ZERGLING).amount < 20 and self._bot.minerals > 1000:
            if larvae.exists and self._bot.can_afford(UnitTypeId.ZERGLING):
                self._bot.do(larvae.random.train(UnitTypeId.ZERGLING))
