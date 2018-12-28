import math

import numpy as np

from ExternalField import ExternalField
from simpleeval import SimpleEval


class ExternalFieldExpression(ExternalField):

    def __init__(self, name, electric_or_magnetic, expression_x, expression_y, expression_z):
        super().__init__(name, electric_or_magnetic)
        self.expression_x = expression_x
        self.expression_y = expression_y
        self.expression_z = expression_z
        self._ev = SimpleEval(functions={"sin": math.sin,
                                         "cos": math.cos,
                                         "sqrt": math.sqrt})
        # todo: inherit SimpleEval and define math functions inside
        # todo: add r, theta, phi names

    def _field_at_position(self, pos):
        self._ev.names["x"] = pos[0]
        self._ev.names["y"] = pos[1]
        self._ev.names["z"] = pos[2]
        fx = self._ev.eval(self.expression_x)
        fy = self._ev.eval(self.expression_y)
        fz = self._ev.eval(self.expression_z)
        return fx, fy, fz

    def get_at_points(self, positions, time):
        positions = np.asarray(positions)
        self._ev.names["t"] = time
        if positions.shape == (3,):
            return np.array(self._field_at_position(positions))
        else:
            return np.array([self._field_at_position(pos) for pos in positions])
