import sys
import numpy as np

from Vec3d import Vec3d

class GeometricPrimitive:

    def __init__(self):
        self.primitive = None
        self.expression = None


    @classmethod
    def init_from_string_dispatch(cls, expression):
        # todo: avoid adding new shapes manually
        for primcls in [Box, CylinderAlongAxis, TubeAlongAxis, Sphere, Cone]:
            newobj = primcls.init_primitive_from_string(expression)
            if newobj:
                return newobj
        print("Can't init Primitive from expression: ", expression)
        print("Aborting")
        sys.exit(-1)


    @classmethod
    def init_primitive_from_string(cls, expression):
        # virtual method
        raise NotImplementedError()


    def check_if_point_inside(self, point):
        # virtual method
        raise NotImplementedError()


    def generate_random_point_uniform(self, random_in_range_function):
        # virtual method
        raise NotImplementedError()


    def write_hdf5_attributes(self, h5group):
        # virtual method
        raise NotImplementedError()



class Box(GeometricPrimitive):

    def __init__(self, center=(0, 0, 0), size=(1, 1, 1)):
        super().__init__()
        self.center = center
        self.size = size
        self.x_left = center[0] + size[0] / 2
        self.x_right = center[0] - size[0] / 2
        self.y_top = center[1] + size[1] / 2
        self.y_bottom = center[1] - size[1] / 2
        self.z_far = center[2] + size[2] / 2
        self.z_near = center[2] - size[2] / 2


    def check_if_point_inside(self, point):
        inside = (point.x <= self.x_left) and (point.x >= self.x_right)
        inside = inside and (point.y <= self.y_top) and (point.y >= self.y_bottom)
        inside = inside and (point.z <= self.z_far) and (point.z >= self.z_near)
        return inside


    def generate_random_point_uniform(self, random_in_range_function):
        p = Vec3d(random_in_range_function(self.x_left, self.x_right),
                  random_in_range_function(self.y_bottom, self.y_top),
                  random_in_range_function(self.z_near, self.z_far))
        return p


    def write_hdf5_attributes(self, h5group):
        # virtual method
        raise NotImplementedError()


class CylinderAlongAxis(GeometricPrimitive):

    def __init__(self, start=(0, 0, 0), length=1, radius=1, axis='z'):
        super().__init__()
        self.start = Vec3d(*start) # '*' unrolls tuple
        self.length = length
        self.axis = axis
        self.radius = radius


    def check_if_point_inside(self, point):
        shifted = point - self.start
        point_r = None
        if self.axis == 'z':
            if (shifted.z >= 0) and (shifted.z <= self.length):
                point_r_sqr = shifted.x**2 + shifted.y**2
        elif self.axis == 'y':
            if (shifted.y >= 0) and (shifted.y <= self.length):
                point_r_sqr = shifted.x**2 + shifted.z**2
        elif self.axis == 'x':
            if (shifted.x >= 0) and (shifted.x <= self.length):
                point_r_sqr = shifted.y**2 + shifted.z**2
        else:
            print("Unexpected axis; aborting")
            sys.exit(-1)
        inside = point_r and point_r <= self.radius * self.radius
        return inside


    def uniform_position_in_cylinder(self, random_in_range_function):
        r = np.sqrt(random_in_range_function(0.0, 1.0)) * self.radius
        phi = random_in_range_function(0.0, 2.0 * np.pi)
        along_axis = random_in_range_function(0.0, self.length)
        #
        if self.axis == 'z':
            x = self.start.x + r * np.cos(phi)
            y = self.start.y + r * np.sin(phi)
            z = self.start.z + along_axis
        elif self.axis == 'y':
            x = self.start.x + r * np.cos(phi)
            y = self.start.y + along_axis
            z = self.start.z + r * np.sin(phi)
        elif self.axis == 'x':
            x = self.start.x + along_axis
            y = self.start.y + r * np.sin(phi)
            z = self.start.z + r * np.cos(phi)
        else:
            print("Unexpected axis; aborting")
            sys.exit(-1)
        return Vec3d(x, y, z)



class TubeAlongAxis(GeometricPrimitive):

    def __init__(self, start=(0, 0, 0), length=1,
                 inner_radius=1, outer_radius=2, axis='z'):
        super().__init__()
        self.start = Vec3d(*start) # '*' unrolls tuple
        self.length = length
        self.axis = axis
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius


    def check_if_point_inside(self, point):
        shifted = point - self.start
        point_r = None
        if self.axis == 'z':
            if (shifted.z >= 0) and (shifted.z <= self.length):
                point_r_sqr = shifted.x**2 + shifted.y**2
        elif self.axis == 'y':
            if (shifted.y >= 0) and (shifted.y <= self.length):
                point_r_sqr = shifted.x**2 + shifted.z**2
        elif self.axis == 'x':
            if (shifted.x >= 0) and (shifted.x <= self.length):
                point_r_sqr = shifted.y**2 + shifted.z**2
        else:
            print("Unexpected axis; aborting")
            sys.exit(-1)
        inside = point_r and (point_r_sqr >= self.inner_radius * self.inner_radius) \
                 and (point_r_sqr <= self.outer_radius * self.outer_radius)
        return inside


    def uniform_position_in_tube(self, random_in_range_function):
        r = np.sqrt(random_in_range_function(self.inner_radius / self.outer_radius, 1.0)) \
            * self.outer_radius
        phi = random_in_range_function(0.0, 2.0 * np.pi)
        along_axis = random_in_range_function(0.0, self.length)
        #
        if self.axis == 'z':
            x = self.start.x + r * np.cos(phi)
            y = self.start.y + r * np.sin(phi)
            z = self.start.z + along_axis
        elif self.axis == 'y':
            x = self.start.x + r * np.cos(phi)
            y = self.start.y + along_axis
            z = self.start.z + r * np.sin(phi)
        elif self.axis == 'x':
            x = self.start.x + along_axis
            y = self.start.y + r * np.sin(phi)
            z = self.start.z + r * np.cos(phi)
        else:
            print("Unexpected axis; aborting")
            sys.exit(-1)
        return Vec3d(x, y, z)



class Sphere(GeometricPrimitive):

    def __init__(self, center=(0, 0, 0), radius=1):
        super().__init__()
        self.center = Vec3d(*center) # '*' unrolls tuple
        self.radius = radius


    def check_if_point_inside(self, point):
        shifted = point - self.center
        point_r = shifted.x**2 + shifted.y**2 + shifted.z**2
        return point_r <= self.radius * self.radius


    def uniform_position_in_sphere(self, random_in_range_function):
        # http://mathworld.wolfram.com/SpherePointPicking.html
        r = np.sqrt(random_in_range_function(0.0, 1.0)) * self.radius
        theta = random_in_range_function(0.0, 2.0 * np.pi)
        u = random_in_range_function(-1.0, 1.0)
        x = r * np.sqrt(1.0 - u*u) * np.cos(theta)
        y = r * np.sqrt(1.0 - u*u) * np.sin(theta)
        z = r * u
        return Vec3d(x, y, z)


class Cone(GeometricPrimitive):
    def __init__(self, start=(0, 0, 0), end=(0, 0, 1),
                 start_radii=(1, 2), end_radii=(3, 4)):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.start_radii = np.array(start_radii, np.float)
        self.end_radii = np.array(end_radii, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cone(self.start, self.end,
                             self.start_radii, self.end_radii, **kwargs)
