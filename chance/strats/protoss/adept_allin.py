import random

from chance.strats.strat import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.general.extended_power import ExtendedPower
from sharpy.knowledges import Knowledge
from sharpy.plans import BuildOrder, Step, SequentialList
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *
from sharpy.plans.tactics.protoss import *


class TheAttack(PlanZoneAttack):
    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)
        # self.combat.move_formation = Formation.Nothing
        # self.combat.offensive_stutter_step = False

    def _should_attack(self, power: ExtendedPower) -> bool:
        return len(self.cache.own(UnitTypeId.ADEPT)) > 10


class AdeptAllIn(Strat):
    async def create_plan(self) -> BuildOrder:
        number = random.randint(10, 15)
        attack = TheAttack(number + 1)
        return BuildOrder(
            Step(
                None,
                ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS),
                skip=UnitExists(UnitTypeId.PROBE, 20, include_pending=True),
                skip_until=UnitExists(UnitTypeId.ASSIMILATOR, 1),
            ),
            SequentialList(
                GridBuilding(UnitTypeId.PYLON, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 14),
                GridBuilding(UnitTypeId.GATEWAY, 1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 16),
                BuildGas(1),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 17),
                GridBuilding(UnitTypeId.GATEWAY, 2),
                ActUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 20),
                ArtosisPylon(2),
                BuildOrder(
                    AutoPylon(),
                    SequentialList(
                        Step(
                            None,
                            GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                            skip_until=UnitReady(UnitTypeId.GATEWAY, 1),
                        ),
                        Step(
                            UnitReady(UnitTypeId.CYBERNETICSCORE, 1), ProtossUnit(UnitTypeId.ADEPT, 2, only_once=True),
                        ),
                        Tech(UpgradeId.WARPGATERESEARCH),
                        ProtossUnit(UnitTypeId.ADEPT, 100),
                    ),
                    Step(
                        UnitExists(UnitTypeId.CYBERNETICSCORE, 1),
                        GridBuilding(UnitTypeId.GATEWAY, 4),
                        skip_until=Minerals(200),
                    ),
                    Step(None, ProtossUnit(UnitTypeId.ZEALOT, 100), skip=Gas(25), skip_until=Minerals(200), ),
                ),
            ),
            SequentialList(
                MineOpenBlockedBase(),
                ChronoAnyTech(0),
                PlanZoneDefense(),
                RestorePower(),
                DistributeWorkers(),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                PlanZoneGather(),
                DoubleAdeptScout(number),
                attack,
                PlanFinishEnemy(),
            ),
        )
