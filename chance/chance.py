import random

# STRAT IMPORTS
# noinspection PyUnresolvedReferences
from chance.strats.random.worker_rush import WorkerRush
# noinspection PyUnresolvedReferences
from chance.strats.protoss.four_gate_stalkers import FourGateStalkers

from chance.strats.strat import Strat
from sc2 import Race
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder


class Chance(KnowledgeBot):
    RANDOM_STRATS = ['WorkerRush', ]
    TERAN_STRATS = [] + RANDOM_STRATS
    ZERG_STRATS = [] + RANDOM_STRATS
    PROTOSS_STRATS = [] + RANDOM_STRATS

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

    async def create_plan(self) -> BuildOrder:
        return await self._get_strat(random.choice(self.AVAILABLE_STRATS[self.race])).create_plan()

    def _get_strat(self, strat_class: str) -> Strat:
        if self._force_strat is not None:
            strat_class = self._force_strat
        # constructs the class based on the classes name as a string
        return globals()[strat_class](self)
