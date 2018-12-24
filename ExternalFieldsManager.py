from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


class ExternalFieldsManager(SerializableH5):

    def __init__(self, electric=(), magnetic=()):
        self.electric = list(electric)
        self.magnetic = list(magnetic)

    def total_electric_field_at_position(self, position, current_time):
        total_el_field = Vec3d.zero()
        for f in self.electric:
            el_field = f.field_at_position(Vec3d(*position), current_time)
            total_el_field = total_el_field.add(el_field)
        return total_el_field

    def total_electric_field_at_particle_position(self, particle, current_time):
        return self.total_electric_field_at_position(particle._position, current_time)

    def total_magnetic_field_at_position(self, position, current_time):
        total_mgn_field = Vec3d.zero()
        for f in self.magnetic:
            mgn_field = f.field_at_position(Vec3d(*position), current_time)
            total_mgn_field = total_mgn_field.add(mgn_field)
        return total_mgn_field

    def total_magnetic_field_at_particle_position(self, particle, current_time):
        return self.total_magnetic_field_at_position(particle._position, current_time)
