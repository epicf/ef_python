from ef.util.serializable_h5 import SerializableH5


class ExternalField(SerializableH5):

    def __init__(self, name, electric_or_magnetic):
        self.name = name
        self.electric_or_magnetic = electric_or_magnetic

    def field_at_position(self, position, current_time):
        raise NotImplementedError()
