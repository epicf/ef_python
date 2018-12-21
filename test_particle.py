import h5py

import physical_constants
from Particle import Particle
from Vec3d import Vec3d


class TestParticle:
    def test_h5(self, tmpdir):
        fname = tmpdir.join('test_particle.h5')
        p1 = Particle(123, -1.0, 2.0, Vec3d(0., 0., 1.), Vec3d(1., 0., 2.))
        with h5py.File(fname, mode="w") as h5file:
            p1.save_h5(h5file)
        with h5py.File(fname, mode="r") as h5file:
            p2 = Particle.load_h5(h5file)
        assert p1 == p2

    def test_update_position(self):
        p = Particle(123, -1.0, 2.0, Vec3d(0., 0., 1.), Vec3d(1., 0., 3.))
        p.update_position(10.0)
        assert p.position == Vec3d(5., 0., 16.)

    def test_field_at_point(self):
        p = Particle(123, -16.0, 2.0, Vec3d(0., 0., 1.), Vec3d(1., 0., 3.))
        assert p.field_at_point(Vec3d(2., 0., 1.)) == Vec3d(-4, 0, 0)
        assert p.field_at_point(Vec3d(0., 0., 1.)) is None # TODO: return zero so that total field does not break?

    def test_update_momentum_no_mgn(self):
        p = Particle(123, -1.0, 2.0, Vec3d(0., 0., 1.), Vec3d(1., 0., 3.))
        p.boris_update_momentum_no_mgn(0.1, Vec3d(-1.0, 2.0, 3.0))
        assert p.momentum == Vec3d(1.1, -0.2, 2.7)

    def test_update_momentum(self):
        p = Particle(123, -1.0, 2.0, Vec3d(0., 0., 1.), Vec3d(1., 0., 3.))
        p.boris_update_momentum(0.1, Vec3d(-1.0, 2.0, 3.0), Vec3d(0, 0, 0))
        assert p.momentum == Vec3d(1.1, -0.2, 2.7)

        p = Particle(123, -1.0, 2.0, Vec3d(0., 0., 1.), Vec3d(1., 0., 3.))
        p.boris_update_momentum(2, Vec3d(-1.0, 2.0, 3.0), Vec3d(2, 0, 0).times_scalar(
            physical_constants.speed_of_light))
        assert p.momentum == Vec3d(3, -2, -5)
