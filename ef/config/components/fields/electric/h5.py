__all__ = []

from ef.config.components.fields.field import Field


class ExternalFieldElectricOnRegularGridFromH5File(Field):

    def __init__(self, name="elec_file", filename="field.h5"):
        self.name = name
        self.filename = filename

    def visualize(self, ax):
        pass

# TODO: Section class and tests

