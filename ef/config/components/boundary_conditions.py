from collections import namedtuple

from ef.config.section import register, ConfigSection
from ef.config.component import ConfigComponent


class BoundaryConditions(ConfigComponent):

    def __init__(self, potential=0):
        self.potential = float(potential)

    def to_conf(self):
        return BoundaryConditionsConf(*[self.potential] * 6)


@register
class BoundaryConditionsConf(ConfigSection):
    section = "Boundary conditions"
    ContentTuple = namedtuple("BoundaryConditionsTuple",
                              ('boundary_phi_right', 'boundary_phi_left', 'boundary_phi_bottom',
                               'boundary_phi_top', 'boundary_phi_near', 'boundary_phi_far'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        if any(v != self.content[0] for v in self.content):
            raise ValueError("Expecting all boundary_phi to be the same.")
        return BoundaryConditions(self.content.boundary_phi_right)
