import sys

from Vec3d import Vec3d
from ExternalFieldUniform import ExternalFieldUniform
from ExternalFieldExpression import ExternalFieldExpression
from ExternalFieldFromFile import ExternalFieldFromFile


class ExternalFieldsManager():

    def __init__(self):
        self.electric = []
        self.magnetic = []


    @classmethod
    def init_from_config(cls, conf):
        new_obj = cls()
        new_obj.electric = []
        new_obj.magnetic = []
        for sec_name in conf:
            field = None
            if ExternalFieldUniform.is_relevant_config_part(sec_name):
                field = ExternalFieldUniform.init_from_config(conf[sec_name], sec_name)
            elif ExternalFieldExpression.is_relevant_config_part(sec_name):
                field = ExternalFieldExpression.init_from_config(conf[sec_name], sec_name)
            elif ExternalFieldFromFile.is_relevant_config_part(sec_name):
                field = ExternalFieldFromFile.init_from_config(conf[sec_name], sec_name)
            if field:
                if conf[sec_name]["electric_or_magnetic"] == 'electric':
                    new_obj.electric.append(field)
                elif conf[sec_name]["electric_or_magnetic"] == 'magnetic':
                    new_obj.magnetic.append(field)
                ExternalFieldsManager.mark_extfield_sec_as_used(sec_name, conf)
        return new_obj


    @staticmethod
    def mark_extfield_sec_as_used(sec_name, conf):
        # For now simply mark sections as 'used' instead of removing them.
        conf[sec_name]["used"] = "True"


    @classmethod
    def init_from_h5(cls, h5_external_fields_group):
        new_obj = cls()
        new_obj.electric = []
        new_obj.magnetic = []
        for field_name in h5_external_fields_group.keys():
            current_field_grpid = h5_external_fields_group[field_name]
            new_obj.parse_hdf5_external_field(current_field_grpid)
        return new_obj


    def parse_hdf5_external_field(self, current_field_grpid):
        field_type = current_field_grpid.attrs["field_type"]
        if field_type == "uniform":
            field = ExternalFieldUniform.init_from_h5(current_field_grpid)
        elif field_type == "expression":
            field = ExternalFieldExpression.init_from_h5(current_field_grpid)
        elif field_type == "from_file":
            field = ExternalFieldFromFile.init_from_h5(current_field_grpid)
        else:
            print("In ExternalFieldsManager constructor-from-h5: ")
            print("Unknown external_field type. Aborting")
            sys.exit(-1)
        if field.electric_or_magnetic == 'electric':
            self.electric.append(field)
        elif field.electric_or_magnetic == 'magnetic':
            self.magnetic.append(field)


    def total_electric_field_at_particle_position(self, particle, current_time):
        total_el_field = Vec3d.zero()
        for f in self.electric:
            el_field = f.field_at_particle_position(particle, current_time)
            total_el_field = total_el_field.add(el_field)
        return total_el_field


    def total_magnetic_field_at_particle_position(self, particle, current_time):
        total_mgn_field = Vec3d.zero()
        for f in self.magnetic:
            mgn_field = f.field_at_particle_position(particle, current_time)
            total_mgn_field = total_mgn_field.add(mgn_field)
        return total_mgn_field


    def write_to_file(self, hdf5_file_id):
        hdf5_groupname = "/ExternalFields"
        n_of_electric_fields = len(self.electric)
        n_of_magnetic_fields = len(self.magnetic)
        fields_group = hdf5_file_id.create_group(hdf5_groupname)
        fields_group.attrs.create("number_of_electric_fields", n_of_electric_fields)
        fields_group.attrs.create("number_of_magnetic_fields", n_of_magnetic_fields)
        for el_field in self.electric:
            el_field.write_to_file(fields_group)
        for mgn_field in self.magnetic:
            mgn_field.write_to_file(fields_group)


    def print_fields(self):
        for el_field in self.electric:
            el_field.print()
        for mgn_field in self.magnetic:
            mgn_field.print()
