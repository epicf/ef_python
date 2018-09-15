__all__ = ["ExternalElectricFieldUniform", "ExternalElectricFieldUniformConf"]

from collections import namedtuple

import numpy as np

from ef.config.components.fields.field import Field
from ef.config.section import register, NamedConfigSection


class ExternalElectricFieldUniform(Field):
    def __init__(self, name="ExternalElectricFieldUniform1", field=(0, 0, 0)):
        self.name = name
        self.field = np.array(field, np.float)

    def to_conf(self):
        return ExternalElectricFieldUniformConf(self.name, *self.field)


@register
class ExternalElectricFieldUniformConf(NamedConfigSection):
    section = "ExternalElectricFieldUniform"
    ContentTuple = namedtuple("ExternalElectricFieldUniform",
                              ('electric_field_x', 'electric_field_y', 'electric_field_z'))
    convert = ContentTuple(float, float, float)

    def make(self):
        return ExternalElectricFieldUniform(self.name, self.content)
