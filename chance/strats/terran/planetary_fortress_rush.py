from chance.strats.strat import Strat
from sc2 import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import BuildOrder, SequentialList, StepBuildGas, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.terran import AutoDepot, ActBuildAddon
from sharpy.plans.require import RequiredAny, RequiredGas, RequiredUnitExists, RequiredTechReady
from sharpy.plans.tactics import *
from sharpy.plans.tactics.terran import LowerDepots, ManTheBunkers, Repair, ContinueBuilding, PlanZoneGatherTerran


class MorphProxyPlanetary(MorphPlanetary):
    def __init__(self):
        super().__init__(1)

    async def execute(self) -> bool:
        target_count = self.cache.own(self.result_type).amount
        start_buildings = self.cache.own(self.building_type).ready.sorted_by_distance_to(
            self.knowledge.enemy_main_zone.center_location)

        for target in start_buildings:  # type: Unit
            if target.orders and target.orders[0].ability.id == self.ability_type:
                target_count += 1

        if target_count >= self.target_count:
            return True

        for target in start_buildings:
            if target.is_ready:
                if self.knowledge.can_afford(self.ability_type):
                    self.do(target(self.ability_type))

                self.knowledge.reserve_costs(self.ability_type)
                target_count += 1

                if target_count >= self.target_count:
                    return True
        if start_buildings:
            return False
        return True


class PlanetaryFortressRush(Strat):
    async def create_plan(self) -> BuildOrder:
        finish_rush = RequiredAny([RequiredGas(150), RequiredUnitExists(UnitTypeId.PLANETARYFORTRESS)])
        return BuildOrder([
            SequentialList([
                BuildPosition(UnitTypeId.COMMANDCENTER, self._bot.knowledge.zone_manager.enemy_natural.center_location,
                              exact=True, only_once=True),
                StepBuildGas(2),
                ActBuilding(UnitTypeId.ENGINEERINGBAY),
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 17),
                MorphProxyPlanetary(),
                GridBuilding(UnitTypeId.SUPPLYDEPOT, 1),
                BuildOrder([
                    ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 38),
                    ActUnit(UnitTypeId.SCV, UnitTypeId.PLANETARYFORTRESS, 38),
                    GridBuilding(UnitTypeId.BARRACKS, 4),
                    ActBuildAddon(UnitTypeId.BARRACKSTECHLAB, UnitTypeId.BARRACKS, 2),
                    ActBuildAddon(UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKS, 2),
                    ActTech(UpgradeId.STIMPACK, UnitTypeId.BARRACKSTECHLAB),
                    ActTech(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1, UnitTypeId.ENGINEERINGBAY),
                    AutoDepot(),
                    ActUnit(UnitTypeId.MARAUDER, UnitTypeId.BARRACKS, 50),
                    ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 100),

                    GridBuilding(UnitTypeId.BARRACKS, 6),
                    ActBuildAddon(UnitTypeId.BARRACKSREACTOR, UnitTypeId.BARRACKS, 4),
                ]),
            ]),
            SequentialList([
                Step(None, PlanDistributeWorkers(min_gas=6), skip=finish_rush),
                Step(finish_rush, PlanDistributeWorkers(max_gas=4)),
            ]),
            SequentialList(
                [
                    PlanCancelBuilding(),
                    LowerDepots(),
                    PlanZoneDefense(),
                    ManTheBunkers(),
                    Repair(),
                    ContinueBuilding(),
                    PlanZoneGatherTerran(),
                    Step(RequiredTechReady(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1), PlanZoneAttack(20)),
                    PlanFinishEnemy(),
                ])
        ])
