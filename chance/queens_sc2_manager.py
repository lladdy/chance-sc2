from abc import ABC, abstractmethod
from typing import Dict

from queens_sc2.queens import Queens
from sharpy.managers import ManagerBase


class QueensSc2Manager(ManagerBase):
    """
    A basic custom sharpy manager to utilize queens-sc2 in the context of a sharpy bot.
    ManagerBase is from https://github.com/lladdy/sharpy-sc2/blob/40593cf04946132d28e98e9d0cd225e83d30c8bd/sharpy/managers/core/manager_base.py
    """

    def __init__(self, queen_policy: Dict = None):
        super().__init__()
        self.queen_policy = queen_policy
        self.queens = None

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)

        self.queens = Queens(
            self.ai, debug=self.debug, queen_policy=self.queen_policy
        )

    async def update(self):
        await self.queens.manage_queens(self.knowledge.iteration)

    async def post_update(self):
        pass

    def set_new_policy(self, queen_policy: Dict):
        self.queens.set_new_policy(queen_policy)
