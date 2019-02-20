import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection


class Visualizer3d:
    def __init__(self, equal_aspect=True, potential_colormap='seismic'):
        fig = plt.figure()
        self.ax = fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.equal_aspect = equal_aspect
        plt.rcParams["figure.figsize"] = [9, 8]
        self.potential_mapper = matplotlib.cm.ScalarMappable(cmap=potential_colormap)

    def set_potential_lim(self, p_min, p_max):
        self.potential_mapper.set_clim(p_min, p_max)

    def visualize(self, config_objects):
        for conf in config_objects:
            conf.visualize(self)

    def show(self):
        if self.equal_aspect:
            self.axis_equal_3d()
        self.ax.legend()
        plt.show()

    def axis_equal_3d(self):
        # https://stackoverflow.com/questions/8130823/set-matplotlib-3d-plot-aspect-ratio
        extents = np.array([getattr(self.ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:, 1] - extents[:, 0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize / 2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(self.ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

    def draw_box(self, size, position=np.zeros(3), wireframe=False, **kwargs):
        cube = np.mgrid[0:2, 0:2, 0:2].reshape(3, 8).T
        vertices = size * cube + position
        # tell ax our extents, so that xyz limits are set correctly
        self.ax.scatter(*[vertices[:, i] for i in (0, 1, 2)], alpha=0.0)
        if wireframe:
            edge_masks = [np.logical_and(cube[:, i] == v, cube[:, j] == w)
                          for w in (0, 1) for v in (0, 1) for i in (0, 1) for j in range(i + 1, 3)]
            edges = [vertices[edge, :] for edge in edge_masks]
            self.ax.add_collection(Line3DCollection(edges, **kwargs))
        else:
            face_masks = [cube[:, i] == v for v in (0, 1) for i in (0, 1, 2)]
            polygons = [vertices[face, :][(0, 1, 3, 2), :] for face in face_masks]
            self.ax.add_collection(Poly3DCollection(polygons, **kwargs))

    @staticmethod
    def rotate_vectors_from_z_axis_towards_vector(arr, v):
        length = np.linalg.norm(v)
        if length == 0:
            return arr
        projection = v[:2]
        shadow = np.linalg.norm(projection)
        height = v[2]
        cos_alpha = height / length
        sin_alpha = shadow / length
        arr = arr.dot(np.array([[cos_alpha, 0, -sin_alpha],
                                [0, 1, 0],
                                [sin_alpha, 0, cos_alpha]]))
        if shadow == 0:
            return arr
        cos_beta = v[0] / shadow
        sin_beta = v[1] / shadow
        return arr.dot(np.array([[cos_beta, sin_beta, 0],
                                 [-sin_beta, cos_beta, 0],
                                 [0, 0, 1]]))

    def draw_cylinder(self, a, b, r, wireframe=False, **kwargs):
        phi = np.radians(np.linspace(0, 360, 32, endpoint=wireframe))
        circle = np.stack((np.cos(phi), np.sin(phi), np.zeros_like(phi))).T
        circle = self.rotate_vectors_from_z_axis_towards_vector(circle, b - a)
        # tell ax our extents, so that xyz limits are set correctly
        self.ax.scatter(*(a + circle * r).T, alpha=0.0)
        self.ax.scatter(*(b + circle * r).T, alpha=0.0)
        if wireframe:
            lines = (a + circle * r, b + circle * r)
            self.ax.add_collection(Line3DCollection(lines, **kwargs))
        else:
            # cap = np.stack((np.zeros_like(circle), r * np.roll(circle, 1, axis=0), r * circle), axis=1)
            sides = np.stack((a + r * circle, a + r * np.roll(circle, 1, axis=0),
                              b + r * np.roll(circle, 1, axis=0), b + r * circle), axis=1)
            # caps = np.concatenate((a + cap, b + cap))
            self.ax.add_collection(Poly3DCollection(sides, **kwargs))
            # self.ax.add_collection(Poly3DCollection(caps, **kwargs))

    def draw_tube(self, a, b, r, R, wireframe=False, **kwargs):
        phi = np.radians(np.linspace(0, 360, 32, endpoint=wireframe))
        circle = np.stack((np.cos(phi), np.sin(phi), np.zeros_like(phi))).T
        circle = self.rotate_vectors_from_z_axis_towards_vector(circle, b - a)
        # tell ax our extents, so that xyz limits are set correctly
        self.ax.scatter(*(b + circle * R).T, alpha=0.0)
        if wireframe:
            lines = (a + circle * r, a + circle * R, b + circle * r, b + circle * R)
            self.ax.add_collection(Line3DCollection(lines, **kwargs))
        else:
            ring = np.stack((r * circle,
                             r * np.roll(circle, 1, axis=0),
                             R * np.roll(circle, 1, axis=0),
                             R * circle),
                            axis=1)
            self.ax.add_collection(Poly3DCollection(a + ring, **kwargs))
            self.ax.add_collection(Poly3DCollection(b + ring, **kwargs))

    def draw_sphere(self, origin, radius, wireframe=False, **kwargs):
        longitude = np.radians(np.linspace(0, 360, 16, endpoint=False))[:, np.newaxis]
        latitude = np.radians(np.linspace(-90, 90, 8, endpoint=True))[np.newaxis, :]
        z = np.sin(latitude)
        r = np.cos(latitude)
        x = r*np.cos(longitude)
        y = r*np.sin(longitude)
        unit_sphere = np.stack((x, y, np.broadcast_to(z, x.shape)), axis=-1)
        sphere = unit_sphere * radius + origin
        if wireframe:
            parallels = np.reshape(np.stack((sphere[:, 1:-1], np.roll(sphere[:, 1:-1], 1, axis=0)), axis=2), (-1, 2, 3))
            meridians = np.reshape(np.stack((sphere, np.roll(sphere, 1, axis=1)), axis=-2)[:, 1:], (-1, 2, 3))
            self.ax.add_collection(Line3DCollection(parallels, **kwargs))
            self.ax.add_collection(Line3DCollection(meridians, **kwargs))
        else:
            axis = ((), (0,), (0,1), (1,))
            quads = np.reshape(np.stack([np.roll(sphere, 1, axis=ax) for ax in axis], axis=2), (-1, 4, 3))
            self.ax.add_collection(Poly3DCollection(quads, **kwargs))


    def draw_cone(self, a, b, a_radii, b_radii, wireframe=False, **kwargs):
        phi = np.radians(np.linspace(0, 360, 32, endpoint=wireframe))
        circle = np.stack((np.cos(phi), np.sin(phi), np.zeros_like(phi))).T
        circle = self.rotate_vectors_from_z_axis_towards_vector(circle, b - a)
        # tell ax our extents, so that xyz limits are set correctly
        self.ax.scatter(*(b + circle * np.max(np.append(a_radii, b_radii))).T, alpha=0.0)
        if wireframe:
            lines = (a + circle * a_radii[0],
                     a + circle * a_radii[1],
                     b + circle * b_radii[0],
                     b + circle * b_radii[1])
            self.ax.add_collection(Line3DCollection(lines, **kwargs))
        else:
            # todo: recheck
            ring = np.stack((a_radii[0] * circle,
                             b_radii[0] * np.roll(circle, 1, axis=0),
                             b_radii[1] * np.roll(circle, 1, axis=0),
                             a_radii[1] * circle),
                            axis=1)
            self.ax.add_collection(Poly3DCollection(a + ring, **kwargs))
            self.ax.add_collection(Poly3DCollection(b + ring, **kwargs))

            
def main():
    v = Visualizer3d()
    v.draw_tube(np.array((1, 1, 1)), np.array((5, 8, 7)), 2, 3, facecolors='r', edgecolors='k')
    v.draw_cylinder(np.array((1, 7, 7)), np.array((5, 3, 2)), 1, facecolors='y', edgecolors='k')
    v.draw_box(np.array((5, 2, 2)), np.array((3, 3, 5)), facecolors='g', edgecolors='k')
    v.draw_sphere(np.array((8, 8, 3)), 2, facecolors='navy', edgecolors='k')
    v.draw_tube(np.array((3, 1, 2)), np.array((7, 8, 7)), 1, 3, colors='cyan', wireframe=True)
    v.draw_cylinder(np.array((8, 7, 7)), np.array((5, 3, 8)), 4, wireframe=True)
    v.draw_box(np.array((10, 10, 10)), np.array((0, 0, 0)), colors='k', wireframe=True)
    v.draw_sphere(np.array((8, 3, 3)), 2, colors='purple', wireframe=True)
    v.draw_cone(np.array((4, 5, 8)), np.array((12, 8, 10)),
                np.array((1,2)), np.array((3,4)), colors='orange', wireframe=True)
    v.show()


if __name__ == "__main__":
    main()
