import external_field_expression

__all__ = ["ExternalFieldExpressionConf", "ExternalFieldExpressionSection"]

from collections import namedtuple

from ef.config.components.fields.field import FieldConf
from ef.config.section import NamedConfigSection


class ExternalFieldExpressionConf(FieldConf):
    def __init__(self, name="ExternalFieldExpression_1",
                 electric_or_magnetic="magnetic",
                 field=('0', '0', '0')):
        self.name = name
        self.electric_or_magnetic = electric_or_magnetic
        self.field = field

    def to_conf(self):
        return ExternalFieldExpressionSection(self.name, self.electric_or_magnetic, *self.field)

    def make(self):
        return external_field_expression.ExternalFieldExpression(self.name, self.electric_or_magnetic, *self.field)


class ExternalFieldExpressionSection(NamedConfigSection):
    section = "ExternalFieldExpression"
    ContentTuple = namedtuple("ExternalFieldExpressionTuple",
                              ('electric_or_magnetic', 'field_x', 'field_y', 'field_z'))
    convert = ContentTuple(str, str, str, str)

    def make(self):
        return ExternalFieldExpressionConf(self.name, self.content.electric_or_magnetic, self.content[1:])
