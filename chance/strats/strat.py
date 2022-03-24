from abc import abstractmethod
from typing import List, Optional

from sharpy.knowledges import KnowledgeBot
from sharpy.managers import ManagerBase
from sharpy.plans import BuildOrder


class Strat:
    """
    An abstract strat containing generic functionality
    """

    async def on_start(self, bot: KnowledgeBot):
        self._bot = bot

    @abstractmethod
    async def create_plan(self) -> BuildOrder:
        pass

    def configure_managers(self) -> Optional[List[ManagerBase]]:
        return []
