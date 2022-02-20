from typing import List, Optional

from chance.queens_sc2_acts import SetQueensSc2Policy
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

    async def create_plan(self) -> BuildOrder:
        early_game_queen_policy = {
            "creep_queens": {
                "active": True,
                "priority": 2,
                "max": 4,
                "defend_against_ground": True,
                "first_tumor_position": self._bot.start_location.towards(
                    self._bot.main_base_ramp.top_center, 5
                ),
                "priority_defence_list": {
                    UnitTypeId.BATTLECRUISER,
                    UnitTypeId.LIBERATOR,
                    UnitTypeId.LIBERATORAG,
                    UnitTypeId.VOIDRAY,
                },
            },
            "defence_queens": {
                "priority_defence_list": {
                    UnitTypeId.BATTLECRUISER,
                    UnitTypeId.LIBERATOR,
                    UnitTypeId.LIBERATORAG,
                    UnitTypeId.VOIDRAY,
                }
            },
            "inject_queens": {
                "active": True,
                "priority": False,
                "max": 2,
                "priority_defence_list": {
                    UnitTypeId.BATTLECRUISER,
                    UnitTypeId.LIBERATOR,
                    UnitTypeId.LIBERATORAG,
                    UnitTypeId.VOIDRAY,
                },
            },
        }
        mid_game_queen_policy = {
            "creep_queens": {
                "max": 2,
                "priority": True,
                "distance_between_existing_tumors": 4,
                "defend_against_ground": False,
                "spread_style": "random",
            },
            "defence_queens": {
                "attack_condition": lambda: self._bot.units(UnitTypeId.QUEEN).amount > 20,
            },
            "inject_queens": {"active": False, "max": 0},
        }

        build_drones = lambda ai: self._bot.can_afford(UnitTypeId.DRONE) and self._bot.larva.amount > 0 \
                                  and self._bot.workers.amount < self._bot.townhalls.amount * 16 \
                                  and self._bot.workers.amount < 48  # max 3 base saturation
        build_queens = lambda ai: self._bot.can_afford(UnitTypeId.QUEEN) and self._bot.townhalls.amount > 0 \
                                  and self._bot.townhalls.ready
        return BuildOrder(
            SetQueensSc2Policy(early_game_queen_policy, policy_name="early_game_queen_policy"),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 13),
            ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 1),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
            Expand(2),
            ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 16),
            ActBuilding(UnitTypeId.SPAWNINGPOOL, 1),
            ActUnit(UnitTypeId.OVERLORD, UnitTypeId.LARVA, 2),
            SequentialList(
                Step(None, SetQueensSc2Policy(mid_game_queen_policy, policy_name="mid_game_queen_policy"),
                     skip_until=lambda ai: ai.time > 480),
                DistributeWorkers(max_gas=0),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                AutoOverLord(),
                Step(None, ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA), skip_until=build_drones),
                Step(None, ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY), skip_until=build_queens),
                Step(None, ActBuilding(UnitTypeId.HATCHERY, 3),
                     skip_until=lambda ai: self._bot.townhalls.amount == 2
                                           and self._bot.can_afford(UnitTypeId.HATCHERY)
                                           and self._bot.workers.amount > 0),
                Step(None, Expand(3), skip_until=lambda ai: self._bot.townhalls.amount == 2
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(4), skip_until=lambda ai: self._bot.townhalls.amount == 3
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(5), skip_until=lambda ai: self._bot.townhalls.amount == 4
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(6), skip_until=lambda ai: self._bot.townhalls.amount == 5
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(7), skip_until=lambda ai: self._bot.townhalls.amount == 6
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(8), skip_until=lambda ai: self._bot.townhalls.amount == 7
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(9), skip_until=lambda ai: self._bot.townhalls.amount == 8
                                                            and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                            and self._bot.workers.amount > 0),
                Step(None, Expand(10), skip_until=lambda ai: self._bot.townhalls.amount == 9
                                                             and self._bot.can_afford(UnitTypeId.HATCHERY)
                                                             and self._bot.workers.amount > 0),
            ),
        )

    @staticmethod
    def configure_managers(self) -> Optional[List[ManagerBase]]:
        return [QueensSc2Manager()]
