import argparse
import os
import sys

from sc2 import maps
from sc2.data import Race, Difficulty
from sc2.main import run_game

sys.path.insert(1, "sharpy-sc2")
sys.path.insert(1, os.path.join("sharpy-sc2", "python-sc2"))
sys.path.insert(1, "SC2MapAnalysis")
sys.path.insert(1, "bossman-sc2")

from chance import run_ladder_game
from chance.chance import Chance
from sc2.player import Bot, Computer

race_map = {
    'terran': Race.Terran,
    'zerg': Race.Zerg,
    'protoss': Race.Protoss,
    'random': Race.Random,
}

# Start game
if __name__ == '__main__':
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        bot = Bot(Race.Random, Chance())
        run_ladder_game(bot)
    else:
        # Local game
        print("Starting local game...")

        parser = argparse.ArgumentParser()
        parser.add_argument('--ForceRace', type=str, nargs="?", help='Force a specific race')
        parser.add_argument('--ForceStrategy', type=str, nargs="?", help='Force a specific strategy')
        args, _ = parser.parse_known_args()

        bot: Bot
        if args.ForceRace is None:
            bot = Bot(Race.Random, Chance())
        elif args.ForceStrategy is None:
            bot = Bot(race_map[args.ForceRace], Chance())
        else:
            bot = Bot(race_map[args.ForceRace], Chance(args.ForceStrategy))

        run_game(maps.get("RoyalBloodAIE"), [
            bot,
            Computer(Race.Random, Difficulty.VeryHard),
        ], save_replay_as=f'replays/replay.SC2Replay', realtime=False)

