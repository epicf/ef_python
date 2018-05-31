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
