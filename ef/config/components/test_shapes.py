from numpy.random import RandomState

from ef.config.components import Cylinder, Tube
from ef.config.components.shapes import Box, Sphere


def test_box_point_in():
    b = Box((0, 2, 4), (2, 2, 2))
    # in the box
    assert b.is_point_inside((1, 3, 5))
    assert b.is_point_inside((0.5, 2.5, 5.5))
    # on the surface
    assert b.is_point_inside((0, 2, 4))
    assert b.is_point_inside((2, 4, 6))
    assert b.is_point_inside((0, 3, 5))
    assert b.is_point_inside((1, 2, 6))
    # far on one axis
    assert not b.is_point_inside((-1, 3, 5))
    assert not b.is_point_inside((3, 3, 5))
    assert not b.is_point_inside((1, 0, 5))
    assert not b.is_point_inside((1, 5, 5))
    assert not b.is_point_inside((1, 3, 2))
    assert not b.is_point_inside((1, 3, 9))
    # far on all axis
    assert not b.is_point_inside((10, -10, 10))
    assert not b.is_point_inside((0, 0, 0))


def test_sphere_point_in():
    s = Sphere((2, 0, 0), 1)
    # inside the sphere
    assert s.is_point_inside((2, 0, 0))
    assert s.is_point_inside((2.3, 0.2, -0.3))
    # on the surface
    assert s.is_point_inside((1, 0, 0))
    assert s.is_point_inside((3, 0, 0))
    assert s.is_point_inside((2, 1, 0))
    assert s.is_point_inside((2, -1, 0))
    assert s.is_point_inside((2, 0, 1))
    assert s.is_point_inside((2, 0, -1))
    # far on one axis
    assert not s.is_point_inside((2, 0, -2))
    assert not s.is_point_inside((1, 1, 0))
    assert not s.is_point_inside((4, 0, 0))
    # far on all axis
    assert not s.is_point_inside((3, 4, 5))
    assert not s.is_point_inside((3, -4, 5))
    # in the "corner"
    assert s.is_point_inside((2.5, 0.5, -0.5))
    assert not s.is_point_inside((2.8, -0.8, 0.8))


def test_cylinder_point_in():
    c = Cylinder((2, 2, -2), (5, 2, 2), 5)
    # inside
    assert c.is_point_inside((3, 2, 0))
    assert c.is_point_inside((4, 1, 1))

    # far away
    assert not c.is_point_inside((3, 10, 0))
    assert not c.is_point_inside((3, -10, 0))
    assert not c.is_point_inside((3, 2, 10))
    assert not c.is_point_inside((3, 2, -10))
    assert not c.is_point_inside((10, 2, 0))
    assert not c.is_point_inside((-10, 2, 0))

    # corners of the projection on y=2
    # assert c.is_point_inside((-2.0, 2, 1))  - does not work without exact floating point
    assert c.is_point_inside((-1.9, 2, 1))
    assert not c.is_point_inside((-2.1, 2, 1))
    assert not c.is_point_inside((-2.0, 2, 0.9))
    assert not c.is_point_inside((-2.0, 2, 1.1))
    assert not c.is_point_inside((-2.0, 1.9, 1))
    assert not c.is_point_inside((-2.0, 2.1, 1))
    # assert c.is_point_inside((6.0, 2, -5)) - does not work without exact floating point
    assert c.is_point_inside((6, 2, -4.9))
    assert not c.is_point_inside((6, 2, -5.1))
    assert not c.is_point_inside((6.1, 2, -5))
    assert not c.is_point_inside((5.9, 2, -5))
    assert not c.is_point_inside((6, 1.9, -5))
    assert not c.is_point_inside((6, 2.1, -5))
    # assert c.is_point_inside((1, 2, 5)) - does not work without exact floating point
    assert c.is_point_inside((1, 2, 4.9))
    assert not c.is_point_inside((1, 2, 5.1))
    assert not c.is_point_inside((1.1, 2, 5))
    assert not c.is_point_inside((0.9, 2, 5))
    assert not c.is_point_inside((1, 1.9, 5))
    assert not c.is_point_inside((1, 2.1, 5))


def test_tube_point_in():
    t = Tube((2, 2, -2), (5, 2, 2), 2.5, 5)
    # inside innner cylinder
    assert not t.is_point_inside((3, 2, 0))
    assert not t.is_point_inside((4, 1, 1))

    # inside
    assert t.is_point_inside((0, 2, 1))
    assert t.is_point_inside((2, 2, 4))
    assert t.is_point_inside((5, 2, -3))
    assert t.is_point_inside((7, 2, 0))
    assert t.is_point_inside((3, 6, 0))
    assert t.is_point_inside((3, -1, 0))

    # far away
    assert not t.is_point_inside((3, 10, 0))
    assert not t.is_point_inside((3, -10, 0))
    assert not t.is_point_inside((3, 2, 10))
    assert not t.is_point_inside((3, 2, -10))
    assert not t.is_point_inside((10, 2, 0))
    assert not t.is_point_inside((-10, 2, 0))

    # corners of the projection on y=2
    # assert c.is_point_inside((-2.0, 2, 1))  - does not work without exact floating point
    assert t.is_point_inside((-1.9, 2, 1))
    assert not t.is_point_inside((-2.1, 2, 1))
    assert not t.is_point_inside((-2.0, 2, 0.9))
    assert not t.is_point_inside((-2.0, 2, 1.1))
    assert not t.is_point_inside((-2.0, 1.9, 1))
    assert not t.is_point_inside((-2.0, 2.1, 1))
    # assert c.is_point_inside((6.0, 2, -5)) - does not work without exact floating point
    assert t.is_point_inside((6, 2, -4.9))
    assert not t.is_point_inside((6, 2, -5.1))
    assert not t.is_point_inside((6.1, 2, -5))
    assert not t.is_point_inside((5.9, 2, -5))
    assert not t.is_point_inside((6, 1.9, -5))
    assert not t.is_point_inside((6, 2.1, -5))
    # assert c.is_point_inside((1, 2, 5)) - does not work without exact floating point
    assert t.is_point_inside((1, 2, 4.9))
    assert not t.is_point_inside((1, 2, 5.1))
    assert not t.is_point_inside((1.1, 2, 5))
    assert not t.is_point_inside((0.9, 2, 5))
    assert not t.is_point_inside((1, 1.9, 5))
    assert not t.is_point_inside((1, 2.1, 5))


def test_generate_point():
    for cls in Box, Sphere, Cylinder, Tube:
        shape = cls()
        for i in range(1000):
            point = shape.generate_uniform_random_point(RandomState(0))
            assert shape.is_point_inside(point)
