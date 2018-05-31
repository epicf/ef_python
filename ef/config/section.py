from collections import namedtuple

from ef.config.data_class import DataClass


class ConfigSection(DataClass):
    section_map = {}
    section = "Section header string goes here"
    ContentTuple = namedtuple("ConfigSectionTuple", ())  # expected content of the config section as a namedtuple
    convert = ContentTuple()  # tuple of types to convert config strings into

    @staticmethod
    def parser_to_confs(conf):
        return [ConfigSection.section_map[section.split('.')[0]].from_section(conf[section]) for section in
                conf.sections()]

    @classmethod
    def register(cls):
        cls.section_map[cls.section] = cls

    def __init__(self, *args, **kwargs):
        self.content = self.ContentTuple(*args, **kwargs)

    @classmethod
    def from_section(cls, section):
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


def register(cls):
    ConfigSection.section_map[cls.section] = cls
    return cls


class NamedConfigSection(ConfigSection):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.section = self.section + '.' + name
        super().__init__(*args, **kwargs)

    @classmethod
    def from_section(cls, section):
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
