import numpy as np
from numpy.random import RandomState
from numpy.testing import assert_array_equal

from ef.config.components import Cylinder, Tube
from ef.config.components.shapes import Box, Sphere


def test_box_positions_in():
    b = Box((0, 2, 4), (2, 2, 2))
    # check that non-array call works
    assert b.are_positions_inside((1, 3, 5))
    assert not b.are_positions_inside((-1, 3, 5))
    assert_array_equal(b.are_positions_inside(
        np.array([
            (1, 3, 5), (0.5, 2.5, 5.5),
            (0, 2, 4), (2, 4, 6), (0, 3, 5), (1, 2, 6),
            (-1, 3, 5), (3, 3, 5), (1, 0, 5), (1, 5, 5), (1, 3, 2), (1, 3, 9),
            (10, -10, 10), (0, 0, 0)])),
        [1, 1,  # in the box
         1, 1, 1, 1,  # on the surface
         0, 0, 0, 0, 0, 0,  # far on one axis
         0, 0])  # far on all axes


def test_sphere_positions_in():
    s = Sphere((2, 0, 0), 1)

    # check that non-array call works
    assert s.are_positions_inside((2, 0, 0))
    assert not s.are_positions_inside((2.8, -0.8, 0.8))

    assert_array_equal(s.are_positions_inside(
        np.array([(2, 0, 0), (2.3, 0.2, -0.3),
                  (1, 0, 0), (3, 0, 0), (2, 1, 0), (2, -1, 0), (2, 0, 1), (2, 0, -1),
                  (2, 0, -2), (1, 1, 0), (4, 0, 0),
                  (3, 4, 5), (3, -4, 5),
                  (2.5, 0.5, -0.5), (2.8, -0.8, 0.8)])),
        [1, 1,  # inside the sphere
         1, 1, 1, 1, 1, 1,  # on the surface
         0, 0, 0,  # far on one axis
         0, 0,  # far on all axes
         1, 0])  # on the diagonal


def test_cylinder_positions_in():
    c = Cylinder((2, 2, -2), (5, 2, 2), 5)

    # check that non-array call works
    assert c.are_positions_inside((3, 2, 0))
    assert not c.are_positions_inside((3, 10, 0))

    # assert c.are_positions_inside((-2.0, 2, 1))  - does not work without exact floating point
    # assert c.are_positions_inside((6.0, 2, -5)) - does not work without exact floating point
    # assert c.are_positions_inside((1, 2, 5)) - does not work without exact floating point

    assert_array_equal(c.are_positions_inside(np.array([
        (3, 2, 0), (4, 1, 1),
        (3, 10, 0), (3, -10, 0), (3, 2, 10), (3, 2, -10), (10, 2, 0), (-10, 2, 0),
        (-1.9, 2, 1), (-2.1, 2, 1), (-2.0, 2, 0.9), (-2.0, 2, 1.1), (-2.0, 1.9, 1), (-2.0, 2.1, 1),
        (6, 2, -4.9), (6, 2, -5.1), (6.1, 2, -5), (5.9, 2, -5), (6, 1.9, -5), (6, 2.1, -5),
        (1, 2, 4.9), (1, 2, 5.1), (1.1, 2, 5), (0.9, 2, 5), (1, 1.9, 5), (1, 2.1, 5)])),
        [1, 1,  # inside
         0, 0, 0, 0, 0, 0,  # far away
         1, 0, 0, 0, 0, 0,  # corners of the projection on y=2
         1, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0])


def test_tube_positions_in():
    t = Tube((2, 2, -2), (5, 2, 2), 2.5, 5)
    assert not t.are_positions_inside((3, 2, 0))
    assert t.are_positions_inside((0, 2, 1))

    # assert c.are_positions_inside((-2.0, 2, 1))  - does not work without exact floating point
    # assert c.are_positions_inside((6.0, 2, -5)) - does not work without exact floating point
    # assert c.are_positions_inside((1, 2, 5)) - does not work without exact floating point

    assert_array_equal(t.are_positions_inside(np.array([
        (3, 2, 0), (4, 1, 1),
        (0, 2, 1), (2, 2, 4), (5, 2, -3), (7, 2, 0), (3, 6, 0), (3, -1, 0),
        (3, 10, 0), (3, -10, 0), (3, 2, 10), (3, 2, -10), (10, 2, 0), (-10, 2, 0),
        (-1.9, 2, 1), (-2.1, 2, 1), (-2.0, 2, 0.9), (-2.0, 2, 1.1), (-2.0, 1.9, 1), (-2.0, 2.1, 1),
        (6, 2, -4.9), (6, 2, -5.1), (6.1, 2, -5), (5.9, 2, -5), (6, 1.9, -5), (6, 2.1, -5),
        (1, 2, 4.9), (1, 2, 5.1), (1.1, 2, 5), (0.9, 2, 5), (1, 1.9, 5), (1, 2.1, 5)])),
        [0, 0,  # inside innner cylinder
         1, 1, 1, 1, 1, 1,
         0, 0, 0, 0, 0, 0,  # far away
         1, 0, 0, 0, 0, 0,  # corners of the projection on y=2
         1, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0])


def test_generate_positions():
    for cls in Box, Sphere, Cylinder, Tube:
        shape = cls()
        for i in range(1000):
            point = shape.generate_uniform_random_position(RandomState(0))
            assert shape.are_positions_inside(point)

        points = shape.generate_uniform_random_posititons(RandomState(0), 100000)
        assert shape.are_positions_inside(points).all()
