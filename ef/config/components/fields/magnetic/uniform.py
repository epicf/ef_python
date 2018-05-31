__all__ = ["ExternalMagneticFieldUniform", "ExternalMagneticFieldUniformConf"]

from collections import namedtuple

import numpy as np

from ef.config.components.fields.field import Field
from ef.config.section import register, NamedConfigSection


class ExternalMagneticFieldUniform(Field):
    def __init__(self, name="ExternalMagneticFieldUniform1", field=(0, 0, 0)):
        self.name = name
        self.field = np.array(field, np.float)

    def to_conf(self):
        return ExternalMagneticFieldUniformConf(self.name, *self.field)


@register
class ExternalMagneticFieldUniformConf(NamedConfigSection):
    section = "External_magnetic_field_uniform"
    ContentTuple = namedtuple("ExternalMagneticFieldUniform",
                              ('magnetic_field_x', 'magnetic_field_y', 'magnetic_field_z'))
    convert = ContentTuple(float, float, float)

    def make(self):
        return ExternalMagneticFieldUniform(self.name, self.content)
