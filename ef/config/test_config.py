from configparser import ConfigParser

from ef.config.components import *
from ef.config.efconf import EfConf
from ef.config.section import ConfigSection

comp_list = [BoundaryConditions, InnerRegion, OutputFile, ParticleInteractionModel,
             ParticleSource, SpatialMesh, TimeGrid, ExternalFieldUniform]


def test_components_to_conf_and_back():
    for Component in comp_list:
        x = Component()
        y = x.to_conf().make()
        assert x == y


def test_conf_to_configparser_and_back():
    confs = [C().to_conf() for C in comp_list]
    parser = ConfigParser()
    for c in confs:
        c.add_section_to_parser(parser)
    conf2 = ConfigSection.parser_to_confs(parser)
    assert conf2 == confs


def test_minimal_example():
    parser = ConfigParser()
    parser.read("examples/minimal_working_example/minimal_conf.conf")
    components = [conf.make() for conf in ConfigSection.parser_to_confs(parser)]
    assert components == [TimeGrid(1e-7, 1e-9, 1e-9), SpatialMesh((5, 5, 15), (0.5, 0.5, 1.5)),
                          ParticleInteractionModel('noninteracting'), BoundaryConditions(0),
                          ExternalFieldUniform('mgn_uni', 'magnetic'),
                          ExternalFieldUniform('el_uni', 'electric'),
                          OutputFile('example_', '.h5')]


class TestEfConf:
    def test_conf_export(self):
        conf = EfConf(sources=[ParticleSource()], inner_regions=(InnerRegion(),))
        s = conf.export_to_string()
        c1 = EfConf.from_string(s)
        assert c1 == conf

    def test_conf_repr(self):
        from numpy import array  # for use in eval
        conf = EfConf(sources=[ParticleSource()], inner_regions=(InnerRegion(),))
        s = repr(conf)
        c1 = eval(s)
        assert c1 == conf
