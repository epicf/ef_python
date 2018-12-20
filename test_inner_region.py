from InnerRegion import InnerRegion
from Node import Node
from Particle import Particle
from SpatialMesh import SpatialMesh
from Vec3d import Vec3d
from ef.config.components import BoundaryConditionsConf, Box


class TestInnerRegion:
    def test_init(self):
        ir = InnerRegion('test', Box())
        assert ir.name == 'test'
        assert ir.shape == Box()
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0

    def test_absorb_charge(self):
        particle_in = Particle(123, -2.0, 1.0, Vec3d(0, 0, 0), Vec3d(0, 0, 0))
        particle_out = Particle(123, 1.0, 1.0, Vec3d(10, 10, 10), Vec3d(0, 0, 0))
        ir = InnerRegion('test', Box())
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0
        ir.check_if_particle_inside_and_count_charge(particle_out)
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0
        ir.check_if_particle_inside_and_count_charge(particle_in)
        assert ir.total_absorbed_particles == 1
        assert ir.total_absorbed_charge == -2
