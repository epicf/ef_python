import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

from ExternalFieldExpression import ExternalFieldExpression
from ExternalFieldFromFile import ExternalFieldFromFile
from ExternalFieldUniform import ExternalFieldUniform
from ExternalFieldsManager import ExternalFieldsManager
from Vec3d import Vec3d


class TestFields:

    def test_uniform(self):
        f = ExternalFieldUniform('u1', 'electric', np.array((3.14, 2.7, -0.5)))
        assert_array_equal(f.field_at_position(Vec3d(1, 2, 3), 0.), Vec3d(3.14, 2.7, -0.5))
        assert_array_equal(f.field_at_position(Vec3d(1, 2, 3), 5.), Vec3d(3.14, 2.7, -0.5))
        assert_array_equal(f.field_at_position(Vec3d(3, 2, 1), 5.), Vec3d(3.14, 2.7, -0.5))
        m = ExternalFieldsManager([f], [f, f])
        assert_array_almost_equal(m.total_electric_field_at_position((0, 0, 0), 2), Vec3d(3.14, 2.7, -0.5))
        assert_array_almost_equal(m.total_magnetic_field_at_position((1, 2, 3), 5), Vec3d(6.28, 5.4, -1))

    def test_expression(self):
        f = ExternalFieldExpression('e1', 'electric', '-1+t', 'x*y-z', 'x+y*z')
        assert_array_equal(f.field_at_position(Vec3d(1, 2, 3), 0.), Vec3d(-1, -1, 7))
        assert_array_equal(f.field_at_position(Vec3d(1, 2, 3), 5.), Vec3d(4, -1, 7))
        assert_array_equal(f.field_at_position(Vec3d(3, 2, 1), 5.), Vec3d(4, 5, 5))
        m = ExternalFieldsManager([f], [])
        assert_array_almost_equal(m.total_electric_field_at_position((1, 2, 3), 0), Vec3d(-1, -1, 7))
        assert_array_almost_equal(m.total_electric_field_at_position((1, 2, 3), 5), Vec3d(4, -1, 7))
        assert_array_almost_equal(m.total_electric_field_at_position((3, 2, 1), 5), Vec3d(4, 5, 5))

    def test_from_file(self):
        f = ExternalFieldFromFile('f1', 'electric', 'examples/test_field.csv')
        assert_array_equal(f.field_at_position(Vec3d(0, 0, 0), 0.), Vec3d(1, 1, 1))
        assert_array_equal(f.field_at_position(Vec3d(1, 1, 1), 5.), Vec3d(-1, -1, -1))
        assert_array_equal(f.field_at_position(Vec3d(1, 0, 1), 5.), Vec3d(3, 2, 1))
        assert_array_equal(f.field_at_position(Vec3d(.5, .5, .5), 10), Vec3d(1, 1, 1))
        assert_array_almost_equal(f.field_at_position(Vec3d(.5, 1., .3), 10.), (0., .5, 1.))
        assert_array_almost_equal(f.field_at_position(Vec3d(0, .5, .7), 10), (1, 1.5, 2))
        m = ExternalFieldsManager([f], [])
        assert_array_almost_equal(m.total_electric_field_at_position((.5, 1., .3), 10.), Vec3d(0, .5, 1))
        assert_array_almost_equal(m.total_electric_field_at_position((0, .5, .7), 10), Vec3d(1, 1.5, 2))

    def test_manager(self):
        u = ExternalFieldUniform('u1', 'electric', np.array((3.14, 2.7, -0.5)))
        e = ExternalFieldExpression('e1', 'electric', '-1+t', 'x*y-z', 'x+y*z')
        f = ExternalFieldFromFile('f1', 'electric', 'examples/test_field.csv')
        m = ExternalFieldsManager([u, e, f], [e, u, f])
        assert_array_almost_equal(m.total_electric_field_at_position((.5, 1., .3), 10.), Vec3d(12.14, 3.4, 1.3))
        assert_array_almost_equal(m.total_magnetic_field_at_position((.5, 1., .3), 10.), Vec3d(12.14, 3.4, 1.3))
