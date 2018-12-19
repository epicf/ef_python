import math

from ExternalField import ExternalField
from Vec3d import Vec3d
from libs.simpleeval.simpleeval import SimpleEval


class ExternalFieldExpression(ExternalField):

    def __init__(self, name, electric_or_magnetic, expression_x, expression_y, expression_z):
        super().__init__(name, electric_or_magnetic)
        self.expression_x = expression_x
        self.expression_y = expression_y
        self.expression_z = expression_z

    def field_at_particle_position(self, particle, current_time):
        ev = SimpleEval(names={"x": particle.position.x,
                               "y": particle.position.y,
                               "z": particle.position.z,
                               "t": current_time},
                        functions={"sin": math.sin,
                                   "cos": math.cos,
                                   "sqrt": math.sqrt})
        # todo: inherit SimpleEval and define math functions inside
        # todo: add r, theta, phi names
        fx = ev.eval(self.expression_x)
        fy = ev.eval(self.expression_y)
        fz = ev.eval(self.expression_z)
        return Vec3d(fx, fy, fz)
