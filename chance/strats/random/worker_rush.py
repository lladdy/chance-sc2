from chance.strats.strat import Strat
from sc2 import Race, UnitTypeId
from sc2.units import Units
from sharpy.general.extended_power import ExtendedPower
from sharpy.managers.core.roles import UnitTask
from sharpy.plans import BuildOrder, Step, StepBuildGas, SequentialList
from sharpy.plans.acts import ActBase, ActUnit, ActBuilding
from sharpy.plans.acts.zerg import MorphLair, ZergUnit, AutoOverLord
from sharpy.plans.require import RequireCustom, UnitReady
from sharpy.plans.tactics import PlanFinishEnemy, PlanZoneGather, PlanZoneDefense, PlanZoneAttack, DistributeWorkers
from sharpy.plans.tactics.zerg import InjectLarva
from sharpy.plans.tactics.zone_attack_all_in import PlanZoneAttackAllIn


class WorkerAttack(PlanZoneAttackAllIn):
    def __init__(self):
        super().__init__(0)

    def _should_attack(self, power: ExtendedPower):
        return True  # attack no matter what

    def _start_attack(self, power: ExtendedPower, attackers: Units):
        self.ai.client.game_step = 1  # improve our worker micro

        return super()._start_attack(power, attackers)

    async def execute(self) -> bool:
        for unit in self.knowledge.ai.workers:
            self.knowledge.roles.set_task(UnitTask.Attacking, unit)
        return await super().execute()



class CleanUp(ActBase):
    def __init__(self):
        super().__init__()

    async def start(self, knowledge: 'Knowledge'):
        build_order = []
        if knowledge.my_race == Race.Zerg:
            build_order = [
                DistributeWorkers(),
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
                        Step(UnitReady(UnitTypeId.MUTALISK), PlanZoneAttack(10)),
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
                                            k: self._bot.zone_manager.enemy_main_zone.is_scouted_at_least_once and not self._bot.zone_manager.enemy_main_zone.is_enemys)
        return BuildOrder([
            Step(None, WorkerAttack(), skip=perform_cleanup),
            Step(None, CleanUp(), skip_until=perform_cleanup),
        ])
