from typing import List, Optional

from chance.queens_sc2_manager import QueensSc2Manager
from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sharpy.managers import ManagerBase
from sharpy.plans import BuildOrder, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import AutoOverLord
from sharpy.plans.tactics import DistributeWorkers, SpeedMining


class QueensSc2(Strat):
    """A strategy using the queens sc2 library"""

    def build(self):
        self._bot.can_afford(UnitTypeId.HATCHERY) and self._bot.workers.amount > 0

    async def create_plan(self) -> BuildOrder:
        build_drones = lambda ai: self._bot.can_afford(UnitTypeId.DRONE) and self._bot.larva.amount > 0 \
                                  and self._bot.workers.amount < self._bot.townhalls.amount * 16 \
                                  and self._bot.workers.amount < 48  # max 3 base saturation
        build_queens = lambda ai: self._bot.can_afford(UnitTypeId.QUEEN) and self._bot.townhalls.amount > 0 \
                                  and self._bot.townhalls.ready
        return BuildOrder(
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 13),
            ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 1),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
            Expand(2),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 16),
            ActBuilding(UnitTypeId.SPAWNINGPOOL, 1),
            ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
            SequentialList(
                DistributeWorkers(max_gas=0),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                AutoOverLord(),
                Step(None, ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA), skip_until=build_drones),
                Step(None, ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY), skip_until=build_queens),
                Step(None, Expand(3), skip_until=lambda ai: self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
            ),
        )

    @staticmethod
    def configure_managers(self) -> Optional[List[ManagerBase]]:
        return [QueensSc2Manager()]
