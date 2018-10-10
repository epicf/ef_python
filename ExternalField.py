import os

import physical_constants

class ExternalField:

    def __init__(self):
        self.name = None
        self.electric_or_magnetic = None
        self.field_type = None


    def init_common_parameters_from_config(self, field_conf, field_conf_name):
        self.name = field_conf_name[field_conf_name.rfind(".") + 1:]
        self.electric_or_magnetic = field_conf["electric_or_magnetic"]
        if self.electric_or_magnetic not in ["electric", "magnetic"]:
            raise ValueError(
                "ExternalField {} should be 'electric' or 'magnetic'".format(self.name))


    def init_common_parameters_from_h5(self, h5group):
        self.name = os.path.basename(h5group.name)
        self.electric_or_magnetic = h5group.attrs["electric_or_magnetic"]


    def write_to_file(self, h5_fields_group):
        current_field_group = h5_fields_group.create_group("./" + self.name)
        current_field_group.attrs["electric_or_magnetic"] = self.electric_or_magnetic
        current_field_group.attrs.create("speed_of_light", physical_constants.speed_of_light)
        current_field_group.attrs["field_type"] = self.field_type
        self.write_hdf5_field_parameters(current_field_group)


    def write_hdf5_field_parameters(self, current_field_group):
        # virtual method
        raise NotImplementedError()


    def field_at_particle_position(self, particle, current_time):
        # virtual method
        raise NotImplementedError()
