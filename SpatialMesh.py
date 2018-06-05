import logging
import sys

import numpy as np

from Vec3d import Vec3d
from ef.config.components import spatial_mesh, boundary_conditions
from ef.util.data_class import DataClass


class SpatialMesh(DataClass):
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
        self = cls()

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

        self.size = size
        self.n_nodes = np.ceil(size / step).astype(int) + 1
        self.cell = size / (self.n_nodes - 1)
        for i in np.nonzero(self.cell != step_size)[0]:
            logging.warning(f"{('X', 'Y', 'Z')[i]} step on spatial grid was reduced to "
                            f"{self.cell[i]:.3f} from {step_size[i]:.3f} "
                            f"to fit in a round number of cells.")

        self.allocate_ongrid_values()
        self.fill_node_coordinates()
        self.potential[:, 0, :] = boundary_conditions.bottom
        self.potential[:, -1, :] = boundary_conditions.top
        self.potential[0, :, :] = boundary_conditions.right
        self.potential[-1, :, :] = boundary_conditions.left
        self.potential[:, :, 0] = boundary_conditions.near
        self.potential[:, :, -1] = boundary_conditions.far
        return self

    @classmethod
    def init_from_config(cls, conf):
        mesh_config = spatial_mesh.SpatialMeshConf.from_section(conf["SpatialMesh"]).make()
        boundary_config = boundary_conditions.BoundaryConditionsConf.from_section(conf["BoundaryConditions"]).make()
        return cls.do_init(mesh_config.size, mesh_config.step, boundary_config)

    @classmethod
    def init_from_h5(cls, h5group):
        new_obj = cls()
        new_obj.size = np.array([h5group.attrs[f"{i}_volume_size"] for i in 'xyz'])
        new_obj.n_nodes = np.array([h5group.attrs[f"{i}_n_nodes"] for i in 'xyz'])
        new_obj.cell = np.array([h5group.attrs[f"{i}_cell_size"] for i in 'xyz'])
        #
        # todo: don't allocate. read into flat arrays. then reshape
        new_obj.allocate_ongrid_values()
        new_obj.fill_node_coordinates()

        if (new_obj._node_coordinates[:, :, :, 0].ravel(order='C') != h5group[f"./node_coordinates_x"]).any():
            raise ValueError("Node coordinates read from hdf5 are incorrect")
        if (new_obj._node_coordinates[:, :, :, 1].ravel(order='C') != h5group[f"./node_coordinates_y"]).any():
            raise ValueError("Node coordinates read from hdf5 are incorrect")
        if (new_obj._node_coordinates[:, :, :, 2].ravel(order='C') != h5group[f"./node_coordinates_z"]).any():
            raise ValueError("Node coordinates read from hdf5 are incorrect")

        tmp_rho = h5group["./charge_density"]
        tmp_phi = h5group["./potential"]
        for global_idx, (rho, phi) in enumerate(zip(tmp_rho, tmp_phi)):
            i, j, k = new_obj.global_idx_to_node_ijk(global_idx)
            new_obj.charge_density[i][j][k] = rho
            new_obj.potential[i][j][k] = phi
        #
        tmp_x = h5group["./electric_field_x"]
        tmp_y = h5group["./electric_field_y"]
        tmp_z = h5group["./electric_field_z"]
        for global_idx, (vx, vy, vz) in enumerate(zip(tmp_x, tmp_y, tmp_z)):
            i, j, k = new_obj.global_idx_to_node_ijk(global_idx)
            new_obj._electric_field[i][j][k][0] = vx
            new_obj._electric_field[i][j][k][1] = vy
            new_obj._electric_field[i][j][k][2] = vz
        #
        return new_obj

    def allocate_ongrid_values(self):
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        self._node_coordinates = np.empty((nx, ny, nz, 3), dtype='f8')
        self.charge_density = np.zeros((nx, ny, nz), dtype='f8')
        self.potential = np.zeros((nx, ny, nz), dtype='f8')
        self._electric_field = np.zeros((nx, ny, nz, 3), dtype='f8')

    def fill_node_coordinates(self):
        self._node_coordinates = np.moveaxis(np.mgrid[0:self.x_n_nodes, 0:self.y_n_nodes, 0:self.z_n_nodes], 0, -1) \
                                 * self.cell

    def clear_old_density_values(self):
        self.charge_density.fill(0)

    def is_potential_equal_on_boundaries(self):
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        return \
            (self.potential[0][2][2] == self.potential[nx - 1][2][2] == \
             self.potential[2][0][2] == self.potential[2][ny - 1][2] == \
             self.potential[2][2][0] == self.potential[2][2][nz - 1])

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
        self.write_hdf5_attributes(h5group)
        self.write_hdf5_ongrid_values(h5group)

    def write_hdf5_attributes(self, h5group):
        h5group.attrs.create("x_volume_size", self.x_volume_size)
        h5group.attrs.create("y_volume_size", self.y_volume_size)
        h5group.attrs.create("z_volume_size", self.z_volume_size)
        h5group.attrs.create("x_cell_size", self.x_cell_size)
        h5group.attrs.create("y_cell_size", self.y_cell_size)
        h5group.attrs.create("z_cell_size", self.z_cell_size)
        h5group.attrs.create("x_n_nodes", self.x_n_nodes)
        h5group.attrs.create("y_n_nodes", self.y_n_nodes)
        h5group.attrs.create("z_n_nodes", self.z_n_nodes)

    def write_hdf5_ongrid_values(self, h5group):
        h5group.create_dataset("./node_coordinates_x", data=self._node_coordinates[:, :, :, 0].ravel(order='C'))
        h5group.create_dataset("./node_coordinates_y", data=self._node_coordinates[:, :, :, 1].ravel(order='C'))
        h5group.create_dataset("./node_coordinates_z", data=self._node_coordinates[:, :, :, 2].ravel(order='C'))
        h5group.create_dataset("./potential", data=self.potential.ravel(order='C'))
        h5group.create_dataset("./charge_density", data=self.charge_density.ravel(order='C'))
        h5group.create_dataset("./electric_field_x", data=self._electric_field[:, :, :, 0].ravel(order='C'))
        h5group.create_dataset("./electric_field_y", data=self._electric_field[:, :, :, 1].ravel(order='C'))
        h5group.create_dataset("./electric_field_z", data=self._electric_field[:, :, :, 2].ravel(order='C'))

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

    def global_idx_to_node_ijk(self, global_idx):
        # In row-major order: (used to save on disk)
        # global_index = i * nz * ny +
        #                j * nz +
        #                k
        #
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        i = global_idx // (nz * ny)
        j_and_k_part = global_idx % (nz * ny)
        j = j_and_k_part // nz
        k = j_and_k_part % nz
        return (i, j, k)
