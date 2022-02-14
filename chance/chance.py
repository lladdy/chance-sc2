import random

# STRAT IMPORTS
from chance.strats.random import *
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
from sc2.data import Race
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder


class Chance(KnowledgeBot):
    RANDOM_STRATS = get_strats_from_module('chance.strats.random')
    TERAN_STRATS = get_strats_from_module('chance.strats.terran') + RANDOM_STRATS
    ZERG_STRATS = get_strats_from_module('chance.strats.zerg') + RANDOM_STRATS
    PROTOSS_STRATS = get_strats_from_module('chance.strats.protoss') + RANDOM_STRATS

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
        self.decider = Decider()

    async def create_plan(self) -> BuildOrder:
        build, probability = self.decider.decide(f'build_{self.opponent_id}_{self.race}', self.AVAILABLE_STRATS[self.race])

        # Useful for debugging specific strats.
        if self._force_strat is not None:
            build = self._force_strat

        self.knowledge.data_manager.set_build(build)
        await self.chat_send(f'Tag: {build}')
        await self.chat_send(f'P: {probability}')
        return await self._get_strat(build).create_plan()

    def _get_strat(self, strat_class: str) -> Strat:
        # constructs the class based on the classes name as a string
        return globals()[strat_class](self)

    def _create_start_msg(self) -> str:
        msg: str = ""

        if self.name is not None:
            msg += self.name

        version = get_version()
        if len(version) >= 2:
            msg += f" {version[0]} {version[1]} {int(self.random_build_used)}"

        return msg
