from chance.strats.strat import Strat
from sc2 import Race, UnitTypeId
from sharpy.knowledges import KnowledgeBot
from sharpy.plans import BuildOrder, Step, StepBuildGas, SequentialList
from sharpy.plans.acts import ActBase, ActUnit, ActBuilding
from sharpy.plans.acts.zerg import MorphLair, ZergUnit, AutoOverLord
from sharpy.plans.require import RequireCustom, RequiredUnitReady
from sharpy.plans.tactics import PlanDistributeWorkers, PlanFinishEnemy, PlanZoneGather, PlanZoneDefense, PlanZoneAttack
from sharpy.plans.tactics.zerg import InjectLarva


class WorkerAttack(ActBase):

    def __init__(self, bot: KnowledgeBot):
        super().__init__()
        self._bot = bot

    async def execute(self) -> bool:
        for worker in self._bot.workers:
            self._bot.do(worker.attack(self._bot.enemy_start_locations[0]))
        return True


class CleanUp(ActBase):
    def __init__(self):
        super().__init__()

    async def start(self, knowledge: 'Knowledge'):
        build_order = []
        if knowledge.my_race == Race.Zerg:
            build_order = [
                PlanDistributeWorkers(),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                StepBuildGas(2),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 14),
                ActBuilding(UnitTypeId.SPAWNINGPOOL),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 20),
                MorphLair(),
                ActUnit(UnitTypeId.DRONE, UnitTypeId.LARVA, 30),
                StepBuildGas(4),
                ActBuilding(UnitTypeId.SPIRE),
                ZergUnit(UnitTypeId.MUTALISK, 100, priority=True),
                SequentialList(
                    [
                        PlanZoneDefense(),
                        AutoOverLord(),
                        InjectLarva(),
                        PlanZoneGather(),
                        Step(RequiredUnitReady(UnitTypeId.MUTALISK), PlanZoneAttack(10)),
                        PlanFinishEnemy(),
                    ])
            ]

        self.build_order = BuildOrder(build_order)
        await self.build_order.start(knowledge)

    async def execute(self) -> bool:
        return await self.build_order.execute()


class WorkerRush(Strat):
    def __init__(self, _bot):
        super().__init__(_bot)

    async def create_plan(self) -> BuildOrder:
        perform_cleanup = RequireCustom(lambda
                                            k: self._bot.knowledge.enemy_main_zone.is_scouted_at_least_once and not self._bot.knowledge.enemy_main_zone.is_enemys)
        return BuildOrder([
            Step(None, WorkerAttack(self._bot), skip=perform_cleanup),
            Step(None, CleanUp(), skip_until=perform_cleanup),
        ])
