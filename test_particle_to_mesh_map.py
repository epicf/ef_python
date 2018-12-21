import numpy as np
from numpy.testing import assert_array_equal

from Particle import Particle
from ParticleSourcesManager import ParticleSourcesManager
from ParticleToMeshMap import ParticleToMeshMap
from Vec3d import Vec3d
from ef.config.components import ParticleSourceConf, SpatialMeshConf, BoundaryConditionsConf


class TestParticleToMeshMap:

    def test_weight_particles_charge_to_mesh(self):
        mesh = SpatialMeshConf((2, 4, 8), (1, 2, 4)).make(BoundaryConditionsConf())
        sources = ParticleSourcesManager([ParticleSourceConf().make()])
        sources.sources[0].particles = [Particle(1, -2, 4, (1, 1, 3), (0, 0, 0))]
        ParticleToMeshMap.weight_particles_charge_to_mesh(mesh, sources)
        assert_array_equal(mesh.charge_density,
                           np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                     [[-0.25 / 8, -0.75 / 8, 0], [-0.25 / 8, -0.75 / 8, 0], [0, 0, 0]],
                                     [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]))

    def test_field_at_position(self):
        mesh = SpatialMeshConf((2, 4, 8), (1, 2, 4)).make(BoundaryConditionsConf())
        mesh.electric_field[1:2, 0:2, 0:2] = np.array([[[2, 1, 0], [-3, 1, 0]],
                                                       [[0, -1, 0], [-1, 0, 0]]])
        assert ParticleToMeshMap.field_at_position(mesh, np.array((1, 1, 3))) == Vec3d(-1.25, 0.375, 0)
