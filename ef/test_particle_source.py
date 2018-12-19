import h5py

from ParticleSource import ParticleSource
from Vec3d import Vec3d
from ef.config.components import Box


class TestParticleSource:
    def test_h5(self, tmpdir):
        fname = tmpdir.join('test_particle_source.h5')
        p1 = ParticleSource("test", Box(), 120, 5, Vec3d(1, 0, 0), 0, -1, 2)
        with h5py.File(fname, mode="w") as h5file:
            p1.save_h5(h5file)
        with h5py.File(fname, mode="r") as h5file:
            p2 = ParticleSource.load_h5(h5file)
        assert p1 == p2
