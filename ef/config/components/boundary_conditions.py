__all__ = ["BoundaryConditions", "BoundaryConditionsConf"]

from collections import namedtuple

import numpy as np

from ef.config.section import register, ConfigSection
from ef.config.component import ConfigComponent


class BoundaryConditions(ConfigComponent):
    def __init__(self, potential=0):
        self.potential = float(potential)

    def to_conf(self):
        return BoundaryConditionsConf(*[self.potential] * 6)

    def visualize(self, visualizer, volume_size=(1, 1, 1)):
        visualizer.draw_box(np.array(volume_size, np.float), wireframe=True,
                            colors=visualizer.potential_mapper.to_rgba(self.potential))


@register
class BoundaryConditionsConf(ConfigSection):
    section = "BoundaryConditions"
    ContentTuple = namedtuple("BoundaryConditionsTuple",
                              ('boundary_phi_right', 'boundary_phi_left', 'boundary_phi_bottom',
                               'boundary_phi_top', 'boundary_phi_near', 'boundary_phi_far'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        if any(v != self.content[0] for v in self.content):
            raise ValueError("Expecting all boundary_phi to be the same.")
        return BoundaryConditions(self.content.boundary_phi_right)
