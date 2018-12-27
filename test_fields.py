import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

from ExternalFieldExpression import ExternalFieldExpression
from ExternalFieldFromFile import ExternalFieldFromFile
from ExternalFieldUniform import ExternalFieldUniform


class TestFields:

    def test_uniform(self):
        f = ExternalFieldUniform('u1', 'electric', np.array((3.14, 2.7, -0.5)))
        assert_array_equal(f.field_at_position((1, 2, 3), 0.), (3.14, 2.7, -0.5))
        assert_array_equal(f.field_at_position((1, 2, 3), 5.), (3.14, 2.7, -0.5))
        assert_array_equal(f.field_at_position((3, 2, 1), 5.), (3.14, 2.7, -0.5))

    def test_expression(self):
        f = ExternalFieldExpression('e1', 'electric', '-1+t', 'x*y-z', 'x+y*z')
        assert_array_equal(f.field_at_position((1, 2, 3), 0.), (-1, -1, 7))
        assert_array_equal(f.field_at_position((1, 2, 3), 5.), (4, -1, 7))
        assert_array_equal(f.field_at_position((3, 2, 1), 5.), (4, 5, 5))

    def test_from_file(self):
        f = ExternalFieldFromFile('f1', 'electric', 'examples/test_field.csv')
        assert_array_equal(f.field_at_position((0, 0, 0), 0.), (1, 1, 1))
        assert_array_equal(f.field_at_position((1, 1, 1), 5.), (-1, -1, -1))
        assert_array_equal(f.field_at_position((1, 0, 1), 5.), (3, 2, 1))
        assert_array_equal(f.field_at_position((.5, .5, .5), 10), (1, 1, 1))
        assert_array_almost_equal(f.field_at_position((.5, 1., .3), 10.), (0., .5, 1.))
        assert_array_almost_equal(f.field_at_position((0, .5, .7), 10), (1, 1.5, 2))
