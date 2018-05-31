from configparser import ConfigParser

from ef.config.components.boundary_conditions import BoundaryConditions
from ef.config.components.fields.electric.uniform import ExternalElectricFieldUniform
from ef.config.components.fields.magnetic.uniform import ExternalMagneticFieldUniform
from ef.config.components.inner_region import InnerRegion
from ef.config.components.output_file import OutputFile
from ef.config.components.particle_interaction_model import ParticleInteractionModel
from ef.config.components.particle_source import ParticleSource
from ef.config.components.spatial_mesh import SpatialMesh
from ef.config.components.time_grid import TimeGrid
from ef.config.section import ConfigSection

comp_list = [BoundaryConditions, InnerRegion, OutputFile, ParticleInteractionModel,
             ParticleSource, SpatialMesh, TimeGrid]


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
                          ExternalMagneticFieldUniform('mgn_uni'),  ExternalElectricFieldUniform('el_uni'),
                          OutputFile('example_', '.h5')]
