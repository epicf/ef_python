import logging
import sys

import numpy as np

from Vec3d import Vec3d
from ef.config.components import spatial_mesh, boundary_conditions
from ef.util.data_class import DataClass


class SpatialMesh(DataClass):
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
        d['_electric_field'] = self._electric_field
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
        mesh_config = spatial_mesh.SpatialMeshConf.from_section(conf["SpatialMesh"]).make()
        boundary_config = boundary_conditions.BoundaryConditionsConf.from_section(conf["BoundaryConditions"]).make()
        return cls.do_init(mesh_config.size, mesh_config.step, boundary_config)

    @classmethod
    def init_from_h5(cls, h5group):
        size = np.array([h5group.attrs[f"{i}_volume_size"] for i in 'xyz'])
        n_nodes = np.array([h5group.attrs[f"{i}_n_nodes"] for i in 'xyz'])

        charge_density = np.reshape(h5group["./charge_density"], n_nodes)
        potential = np.reshape(h5group["./potential"], n_nodes)
        electric_field = np.stack([np.reshape(h5group[f"./electric_field_{c}"], n_nodes) for c in "xyz"], -1)
        new_obj = cls(size, n_nodes, charge_density, potential, electric_field)
        if (new_obj.cell != np.array([h5group.attrs[f"{i}_cell_size"] for i in 'xyz'])).any():
            raise ValueError("hdf5 volume_size, cell_size and n_nodes values are incompatible")
        for i, c in enumerate("xyz"):
            if (new_obj._node_coordinates[:, :, :, i].ravel(order='C') != h5group[f"./node_coordinates_{c}"]).any():
                raise ValueError(f"hdf5 node_coordinates are incorrect")
        return new_obj

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
        for c in "xyz":
            for attr in f"{c}_volume_size", f"{c}_cell_size", f"{c}_n_nodes":
                h5group.attrs.create(attr, getattr(self, attr))
        h5group.create_dataset("./potential", data=self.potential.ravel(order='C'))
        h5group.create_dataset("./charge_density", data=self.charge_density.ravel(order='C'))
        for i, c in enumerate("xyz"):
            h5group.create_dataset(f"./node_coordinates_{c}", data=self._node_coordinates[:, :, :, i].ravel(order='C'))
            h5group.create_dataset(f"./electric_field_{c}", data=self._electric_field[:, :, :, i].ravel(order='C'))

    def node_number_to_coordinate_x(self, i):
        if i >= 0 and i < self.x_n_nodes:
            return i * self.x_cell_size
        else:
            print("invalid node number i={:d} "
                  "at node_number_to_coordinate_x".format(i))
            sys.exit(-1)

    def node_number_to_coordinate_y(self, j):
        if j >= 0 and j < self.y_n_nodes:
            return j * self.y_cell_size
        else:
            print("invalid node number j={:d} "
                  "at node_number_to_coordinate_y".format(j))
            sys.exit(-1)

    def node_number_to_coordinate_z(self, k):
        if k >= 0 and k < self.z_n_nodes:
            return k * self.z_cell_size
        else:
            print("invalid node number k={:d} "
                  "at node_number_to_coordinate_z".format(k))
            sys.exit(-1)
