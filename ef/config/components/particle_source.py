__all__ = ["ParticleSource", "ParticleSourceBoxConf", "ParticleSourceCylinderConf", "ParticleSourceTubeConf"]

from collections import namedtuple

import numpy as np

from ef.config.components.shapes import Box, Cylinder, Tube
from ef.config.section import register, NamedConfigSection
from ef.config.component import ConfigComponent


class ParticleSource(ConfigComponent):
    def __init__(self, name='ParticleSource1', shape=Box(),
                 initial_particles=500,
                 particles_to_generate_each_step=500,
                 momentum=(0, 0, 6.641e-15),
                 temperature=0.0,
                 charge=-1.799e-6,
                 mass=3.672e-24):
        self.name = name
        self.shape = shape
        self.initial_particles = initial_particles
        self.particles_to_generate_each_step = particles_to_generate_each_step
        self.momentum = np.array(momentum, np.float)
        self.temperature = temperature
        self.charge = charge
        self.mass = mass

    def visualize(self, visualizer):
        self.shape.visualize(visualizer, wireframe=True, label=self.name, colors='c', linewidths=1)

    @classmethod
    def _from_content(cls, name, shape, c):
        return cls(name, shape, c.initial_number_of_particles, c.particles_to_generate_each_step,
                   (c.mean_momentum_x, c.mean_momentum_y, c.mean_momentum_z),
                   c.temperature, c.charge, c.mass)

    def to_conf(self):
        if type(self.shape) is Box:
            r, b, n = self.shape.origin
            l, t, f = self.shape.origin + self.shape.size
            shape_args = [l, r, b, t, n, f]
            cls = ParticleSourceBoxConf
        elif type(self.shape) is Cylinder:
            shape_args = list(self.shape.start) + list(self.shape.end) + [self.shape.r]
            cls = ParticleSourceCylinderConf
        elif type(self.shape) is Tube:
            shape_args = list(self.shape.start) + list(self.shape.end) + [self.shape.r, self.shape.R]
            cls = ParticleSourceTubeConf
        else:
            raise TypeError("Shape of particle source not supported by config")
        return cls(self.name, *(shape_args + [self.initial_particles, self.particles_to_generate_each_step] +
                                list(self.momentum) + [self.temperature, self.charge, self.mass]))


@register
class ParticleSourceBoxConf(NamedConfigSection):
    section = "ParticleSourceBox"
    ContentTuple = namedtuple("ParticleSourceBoxTuple", ('box_x_left', 'box_x_right', 'box_y_bottom',
                                                         'box_y_top', 'box_z_near', 'box_z_far',
                                                         'initial_number_of_particles',
                                                         'particles_to_generate_each_step',
                                                         'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                         'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 6 + [int] * 2 + [float] * 6))

    def make(self):
        l, r, b, t, n, f = self.content[:6]
        box = Box((r, b, n), (l - r, t - b, f - n))
        return ParticleSource._from_content(self.name, box, self.content)


@register
class ParticleSourceCylinderConf(NamedConfigSection):
    section = "ParticleSourceCylinder"
    ContentTuple = namedtuple("ParticleSourceCylinderTuple", ('cylinder_axis_start_x', 'cylinder_axis_start_y',
                                                              'cylinder_axis_start_z', 'cylinder_axis_end_x',
                                                              'cylinder_axis_end_y', 'cylinder_axis_end_z',
                                                              'cylinder_radius',
                                                              'initial_number_of_particles',
                                                              'particles_to_generate_each_step',
                                                              'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                              'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 7 + [int] * 2 + [float] * 6))

    def make(self):
        cylinder = Cylinder(self.content[:3], self.content[3:6], self.content.cylinder_radius)
        return ParticleSource(self.name, cylinder, self.content)


@register
class ParticleSourceTubeConf(NamedConfigSection):
    section = "ParticleSourceTube"
    ContentTuple = namedtuple("ParticleSourceTubeTuple", ('tube_axis_start_x', 'tube_axis_start_y',
                                                          'tube_axis_start_z', 'tube_axis_end_x',
                                                          'tube_axis_end_y', 'tube_axis_end_z',
                                                          'tube_inner_radius', 'tube_outer_radius',
                                                          'initial_number_of_particles',
                                                          'particles_to_generate_each_step',
                                                          'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                          'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 8 + [int] * 2 + [float] * 6))

    def make(self):
        tube = Tube(self.content[:3], self.content[3:6], self.content.tube_inner_radius, self.content.tube_outer_radius)
        return ParticleSource(self.name, tube, self.content)
