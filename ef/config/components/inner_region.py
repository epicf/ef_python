__all__ = ["InnerRegionConf", "InnerRegionBoxSection", "InnerRegionCylinderSection",
           "InnerRegionTubeSection", "InnerRegionSphereSection", "InnerRegionConeAlongZSection"]

from collections import namedtuple

import InnerRegion
from ef.config.component import ConfigComponent
from ef.config.components.shapes import Box, Cylinder, Tube, Sphere, Cone
from ef.config.section import NamedConfigSection


class InnerRegionConf(ConfigComponent):
    def __init__(self, name="InnerRegion1", shape=Box(), potential=0):
        self.name = name
        self.shape = shape
        self.potential = float(potential)

    def visualize(self, visualizer):
        self.shape.visualize(visualizer, facecolors=visualizer.potential_mapper.to_rgba(self.potential),
                             wireframe=False, linewidths=0)

    def to_conf(self):
        if type(self.shape) is Box:
            r, b, n = self.shape.origin
            l, t, f = self.shape.origin + self.shape.size
            shape_args = [l, r, b, t, n, f]
            cls = InnerRegionBoxSection
        elif type(self.shape) is Cylinder:
            shape_args = list(self.shape.start) + list(self.shape.end) + [self.shape.r]
            cls = InnerRegionCylinderSection
        elif type(self.shape) is Tube:
            shape_args = list(self.shape.start) + list(self.shape.end) + [self.shape.r, self.shape.R]
            cls = InnerRegionTubeSection
        elif type(self.shape) is Sphere:
            shape_args = list(self.shape.origin) + [self.shape.r]
            cls = InnerRegionSphereSection
        elif type(self.shape) is Cone:
            shape_args = list(self.shape.start) + list(self.shape.start_radii) + list(self.shape.end_radii)
            cls = InnerRegionConeAlongZSection
        else:
            raise TypeError("Config can not represent inner region shape", self.shape)
        return cls(self.name, *(shape_args + [self.potential]))

    def make(self):
        return InnerRegion.InnerRegion(self.name, self.shape, self.potential)


class InnerRegionBoxSection(NamedConfigSection):
    section = "InnerRegionBox"
    ContentTuple = namedtuple("InnerRegionBoxTuple", ('box_x_left', 'box_x_right', 'box_y_bottom',
                                                      'box_y_top', 'box_z_near', 'box_z_far',
                                                      'potential'))
    convert = ContentTuple(*[float] * 7)

    def make(self):
        l, r, b, t, n, f = self.content[:6]
        box = Box((r, b, n), (l - r, t - b, f - n))
        return InnerRegionConf(self.name, box, self.content.potential)


class InnerRegionCylinderSection(NamedConfigSection):
    section = "InnerRegionCylinder"
    ContentTuple = namedtuple("InnerRegionCylinderTuple", ('cylinder_axis_start_x', 'cylinder_axis_start_y',
                                                           'cylinder_axis_start_z', 'cylinder_axis_end_x',
                                                           'cylinder_axis_end_y', 'cylinder_axis_end_z',
                                                           'cylinder_radius', 'potential'))
    convert = ContentTuple(*[float] * 8)

    def make(self):
        cylinder = Cylinder(self.content[:3], self.content[3:6], self.content.cylinder_radius)
        return InnerRegionConf(self.name, cylinder, self.content.potential)


class InnerRegionTubeSection(NamedConfigSection):
    section = "InnerRegionTube"
    ContentTuple = namedtuple("InnerRegionTubeTuple", ('tube_axis_start_x', 'tube_axis_start_y',
                                                       'tube_axis_start_z', 'tube_axis_end_x',
                                                       'tube_axis_end_y', 'tube_axis_end_z',
                                                       'tube_inner_radius', 'tube_outer_radius',
                                                       'potential'))
    convert = ContentTuple(*[float] * 9)

    def make(self):
        tube = Tube(self.content[:3], self.content[3:6], self.content.tube_inner_radius, self.content.tube_outer_radius)
        return InnerRegionConf(self.name, tube, self.content.potential)


class InnerRegionSphereSection(NamedConfigSection):
    section = "Inner_region_sphere"
    ContentTuple = namedtuple("InnerRegionSphereTuple", ('sphere_origin_x', 'sphere_origin_y',
                                                         'sphere_origin_z', 'sphere_radius', 'potential'))
    convert = ContentTuple(*[float] * 5)

    def make(self):
        sphere = Sphere(self.content[:3], self.content.sphere_radius)
        return InnerRegionConf(self.name, sphere, self.content.potential)


class InnerRegionConeAlongZSection(NamedConfigSection):
    section = "InnerRegionConeAlongZ"
    ContentTuple = namedtuple("InnerRegionConeAlongZTuple",
                              ('cone_axis_x', 'cone_axis_y',
                               'cone_axis_start_z', 'cone_axis_end_z',
                               'cone_start_inner_radius', 'cone_start_outer_radius',
                               'cone_end_inner_radius', 'cone_end_outer_radius',
                               'potential'))
    convert = ContentTuple(*[float] * 9)

    def make(self):
        cone = Cone((self.content.cone_axis_x,
                     self.content.cone_axis_y,
                     self.content.cone_axis_start_z,
                     self.content.cone_axis_end_z),
                    (self.content.cone_start_inner_radius,
                     self.content.cone_start_outer_radius),
                    (self.content.cone_end_inner_radius,
                     self.content.cone_end_outer_radius))
        return InnerRegionConf(self.name, cone, self.content.potential)
