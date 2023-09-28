from typing import List, Optional

from chance.strats import Strat
from queens_sc2.consts import QueenRoles
from queens_sc2.sharpy import QueensSc2Manager, SetQueensSc2Policy
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.managers import ManagerBase
from sharpy.plans import BuildOrder, SequentialList, Step
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import AutoOverLord, MorphLair, MorphHive
from sharpy.plans.require import UnitReady, TechReady
from sharpy.plans.tactics import DistributeWorkers, SpeedMining


class QueensSc2(Strat):
    """A strategy using the queens sc2 library"""

    async def create_plan(self) -> BuildOrder:
        queens_manager = self._bot.knowledge.get_manager(QueensSc2Manager)

        # Policies originally from QueenBot: https://aiarena.net/bots/201/
        early_game_queen_policy = {
            "creep_queens": {
                "active": True,
                "distance_between_queen_tumors": 3,
                "first_tumor_position": self._bot.zone_manager.own_natural.center_location.towards(
                    self._bot.game_info.map_center, 9
                ),
                "priority": True,
                "prioritize_creep": lambda: True,
                "max": 2,
                "defend_against_ground": True,
                "rally_point": self._bot.zone_manager.own_natural.center_location,
                "priority_defence_list": {
                    UnitTypeId.ZERGLING,
                    UnitTypeId.MARINE,
                    UnitTypeId.ZEALOT
                },
            },
            "creep_dropperlord_queens": {
                "active": True,
                "priority": True,
                "max": 1,
                "pass_own_threats": True,
                "target_expansions": [
                    el[0] for el in self._bot.expansion_locations_list[-6:-3]
                ],
            },
            "defence_queens": {
                "attack_condition": lambda: self._bot.enemy_units.filter(
                    lambda u: u.type_id == UnitTypeId.WIDOWMINEBURROWED
                              and u.distance_to(self._bot.enemy_start_locations[0]) > 50
                              and not queens_manager.queens.defence.enemy_air_threats
                              and not queens_manager.queens.defence.enemy_ground_threats
                )
                                            or (
                                                self._bot.structures(UnitTypeId.NYDUSCANAL)
                                                and self._bot.units(UnitTypeId.QUEEN).amount > 25
                                            ),
                "rally_point": self._bot.zone_manager.own_natural.center_location,
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
            "nydus_queens": {
                "active": True,
                "max": 12,
                "steal_from": {QueenRoles.Defence},
            },
        }

        mid_game_queen_policy = {
            "creep_queens": {
                "max": 2,
                "priority": True,
                "defend_against_ground": True,
                "distance_between_queen_tumors": 3,
                "priority_defence_list": {
                    UnitTypeId.BATTLECRUISER,
                    UnitTypeId.LIBERATOR,
                    UnitTypeId.LIBERATORAG,
                    UnitTypeId.VOIDRAY,
                },
            },
            "creep_dropperlord_queens": {
                "active": True,
                "priority": True,
                "max": 1,
                "pass_own_threats": True,
                "priority_defence_list": set(),
                "target_expansions": [
                    el for el in self._bot.expansion_locations_list
                ],
            },
            "defence_queens": {
                "attack_condition": lambda: (
                                                sum([unit.energy for unit in self._bot.units(UnitTypeId.QUEEN)])
                                                / self._bot.units(UnitTypeId.QUEEN).amount
                                                >= 75
                                                and self._bot.units(UnitTypeId.QUEEN).amount > 40
                                            )
                                            or self._bot.enemy_units.filter(
                    lambda u: u.type_id == UnitTypeId.WIDOWMINEBURROWED
                              and u.distance_to(self._bot.enemy_start_locations[0]) > 50
                              and not queens_manager.queens.defence.enemy_air_threats
                              and not queens_manager.queens.defence.enemy_ground_threats
                )
                                            or self._bot.structures(UnitTypeId.NYDUSCANAL),
                "rally_point": self._bot.zone_manager.own_natural.center_location,
            },
            "inject_queens": {"active": False},
            "nydus_queens": {
                "active": True,
                "max": 12,
                "steal_from": {QueenRoles.Defence},
            },
        }

        gas_workers = 4
        build_drones = lambda ai: self._bot.workers.amount >= self._bot.townhalls.amount * 16 + gas_workers \
                                  or self._bot.workers.amount >= 16 * 3 + gas_workers  # max 3 base saturation

        upgrades = [
            Step(UnitReady(UnitTypeId.EVOLUTIONCHAMBER, 1),
                 Tech(UpgradeId.ZERGMISSILEWEAPONSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER)),
            Tech(UpgradeId.ZERGGROUNDARMORSLEVEL1, UnitTypeId.EVOLUTIONCHAMBER),
            Tech(UpgradeId.ZERGMISSILEWEAPONSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
            Tech(UpgradeId.ZERGGROUNDARMORSLEVEL2, UnitTypeId.EVOLUTIONCHAMBER),
            Tech(UpgradeId.ZERGMISSILEWEAPONSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
            Tech(UpgradeId.ZERGGROUNDARMORSLEVEL3, UnitTypeId.EVOLUTIONCHAMBER),
        ]

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
                MineOpenBlockedBase(),
                Step(None, SetQueensSc2Policy(mid_game_queen_policy, policy_name="mid_game_queen_policy"),
                     skip_until=lambda ai: ai.time > 480),
                BuildOrder(
                    Step(None, DistributeWorkers(max_gas=4), skip=TechReady(UpgradeId.ZERGGROUNDARMORSLEVEL3, 0.01)),
                    Step(None, DistributeWorkers(max_gas=0),
                         skip_until=TechReady(UpgradeId.ZERGGROUNDARMORSLEVEL3, 0.01)),
                ),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                AutoOverLord(),
                BuildOrder(
                    Step(None, ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA), skip=build_drones),
                    Step(None, MorphLair(), skip_until=TechReady(UpgradeId.ZERGGROUNDARMORSLEVEL1, 0.5)),
                    Step(None, ActBuilding(UnitTypeId.INFESTATIONPIT),
                         skip_until=TechReady(UpgradeId.ZERGGROUNDARMORSLEVEL2, 0.01)),
                    Step(None, MorphHive(), skip_until=TechReady(UpgradeId.ZERGGROUNDARMORSLEVEL2, 0.5)),
                    Step(None, ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY)),
                    Expand(4),  # 4 mining bases
                    BuildGas(2),
                    ActBuilding(UnitTypeId.EVOLUTIONCHAMBER, 2),
                    upgrades,
                    ActBuilding(UnitTypeId.HATCHERY, 20),
                )
            ),
        )

    def configure_managers(self) -> Optional[List[ManagerBase]]:
        return [QueensSc2Manager(use_sc2_map_analyzer=True)]
