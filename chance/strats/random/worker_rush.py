from chance.strats.strat import Strat
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder
from sharpy.plans.acts import ActBase


class WorkerAttack(ActBase):

    def __init__(self, bot: KnowledgeBot):
        super().__init__()
        self._bot = bot

    async def execute(self) -> bool:
        for worker in self._bot.workers:
            self._bot.do(worker.attack(self._bot.enemy_start_locations[0]))
        return True


class WorkerRush(Strat):
    def __init__(self, _bot):
        super().__init__(_bot)

    async def create_plan(self) -> BuildOrder:
        return BuildOrder([WorkerAttack(self._bot)])
