from chance.strats import Strat
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.plans import BuildOrder, Step, SequentialList, StepBuildGas
from sharpy.plans.acts import *
from sharpy.plans.acts.protoss import *
from sharpy.plans.require import *
from sharpy.plans.tactics import *


class MacroVoidray(Strat):

    async def create_plan(self) -> BuildOrder:
        return BuildOrder(
            Step(
                None,
                ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS),
                skip=UnitExists(UnitTypeId.PROBE, 30, include_pending=True),
                skip_until=UnitExists(UnitTypeId.ASSIMILATOR, 1),
            ),
            ChronoUnit(UnitTypeId.VOIDRAY, UnitTypeId.STARGATE),
            SequentialList(
                ProtossUnit(UnitTypeId.PROBE, 14),
                GridBuilding(UnitTypeId.PYLON, 1),
                ProtossUnit(UnitTypeId.PROBE, 16),
                BuildGas(1),
                GridBuilding(UnitTypeId.GATEWAY, 1),
                ProtossUnit(UnitTypeId.PROBE, 20),
                GridBuilding(UnitTypeId.CYBERNETICSCORE, 1),
                ProtossUnit(UnitTypeId.PROBE, 21),
                Expand(2),
                ProtossUnit(UnitTypeId.PROBE, 22),
                BuildGas(2),
                GridBuilding(UnitTypeId.PYLON, 1),
                BuildOrder(
                    AutoPylon(),
                    ProtossUnit(UnitTypeId.STALKER, 2, priority=True),
                    Tech(UpgradeId.WARPGATERESEARCH),
                    [
                        ProtossUnit(UnitTypeId.PROBE, 22),
                        Step(UnitExists(UnitTypeId.NEXUS, 2), ProtossUnit(UnitTypeId.PROBE, 44)),
                        StepBuildGas(3, skip=Gas(300)),
                        Step(UnitExists(UnitTypeId.NEXUS, 3), ProtossUnit(UnitTypeId.PROBE, 56)),
                        StepBuildGas(5, skip=Gas(200)),
                    ],
                    SequentialList(
                        [
                            Step(
                                UnitReady(UnitTypeId.CYBERNETICSCORE, 1), GridBuilding(UnitTypeId.TWILIGHTCOUNCIL, 1),
                            ),
                            GridBuilding(UnitTypeId.STARGATE, 1),
                            Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL, 1), Tech(UpgradeId.CHARGE)),
                            Step(UnitReady(UnitTypeId.TWILIGHTCOUNCIL, 1), Tech(UpgradeId.ADEPTPIERCINGATTACK)),
                        ]
                    ),
                    [ProtossUnit(UnitTypeId.VOIDRAY, 20, priority=True)],
                    Step(Time(60 * 5), Expand(3)),
                    [
                        ProtossUnit(UnitTypeId.ZEALOT, 6),
                        ProtossUnit(UnitTypeId.ADEPT, 10),
                        ProtossUnit(UnitTypeId.ZEALOT, 15),
                        ProtossUnit(UnitTypeId.ADEPT, 20),
                        ProtossUnit(UnitTypeId.ZEALOT, 23),
                        ProtossUnit(UnitTypeId.ADEPT, 30),
                    ],
                    [
                        GridBuilding(UnitTypeId.GATEWAY, 4),
                        StepBuildGas(4, skip=Gas(200)),
                        GridBuilding(UnitTypeId.STARGATE, 2),
                    ],
                ),
            ),
            SequentialList(
                MineOpenBlockedBase(),
                PlanZoneDefense(),
                RestorePower(),
                DistributeWorkers(),
                Step(None, SpeedMining(), lambda ai: ai.client.game_step > 5),
                PlanZoneGather(),
                Step(UnitReady(UnitTypeId.VOIDRAY, 3), PlanZoneAttack(4)),
                PlanFinishEnemy(),
            ),
        )
