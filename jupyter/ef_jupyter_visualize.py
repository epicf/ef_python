import configparser
import io
import os
import shlex
import subprocess
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection


class Visualizer3d:
    def __init__(self, equal_aspect=True):
        fig = plt.figure()
        self.ax = fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.equal_aspect = equal_aspect
        plt.rcParams["figure.figsize"] = [9, 8]

    def visualize(self, config_objects):
        for conf in config_objects:
            conf.visualize(self)
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
        if length==0:
            return arr
        projection = v[:2]
        shadow = np.linalg.norm(projection)
        height = v[2]
        cos_alpha = height / length
        sin_alpha = shadow / length
        arr = arr.dot(np.array([[cos_alpha, 0, -sin_alpha],
                                [0, 1, 0],
                                [sin_alpha, 0, cos_alpha]]))
        if shadow==0:
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
        if wireframe:
            lines = (a + circle * r, a + circle * R, b + circle * r, b + circle * R)
            self.ax.add_collection(Line3DCollection(lines, **kwargs))
        else:
            ring = np.stack((r * circle, r * np.roll(circle, 1, axis=0), R * np.roll(circle, 1, axis=0), R * circle),
                            axis=1)
            rings = np.concatenate((a + ring, b + ring))
            self.ax.add_collection(Poly3DCollection(rings, **kwargs))


class EfConf:

    def __init__(self):
        self.time_grid = TimeGrid()
        self.spatial_mesh = SpatialMesh()
        self.sources = []
        self.inner_regions = []
        self.output_file = OutputFile()
        self.boundary_conditions = BoundaryConditions()
        self.particle_interaction_model = ParticleInteractionModel()
        self.ex_fields = []

    def add_source(self, src):
        self.sources.append(src)

    def add_inner_region(self, ir):
        self.inner_regions.append(ir)

    def add_ex_field(self, ef):
        self.ex_fields.append(ef)

    def visualize_all(self, visualizer):
        visualizer.visualize([self.time_grid, self.spatial_mesh] + self.sources + self.inner_regions + self.ex_fields)

    def export_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.as_text())

    def as_text(self):
        as_dict = {}
        as_dict.update(self.time_grid.export())
        as_dict.update(self.spatial_mesh.export())
        for src in self.sources:
            as_dict.update(src.export())
        for ir in self.inner_regions:
            as_dict.update(ir.export())
        as_dict.update(self.output_file.export())
        as_dict.update(self.boundary_conditions.export())
        as_dict.update(self.particle_interaction_model.export())
        for ef in self.ex_fields:
            as_dict.update(ef.export())
        # can't construct config from dictionary; have to do it manually
        # config = configparser.ConfigParser( as_dict )
        config = configparser.ConfigParser()
        for sec_name, sec in as_dict.items():
            config[sec_name] = {}
            for k, v in sec.items():
                config[sec_name][k] = str(v)
        f = io.StringIO()
        config.write(f)
        return f.getvalue()

    def print_config(self):
        print(self.as_text())

    def run(self, ef_command="python3 ../../main.py", workdir="./",
            save_config_as=None):
        current_dir = os.getcwd()
        os.chdir(workdir)
        if save_config_as:
            self.export(save_config_as)
            command = ef_command + " " + save_config_as
        else:
            tmpfile, tmpfilename = tempfile.mkstemp(suffix=".ini", text=True)
            self.export(tmpfilename)
            command = ef_command + " " + tmpfilename
        print("command:", command)
        self.run_command(command)
        # stdout = subprocess.Popen( command, shell = True,
        #                           stdout = subprocess.PIPE ).stdout.read()
        # Jupyter magick
        # !{command}
        # print( stdout )
        if tmpfile:
            os.remove(tmpfilename)
        os.chdir(current_dir)

    @classmethod
    def run_from_file(cls, startfile, ef_command="python3 ../../main.py", workdir="./"):
        current_dir = os.getcwd()
        os.chdir(workdir)
        command = ef_command + " " + startfile
        print("command:", command)
        stdout = subprocess.Popen(command, shell=True,
                                  stdout=subprocess.PIPE).stdout.read()
        print(stdout)
        os.chdir(current_dir)

    def run_command(self, command):
        # https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc
    # try instead
    # https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running


class TimeGrid:

    def __init__(self, total_time=100.0, time_save_step=10.0, time_step_size=1.0):
        self.total_time = total_time
        self.time_save_step = time_save_step
        self.time_step_size = time_step_size

    def visualize(self, ax):
        pass


