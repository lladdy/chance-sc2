from chance.strats.strat import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.plans import BuildOrder, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.terran import AutoDepot
from sharpy.plans.tactics import *
from sharpy.plans.tactics.terran import LowerDepots, ManTheBunkers, Repair, ContinueBuilding, PlanZoneGatherTerran


class BunkerContain(Strat):
    """
    Contributed by Ratosh.
    """
    async def create_plan(self) -> BuildOrder:
        bunker_location = self._bot.zone_manager.expansion_zones[-2].center_location.towards(
            self._bot.game_info.map_center, 11.0)
        return BuildOrder([SequentialList(
            [
                GridBuilding(UnitTypeId.SUPPLYDEPOT, 1),
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 15),
                GridBuilding(UnitTypeId.BARRACKS, 2),
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 16),
                BuildPosition(UnitTypeId.BUNKER, bunker_location, exact=False, only_once=True),
                ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 1),
                GridBuilding(UnitTypeId.BARRACKS, 3),
                ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 2),
                GridBuilding(UnitTypeId.SUPPLYDEPOT, 2),
                ActUnit(UnitTypeId.SCV, UnitTypeId.COMMANDCENTER, 18),
                ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 6),
                GridBuilding(UnitTypeId.BARRACKS, 6),
                BuildOrder([AutoDepot(), ActUnit(UnitTypeId.MARINE, UnitTypeId.BARRACKS, 200), ])]), SequentialList(
            [PlanCancelBuilding(), LowerDepots(), PlanZoneDefense(), DistributeWorkers(),
             Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5), ManTheBunkers(), Repair(),
             ContinueBuilding(), PlanZoneGatherTerran(), PlanZoneAttack(26), PlanFinishEnemy()])])
