__all__ = ["OutputFile", "OutputFilenameConf"]

from collections import namedtuple

from ef.config.section import register, ConfigSection
from ef.config.component import ConfigComponent


class OutputFile(ConfigComponent):
    def __init__(self, prefix="out_", suffix=".h5"):
        self.prefix = prefix
        self.suffix = suffix

    def to_conf(self):
        return OutputFilenameConf(self.prefix, self.suffix)


@register
class OutputFilenameConf(ConfigSection):
    section = "OutputFilename"
    ContentTuple = namedtuple("OutputFileNameTuple", ('output_filename_prefix', 'output_filename_suffix'))
    convert = ContentTuple(str, str)

    def make(self):
        return OutputFile(*self.content)
