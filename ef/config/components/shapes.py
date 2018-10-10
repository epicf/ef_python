__all__ = ['Shape', 'Box', 'Cylinder', 'Tube', 'Sphere', 'Cone']

import numpy as np

from ef.config.component import ConfigComponent


class Shape(ConfigComponent):
    pass


class Box(Shape):
    def __init__(self, origin=(0, 0, 0), size=(1, 1, 1)):
        self.origin = np.array(origin, np.float)
        self.size = np.array(size, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_box(self.size, self.origin, **kwargs)


class Cylinder(Shape):
    def __init__(self, start=(0, 0, 0), end=(1, 0, 0), radius=1):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.r = float(radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cylinder(self.start, self.end, self.r, **kwargs)


class Tube(Shape):
    def __init__(self, start=(0, 0, 0), end=(1, 0, 0), inner_radius=1, outer_radius=2):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.r = float(inner_radius)
        self.R = float(outer_radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_tube(self.start, self.end, self.r, self.R, **kwargs)


class Sphere(Shape):
    def __init__(self, origin=(0,0,0), radius=1):
        self.origin = np.array(origin)
        self.r = float(radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_sphere(self.origin, self.r, **kwargs)


class Cone(Shape):
    def __init__(self, start=(0, 0, 0, 1),
                 start_radii=(1, 2), end_radii=(3, 4)):
        self.start = np.array(start, np.float)
        self.start_radii = np.array(start_radii, np.float)
        self.end_radii = np.array(end_radii, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cone(self.start, self.end,
                             self.start_radii, self.end_radii, **kwargs)
