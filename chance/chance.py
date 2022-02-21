import random

# STRAT IMPORTS
from typing import Optional, List, Callable

# noinspection PyUnresolvedReferences
from chance.strats.terran import *
# noinspection PyUnresolvedReferences
from chance.strats.zerg import *
# noinspection PyUnresolvedReferences
from chance.strats.protoss import *

from chance.strats import Strat
from chance.util import get_strats_from_module
from config import get_version
from decider import Decider
from sc2.data import Race, Result
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder


class Chance(KnowledgeBot):
    AVAILABLE_STRATS = {
        Race.Terran: get_strats_from_module('chance.strats.terran'),
        Race.Zerg: get_strats_from_module('chance.strats.zerg'),
        Race.Protoss: get_strats_from_module('chance.strats.protoss'),
    }

    def __init__(self, strat_name=None):
        super().__init__("Chance")
        if strat_name is not None:
            self._force_strat = strat_name
        else:
            self._force_strat = None

        self.random_build_used = False
        self.decider = Decider()

    async def on_start(self):
        # Useful for debugging specific strats.
        if self._force_strat is not None:
            self.build_name = self._force_strat
            self.probability = 1.0
        else:
            # do this here because we need to know the build in order to create required managers
            self.build_name, self.probability = self.decider.decide(f'build_{self.opponent_id}_{self.race}', self.AVAILABLE_STRATS[self.race])

        self.strat = self._get_strat(self.build_name)
        await self.strat.on_start(self)
        await super().on_start()

    async def create_plan(self) -> BuildOrder:
        self.knowledge.data_manager.set_build(self.build_name)
        await self.chat_send(f'Tag: {self.build_name}')
        await self.chat_send(f'P: {self.probability}')
        return await self.strat.create_plan()

    def configure_managers(self) -> Optional[List["ManagerBase"]]:
        return self.strat.configure_managers()

    async def on_end(self, game_result: Result):
        self.decider.register_result(game_result==Result.Victory)
        await super().on_end(game_result)

    def _get_strat(self, strat_class: str) -> Strat:
        """
        Constructs the class based on the classes name as a string
        """
        return self._get_strat_class(strat_class)()

    def _get_strat_class(self, strat_class_name: str) -> type(Strat):
        """
        Gets the class based on the classes name as a string
        """
        return globals()[strat_class_name]

    def _create_start_msg(self) -> str:
        msg: str = ""

        if self.name is not None:
            msg += self.name

        version = get_version()
        if len(version) >= 2:
            msg += f" {version[0]} {version[1]}"

        return msg
