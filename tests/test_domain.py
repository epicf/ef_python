from configparser import ConfigParser
from math import sqrt

import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from ef.external_field_expression import ExternalFieldExpression
from ef.external_field_uniform import ExternalFieldUniform
from ef.field_solver import FieldSolver
from ef.inner_region import InnerRegion
from ef.particle_array import ParticleArray
from ef.particle_interaction_model import ParticleInteractionModel
from ef.particle_source import ParticleSource
from ef.spatial_mesh import SpatialMesh
from ef.time_grid import TimeGrid
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
        assert dom.inner_regions == []
        assert type(dom._field_solver) == FieldSolver
        assert dom.particle_sources == []
        assert dom.electric_fields == []
        assert dom.magnetic_fields == []
        assert dom.particle_interaction_model == ParticleInteractionModel("PIC")
        assert dom._output_filename_prefix == "out_"
        assert dom._output_filename_suffix == ".h5"

    @pytest.mark.slowish
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
        assert dom.inner_regions == [InnerRegion('1', Box(), 1),
                                     InnerRegion('2', Sphere(), -2),
                                     InnerRegion('3', Cylinder(), 0),
                                     InnerRegion('4', Tube(), 4)]
        assert type(dom._field_solver) == FieldSolver
        assert dom.particle_sources == [ParticleSourceConf('a', Box()).make(),
                                        ParticleSourceConf('c', Cylinder()).make(),
                                        ParticleSourceConf('d', Tube()).make()]
        assert dom.electric_fields == [ExternalFieldUniform('x', 'electric', np.array((-2, -2, 1)))]
        assert dom.magnetic_fields == [ExternalFieldExpression('y', 'magnetic', '0', '0', '3*x + sqrt(y) - z**2')]
        assert dom.particle_interaction_model == ParticleInteractionModel("binary")
        assert dom._output_filename_prefix == "out_"
        assert dom._output_filename_suffix == ".h5"

    def test_binary_field(self):
        d = EfConf().make()
        d.particle_sources = [
            ParticleSource('s1', Box(), 1, 0, mean_momentum=np.zeros(3), temperature=0, charge=1, mass=1,
                           particle_arrays=[ParticleArray(1, -1, 1, [(1, 2, 3)], [(-2, 2, 0)], False)], max_id=0)]
        assert_array_almost_equal(d.binary_electric_field_at_positions((1, 2, 3)), (0, 0, 0))
        assert_array_almost_equal(d.binary_electric_field_at_positions((1, 2, 4)), (0, 0, -1))
        assert_array_almost_equal(d.binary_electric_field_at_positions((0, 2, 3)), (1, 0, 0))
        assert_array_almost_equal(d.binary_electric_field_at_positions((0, 1, 2)), (1 / sqrt(27), 1 / sqrt(27), 1 / sqrt(27)))

    @pytest.mark.parametrize('model', ['noninteracting', 'PIC', 'binary'])
    def test_cube_of_gas(self, model, monkeypatch, tmpdir):
        monkeypatch.chdir(tmpdir)
        EfConf(TimeGridConf(1.0, save_step=.5, step=.1), SpatialMeshConf((10, 10, 10), (1, 1, 1)),
               [ParticleSourceConf('gas', Box(size=(10, 10, 10)), 50, 0, np.zeros(3), 300)],
               particle_interaction_model=ParticleInteractionModelConf(model)
               ).make().start_pic_simulation()

    @pytest.mark.parametrize('model', ['noninteracting', 'PIC', 'binary'])
    def test_cube_of_gas_with_hole(self, model, monkeypatch, tmpdir):
        monkeypatch.chdir(tmpdir)
        EfConf(TimeGridConf(1.0, save_step=.5, step=.1), SpatialMeshConf((10, 10, 10), (1, 1, 1)),
               [ParticleSourceConf('gas', Box(size=(10, 10, 10)), 50, 0, np.zeros(3), 300)],
               [InnerRegionConf('hole', Box(origin=(4, 4, 4), size=(2, 2, 2)))],
               particle_interaction_model=ParticleInteractionModelConf(model)
               ).make().start_pic_simulation()
