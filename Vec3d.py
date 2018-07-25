from math import sqrt

class Vec3d():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0, 0.0)


    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


    def negate(self):
        return Vec3d(-self.x, -self.y, -self.z)


    def __neg__(self):
        return self.negate()


    def add(self, v2):
        # todo: consider modify self inplace and return it
        return Vec3d(self.x + v2.x,
                     self.y + v2.y,
                     self.z + v2.z)


    def __add__(self, v2):
        return self.add(v2)


    def sub(self, v2):
        return Vec3d(self.x - v2.x,
                     self.y - v2.y,
                     self.z - v2.z)


    def __sub__(self, v2):
        return self.sub(v2)


    def dot_product(self, v2):
        return (self.x * v2.x +
                self.y * v2.y +
                self.z * v2.z)


    def times_scalar(self, a):
        return Vec3d(a * self.x,
                     a * self.y,
                     a * self.z)


    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.dot_product(other)
        elif isinstance(other, (int, float)):
            return self.times_scalar(other)
        else:
            raise TypeError("Vec3d * b; only Vec3d, int or float are allowed for 'b'")


    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self.times_scalar(1.0 / other)
        else:
            raise TypeError("Vec3d / b; only int or float are allowed for 'b'")


    def cross_product(self, v2):
        prod_x = self.y * v2.z - self.z * v2.y
        prod_y = self.z * v2.x - self.x * v2.z
        prod_z = self.x * v2.y - self.y * v2.x
        return Vec3d(prod_x, prod_y, prod_z)


    def normalized(self):
        len_v = self.length()
        if len_v != 0.0:
            unit_v = self.times_scalar(1.0 / len_v)
        else:
            unit_v = Vec3d.zero()
        return unit_v


    def __repr__(self):
        return "{:.3f}, {:.3f}, {:.3f}".format(self.x, self.y, self.z)


    def __str__(self):
        return "{:.13f}, {:.13f}, {:.13f}".format(self.x, self.y, self.z)
