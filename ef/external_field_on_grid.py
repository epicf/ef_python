import os.path

import numpy as np

from ef.external_field import ExternalField
from ef.spatial_mesh import MeshGrid


class ExternalFieldOnGrid(ExternalField):

    def __init__(self, name, electric_or_magnetic, field_filename):
        super().__init__(name, electric_or_magnetic)
        self.field_filename = field_filename
        if not os.path.exists(field_filename):
            raise FileNotFoundError("Field file not found")
        self.field = None
        mesh = np.loadtxt(self.field_filename)
        # assume X Y Z Fx Fy Fz columns
        # sort by column 0, then 1, then 2
        # https://stackoverflow.com/a/38194077
        ind = mesh[:, 2].argsort()  # First sort doesn't need to be stable.
        mesh = mesh[ind]
        ind = mesh[:, 1].argsort(kind='mergesort')
        mesh = mesh[ind]
        ind = mesh[:, 0].argsort(kind='mergesort')
        mesh = mesh[ind]
        size = (mesh[-1, :3] - mesh[0, :3])
        origin = mesh[0, :3]
        dist = mesh[:, :3] - mesh[0, :3]
        step = np.min(dist[dist > 0], axis=0)
        self.grid = MeshGrid.from_step(size, step, origin)
        self.field = mesh[:, 3:].reshape((*self.grid.n_nodes, 3))

    def get_at_points(self, positions, time):
        return self.grid.interpolate_field_at_positions(self.field, positions)
