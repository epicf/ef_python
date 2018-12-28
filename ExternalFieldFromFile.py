import os.path
from math import ceil

import numpy as np

from ExternalField import ExternalField


class ExternalFieldFromFile(ExternalField):

    def __init__(self, name, electric_or_magnetic, field_filename):
        super().__init__(name, electric_or_magnetic)
        self.field_filename = field_filename
        if not os.path.exists(field_filename):
            raise FileNotFoundError("Field file not found")
        self.field_from_file = None
        self.x_start = None
        self.y_start = None
        self.z_start = None
        self.x_end = None
        self.y_end = None
        self.z_end = None
        self.x_volume_size = None
        self.y_volume_size = None
        self.z_volume_size = None
        self.x_cell_size = None
        self.y_cell_size = None
        self.z_cell_size = None
        self.x_n_nodes = None
        self.y_n_nodes = None
        self.z_n_nodes = None
        self.read_field_from_file()

    def read_field_from_file(self):
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
        #
        self.determine_volume_sizes(mesh)
        self.determine_cell_sizes(mesh)
        self.determine_n_nodes(mesh)
        self.determine_start_end_grid_points(mesh)
        #
        self.field_from_file = np.zeros((self.x_n_nodes, self.y_n_nodes, self.z_n_nodes, 3))

        for global_idx, (Fx, Fy, Fz) in enumerate(zip(mesh[:, 3], mesh[:, 4], mesh[:, 5])):
            i, j, k = self.global_idx_to_node_ijk(global_idx)
            self.field_from_file[i][j][k] = (Fx, Fy, Fz)

    def determine_volume_sizes(self, mesh):
        self.x_volume_size = mesh[-1, 0] - mesh[0, 0]
        self.y_volume_size = mesh[-1, 1] - mesh[0, 1]
        self.z_volume_size = mesh[-1, 2] - mesh[0, 2]

    def determine_cell_sizes(self, mesh):
        self.x_cell_size = 0.0
        self.y_cell_size = 0.0
        self.z_cell_size = 0.0
        x0 = mesh[0, 0]
        for x in mesh[:, 0]:
            if x0 != x:
                self.x_cell_size = x - x0
                break
        y0 = mesh[0, 1]
        for y in mesh[:, 1]:
            if y0 != y:
                self.y_cell_size = y - y0
                break
        z0 = mesh[0, 2]
        for z in mesh[:, 2]:
            if z0 != z:
                self.z_cell_size = z - z0
                break

    def determine_n_nodes(self, mesh):
        self.x_n_nodes = int(round(self.x_volume_size / self.x_cell_size)) + 1
        self.y_n_nodes = int(round(self.y_volume_size / self.y_cell_size)) + 1
        self.z_n_nodes = int(round(self.z_volume_size / self.z_cell_size)) + 1

    def determine_start_end_grid_points(self, mesh):
        self.x_start = mesh[0, 0]
        self.y_start = mesh[0, 1]
        self.z_start = mesh[0, 2]
        self.x_end = mesh[-1, 0]
        self.y_end = mesh[-1, 1]
        self.z_end = mesh[-1, 2]

    def global_idx_to_node_ijk(self, global_idx):
        # In row-major order:
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

    def inside_mesh(self, point):
        x, y, z = point
        inside = (x >= self.x_start) and (x <= self.x_end) \
                 and \
                 (y >= self.y_start) and (y <= self.y_end) \
                 and \
                 (z >= self.z_start) and (z <= self.z_end)
        return inside

    def get_at_points(self, positions, time):
        if self.inside_mesh(positions):
            field = self.field_from_grid(positions)
        else:
            field = np.zeros(3)
        return field

    # todo: refactor
    def field_from_grid(self, position):
        dx = self.x_cell_size
        dy = self.y_cell_size
        dz = self.z_cell_size
        # 'tlf' = 'top_left_far'
        tlf_i, tlf_x_weight = self.next_node_num_and_weight(
            position[0], dx, self.x_start)
        tlf_j, tlf_y_weight = self.next_node_num_and_weight(
            position[1], dy, self.y_start)
        tlf_k, tlf_z_weight = self.next_node_num_and_weight(
            position[2], dz, self.z_start)
        # tlf
        total_field = np.zeros(3)
        field_from_node = self.field_from_file[tlf_i][tlf_j][tlf_k] * tlf_x_weight
        field_from_node *= tlf_y_weight
        field_from_node *= tlf_z_weight
        total_field += field_from_node
        # trf
        field_from_node = self.field_from_file[tlf_i - 1][tlf_j][tlf_k] * (1.0 - tlf_x_weight)
        field_from_node *= tlf_y_weight
        field_from_node *= tlf_z_weight
        total_field += field_from_node
        # blf
        field_from_node = self.field_from_file[tlf_i][tlf_j - 1][tlf_k] * tlf_x_weight
        field_from_node *= (1.0 - tlf_y_weight)
        field_from_node *= tlf_z_weight
        total_field += field_from_node
        # brf
        field_from_node = self.field_from_file[tlf_i - 1][tlf_j - 1][tlf_k] * (1.0 - tlf_x_weight)
        field_from_node *= (1.0 - tlf_y_weight)
        field_from_node *= tlf_z_weight
        total_field += field_from_node
        # tln
        field_from_node = self.field_from_file[tlf_i][tlf_j][tlf_k - 1] * tlf_x_weight
        field_from_node *= tlf_y_weight
        field_from_node *= (1.0 - tlf_z_weight)
        total_field += field_from_node
        # trn
        field_from_node = self.field_from_file[tlf_i - 1][tlf_j][tlf_k - 1] * (1.0 - tlf_x_weight)
        field_from_node *= tlf_y_weight
        field_from_node *= (1.0 - tlf_z_weight)
        total_field += field_from_node
        # bln
        field_from_node = self.field_from_file[tlf_i][tlf_j - 1][tlf_k - 1] * tlf_x_weight
        field_from_node *= (1.0 - tlf_y_weight)
        field_from_node *= (1.0 - tlf_z_weight)
        total_field += field_from_node
        # brn
        field_from_node = self.field_from_file[tlf_i - 1][tlf_j - 1][tlf_k - 1] * (1.0 - tlf_x_weight)
        field_from_node *= (1.0 - tlf_y_weight)
        field_from_node *= (1.0 - tlf_z_weight)
        total_field += field_from_node
        #
        return total_field

    @staticmethod
    def next_node_num_and_weight(x, grid_step, x_start):
        # todo: take initial grid position into account
        x_in_grid_units = (x - x_start) / grid_step
        next_node = ceil(x_in_grid_units)
        weight = 1.0 - (next_node - x_in_grid_units)
        return (next_node, weight)
