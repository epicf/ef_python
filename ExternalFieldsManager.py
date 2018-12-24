from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


class ExternalFieldsManager(SerializableH5):

    def __init__(self, electric=(), magnetic=()):
        self.electric = list(electric)
        self.magnetic = list(magnetic)

    def total_electric_field_at_position(self, position, current_time):
        if self.electric:
            return Vec3d(*sum(f.field_at_position(Vec3d(*position), current_time) for f in self.electric))
        else:
            return Vec3d.zero()

    def total_electric_field_at_particle_position(self, particle, current_time):
        return self.total_electric_field_at_position(particle._position, current_time)

    def total_magnetic_field_at_position(self, position, current_time):
        if self.magnetic:
            return Vec3d(*sum(f.field_at_position(Vec3d(*position), current_time) for f in self.magnetic))
        else:
            return Vec3d.zero()

    def total_magnetic_field_at_particle_position(self, particle, current_time):
        return self.total_magnetic_field_at_position(particle._position, current_time)
