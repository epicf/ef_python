import os

class ExternalField:

    def __init__(self):
        self.name = None
        self.field_type = None


    def init_common_fields_from_config(self, field_conf, field_conf_name):
        self.name = field_conf_name[field_conf_name.rfind(".") + 1 :]


    def init_common_fields_from_h5(self, h5group):
        self.name = os.path.basename(h5group.name)


    def write_to_file(self, h5_fields_group):
        current_field_group = h5_fields_group.create_group("./" + self.name)
        self.write_hdf5_field_parameters(current_field_group)


    def write_hdf5_field_parameters(self, current_field_group):
        # virtual method
        raise NotImplementedError()


    def field_at_particle_position(self, particle, current_time):
        # virtual method
        raise NotImplementedError()
