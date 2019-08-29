import os

import sc2
from sc2 import Race

from chance.strats.random.worker_rush import WorkerRush

LOCAL_DIRECTORY = os.path.dirname(__file__)


class Chance(sc2.BotAI):

    def __init__(self):
        super().__init__()
        self.iteration = None
        # todo: dynamically pick strat/build order here somehow...
        self._strat = WorkerRush(self)

    async def on_step(self, iteration):
        self.iteration = iteration
        await self._strat.on_step()
