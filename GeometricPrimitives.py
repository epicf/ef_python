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
        for primcls in [Box, CylinderAlongAxis, TubeAlongAxis, Sphere, ConeTubeAlongAxis]:
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


    @classmethod
    def init_primitive_from_hdf5(cls, h5field):
        # virtual method
        raise NotImplementedError()


    def check_if_point_inside(self, point):
        # virtual method
        raise NotImplementedError()


    def generate_random_point_uniform(self, random_in_range_function):
        # virtual method
        raise NotImplementedError()


    def write_hdf5_attributes(self, h5field):
        # virtual method
        raise NotImplementedError()


    @staticmethod
    def get_classname(expression):
        tmp = expression.split('(', 1)
        if len(tmp) < 2:
            raise SyntaxError("Can't get class from expression '{}'".format(expression))
        clsname, rest = tmp
        rest = rest.rsplit(')', 1)[0]
        return clsname, rest


    @staticmethod
    def get_args_as_key_value(expression):
        result = {}
        while expression:
            key, val, expression = GeometricPrimitive.get_keyvalue_pair(expression)
            result[key] = val
        return result


    @staticmethod
    def get_keyvalue_pair(expression):
        tmp = expression.split('=', 1)
        if len(tmp) < 2:
            raise SyntaxError("Can't get key from expression '{}'".format(expression))
        key, rest = tmp
        if rest.lstrip()[0] == '(':
            # val is tuple
            val, rest = rest.split(')', 1)
            val = val + ')'
            tmp = rest.split(',', 1)
            if len(tmp) < 2:
                rest = None
            else:
                rest = tmp[1]
        else:
            # val is number or string
            tmp = rest.split(',', 1)
            val = tmp[0]
            if len(tmp) < 2:
                rest = None
            else:
                rest = tmp[1]
        return key, val, rest


    @staticmethod
    def parse_number_or_tuple_of_numbers(expression):
        if expression.lstrip()[0] == '(':
            expression = expression.lstrip(' (')
            expression = expression.rsplit(')', 1)[0]
            result = []
            while expression:
                tmp = expression.split(',', 1)
                if len(tmp) < 2:
                    expression = None
                else:
                    expression = tmp[1]
                number = GeometricPrimitive.parse_number(tmp[0])
                result.append(number)
                result = tuple(result)
        else:
            result = GeometricPrimitive.parse_number(expression)
        return result


    @staticmethod
    def parse_number(expression):
        expression = expression.lstrip()
        if expression[0].isdigit():
            result = float(expression)
            return result
        else:
            raise SyntaxError("Can't interpret as a number: '{}'".format(expression))


    @staticmethod
    def parse_string(expression):
        expression = expression.lstrip()
        expression = expression.rstrip()
        if expression[0] == '"' or expression[0] == "'":
            result = expression[1:-1].decode("string-escape")
            return result
        else:
            raise SyntaxError("Can't interpret expression as string: '{}'".format(expression))



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


    @classmethod
    def init_primitive_from_string(cls, expression):
        # virtual method
        raise NotImplementedError()


    @classmethod
    def init_primitive_from_hdf5(cls, h5field):
        # todo: do something with construction procedure
        x_left = h5field.attrs["x_left"]
        x_right = h5field.attrs["x_right"]
        y_top = h5field.attrs["y_top"]
        y_bottom = h5field.attrs["y_bottom"]
        z_far = h5field.attrs["z_far"]
        z_near = h5field.attrs["z_near"]
        center = ((x_left + x_right)/2, (y_top + y_bottom)/2, (z_far + z_near)/2)
        size = (x_left - x_right, y_top - y_bottom, z_far - z_near)
        newobj = cls(center=center, size=size)
        newobj.primitive = h5field.attrs["primitive"]
        newobj.expression = h5field.attrs["expression"]
        return newobj


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


    def write_hdf5_attributes(self, h5field):
        h5field.attrs.create("primitive", self.primitive)
        h5field.attrs.create("expression", self.expression)
        h5field.attrs.create("x_left", self.x_left)
        h5field.attrs.create("x_right", self.x_right)
        h5field.attrs.create("y_top", self.y_top)
        h5field.attrs.create("y_bottom", self.y_bottom)
        h5field.attrs.create("z_far", self.z_far)
        h5field.attrs.create("z_near", self.z_near)


