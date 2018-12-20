from configparser import ConfigParser

import numpy as np

from ExternalFieldExpression import ExternalFieldExpression
from ExternalFieldUniform import ExternalFieldUniform
from ExternalFieldsManager import ExternalFieldsManager
from FieldSolver import FieldSolver
from InnerRegion import InnerRegion
from InnerRegionsManager import InnerRegionsManager
from ParticleInteractionModel import ParticleInteractionModel
from ParticleSourcesManager import ParticleSourcesManager
from ParticleToMeshMap import ParticleToMeshMap
from SpatialMesh import SpatialMesh
from TimeGrid import TimeGrid
from ef.config.components import *
from ef.config.efconf import EfConf


class TestDomain:
    def test_init_from_config(self):
        efconf = EfConf()
        parser = ConfigParser()
        parser.read_string(efconf.export_to_string())
        dom = EfConf.from_configparser(parser).make()
        assert dom.time_grid == TimeGrid(100, 1, 10)
        assert dom.spat_mesh == SpatialMesh.do_init((10, 10, 10), (1, 1, 1), BoundaryConditionsConf(0))
        assert dom.inner_regions == InnerRegionsManager([])
        assert dom.particle_to_mesh_map == ParticleToMeshMap()
        assert type(dom._field_solver) == FieldSolver
        assert dom.particle_sources == ParticleSourcesManager([])
        assert dom.external_fields == ExternalFieldsManager([], [])
        assert dom.particle_interaction_model == ParticleInteractionModel("PIC")
        assert dom._output_filename_prefix == "out_"
        assert dom._output_filename_suffix == ".h5"

    def test_all_config(self):
        efconf = EfConf(TimeGridConf(200, 20, 2), SpatialMeshConf((5, 5, 5), (.1, .1, .1)),
                        sources=[ParticleSourceConf('a', Box()),
                                 ParticleSourceConf('c', Cylinder()),
                                 ParticleSourceConf('d', Tube())],
                        inner_regions=[InnerRegionConf('1', Box(), 1),
                                       InnerRegionConf('2', Sphere(), -2),
                                       InnerRegionConf('3', Cylinder(), 0),
                                       InnerRegionConf('4', Tube(), 4)],
                        output_file=OutputFileConf(), boundary_conditions=BoundaryConditionsConf(-2.7),
                        particle_interaction_model=ParticleInteractionModelConf('binary'),
                        external_fields=[ExternalFieldUniformConf('x', 'electric', (-2, -2, 1)),
                                         ExternalFieldExpressionConf('y', 'magnetic',
                                                                     ('0', '0', '3*x + sqrt(y) - z**2'))])

        parser = ConfigParser()
        parser.read_string(efconf.export_to_string())
        dom = EfConf.from_configparser(parser).make()
        assert dom.time_grid == TimeGrid(200, 2, 20)
        assert dom.spat_mesh == SpatialMesh.do_init((5, 5, 5), (.1, .1, .1), BoundaryConditionsConf(-2.7))
        assert dom.inner_regions == InnerRegionsManager([InnerRegion('1', Box(), 1),
                                                         InnerRegion('2', Sphere(), -2),
                                                         InnerRegion('3', Cylinder(), 0),
                                                         InnerRegion('4', Tube(), 4)])
        assert dom.particle_to_mesh_map == ParticleToMeshMap()
        assert type(dom._field_solver) == FieldSolver
        assert dom.particle_sources == ParticleSourcesManager([ParticleSourceConf('a', Box()).make(),
                                                               ParticleSourceConf('c', Cylinder()).make(),
                                                               ParticleSourceConf('d', Tube()).make()])
        assert dom.external_fields == ExternalFieldsManager(
            [ExternalFieldUniform('x', 'electric', np.array((-2, -2, 1)))],
            [ExternalFieldExpression('y', 'magnetic',
                                     '0', '0',
                                     '3*x + sqrt(y) - z**2')])
        assert dom.particle_interaction_model == ParticleInteractionModel("binary")
        assert dom._output_filename_prefix == "out_"
        assert dom._output_filename_suffix == ".h5"
