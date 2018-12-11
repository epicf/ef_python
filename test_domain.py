from configparser import ConfigParser

from Domain import Domain
from ExternalFieldsManager import ExternalFieldsManager
from FieldSolver import FieldSolver
from InnerRegionsManager import InnerRegionsManager
from ParticleInteractionModel import ParticleInteractionModel
from ParticleSourcesManager import ParticleSourcesManager
from ParticleToMeshMap import ParticleToMeshMap
from SpatialMesh import SpatialMesh
from TimeGrid import TimeGrid
from ef.config.components import BoundaryConditions
from ef.config.efconf import EfConf


class TestDomain:
    def test_init_from_config(self):
        efconf = EfConf()
        parser = ConfigParser()
        parser.read_string(efconf.export_to_string())
        dom = Domain.init_from_config(parser)
        assert dom.time_grid == TimeGrid(100, 1, 10)
        assert type(dom.spat_mesh) == SpatialMesh
        assert type(dom.inner_regions) == InnerRegionsManager
        assert dom.inner_regions.regions == []
        assert type(dom.particle_to_mesh_map) == ParticleToMeshMap
        assert type(dom.field_solver) == FieldSolver
        assert type(dom.particle_sources) == ParticleSourcesManager
        assert dom.particle_sources.sources == []
        assert type(dom.external_fields) == ExternalFieldsManager
        assert dom.external_fields.electric == []
        assert dom.external_fields.magnetic == []
        assert type(dom.particle_interaction_model) == ParticleInteractionModel
        assert dom.particle_interaction_model.particle_interaction_model == "PIC"
        assert dom.particle_interaction_model.pic == True
        assert dom.output_filename_prefix == "out_"
        assert dom.output_filename_suffix == ".h5"