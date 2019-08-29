import sc2


class Strat:
    """
    An abstract strat containing generic functionality
    """

    _bot = None  # reference to the bot instance

    def __init__(self, _bot: sc2.BotAI):
        self._bot = _bot

    async def on_step(self):
        """
        Override this
        """
        pass
