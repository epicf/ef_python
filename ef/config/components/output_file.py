__all__ = ["OutputFileConf", "OutputFilenameSection"]

from collections import namedtuple

from ef.config.section import ConfigSection
from ef.config.component import ConfigComponent


class OutputFileConf(ConfigComponent):
    def __init__(self, prefix="out_", suffix=".h5"):
        self.prefix = prefix
        self.suffix = suffix

    def to_conf(self):
        return OutputFilenameSection(self.prefix, self.suffix)


class OutputFilenameSection(ConfigSection):
    section = "OutputFilename"
    ContentTuple = namedtuple("OutputFileNameTuple", ('output_filename_prefix', 'output_filename_suffix'))
    convert = ContentTuple(str, str)

    def make(self):
        return OutputFileConf(*self.content)
