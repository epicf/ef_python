from ExternalField import ExternalField
from Vec3d import Vec3d


class ExternalFieldUniform(ExternalField):

    def __init__(self, name, electric_or_magnetic, uniform_field_vector):
        super().__init__(name, electric_or_magnetic)
        self.uniform_field_vector = uniform_field_vector

    def field_at_particle_position(self, particle, current_time):
        return Vec3d(*self.uniform_field_vector)
