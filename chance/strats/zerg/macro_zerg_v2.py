from typing import Optional, List

from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.managers.core import ManagerBase
from sharpy.plans import BuildOrder, Step, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.zerg import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *
from sharpy.plans.tactics.zerg import *


class MacroBuild(BuildOrder):
    def __init__(self):
        ultras = [
            Step(UnitExists(UnitTypeId.ULTRALISKCAVERN, 1), None),
            Step(Gas(500), ActUnit(UnitTypeId.ULTRALISK, UnitTypeId.LARVA, priority=True)),
        ]

        units = [
            Step(None, ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 100), skip=UnitExists(UnitTypeId.HIVE, 1)),
            Step(None, ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 50)),
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), ActUnit(UnitTypeId.ZERGLING, UnitTypeId.LARVA), None),
        ]

        build_step_expansions = [
            Step(None, Expand(999)),
        ]

        queens = [
            Step(UnitExists(UnitTypeId.SPAWNINGPOOL, 1), None),
            Step(Minerals(500), ActUnit(UnitTypeId.QUEEN, UnitTypeId.HATCHERY, 5)),
        ]

        pool_and_tech = [
            Step(None, ActBuilding(UnitTypeId.SPAWNINGPOOL, 1)),
            StepBuildGas(2, None),
            Step(None, Tech(UpgradeId.ZERGLINGMOVEMENTSPEED)),
            Step(Gas(120), ActBuilding(UnitTypeId.EVOLUTIONCHAMBER, 2)),
            Step(UnitExists(UnitTypeId.EVOLUTIONCHAMBER, 1), Tech(UpgradeId.ZERGMELEEWEAPONSLEVEL1)),
            Step(None, Tech(UpgradeId.ZERGGROUNDARMORSLEVEL1)),
            Step(None, MorphLair(), skip=UnitExists(UnitTypeId.HIVE, 1)),
            StepBuildGas(4, None),
            Step(None, Tech(UpgradeId.ZERGMELEEWEAPONSLEVEL2)),
            Step(None, Tech(UpgradeId.ZERGGROUNDARMORSLEVEL2)),
            # Infestation pit required
            Step(None, ActBuilding(UnitTypeId.INFESTATIONPIT, 1)),
            Step(UnitReady(UnitTypeId.INFESTATIONPIT, 1), MorphHive()),
            Step(UnitReady(UnitTypeId.HIVE, 1), Tech(UpgradeId.ZERGLINGATTACKSPEED)),
            StepBuildGas(6, None),
            Step(None, ActBuilding(UnitTypeId.ULTRALISKCAVERN, 1)),
            Step(None, Tech(UpgradeId.ZERGMELEEWEAPONSLEVEL3)),
            Step(None, Tech(UpgradeId.ZERGGROUNDARMORSLEVEL3)),
            Step(None, Tech(UpgradeId.CHITINOUSPLATING)),
            Step(None, Tech(UpgradeId.ANABOLICSYNTHESIS)),
        ]

        super().__init__(self.overlords, ultras, units, build_step_expansions, queens, pool_and_tech)


class MacroZergV2(Strat):
    """Macro Zerg bot that expands like crazy, makes drones and finally transitions to waves of zerglings."""

    def configure_managers(self) -> Optional[List[ManagerBase]]:
        self._bot.combat.default_rules.regroup = False
        return None

    async def create_plan(self) -> BuildOrder:
        attack = PlanZoneAttack(120)
        attack.retreat_multiplier = 0.3
        tactics = [
            MineOpenBlockedBase(),
            PlanCancelBuilding(),
            InjectLarva(),
            DistributeWorkers(),
            Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
            attack,
            PlanFinishEnemy(),
        ]
        return CounterTerranTie([MacroBuild(), tactics])
