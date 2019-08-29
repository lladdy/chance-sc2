import random

import sc2
# noinspection PyUnresolvedReferences
from chance.strats.random.worker_rush import WorkerRush
from chance.strats.strat import Strat
# noinspection PyUnresolvedReferences
from chance.strats.zerg.zerg_rush import ZergRush


class Chance(sc2.BotAI):
    RANDOM_STRATS = ['WorkerRush', ]
    TERAN_STRATS = [] + RANDOM_STRATS
    ZERG_STRATS = ['ZergRush', ] + RANDOM_STRATS
    PROTOSS_STRATS = [] + RANDOM_STRATS

    def __init__(self):
        super().__init__()
        self.iteration = None
        self._strat = self._get_strat()

    def _get_strat(self) -> Strat:
        # constructs the class based on the string
        return globals()[random.choice(self.ZERG_STRATS)](self)

    async def on_step(self, iteration):
        self.iteration = iteration
        await self._strat.on_step()
