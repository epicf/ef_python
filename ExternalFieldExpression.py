import math
from Vec3d import Vec3d
from ExternalField import ExternalField
from libs.simpleeval.simpleeval import SimpleEval

class ExternalFieldExpression(ExternalField):

    def __init__(self):
        super().__init__()
        self.expression_x = None
        self.expression_y = None
        self.expression_z = None


    @classmethod
    def init_from_config(cls, field_conf, field_conf_name):
        new_obj = cls()
        new_obj.init_common_parameters_from_config(field_conf, field_conf_name)
        new_obj.field_type = "expression"
        new_obj.check_correctness_of_related_config_fields(field_conf)
        new_obj.get_values_from_config(field_conf)
        return new_obj


    def check_correctness_of_related_config_fields(self, field_conf):
        pass
        # todo: check expression correctness


    def get_values_from_config(self, field_conf):
        self.expression_x = field_conf["field_x"]
        self.expression_y = field_conf["field_y"]
        self.expression_z = field_conf["field_z"]


    @classmethod
    def init_from_h5(cls, h5_field_group):
        new_obj = cls()
        new_obj.init_common_parameters_from_h5(h5_field_group)
        new_obj.field_type = "expression"
        new_obj.expression_x = h5_field_group.attrs["field_x"]
        new_obj.expression_y = h5_field_group.attrs["field_y"]
        new_obj.expression_z = h5_field_group.attrs["field_z"]
        return new_obj


    def field_at_particle_position(self, particle, current_time):
        ev = SimpleEval(names={"x":particle.position.x,
                               "y":particle.position.y,
                               "z":particle.position.z,
                               "t":current_time},
                        functions={"sin": math.sin,
                                   "cos": math.cos,
                                   "sqrt":math.sqrt})
        # todo: inherit SimpleEval and define math functions inside
        # todo: add r, theta, phi names
        fx = ev.eval(self.expression_x)
        fy = ev.eval(self.expression_y)
        fz = ev.eval(self.expression_z)
        return Vec3d(fx, fy, fz)


    def write_hdf5_field_parameters(self, current_field_group):
        current_field_group.attrs["field_x"] = self.expression_x
        current_field_group.attrs["field_y"] = self.expression_y
        current_field_group.attrs["field_z"] = self.expression_z


    @classmethod
    def is_relevant_config_part(cls, field_name):
        return "ExternalFieldExpression" in field_name
