__all__ = ['SpatialMeshConf', 'SpatialMeshSection']

from collections import namedtuple

import numpy as np

import spatial_mesh
from ef.config.component import ConfigComponent
from ef.config.section import ConfigSection


class SpatialMeshConf(ConfigComponent):
    def __init__(self, size=(10, 10, 10), step=(1, 1, 1)):
        self.size = np.array(size, np.float)
        self.step = np.array(step, np.float)

    def visualize(self, visualizer):
        visualizer.draw_box(self.size, wireframe=True, label='volume', colors='k', linewidths=1)

    def to_conf(self):
        X, Y, Z = self.size
        x, y, z = self.step
        return SpatialMeshSection(X, x, Y, y, Z, z)

    def make(self, boundary_conditions):
        return spatial_mesh.SpatialMesh.do_init(self.size, self.step, boundary_conditions)


class SpatialMeshSection(ConfigSection):
    section = "SpatialMesh"
    ContentTuple = namedtuple("SpatialMeshTuple", ('grid_x_size', 'grid_x_step', 'grid_y_size',
                                                   'grid_y_step', 'grid_z_size', 'grid_z_step'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        return SpatialMeshConf(self.content[::2], self.content[1::2])
