import os.path
import numpy as np

from Vec3d import Vec3d
import physical_constants

from ExternalField import ExternalField

# Magnetic on regular grid from file

class ExternalFieldMagneticOnRegularGridFromFile(ExternalField):

    def __init__(self):
        super().__init__()
        self.field_file = None
        self.magnetic_field_from_file = None
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
        new_obj = super().init_from_config(field_conf, field_conf_name)
        new_obj.field_type = "magnetic_on_regular_grid_from_file"
        new_obj.check_correctness_of_related_config_fields(field_conf)
        new_obj.get_values_from_config(field_conf)
        new_obj.read_field_from_file()
        return new_obj


    def check_correctness_of_related_config_fields(self, field_conf):
        if not os.path.exists(field_conf["field_file"]):
            raise FileNotFoundError("Field file not found")


    def get_values_from_config(self, field_conf):
        self.field_file = field_conf["field_file"]


    def read_field_from_file(self):
        mesh = np.loadtxt(self.field_file)
        # assume X Y Z Hx Hy Hz columns
        # sort by column 0, then 1, then 2
        # https://stackoverflow.com/a/38194077
        ind = mesh[:, 2].argsort() # First sort doesn't need to be stable.
        mesh = mesh[ind]
        ind = mesh[:, 1].argsort(kind='mergesort')
        mesh = mesh[ind]
        ind = mesh[:, 0].argsort(kind='mergesort')
        mesh = mesh[ind]
        #
        self.x_volume_size = mesh[-1, 0] - mesh[0, 0]
        self.y_volume_size = mesh[-1, 1] - mesh[0, 1]
        self.z_volume_size = mesh[-1, 2] - mesh[0, 2]
        self.x_cell_size = mesh[1, 0] - mesh[0, 0]
        self.y_cell_size = mesh[1, 1] - mesh[0, 1]
        self.z_cell_size = mesh[1, 2] - mesh[0, 2]
        self.x_n_nodes = self.x_volume_size // self.x_cell_size # recheck
        self.y_n_nodes = self.y_volume_size // self.y_cell_size # recheck
        self.z_n_nodes = self.z_volume_size // self.z_cell_size # recheck
        #
        #todo: reshape last 3 col by number of nodes


    @classmethod
    def init_from_h5(cls, h5_field_group):
        new_obj = super().init_from_h5(h5_field_group)
        new_obj.field_type = "magnetic_on_regular_grid_from_file"
        new_obj.field_file = h5_field_group.attrs["field_file"]
        if not os.path.exists(new_obj.field_file):
            raise FileNotFoundError("Field file not found")
        new_obj.read_field_from_file()
        return new_obj


    def field_at_particle_position(self, particle, current_time):
        #return self.magnetic_field
        pass


    def write_hdf5_field_parameters( self, current_field_group_id ):
        current_field_group_id.attrs["field_type"] = self.field_type
        current_field_group_id.attrs["field_file"] = self.field_file


    @classmethod
    def is_relevant_conf_part(cls, field_name):
        return "ExternalMagneticFieldOnRegularGridFromFile" in field_name
