from typing import Dict

import numpy as np

from queens_sc2.queens import Queens
from sharpy.managers import ManagerBase


class QueensSc2Manager(ManagerBase):
    """
    A basic custom sharpy manager to utilize queens-sc2 in the context of a sharpy bot.
    ManagerBase is from https://github.com/lladdy/sharpy-sc2/blob/40593cf04946132d28e98e9d0cd225e83d30c8bd/sharpy/managers/core/manager_base.py
    """

    def __init__(self, queen_policy: Dict = None, use_sc2_map_analyzer=False):
        super().__init__()
        self.queen_policy = queen_policy
        self.queens = None
        self.use_sc2_map_analyzer = use_sc2_map_analyzer

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)

        if self.use_sc2_map_analyzer:
            from SC2MapAnalysis.MapAnalyzer import MapData
            self.map_data = MapData(self.ai)
        else:
            self.map_data = None

        self.queens = Queens(
            self.ai, debug=self.debug, queen_policy=self.queen_policy, map_data=self.map_data
        )

    async def update(self):
        if self.map_data:
            avoidance_grid: np.ndarray = self.map_data.get_pyastar_grid()
            # add cost to avoidance_grid, for example positions of nukes / biles / storms etc
            ground_grid: np.ndarray = self.map_data.get_pyastar_grid()
            # you may want to add cost etc depending on your bot,
        else:
            avoidance_grid = None
            ground_grid = None

        # depending on usecase it may not need a fresh grid every step
        await self.queens.manage_queens(self.knowledge.iteration, avoidance_grid=avoidance_grid, grid=ground_grid)

    async def post_update(self):
        pass

    def set_new_policy(self, queen_policy: Dict):
        self.queens.set_new_policy(queen_policy)