class CylinderAlongAxis(GeometricPrimitive):

    def __init__(self, start=(0, 0, 0), length=1, radius=1, axis='z'):
        super().__init__()
        self.start = Vec3d(*start) # '*' unrolls tuple
        self.length = length
        self.axis = axis
        self.radius = radius


    def check_if_point_inside(self, point):
        shifted = point - self.start
        point_r_sqr = None
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
        inside = point_r_sqr and point_r_sqr <= self.radius * self.radius
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


    def write_hdf5_attributes(self, h5field):
        h5field.attrs.create("primitive", self.primitive)
        h5field.attrs.create("expression", self.expression)
        h5field.attrs.create("start_x", self.start.x)
        h5field.attrs.create("start_y", self.start.y)
        h5field.attrs.create("start_z", self.start.z)
        h5field.attrs.create("length", self.length)
        h5field.attrs.create("radius", self.radius)
        h5field.attrs.create("axis", self.axis)


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
        point_r_sqr = None
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
        inside = point_r_sqr and (point_r_sqr >= self.inner_radius * self.inner_radius) \
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


    def write_hdf5_attributes(self, h5field):
        h5field.attrs.create("primitive", self.primitive)
        h5field.attrs.create("expression", self.expression)
        h5field.attrs.create("start_x", self.start.x)
        h5field.attrs.create("start_y", self.start.y)
        h5field.attrs.create("start_z", self.start.z)
        h5field.attrs.create("length", self.length)
        h5field.attrs.create("inner_radius", self.inner_radius)
        h5field.attrs.create("outer_radius", self.outer_radius)
        h5field.attrs.create("axis", self.axis)



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


    def write_hdf5_attributes(self, h5field):
        h5field.attrs.create("primitive", self.primitive)
        h5field.attrs.create("expression", self.expression)
        h5field.attrs.create("center_x", self.center.x)
        h5field.attrs.create("center_y", self.center.y)
        h5field.attrs.create("center_z", self.center.z)
        h5field.attrs.create("radius", self.radius)


class ConeTubeAlongAxis(GeometricPrimitive):

    def __init__(self, start=(0, 0, 0), length=1,
                 start_radii=(1, 2), end_radii=(3, 4), axis='z'):
        super().__init__()
        self.start = Vec3d(*start)
        self.length = length
        self.start_radii = start_radii
        self.end_radii = end_radii
        self.axis = axis


    # @staticmethod
    # def point_inside_cone(axis_x, axis_y, axis_start_z, axis_end_z,
    #                       r_start, r_end, x, y, z):
    #     z_len = abs(axis_end_z - axis_start_z)
    #     x_dist = x - axis_x
    #     y_dist = y - axis_y
    #     if z < axis_start_z:
    #         return False
    #     if z > axis_end_z:
    #         return False
    #     if r_start < r_end:
    #         tg_a = (r_end - r_start) / z_len
    #         z_dist = abs(z - axis_start_z)
    #         r = z_dist * tg_a + r_start
    #     else:
    #         tg_a = (r_start - r_end) / z_len
    #         z_dist = abs(z - axis_end_z)
    #         r = z_dist * tg_a + r_end
    #     if r * r > x_dist * x_dist + y_dist * y_dist:
    #         return False
    #     return True


    # def check_if_point_inside(self, x, y, z):
    #     in_outer = self.point_inside_cone(self.axis_x, self.axis_y,
    #                                       self.axis_start_z, self.axis_end_z,
    #                                       self.start_outer_radius, self.end_outer_radius,
    #                                       x, y, z)
    #     if not in_outer: return False
    #     in_inner = self.point_inside_cone(self.axis_x, self.axis_y,
    #                                       self.axis_start_z, self.axis_end_z,
    #                                       self.start_inner_radius, self.end_inner_radius,
    #                                       x, y, z)
    #     if in_inner: return False
    #     return True
