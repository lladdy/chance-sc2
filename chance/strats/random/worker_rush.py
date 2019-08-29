from chance.strats.strat import Strat


class WorkerRush(Strat):
    """
    Immediately attacks with all workers.
    Adapted from https://github.com/BurnySc2/python-sc2/blob/develop/examples/worker_rush.py
    todo: Build a worker and attack with that as well
    todo: Lift command center if any
    """

    def __init__(self, _bot):
        super().__init__(_bot)

    async def on_step(self):
        if self._bot.iteration == 0:
            for worker in self._bot.workers:
                self._bot.do(worker.attack(self._bot.enemy_start_locations[0]))
