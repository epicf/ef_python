from ef.util.serializable_h5 import SerializableH5


class ExternalFieldsManager(SerializableH5):

    def __init__(self, electric=(), magnetic=()):
        self.electric = list(electric)
        self.magnetic = list(magnetic)

    def total_electric_field_at_position(self, position, current_time):
        return sum(f.field_at_position(position, current_time) for f in self.electric)

    def total_magnetic_field_at_position(self, position, current_time):
        return sum(f.field_at_position(position, current_time) for f in self.magnetic)
