from sharpy.plans.acts import ActBase


class SetGameStepSize(ActBase):
    def __init__(self, step_size):
        super().__init__()
        self.step_size = step_size

    async def execute(self) -> bool:
        self.ai.client.game_step = self.step_size
        return True
