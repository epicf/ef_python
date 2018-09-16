__all__ = ["ExternalFieldFromFile", "ExternalFieldFromFileConf"]


from collections import namedtuple

from ef.config.components.fields.field import Field
from ef.config.section import register, NamedConfigSection


class ExternalFieldFromFile(Field):
    def __init__(self, name="mgn_field_from_file",
                 electric_or_magnetic='magnetic',
                 filename=None):
        self.name = name
        self.electric_or_magnetic = electric_or_magnetic
        self.filename = filename


    def to_conf(self):
        return ExternalFieldFromFileConf(self.name, self.electric_or_magnetic, self.filename)


@register
class ExternalFieldFromFileConf(NamedConfigSection):
    section = "ExternalFieldFromFile"
    ContentTuple = namedtuple("ExternalFieldFromFile",
                              ('electric_or_magnetic', 'field_filename'))
    convert = ContentTuple(str, str)


    def make(self):
        return ExternalFieldFromFile(self.name, self.content)
