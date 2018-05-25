from collections import namedtuple

from ef.config.parser import register, ConfigComponent, DataClass


class BoundaryConditions(DataClass):

    def __init__(self, potential=0):
        self.potential = float(potential)

    def to_conf(self):
        return BoundaryConditionsConf(*[self.potential] * 6)


@register
class BoundaryConditionsConf(ConfigComponent):
    section = "Boundary conditions"
    ContentTuple = namedtuple("BoundaryConditionsTuple",
                              ('boundary_phi_right', 'boundary_phi_left', 'boundary_phi_bottom',
                               'boundary_phi_top', 'boundary_phi_near', 'boundary_phi_far'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        if any(v != self.content[0] for v in self.content):
            raise ValueError("Expecting all boundary_phi to be the same.")
        return BoundaryConditions(self.content.boundary_phi_right)
