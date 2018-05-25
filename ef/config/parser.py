import abc
from magic_repr import make_repr


class DataClass:
    __repr__ = make_repr()

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return repr(self) == repr(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class ConfigComponent(abc.ABC, DataClass):
    section_map = {}

    @staticmethod
    def parser_to_confs(conf):
        return [ConfigComponent.section_map[section.split('.')[0]].from_section(conf[section]) for section in
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
    ConfigComponent.section_map[cls.section] = cls
    return cls


class NamedConfigComponent(ConfigComponent):
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

