from ExternalField import ExternalField


class ExternalFieldUniform(ExternalField):

    def __init__(self, name, electric_or_magnetic, uniform_field_vector):
        super().__init__(name, electric_or_magnetic)
        self.uniform_field_vector = uniform_field_vector

    def field_at_position(self, position, current_time):
        return self.uniform_field_vector
