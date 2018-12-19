from collections import namedtuple

from ef.util.data_class import DataClass
from ef.util.subclasses import get_all_subclasses


class ConfigSection(DataClass):
    _section_map = None  # dictionary of section_header_string: section class
    section = "Section header string goes here"
    ContentTuple = namedtuple("ConfigSectionTuple", ())  # expected content of the config section as a namedtuple
    convert = ContentTuple()  # tuple of types to convert config strings into

    @staticmethod
    def parser_to_confs(conf):
        if ConfigSection._section_map is None:
            ConfigSection._section_map = {c.section: c for c in get_all_subclasses(ConfigSection)}
        return [ConfigSection.from_section(section, conf[section]) for section in conf.sections()]

    def __init__(self, *args, **kwargs):
        self.content = self.ContentTuple(*args, **kwargs)

    @staticmethod
    def from_section(section_name, section_content):
        return ConfigSection._section_map[section_name.split('.')[0]]._from_section(section_content)

    @classmethod
    def _from_section(cls, section):
        if section.name != cls.section:
            raise ValueError("Unexpected config section name: {}".format(section.name))
        if set(section.keys()) != set(cls.ContentTuple._fields):
            unexpected = set(section.keys()) - set(cls.ContentTuple._fields)
            if unexpected:
                raise ValueError("Unexpected config variables {} in section {}".
                                 format(tuple(unexpected), section.name))
            missing = set(cls.ContentTuple._fields) - set(section.keys())
            if missing:
                raise ValueError("Missing config variables {} in section {}".
                                 format(tuple(missing), section.name))

        data = {arg: cls.convert._asdict()[arg](section[arg]) for arg in cls.convert._fields}
        return cls(**data)

    def add_section_to_parser(self, conf):
        conf.add_section(self.section)
        for k, v in self.content._asdict().items():
            conf.set(self.section, k, str(v))

    def make(self):
        raise NotImplementedError()


class NamedConfigSection(ConfigSection):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.section = self.section + '.' + name
        super().__init__(*args, **kwargs)

    @classmethod
    def _from_section(cls, section):
        category, name = section.name.split('.', 1)
        if category != cls.section:
            raise ValueError("Unexpected config section name: {}".format(section.name))
        if set(section.keys()) != set(cls.ContentTuple._fields):
            unexpected = set(section.keys()) - set(cls.ContentTuple._fields)
            if unexpected:
                raise ValueError("Unexpected config variables {} in section {}".
                                 format(tuple(unexpected), section.name))
            missing = set(cls.ContentTuple._fields) - set(section.keys())
            if missing:
                raise ValueError("Missing config variables {} in section {}".
                                 format(tuple(missing), section.name))

        data = {arg: cls.convert._asdict()[arg](section[arg]) for arg in cls.convert._fields}
        return cls(name, **data)
