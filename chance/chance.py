import os

import sc2
from sc2 import Race

LOCAL_DIRECTORY = os.path.dirname(__file__)


class Chance(sc2.BotAI):

    def __init__(self, play_race: Race):
        super().__init__()

    async def on_step(self, iteration):

        pass
