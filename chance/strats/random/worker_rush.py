from chance.strats.strat import Strat


class WorkerRush(Strat):
    """
    Immediately attacks with all workers.

    todo: Build a worker and attack with that as well
    todo: Lift command center if any
    """

    def __init__(self, _bot):
        super().__init__(_bot)

    async def on_step(self):
        if self._bot.iteration == 0:
            for worker in self._bot.workers:
                self._bot.do(worker.attack(self._bot.enemy_start_locations[0]))
