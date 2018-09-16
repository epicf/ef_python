from Vec3d import Vec3d

from ExternalField import ExternalField


class ExternalFieldUniform(ExternalField):

    def __init__(self):
        super().__init__()
        self.uniform_field_vec = None


    @classmethod
    def init_from_config(cls, field_conf, field_conf_name):
        new_obj = cls()
        new_obj.init_common_parameters_from_config(field_conf, field_conf_name)
        new_obj.field_type = "uniform"
        new_obj.check_correctness_of_related_config_fields(field_conf)
        new_obj.get_values_from_config(field_conf)
        return new_obj


    def check_correctness_of_related_config_fields(self, field_conf):
        pass
        # nothing to check here


    def get_values_from_config(self, field_conf):
        self.uniform_field_vec = Vec3d(field_conf.getfloat("field_x"),
                                       field_conf.getfloat("field_y"),
                                       field_conf.getfloat("field_z"))


    @classmethod
    def init_from_h5(cls, h5_field_group):
        new_obj = cls()
        new_obj.init_common_parameters_from_h5(h5_field_group)
        new_obj.field_type = "uniform"
        Fx = h5_field_group.attrs["field_x"]
        Fy = h5_field_group.attrs["field_y"]
        Fz = h5_field_group.attrs["field_z"]
        new_obj.uniform_field_vec = Vec3d(Fx, Fy, Fz)
        return new_obj


    def field_at_particle_position(self, particle, current_time):
        return self.uniform_field_vec


    def write_hdf5_field_parameters(self, current_field_group):
        current_field_group.attrs.create("field_x", self.uniform_field_vec.x)
        current_field_group.attrs.create("field_y", self.uniform_field_vec.y)
        current_field_group.attrs.create("field_z", self.uniform_field_vec.z)


    @classmethod
    def is_relevant_config_part(cls, field_name):
        return "ExternalFieldUniform" in field_name
