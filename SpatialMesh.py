import logging
import sys

import numpy as np

from Vec3d import Vec3d
from ef.config.components import spatial_mesh, boundary_conditions
from ef.util.serializable_h5 import SerializableH5


class SpatialMesh(SerializableH5):
    def __init__(self, size, n_nodes, charge_density, potential, electric_field):
        self.size = size
        self.n_nodes = n_nodes
        self.cell = size / (self.n_nodes - 1)
        self._node_coordinates = np.moveaxis(np.mgrid[0:self.x_n_nodes, 0:self.y_n_nodes, 0:self.z_n_nodes], 0, -1) \
                                 * self.cell
        self.charge_density = charge_density
        self.potential = potential
        self._electric_field = electric_field

    @property
    def node_coordinates(self):
        return self._node_coordinates

    @property
    def x_volume_size(self):
        return self.size[0]

    @property
    def y_volume_size(self):
        return self.size[1]

    @property
    def z_volume_size(self):
        return self.size[2]

    @property
    def x_n_nodes(self):
        return self.n_nodes[0]

    @property
    def y_n_nodes(self):
        return self.n_nodes[1]

    @property
    def z_n_nodes(self):
        return self.n_nodes[2]

    @property
    def shape(self):
        return self.n_nodes

    @property
    def x_cell_size(self):
        return self.cell[0]

    @property
    def y_cell_size(self):
        return self.cell[1]

    @property
    def z_cell_size(self):
        return self.cell[2]

    @property
    def electric_field(self):
        return np.apply_along_axis(lambda v: Vec3d(*v), -1, self._electric_field)

    @property
    def dict(self):
        d = super().dict
        del d["cell"]
        d['electric_field'] = self._electric_field
        return d

    @classmethod
    def do_init(cls, grid_size, step_size, boundary_conditions):
        try:
            size = np.array(grid_size, np.float)
        except ValueError as exception:
            raise ValueError("grid_size must be a flat triple", grid_size) from exception
        try:
            step = np.array(step_size, np.float)
        except ValueError as exception:
            raise ValueError("step_size must be a flat triple", step_size) from exception
        # Check argument ranges
        if size.shape != (3,):
            raise ValueError("grid_size must be a flat triple", grid_size)
        if step.shape != (3,):
            raise ValueError("step_size must be a flat triple", step_size)
        if np.any(size <= 0):
            raise ValueError("grid_size must be positive", grid_size)
        if np.any(step <= 0):
            raise ValueError("step_size must be positive", step_size)
        if np.any(step > size):
            raise ValueError("step_size cannot be bigger than grid_size")

        n_nodes = np.ceil(size / step).astype(int) + 1
        charge_density = np.zeros(n_nodes, dtype='f8')
        potential = np.zeros(n_nodes, dtype='f8')
        potential[:, 0, :] = boundary_conditions.bottom
        potential[:, -1, :] = boundary_conditions.top
        potential[0, :, :] = boundary_conditions.right
        potential[-1, :, :] = boundary_conditions.left
        potential[:, :, 0] = boundary_conditions.near
        potential[:, :, -1] = boundary_conditions.far
        electric_field = np.zeros(list(n_nodes) + [3], dtype='f8')

        self = cls(size, n_nodes, charge_density, potential, electric_field)

        for i in np.nonzero(self.cell != step_size)[0]:
            logging.warning(f"{('X', 'Y', 'Z')[i]} step on spatial grid was reduced to "
                            f"{self.cell[i]:.3f} from {step_size[i]:.3f} "
                            f"to fit in a round number of cells.")
        return self

    @classmethod
    def init_from_config(cls, conf):
        mesh_config = spatial_mesh.SpatialMeshSection._from_section(conf["SpatialMesh"]).make()
        boundary_config = boundary_conditions.BoundaryConditionsSection._from_section(conf["BoundaryConditions"]).make()
        return cls.do_init(mesh_config.size, mesh_config.step, boundary_config)

    def clear_old_density_values(self):
        self.charge_density.fill(0)

    def is_potential_equal_on_boundaries(self):
        p = self.potential[0, 0, 0]
        return np.all(self.potential[0] == p) and np.all(self.potential[-1] == p) and \
               np.all(self.potential[:, 0] == p) and np.all(self.potential[:, -1] == p) and \
               np.all(self.potential[:, :, 0] == p) and np.all(self.potential[:, :, -1] == p)

    def print(self):
        self.print_grid()
        self.print_ongrid_values()

    def print_grid(self):
        print("Grid:")
        print("Length: x = {:.3f}, y = {:.3f}, z = {:.3f}".format(
            self.x_volume_size, self.y_volume_size, self.z_volume_size))
        print("Cell size: x = {:.3f}, y = {:.3f}, z = {:.3f}".format(
            self.x_cell_size, self.y_cell_size, self.z_cell_size))
        print("Total nodes: x = {:d}, y = {:d}, z = {:d}".format(
            self.x_n_nodes, self.y_n_nodes, self.z_n_nodes))

    def print_ongrid_values(self):
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        print("x_node   y_node   z_node | "
              "charge_density | potential | electric_field(x,y,z)")
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    "{:8d} {:8d} {:8d} | "
                    "{:14.3f} | {:14.3f} | "
                    "{:14.3f} {:14.3f} {:14.3f}".format(
                        i, j, k,
                        self.charge_density[i][j][k],
                        self.potential[i][j][k],
                        self._electric_field[i][j][k][0],
                        self._electric_field[i][j][k][1],
                        self._electric_field[i][j][k][2])

    def write_to_file(self, h5file):
        groupname = "/SpatialMesh"
        h5group = h5file.create_group(groupname)
        self.save_h5(h5group)
