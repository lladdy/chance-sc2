class Strat:
    """
    An abstract strat containing generic functionality
    """

    _bot = None  # reference to the bot instance

    def __init__(self, _bot):
        self._bot = _bot