class SpatialMesh:

    def __init__(self,
                 grid_size=np.array((10.0, 10.0, 10.0)), grid_step=np.array((1, 1, 1))):
        self.grid_size = grid_size
        self.grid_step = grid_step

    def visualize(self, visualizer):
        visualizer.draw_box(self.grid_size, wireframe=True, label='volume', colors='k', linewidths=1)


class BoundaryConditions:

    def __init__(self,
                 boundary_phi_right=0, boundary_phi_left=0,
                 boundary_phi_bottom=0, boundary_phi_top=0,
                 boundary_phi_near=0, boundary_phi_far=0):
        self.boundary_phi_right = boundary_phi_right
        self.boundary_phi_left = boundary_phi_left
        self.boundary_phi_bottom = boundary_phi_bottom
        self.boundary_phi_top = boundary_phi_top
        self.boundary_phi_near = boundary_phi_near
        self.boundary_phi_far = boundary_phi_far

    def visualize(self, visualizer):
        pass


class Box():
    def __init__(self, origin=(0, 0, 0), size=(1, 1, 1)):
        self.origin = np.array(origin)
        self.size = np.array(size)

    @classmethod
    def init_rlbtnf(cls, r=5, l=6, b=2, t=5, n=1, f=3):
        return cls((r, b, n), (l-r, t-b, f-n))

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_box(self.size, self.origin, **kwargs)


class Cylinder():
    def __init__(self, a=(0,0,0), b=(0, 0, 1), radius=1):
        self.a = np.array(a)
        self.b = np.array(b)
        self.r = radius

    @classmethod
    def init_aligned_z(cls, x=6, y=5, z1=2, z2=5, r=2):
        return cls((x, y, z1), (x, y, z2), r)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cylinder(self.a, self.b, self.r, **kwargs)


class Tube():
    def __init__(self, a=(0, 0, 0,), b=(0, 0, 1), inner_radius=1, outer_radius=2):
        self.a = np.array(a)
        self.b = np.array(b)
        self.r = inner_radius
        self.R = outer_radius

    @classmethod
    def init_aligned_z(cls, x=3, y=4, z1=3, z2=7, r=1, R=3):
        return cls((x, y, z1), (x, y, z2), r, R)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_tube(self.a, self.b, self.r, self.R, **kwargs)


class ParticleSource():
    def __init__(self, shape,
                 name='particle_source',
                 initial_number_of_particles=500,
                 particles_to_generate_each_step=500,
                 mean_momentum_x=0,
                 mean_momentum_y=0,
                 mean_momentum_z=6.641e-15,
                 temperature=0.0,
                 charge=-1.799e-6,
                 mass=3.672e-24):
        self.name = name
        self.shape = shape
        self.initial_number_of_particles = initial_number_of_particles
        self.particles_to_generate_each_step = particles_to_generate_each_step
        self.mean_momentum_x = mean_momentum_x
        self.mean_momentum_y = mean_momentum_y
        self.mean_momentum_z = mean_momentum_z
        self.temperature = temperature
        self.charge = charge
        self.mass = mass

    def visualize(self, visualizer):
        self.shape.visualize(visualizer, wireframe=True, label=self.name, colors='c', linewidths=1)


class InnerRegion():
    def __init__(self, shape, name='region', potential=0):
        self.shape = shape
        self.name = name
        self.potential = potential

    def visualize(self, visualizer):
        self.shape.visualize(visualizer, wireframe=False, edgecolors='r', facecolors='c', linewidths=1)


class OutputFile:
    def __init__(self, output_filename_prefix="out_", output_filename_suffix=".h5"):
        self.output_filename_prefix = output_filename_prefix
        self.output_filename_suffix = output_filename_suffix

    def visualize(self, ax):
        pass


class ParticleInteractionModel:

    def __init__(self, particle_interaction_model="PIC"):
        self.particle_interaction_model = particle_interaction_model

    def visualize(self, ax):
        pass


class ExternalFieldElectricOnRegularGridFromH5File():

    def __init__(self, name="elec_file", filename="field.h5"):
        self.name = name
        self.filename = filename

    def visualize(self, ax):
        pass


def main():
    conf = EfConf()
    box = ParticleSource(Box.init_rlbtnf())
    tube = ParticleSource(Tube((5,5,5), (7,5,7), 1, 2))
    segment = InnerRegion(Cylinder((2, 2, 2), (1, 1, 1), 1))
    c1 = InnerRegion(Tube.init_aligned_z(8, 3, 2, 5, 2, 3))
    conf.add_source(box)
    conf.add_source(tube)
    conf.add_inner_region(segment)
    conf.add_inner_region(c1)
    vis = Visualizer3d()
    conf.visualize_all(vis)


if __name__ == "__main__":
    main()
