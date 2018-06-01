import logging
import sys

import numpy as np

from Vec3d import Vec3d
from ef.config.components import spatial_mesh, boundary_conditions


class SpatialMesh:
    def __init__(self):
        self.x_volume_size = None
        self.y_volume_size = None
        self.z_volume_size = None
        self.x_cell_size = None
        self.y_cell_size = None
        self.z_cell_size = None
        self.x_n_nodes = None
        self.y_n_nodes = None
        self.z_n_nodes = None
        self.node_coordinates = None
        self.charge_density = None
        self.potential = None
        self.electric_field = None

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

        self.x_volume_size, self.y_volume_size, self.z_volume_size = size
        n_nodes = np.ceil(size / step).astype(int) + 1
        self.x_n_nodes, self.y_n_nodes, self.z_n_nodes = n_nodes
        cell = size / (n_nodes - 1)
        nz = np.nonzero(cell != step_size)[0]
        for i in nz:
            logging.warning(f"{('X', 'Y', 'Z')[i]} step on spatial grid was reduced to "
                            f"{cell[i]:.3f} from {step_size[i]:.3f} "
                            f"to fit in a round number of cells.")

        self.x_cell_size, self.y_cell_size, self.z_cell_size = cell
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
        new_obj.x_volume_size = h5group.attrs["x_volume_size"]
        new_obj.y_volume_size = h5group.attrs["y_volume_size"]
        new_obj.z_volume_size = h5group.attrs["z_volume_size"]
        new_obj.x_cell_size = h5group.attrs["x_cell_size"]
        new_obj.y_cell_size = h5group.attrs["y_cell_size"]
        new_obj.z_cell_size = h5group.attrs["z_cell_size"]
        new_obj.x_n_nodes = h5group.attrs["x_n_nodes"]
        new_obj.y_n_nodes = h5group.attrs["y_n_nodes"]
        new_obj.z_n_nodes = h5group.attrs["z_n_nodes"]
        #
        # todo: don't allocate. read into flat arrays. then reshape
        new_obj.allocate_ongrid_values()
        #
        dim = new_obj.node_coordinates.size
        tmp_x = np.empty(dim, dtype='f8')
        tmp_y = np.empty_like(tmp_x)
        tmp_z = np.empty_like(tmp_x)
        #
        tmp_x = h5group["./node_coordinates_x"]
        tmp_y = h5group["./node_coordinates_y"]
        tmp_z = h5group["./node_coordinates_z"]
        for global_idx, (vx, vy, vz) in enumerate(zip(tmp_x, tmp_y, tmp_z)):
            # todo: highly nonoptimal; make view or reshape?
            i, j, k = new_obj.global_idx_to_node_ijk(global_idx)
            new_obj.node_coordinates[i][j][k] = Vec3d(vx, vy, vz)
        #
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
            new_obj.electric_field[i][j][k] = Vec3d(vx, vy, vz)
        #
        return new_obj

    def allocate_ongrid_values(self):
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        self.node_coordinates = np.empty((nx, ny, nz), dtype=object)
        self.charge_density = np.zeros((nx, ny, nz), dtype='f8')
        self.potential = np.zeros((nx, ny, nz), dtype='f8')
        self.electric_field = np.full((nx, ny, nz), Vec3d.zero(), dtype=object)

    def fill_node_coordinates(self):
        for i in range(self.x_n_nodes):
            for j in range(self.y_n_nodes):
                for k in range(self.z_n_nodes):
                    self.node_coordinates[i][j][k] = Vec3d(
                        i * self.x_cell_size, j * self.y_cell_size, k * self.z_cell_size)

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
                        self.electric_field[i][j][k].x,
                        self.electric_field[i][j][k].y,
                        self.electric_field[i][j][k].z)

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
        # todo: without compound datasets
        # there is this copying problem.
        dim = self.node_coordinates.size
        tmp_x = np.empty(dim, dtype='f8')
        tmp_y = np.empty_like(tmp_x)
        tmp_z = np.empty_like(tmp_x)
        # todo: make view instead of copy
        flat_node_coords = self.node_coordinates.ravel(order='C')
        for i, v in enumerate(flat_node_coords):
            tmp_x[i] = v.x
            tmp_y[i] = v.y
            tmp_z[i] = v.z
        h5group.create_dataset("./node_coordinates_x", data=tmp_x)
        h5group.create_dataset("./node_coordinates_y", data=tmp_y)
        h5group.create_dataset("./node_coordinates_z", data=tmp_z)
        # C (C-order): index along the first axis varies slowest
        # in self.node_coordinates.flat above default order is C
        flat_phi = self.potential.ravel(order='C')
        h5group.create_dataset("./potential", data=flat_phi)
        flat_rho = self.charge_density.ravel(order='C')
        h5group.create_dataset("./charge_density", data=flat_rho)
        #
        flat_field = self.electric_field.ravel(order='C')
        for i, v in enumerate(flat_field):
            tmp_x[i] = v.x
            tmp_y[i] = v.y
            tmp_z[i] = v.z
        h5group.create_dataset("./electric_field_x", data=tmp_x)
        h5group.create_dataset("./electric_field_y", data=tmp_y)
        h5group.create_dataset("./electric_field_z", data=tmp_z)

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
