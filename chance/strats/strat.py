from abc import abstractmethod
from multiprocessing.managers import BaseManager
from typing import List, Optional

from sharpy.knowledges import KnowledgeBot
from sharpy.managers import ManagerBase
from sharpy.plans import BuildOrder


class Strat:
    """
    An abstract strat containing generic functionality
    """

    def __init__(self, bot: KnowledgeBot):
        self._bot = bot

    @abstractmethod
    async def create_plan(self) -> BuildOrder:
        pass

    @staticmethod
    def configure_managers(self) -> Optional[List[ManagerBase]]:
        return []
