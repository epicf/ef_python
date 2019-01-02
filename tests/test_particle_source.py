import h5py
import numpy as np

from ef.particle_source import ParticleSource
from ef.config.components import Box


class TestParticleSource:
    def test_h5(self, tmpdir):
        fname = tmpdir.join('test_particle_source.h5')
        p1 = ParticleSource("test", Box(), 120, 5, np.array((1, 0, 0)), 0, -1, 2)
        with h5py.File(fname, mode="w") as h5file:
            p1.save_h5(h5file)
        with h5py.File(fname, mode="r") as h5file:
            p2 = ParticleSource.load_h5(h5file)
        assert p1 == p2

    def test_h5_with_particles(self, tmpdir):
        fname = tmpdir.join('test_particle_source.h5')
        p1 = ParticleSource("test", Box(), 120, 5, np.array((1, 0, 0)), 0, -1, 2)
        p1.generate_initial_particles()
        with h5py.File(fname, mode="w") as h5file:
            p1.save_h5(h5file)
        with h5py.File(fname, mode="r") as h5file:
            p2 = ParticleSource.load_h5(h5file)
        assert p1 == p2

    def test_generate(self):
        p1 = ParticleSource("test", Box(), 120, 5, np.array((1, 0, 0)), 200, -1, 2)
        p2 = ParticleSource("test", Box(), 120, 5, np.array((1, 0, 0)), 200, -1, 2)
        p3 = ParticleSource("test", Box(), 120, 5, np.array((1, 0, 0)), 200, -1, 2)
        p3._generator.set_state(p1._generator.get_state())
        p1.generate_initial_particles()
        p2.generate_initial_particles()
        p3.generate_initial_particles()
        assert p1 != p2
        assert p1 == p3
        p3.generate_each_step()
        assert p1 != p3
        p1.generate_each_step()
        assert p1 == p3
