__all__ = ["ExternalFieldUniform", "ExternalFieldUniformConf"]

from collections import namedtuple

import numpy as np

from ef.config.components.fields.field import Field
from ef.config.section import register, NamedConfigSection


class ExternalFieldUniform(Field):
    def __init__(self, name="ExternalFieldUniform_1",
                 electric_or_magnetic="magnetic",
                 field=(0, 0, 0)):
        self.name = name
        self.electric_or_magnetic = electric_or_magnetic
        self.field = np.array(field, np.float)

    def to_conf(self):
        return ExternalFieldUniformConf(self.name, self.electric_or_magnetic, *self.field)


@register
class ExternalFieldUniformConf(NamedConfigSection):
    section = "ExternalFieldUniform"
    ContentTuple = namedtuple("ExternalFieldUniform",
                              ('electric_or_magnetic', 'field_x', 'field_y', 'field_z'))
    convert = ContentTuple(str, float, float, float)

    def make(self):
        return ExternalFieldUniform(self.name, self.content)
