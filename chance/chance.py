import abc
import random

# STRAT IMPORTS
# noinspection PyUnresolvedReferences
from typing import Optional, List, Union

from chance.strats.random.worker_rush import WorkerRush
# noinspection PyUnresolvedReferences
from chance.strats.terran.four_rax import FourRax
# noinspection PyUnresolvedReferences
from chance.strats.terran.five_rax import FiveRax
# noinspection PyUnresolvedReferences
from chance.strats.terran.planetary_fortress_rush import PlanetaryFortressRush
# noinspection PyUnresolvedReferences
from chance.strats.zerg.ling_rush import LingRush
# noinspection PyUnresolvedReferences
from chance.strats.zerg.roach_rush import RoachRush
# noinspection PyUnresolvedReferences
from chance.strats.zerg.ravager_rush import RavagerRush
# noinspection PyUnresolvedReferences
from chance.strats.protoss.four_gate_stalkers import FourGateStalkers

from chance.strats.strat import Strat
from config import get_version
from sc2.data import Race
from sharpy.knowledges import KnowledgeBot, SkeletonBot
from sharpy.plans import BuildOrder


class Chance(KnowledgeBot):
    RANDOM_STRATS = ['WorkerRush', ]
    TERAN_STRATS = ['FourRax', 'FiveRax', 'PlanetaryFortressRush', ] + RANDOM_STRATS
    ZERG_STRATS = ['LingRush', 'RavagerRush', 'RoachRush', ] + RANDOM_STRATS
    PROTOSS_STRATS = ['FourGateStalkers', ] + RANDOM_STRATS

    AVAILABLE_STRATS = {
        Race.Terran: TERAN_STRATS,
        Race.Zerg: ZERG_STRATS,
        Race.Protoss: PROTOSS_STRATS,
    }

    def __init__(self, strat_name=None):
        super().__init__("Chance")
        if strat_name is not None:
            self._force_strat = strat_name
        else:
            self._force_strat = None

        self.random_build_used = False

    async def create_plan(self) -> BuildOrder:
        if self.knowledge.data_manager.last_result is not None and self.knowledge.data_manager.last_result.result == 1 \
                and self.knowledge.data_manager.last_result.build_used != ""\
                and self.knowledge.data_manager.last_result.build_used in self.AVAILABLE_STRATS[self.race]:
            build = self.knowledge.data_manager.last_result.build_used
        else:
            build = random.choice(self.AVAILABLE_STRATS[self.race])
            self.random_build_used = True

        if self._force_strat is not None:
            build = self._force_strat

        self.knowledge.data_manager.set_build(build)
        await self.chat_send(f'Tag: {build}')
        return await self._get_strat(build).create_plan()

    def _is_dummy_bot_class(self, strat_class) -> bool:
        return type(strat_class) == abc.ABCMeta  # hacky way to detect that this is a sharpy dummy class

    def _instantiate_strat(self, strat_class: str):
        class_type = globals()[strat_class]
        if self._is_dummy_bot_class(class_type):
            return class_type()
        else:
            return class_type(self)

    def _get_strat(self, strat_class: str) -> Union[Strat, SkeletonBot]:
        # constructs the class based on the classes name as a string
        return self._instantiate_strat(strat_class)

    def _create_start_msg(self) -> str:
        msg: str = ""

        if self.name is not None:
            msg += self.name

        version = get_version()
        if len(version) >= 2:
            msg += f" {version[0]} {version[1]} {int(self.random_build_used)}"

        return msg
