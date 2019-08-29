from chance.strats.strat import Strat
from sc2.constants import *
from sc2.ids.buff_id import BuffId


class ThreebaseVoidray(Strat):
    """
    Adapted from https://github.com/BurnySc2/python-sc2/blob/develop/examples/protoss/threebase_voidray.py
    """
    async def on_step(self):

        if not self._bot.townhalls.ready:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self._bot.workers:
                self._bot.do(worker.attack(self._bot.enemy_start_locations[0]))
            return
        else:
            nexus = self._bot.townhalls.ready.random

        # If this random nexus is not idle and has not chrono buff, chrono it with one of the nexuses we have
        if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            nexuses = self._bot.structures(UnitTypeId.NEXUS)
            abilities = await self._bot.get_available_abilities(nexuses)
            for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                    self._bot.do(loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
                    break

        # If we have at least 5 void rays, attack closes enemy unit/building, or if none is visible: attack move towards enemy spawn
        if self._bot.units(UnitTypeId.VOIDRAY).amount > 5:
            for vr in self._bot.units(UnitTypeId.VOIDRAY):
                # Activate charge ability if the void ray just attacked
                if vr.weapon_cooldown > 0:
                    self._bot.do(vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT))
                # Choose target and attack, filter out invisible targets
                targets = (self._bot.enemy_units | self._bot.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(vr)
                    self._bot.do(vr.attack(target))
                else:
                    self._bot.do(vr.attack(self._bot.enemy_start_locations[0]))

        # Distribute workers in gas and across bases
        await self._bot.distribute_workers()

        # If we are low on supply, build pylon
        if (
            self._bot.supply_left < 2
            and self._bot.already_pending(UnitTypeId.PYLON) == 0
            or self._bot.supply_used > 15
            and self._bot.supply_left < 4
            and self._bot.already_pending(UnitTypeId.PYLON) < 2
        ):
            # Always check if you can afford something before you build it
            if self._bot.can_afford(UnitTypeId.PYLON):
                await self._bot.build(UnitTypeId.PYLON, near=nexus)

        # Train probe on nexuses that are undersaturated (avoiding distribute workers functions)
        # if nexus.assigned_harvesters < nexus.ideal_harvesters and nexus.is_idle:
        if self._bot.supply_workers + self._bot.already_pending(
            UnitTypeId.PROBE) < self._bot.townhalls.amount * 22 and nexus.is_idle:
            if self._bot.can_afford(UnitTypeId.PROBE):
                self._bot.do(nexus.train(UnitTypeId.PROBE), subtract_cost=True, subtract_supply=True)

        # If we have less than 3 nexuses and none pending yet, expand
        if self._bot.townhalls.ready.amount + self._bot.already_pending(UnitTypeId.NEXUS) < 3:
            if self._bot.can_afford(UnitTypeId.NEXUS):
                await self._bot.expand_now()

        # Once we have a pylon completed
        if self._bot.structures(UnitTypeId.PYLON).ready:
            pylon = self._bot.structures(UnitTypeId.PYLON).ready.random
            if self._bot.structures(UnitTypeId.GATEWAY).ready:
                # If we have gateway completed, build cyber core
                if not self._bot.structures(UnitTypeId.CYBERNETICSCORE):
                    if self._bot.can_afford(UnitTypeId.CYBERNETICSCORE) and self._bot.already_pending(
                        UnitTypeId.CYBERNETICSCORE) == 0:
                        await self._bot.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            else:
                # If we have no gateway, build gateway
                if self._bot.can_afford(UnitTypeId.GATEWAY) and self._bot.already_pending(UnitTypeId.GATEWAY) == 0:
                    await self._bot.build(UnitTypeId.GATEWAY, near=pylon)

        # Build gas near completed nexuses once we have a cybercore (does not need to be completed
        if self._bot.structures(UnitTypeId.CYBERNETICSCORE):
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

        # If we have less than 3  but at least 3 nexuses, build stargate
        if self._bot.structures(UnitTypeId.PYLON).ready and self._bot.structures(UnitTypeId.CYBERNETICSCORE).ready:
            pylon = self._bot.structures(UnitTypeId.PYLON).ready.random
            if (
                self._bot.townhalls.ready.amount + self._bot.already_pending(UnitTypeId.NEXUS) >= 3
                and self._bot.structures(UnitTypeId.STARGATE).ready.amount + self._bot.already_pending(
                UnitTypeId.STARGATE) < 3
            ):
                if self._bot.can_afford(UnitTypeId.STARGATE):
                    await self._bot.build(UnitTypeId.STARGATE, near=pylon)

        # Save up for expansions, loop over idle completed stargates and queue void ray if we can afford
        if self._bot.townhalls.amount >= 3:
            for sg in self._bot.structures(UnitTypeId.STARGATE).ready.idle:
                if self._bot.can_afford(UnitTypeId.VOIDRAY):
                    self._bot.do(sg.train(UnitTypeId.VOIDRAY), subtract_cost=True, subtract_supply=True)
