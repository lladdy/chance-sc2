import argparse
import os
import sys

from sc2 import maps
from sc2.data import Race, Difficulty, Result
from sc2.main import run_game

sys.path.insert(1, "sharpy-sc2")
sys.path.insert(1, os.path.join("sharpy-sc2", "python-sc2"))

from chance.chance import Chance
from sc2.player import Bot

from sc2.bot_ai import BotAI


class TestBot(BotAI):
    """A test bot that does nothing. This means we should always win."""
    async def on_step(self, iteration: int):
        pass


# Start game
if __name__ == '__main__':
    for race in Chance.AVAILABLE_STRATS.keys():
        for strat in Chance.AVAILABLE_STRATS[race]:
            print(f'Race {race}. Strat: {strat}.')
            bot: Bot = Bot(race, Chance(strat))
            test_bot: Bot = Bot(Race.Random, TestBot())
            result = run_game(maps.get("2000AtmospheresAIE"), [
                bot,
                test_bot,
            ], realtime=False)
            if result == Result.Defeat:
                raise "Test failed - we were defeated (assumed crash)."

