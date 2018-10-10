import os.path
import numpy as np
from math import ceil


from Vec3d import Vec3d
from ExternalField import ExternalField


class ExternalFieldFromFile(ExternalField):

    def __init__(self):
        super().__init__()
        self.field_filename = None
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


    @classmethod
    def init_from_config(cls, field_conf, field_conf_name):
        new_obj = cls()
        new_obj.init_common_parameters_from_config(field_conf, field_conf_name)
        new_obj.field_type = "from_file"
        new_obj.check_correctness_of_related_config_fields(field_conf)
        new_obj.get_values_from_config(field_conf)
        new_obj.read_field_from_file()
        return new_obj


    def check_correctness_of_related_config_fields(self, field_conf):
        if not os.path.exists(field_conf["field_filename"]):
            raise FileNotFoundError("Field file not found")


    def get_values_from_config(self, field_conf):
        self.field_filename = field_conf["field_filename"]


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
        self.field_from_file = np.full((self.x_n_nodes, self.y_n_nodes, self.z_n_nodes),
                                       Vec3d.zero(), dtype=object)
        for global_idx, (Fx, Fy, Fz) in enumerate(zip(mesh[:, 3], mesh[:, 4], mesh[:, 5])):
            i, j, k = self.global_idx_to_node_ijk(global_idx)
            self.field_from_file[i][j][k] = Vec3d(Fx, Fy, Fz)


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
        x = point.x
        y = point.y
        z = point.z
        inside = (x >= self.x_start) and (x <= self.x_end) \
                 and \
                 (y >= self.y_start) and (y <= self.y_end) \
                 and \
                 (z >= self.z_start) and (z <= self.z_end)
        return inside


    @classmethod
    def init_from_h5(cls, h5_field_group):
        new_obj = cls()
        new_obj.init_common_parameters_from_h5(h5_field_group)
        new_obj.field_type = "from_file"
        new_obj.field_filename = h5_field_group.attrs["field_filename"]
        if not os.path.exists(new_obj.field_filename):
            raise FileNotFoundError("Field file not found")
        new_obj.read_field_from_file()
        return new_obj


    def field_at_particle_position(self, particle, current_time):
        if self.inside_mesh(particle.position):
            field = self.field_from_grid(particle)
        else:
            field = Vec3d.zero()
        return field


    # todo: refactor
    def field_from_grid(self, particle):
        dx = self.x_cell_size
        dy = self.y_cell_size
        dz = self.z_cell_size
        # 'tlf' = 'top_left_far'
        tlf_i, tlf_x_weight = self.next_node_num_and_weight(
            particle.position.x, dx, self.x_start)
        tlf_j, tlf_y_weight = self.next_node_num_and_weight(
            particle.position.y, dy, self.y_start)
        tlf_k, tlf_z_weight = self.next_node_num_and_weight(
            particle.position.z, dz, self.z_start)
        # tlf
        total_field = Vec3d.zero()
        field_from_node = self.field_from_file[tlf_i][tlf_j][tlf_k].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # trf
        field_from_node = self.field_from_file[tlf_i-1][tlf_j][tlf_k].times_scalar(1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # blf
        field_from_node = self.field_from_file[tlf_i][tlf_j - 1][tlf_k].times_scalar(tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # brf
        field_from_node = self.field_from_file[tlf_i-1][tlf_j-1][tlf_k].times_scalar(1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # tln
        field_from_node = self.field_from_file[tlf_i][tlf_j][tlf_k-1].times_scalar(tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # trn
        field_from_node = self.field_from_file[tlf_i-1][tlf_j][tlf_k-1].times_scalar(1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # bln
        field_from_node = self.field_from_file[tlf_i][tlf_j - 1][tlf_k-1].times_scalar(tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # brn
        field_from_node = self.field_from_file[tlf_i-1][tlf_j-1][tlf_k-1].times_scalar(1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        #
        return total_field


    @staticmethod
    def next_node_num_and_weight(x, grid_step, x_start):
        # todo: take initial grid position into account
        x_in_grid_units = (x - x_start) / grid_step
        next_node = ceil(x_in_grid_units)
        weight = 1.0 - (next_node - x_in_grid_units)
        return (next_node, weight)


    def write_hdf5_field_parameters(self, current_field_group):
        current_field_group.attrs["field_filename"] = self.field_filename


    @classmethod
    def is_relevant_config_part(cls, field_name):
        return "ExternalFieldFromFile" in field_name
