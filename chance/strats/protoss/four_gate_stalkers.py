from chance.strats.strat import Strat
from sc2.constants import *
from sharpy.knowledges import Knowledge
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import ActUnit, GridBuilding, Tech, MineOpenBlockedBase
from sharpy.plans.acts.protoss import AutoPylon, RestorePower, ChronoUnit, ProtossUnit
from sharpy.plans.require import UnitReady
from sharpy.plans.tactics import PlanZoneAttack, PlanZoneDefense, PlanZoneGather, PlanFinishEnemy, DistributeWorkers, \
    SpeedMining


class TheAttack(PlanZoneAttack):

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)


class FourGateStalkers(Strat):
    """
    Adapted from https://lotv.spawningtool.com/build/62827/
    """

    async def create_plan(self) -> BuildOrder:
        attack = TheAttack(4)
        return BuildOrder([
            Step(None, ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY)),
            SequentialList([
                GridBuilding(UnitTypeId.PYLON, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 15),
                GridBuilding(UnitTypeId.GATEWAY, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 16),
                StepBuildGas(1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 19),
                StepBuildGas(2),
                GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 21),
                GridBuilding(UnitTypeId.PYLON, 2),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 22),
                ProtossUnit(UnitTypeId.STALKER, 1),
                Tech(UpgradeId.WARPGATERESEARCH, UnitTypeId.CYBERNETICSCORE),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 23),
                GridBuilding(UnitTypeId.GATEWAY, 4),
                GridBuilding(UnitTypeId.PYLON, 3),
                BuildOrder(
                    [
                        AutoPylon(),
                        ProtossUnit(UnitTypeId.STALKER, 100)
                    ])
            ]),
            SequentialList(
                [
                    MineOpenBlockedBase(),
                    PlanZoneDefense(),
                    RestorePower(),
                    DistributeWorkers(),
                    Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                    PlanZoneGather(),
                    Step(UnitReady(UnitTypeId.GATEWAY, 4), attack),
                    PlanFinishEnemy(),
                ])
        ])
