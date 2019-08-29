import os
import sys

from chance.strats.strat import Strat

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from sc2.constants import *
from sc2.unit import Unit
from sc2.units import Units


class ZergRush(Strat):

    def __init__(self, _bot):
        super().__init__(_bot)

    async def on_start(self):
        self._bot._client.game_step = 2

    async def on_step(self):

        await self._bot.distribute_workers()

        # If townhall no longer exists: attack move with all units to enemy start location
        if not self._bot.townhalls:
            for unit in self._bot.units.exclude_type({UnitTypeId.EGG, UnitTypeId.LARVA}):
                self._bot.do(unit.attack(self._bot.enemy_start_locations[0]))
            return

        hatch: Unit = self._bot.townhalls[0]

        # Pick a target location
        # target = self._bot.enemy_structures.not_flying.random_or(self._bot.enemy_start_locations[0]).position
        target = self._bot.enemy_start_locations[0]

        # Give all zerglings an attack command
        for zl in self._bot.units(UnitTypeId.ZERGLING):
            self._bot.do(zl.attack(target))

        # Inject hatchery if queen has more than 25 energy
        for queen in self._bot.units(UnitTypeId.QUEEN):
            if queen.energy >= 25 and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                self._bot.do(queen(AbilityId.EFFECT_INJECTLARVA, hatch))

        # Pull workers out of gas if we have almost enough gas mined, this will stop mining when we reached 100 gas mined
        if self._bot.vespene >= 88 or self._bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) > 0:
            gas_drones = self._bot.workers.filter(lambda w: w.is_carrying_vespene and len(w.orders) < 2)
            drone: Unit
            for drone in gas_drones:
                minerals: Units = self._bot.mineral_field.closer_than(10, hatch)
                if minerals:
                    mineral = minerals.closest_to(drone)
                    self._bot.do(drone.gather(mineral, queue=True))

        # If we have 100 vespene, this will try to research zergling speed once the spawning pool is at 100% completion
        if self._bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0 and self._bot.can_afford(
            UpgradeId.ZERGLINGMOVEMENTSPEED
        ):
            spawning_pools_ready = self._bot.structures(UnitTypeId.SPAWNINGPOOL).ready
            if spawning_pools_ready:
                self._bot.research(UpgradeId.ZERGLINGMOVEMENTSPEED)

        # If we have less than 2 supply left and no overlord is in the queue: train an overlord
        if self._bot.supply_left < 2 and self._bot.already_pending(UnitTypeId.OVERLORD) < 1:
            self._bot.train(UnitTypeId.OVERLORD, 1)

        # While we have less than 88 vespene mined: send drones into extractor one frame at a time
        if (
            self._bot.gas_buildings.ready
            and self._bot.vespene < 88
            and self._bot.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0
        ):
            extractor: Unit = self._bot.gas_buildings.first
            if extractor.surplus_harvesters < 0:
                self._bot.do(self._bot.workers.random.gather(extractor))

        # If we have lost of minerals, make a macro hatchery
        if self._bot.minerals > 500:
            for d in range(4, 15):
                pos = hatch.position.towards(self._bot.game_info.map_center, d)
                if await self._bot.can_place(UnitTypeId.HATCHERY, pos):
                    self._bot.do(self._bot.workers.random.build(UnitTypeId.HATCHERY, pos), subtract_cost=True)
                    break

        # While we have less than 16 drones, make more drones
        if self._bot.can_afford(UnitTypeId.DRONE) and self._bot.supply_workers < 16:
            self._bot.train(UnitTypeId.DRONE)

        # If our spawningpool is completed, start making zerglings
        if self._bot.structures(UnitTypeId.SPAWNINGPOOL).ready and self._bot.larva and self._bot.can_afford(
            UnitTypeId.ZERGLING):
            amount_trained = self._bot.train(UnitTypeId.ZERGLING, self._bot.larva.amount)

        # If we have no extractor, build extractor
        if self._bot.gas_buildings.amount + self._bot.already_pending(
            UnitTypeId.EXTRACTOR) == 0 and self._bot.can_afford(
            UnitTypeId.EXTRACTOR
        ):
            drone = self._bot.workers.random
            target = self._bot.vespene_geyser.closest_to(drone)
            self._bot.do(drone.build(UnitTypeId.EXTRACTOR, target))

        # If we have no spawning pool, try to build spawning pool
        elif self._bot.structures(UnitTypeId.SPAWNINGPOOL).amount + self._bot.already_pending(
            UnitTypeId.SPAWNINGPOOL) == 0:
            if self._bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                for d in range(4, 15):
                    pos = hatch.position.towards(self._bot.game_info.map_center, d)
                    if await self._bot.can_place(UnitTypeId.SPAWNINGPOOL, pos):
                        drone = self._bot.workers.closest_to(pos)
                        self._bot.do(drone.build(UnitTypeId.SPAWNINGPOOL, pos))

        # If we have no queen, try to build a queen if we have a spawning pool compelted
        elif (
            self._bot.units(UnitTypeId.QUEEN).amount + self._bot.already_pending(UnitTypeId.QUEEN) == 0
            and self._bot.structures(UnitTypeId.SPAWNINGPOOL).ready
        ):
            if self._bot.can_afford(UnitTypeId.QUEEN):
                self._bot.train(UnitTypeId.QUEEN)
