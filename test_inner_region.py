from InnerRegion import InnerRegion
from Particle import Particle
from ef.config.components import Box


class TestInnerRegion:
    def test_init(self):
        ir = InnerRegion('test', Box())
        assert ir.name == 'test'
        assert ir.shape == Box()
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0

    def test_absorb_charge(self):
        particle_in = Particle(123, -2.0, 1.0, (0, 0, 0), (0, 0, 0))
        particle_out = Particle(123, 1.0, 1.0, (10, 10, 10), (0, 0, 0))
        ir = InnerRegion('test', Box())
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0
        ir.check_if_particle_inside_and_count_charge(particle_out)
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0
        ir.check_if_particle_inside_and_count_charge(particle_in)
        assert ir.total_absorbed_particles == 1
        assert ir.total_absorbed_charge == -2
