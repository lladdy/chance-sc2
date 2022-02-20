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
            from MapAnalyzer import MapData
            self.map_data = MapData(self.ai)

            self.avoidance_grid: np.ndarray = self.map_data.get_pyastar_grid()
            self.ground_grid: np.ndarray = self.map_data.get_pyastar_grid()
        else:
            self.map_data = None
            self.avoidance_grid = None
            self.ground_grid = None

        self.queens = Queens(
            self.ai, debug=self.debug, queen_policy=self.queen_policy, map_data=self.map_data
        )

    async def update(self):
        await self.queens.manage_queens(self.knowledge.iteration, avoidance_grid=self.avoidance_grid, grid=self.ground_grid)

    async def post_update(self):
        pass

    def set_new_policy(self, queen_policy: Dict):
        self.queens.set_new_policy(queen_policy)
