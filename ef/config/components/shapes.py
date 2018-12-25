from math import sqrt, copysign

from ef.util.serializable_h5 import SerializableH5

__all__ = ['Shape', 'Box', 'Cylinder', 'Tube', 'Sphere', 'Cone']

import numpy as np

from ef.config.component import ConfigComponent
from Vec3d import Vec3d


class Shape(ConfigComponent, SerializableH5):
    def visualize(self, visualizer, **kwargs):
        raise NotImplementedError()

    def is_point_inside(self, point):
        raise NotImplementedError()

    def generate_uniform_random_point(self, generator):
        raise NotImplementedError()


class Box(Shape):
    def __init__(self, origin=(0, 0, 0), size=(1, 1, 1)):
        self.origin = np.array(origin, np.float)
        self.size = np.array(size, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_box(self.size, self.origin, **kwargs)

    def is_point_inside(self, point):
        return np.all(point >= self.origin) and np.all(point <= self.origin + self.size)

    def generate_uniform_random_point(self, generator):
        return np.array([generator.uniform(self.origin[i], self.origin[i] + self.size[i]) for i in range(3)])


class Cylinder(Shape):
    def __init__(self, start=(0, 0, 0), end=(1, 0, 0), radius=1):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.r = float(radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cylinder(self.start, self.end, self.r, **kwargs)

    def is_point_inside(self, point):
        pointvec = point - self.start
        axisvec = self.end - self.start
        axis = np.linalg.norm(axisvec)
        unit_axisvec = axisvec / axis
        projection = np.dot(pointvec, unit_axisvec)
        perp_to_axis = pointvec - unit_axisvec * projection
        return 0 <= projection <= axis and np.linalg.norm(perp_to_axis) <= self.r

    def generate_uniform_random_point(self, generator):
        # random point in cylinder along z
        cyl_axis = Vec3d(*(self.end - self.start))
        cyl_axis_length = cyl_axis.length()
        r = sqrt(generator.uniform(0.0, 1.0)) * self.r
        phi = generator.uniform(0.0, 2.0 * np.pi)
        z = generator.uniform(0.0, cyl_axis_length)
        #
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        z = z
        random_pnt_in_cyl_along_z = Vec3d(x, y, z)
        # rotate:
        # see "https://en.wikipedia.org/wiki/Rodrigues'_rotation_formula"
        # todo: Too complicated. Try rejection sampling.
        unit_cyl_axis = cyl_axis.normalized()
        unit_along_z = Vec3d(0, 0, 1.0)
        rotation_axis = unit_along_z.cross_product(unit_cyl_axis)
        rotation_axis_length = rotation_axis.length()
        if rotation_axis_length == 0:
            if copysign(1.0, unit_cyl_axis.z) >= 0:
                random_pnt_in_rotated_cyl = random_pnt_in_cyl_along_z
            else:
                random_pnt_in_rotated_cyl = random_pnt_in_cyl_along_z.negate()
        else:
            unit_rotation_axis = rotation_axis.normalized()
            rot_cos = unit_cyl_axis.dot_product(unit_along_z)
            rot_sin = rotation_axis_length
            random_pnt_in_rotated_cyl = \
                random_pnt_in_cyl_along_z.times_scalar(rot_cos) + \
                unit_rotation_axis.cross_product(random_pnt_in_cyl_along_z) * rot_sin + \
                unit_rotation_axis.times_scalar(
                    (1 - rot_cos) *
                    unit_rotation_axis.dot_product(random_pnt_in_cyl_along_z))
            # shift:
        shifted = random_pnt_in_rotated_cyl.add(Vec3d(*self.start))
        return np.array(shifted)


class Tube(Shape):
    def __init__(self, start=(0, 0, 0), end=(1, 0, 0), inner_radius=1, outer_radius=2):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.r = float(inner_radius)
        self.R = float(outer_radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_tube(self.start, self.end, self.r, self.R, **kwargs)

    def is_point_inside(self, point):
        pointvec = point - self.start
        axisvec = self.end - self.start
        axis = np.linalg.norm(axisvec)
        unit_axisvec = axisvec / axis
        projection = np.dot(pointvec, unit_axisvec)
        perp_to_axis = pointvec - unit_axisvec * projection
        return 0 <= projection <= axis and self.r <= np.linalg.norm(perp_to_axis) <= self.R

    def generate_uniform_random_point(self, generator):
        # random point in tube along z
        cyl_axis = Vec3d(*(self.end - self.start))
        cyl_axis_length = cyl_axis.length()
        r = sqrt(generator.uniform(self.r / self.R, 1.0)) \
            * self.R
        phi = generator.uniform(0.0, 2.0 * np.pi)
        z = generator.uniform(0.0, cyl_axis_length)
        #
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        z = z
        random_pnt_in_cyl_along_z = Vec3d(x, y, z)
        # rotate:
        # see "https://en.wikipedia.org/wiki/Rodrigues'_rotation_formula"
        # todo: Too complicated. Try rejection sampling.
        unit_cyl_axis = cyl_axis.normalized()
        unit_along_z = Vec3d(0, 0, 1.0)
        rotation_axis = unit_along_z.cross_product(unit_cyl_axis)
        rotation_axis_length = rotation_axis.length()
        if rotation_axis_length == 0:
            if copysign(1.0, unit_cyl_axis.z) >= 0:
                random_pnt_in_rotated_cyl = random_pnt_in_cyl_along_z
            else:
                random_pnt_in_rotated_cyl = random_pnt_in_cyl_along_z.negate()
        else:
            unit_rotation_axis = rotation_axis.normalized()
            rot_cos = unit_cyl_axis.dot_product(unit_along_z)
            rot_sin = rotation_axis_length
            random_pnt_in_rotated_cyl = \
                random_pnt_in_cyl_along_z.times_scalar(rot_cos) + \
                unit_rotation_axis.cross_product(random_pnt_in_cyl_along_z) * rot_sin + \
                unit_rotation_axis.times_scalar(
                    (1 - rot_cos) *
                    unit_rotation_axis.dot_product(random_pnt_in_cyl_along_z))
        # shift:
        shifted = random_pnt_in_rotated_cyl.add(
            Vec3d(*self.start))
        return np.array(shifted)


class Sphere(Shape):
    def __init__(self, origin=(0, 0, 0), radius=1):
        self.origin = np.array(origin)
        self.r = float(radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_sphere(self.origin, self.r, **kwargs)

    def is_point_inside(self, point):
        return np.linalg.norm(point - self.origin) <= self.r

    def generate_uniform_random_point(self, generator):
        while True:
            p = np.array([generator.uniform(0, 1) for i in range(3)]) * self.r + self.origin
            if self.is_point_inside(p):
                break
        return p


class Cone(Shape):
    def __init__(self, start=(0, 0, 0, 1),
                 start_radii=(1, 2), end_radii=(3, 4)):
        self.start = np.array(start, np.float)
        self.start_radii = np.array(start_radii, np.float)
        self.end_radii = np.array(end_radii, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cone(self.start, self.end,
                             self.start_radii, self.end_radii, **kwargs)

# TODO: def is_point_inside(self, point)
