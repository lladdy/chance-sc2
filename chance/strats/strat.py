from abc import abstractmethod

import sc2
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder


class Strat:
    """
    An abstract strat containing generic functionality
    """

    _bot: KnowledgeBot = None  # reference to the bot instance

    def __init__(self, bot: KnowledgeBot):
        self._bot = bot

    @abstractmethod
    async def create_plan(self) -> BuildOrder:
        pass
