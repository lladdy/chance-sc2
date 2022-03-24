from sc2.position import Point2
from sharpy.managers.core import BuildingSolver
from sharpy.managers.core.building_solver import is_empty, is_free, fill_padding
from sharpy.managers.core.grids import Rectangle, BlockerType, BuildArea


class ProxySolver(BuildingSolver):
    def massive_grid(self, pos):
        rect = Rectangle(pos.x, pos.y, 6, 9)
        unit_exit_rect = Rectangle(pos.x - 2, pos.y + 4, 2, 2)
        unit_exit_rect2 = Rectangle(pos.x + 6, pos.y + 4, 2, 2)
        padding = Rectangle(pos.x - 2, pos.y - 2, 10, 12)

        if (
            self.grid.query_rect(rect, is_empty)
            and self.grid.query_rect(unit_exit_rect, is_free)
            and self.grid.query_rect(unit_exit_rect2, is_free)
        ):
            pylons = [
                pos + Point2((1 + 2, 1)),
            ]
            gates = [
                pos + Point2((1.5, 3.5)),
                pos + Point2((4.5, 3.5)),
                pos + Point2((1.5, 6.5)),
                pos + Point2((4.5, 6.5)),
            ]
            for pylon_pos in pylons:
                self.fill_and_save(pylon_pos, BlockerType.Building2x2, BuildArea.Pylon)

            for gate_pos in gates:
                self.fill_and_save(gate_pos, BlockerType.Building3x3, BuildArea.Building)

            self.grid.fill_rect(padding, fill_padding)
