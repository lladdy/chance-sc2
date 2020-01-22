from chance.strats.strat import Strat
from sc2.constants import *
from sharpy.knowledges import Knowledge, KnowledgeBot
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import ActUnit, GridBuilding, ActExpand, ActTech
from sharpy.plans.acts.protoss import ChronoUnitProduction, GateUnit, AutoPylon, RestorePower
from sharpy.plans.require import RequiredUnitExists, RequiredGas, RequiredUnitReady
from sharpy.plans.tactics import PlanZoneAttack, PlanZoneDefense, PlanDistributeWorkers, PlanZoneGather, PlanFinishEnemy


class TheAttack(PlanZoneAttack):

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)


class FourGateStalkers(Strat):
    """
    Adapted from https://lotv.spawningtool.com/build/62827/
    """

    def __init__(self, bot: KnowledgeBot):
        super().__init__(bot)

    async def create_plan(self) -> BuildOrder:
        attack = TheAttack(4)
        return BuildOrder([
            Step(None, ChronoUnitProduction(UnitTypeId.STALKER, UnitTypeId.GATEWAY)),
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
                GateUnit(UnitTypeId.STALKER, 1),
                ActTech(UpgradeId.WARPGATERESEARCH, UnitTypeId.CYBERNETICSCORE),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 23),
                GridBuilding(UnitTypeId.GATEWAY, 4),
                GridBuilding(UnitTypeId.PYLON, 3),
                BuildOrder(
                    [
                        AutoPylon(),
                        GateUnit(UnitTypeId.STALKER, 100)
                    ])
            ]),
            SequentialList(
                [
                    PlanZoneDefense(),
                    RestorePower(),
                    PlanDistributeWorkers(),
                    PlanZoneGather(),
                    Step(RequiredUnitReady(UnitTypeId.GATEWAY, 4), attack),
                    PlanFinishEnemy(),
                ])
        ])
