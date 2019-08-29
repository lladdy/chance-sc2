import sc2
from chance.strats.strat import Strat
from sc2.constants import *


class WarpGatePush(Strat):
    def __init__(self, _bot: sc2.BotAI):
        # Initialize inherited class
        super().__init__(_bot)
        self.proxy_built = False

    async def warp_new_units(self, proxy):
        for warpgate in self._bot.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self._bot.get_available_abilities(warpgate)
            # all the units have the same cooldown anyway so let's just look at ZEALOT
            if AbilityId.WARPGATETRAIN_STALKER in abilities:
                pos = proxy.position.to2.random_on_distance(4)
                placement = await self._bot.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    # return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                self._bot.do(warpgate.warp_in(UnitTypeId.STALKER, placement), subtract_cost=True, subtract_supply=True)

    async def on_step(self):
        await self._bot.distribute_workers()

        if not self._bot.townhalls.ready:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self._bot.workers:
                self._bot.do(worker.attack(self._bot.enemy_start_locations[0]))
            return
        else:
            nexus = self._bot.townhalls.ready.random

        # Build pylon when on low supply
        if self._bot.supply_left < 2 and self._bot.already_pending(UnitTypeId.PYLON) == 0:
            # Always check if you can afford something before you build it
            if self._bot.can_afford(UnitTypeId.PYLON):
                await self._bot.build(UnitTypeId.PYLON, near=nexus)
            return

        if self._bot.workers.amount < self._bot.townhalls.amount * 22 and nexus.is_idle:
            if self._bot.can_afford(UnitTypeId.PROBE):
                self._bot.do(nexus.train(UnitTypeId.PROBE), subtract_cost=True, subtract_supply=True)

        elif self._bot.structures(UnitTypeId.PYLON).amount < 5 and self._bot.already_pending(UnitTypeId.PYLON) == 0:
            if self._bot.can_afford(UnitTypeId.PYLON):
                await self._bot.build(UnitTypeId.PYLON, near=nexus.position.towards(self._bot.game_info.map_center, 5))

        if self._bot.structures(UnitTypeId.PYLON).ready:
            proxy = self._bot.structures(UnitTypeId.PYLON).closest_to(self._bot.enemy_start_locations[0])
            pylon = self._bot.structures(UnitTypeId.PYLON).ready.random
            if self._bot.structures(UnitTypeId.GATEWAY).ready:
                # If we have no cyber core, build one
                if not self._bot.structures(UnitTypeId.CYBERNETICSCORE):
                    if self._bot.can_afford(UnitTypeId.CYBERNETICSCORE) and self._bot.already_pending(
                        UnitTypeId.CYBERNETICSCORE) == 0:
                        await self._bot.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            # Build up to 4 gates
            if self._bot.can_afford(UnitTypeId.GATEWAY) and self._bot.structures(
                UnitTypeId.WARPGATE).amount + self._bot.structures(UnitTypeId.GATEWAY).amount < 4:
                await self._bot.build(UnitTypeId.GATEWAY, near=pylon)

        # Build gas
        for nexus in self._bot.townhalls.ready:
            vgs = self._bot.vespene_geyser.closer_than(15, nexus)
            for vg in vgs:
                if not self._bot.can_afford(UnitTypeId.ASSIMILATOR):
                    break
                worker = self._bot.select_build_worker(vg.position)
                if worker is None:
                    break
                if not self._bot.gas_buildings or not self._bot.gas_buildings.closer_than(1, vg):
                    self._bot.do(worker.build(UnitTypeId.ASSIMILATOR, vg), subtract_cost=True)
                    self._bot.do(worker.stop(queue=True))

        # Research warp gate if cybercore is completed
        if (
            self._bot.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self._bot.can_afford(AbilityId.RESEARCH_WARPGATE)
            and self._bot.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
        ):
            ccore = self._bot.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            self._bot.do(ccore(AbilityId.RESEARCH_WARPGATE), subtract_cost=True)

        # Morph to warp gate when research is complete
        for gateway in self._bot.structures(UnitTypeId.GATEWAY).ready.idle:
            if self._bot.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 1:
                self._bot.do(gateway(AbilityId.MORPH_WARPGATE))

        if self.proxy_built:
            await self.warp_new_units(proxy)

        # Make stalkers attack either closest enemy unit or enemy spawn location
        if self._bot.units(UnitTypeId.STALKER).amount > 3:
            for stalker in self._bot.units(UnitTypeId.STALKER).ready.idle:
                targets = (self._bot.enemy_units | self._bot.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(stalker)
                    self._bot.do(stalker.attack(target))
                else:
                    self._bot.do(stalker.attack(self._bot.enemy_start_locations[0]))

        # Build proxy pylon
        if self._bot.structures(
            UnitTypeId.CYBERNETICSCORE).amount >= 1 and not self.proxy_built and self._bot.can_afford(UnitTypeId.PYLON):
            p = self._bot.game_info.map_center.towards(self._bot.enemy_start_locations[0], 20)
            await self._bot.build(UnitTypeId.PYLON, near=p)
            self.proxy_built = True

        # Chrono nexus if cybercore is not ready, else chrono cybercore
        if not self._bot.structures(UnitTypeId.CYBERNETICSCORE).ready:
            if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and not nexus.is_idle:
                if nexus.energy >= 50:
                    self._bot.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
        else:
            ccore = self._bot.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and not ccore.is_idle:
                if nexus.energy >= 50:
                    self._bot.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))
