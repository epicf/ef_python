from collections import namedtuple

import abc
import io
import matplotlib.pyplot as plt
import numpy as np
import os
import shlex
import subprocess
import tempfile
from configparser import ConfigParser
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
        # config = ConfigParser( as_dict )
        config = ConfigParser()
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


class ConfigComponent(abc.ABC):
    section_map = {}

    @classmethod
    def config_to_components(cls, conf):
        return [cls.section_map[section.split('.')[0]].from_section(conf[section]) for section in
                conf.sections()]

    @classmethod
    def register(cls):
        cls.section_map[cls.section] = cls

    def __init__(self, *args, **kwargs):
        self.content = self.ContentTuple(*args, **kwargs)

    @classmethod
    def from_section(cls, section):
        if section.name != cls.section:
            raise ValueError()
        if set(section.keys()) != set(cls.ContentTuple._fields):
            raise ValueError()
        data = {arg: cls.convert._asdict()[arg](section[arg]) for arg in cls.convert._fields}
        return cls(**data)

    def to_section(self, conf):
        conf.add_section(self.section)
        for k, v in self.content._asdict().items():
            conf.set(self.section, k, str(v))

    def make(self):
        raise NotImplementedError()

    def __repr__(self):
        return "{}(section={}, data={})".format(self.__class__.__name__, self.section, repr(self.content))

    def __str__(self):
        return "{}: {}".format(self.section, dict(self.content._asdict()))


def register(cls):
    ConfigComponent.section_map[cls.section] = cls
    return cls


class NamedConfigComponent(ConfigComponent):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.section = self.section + '.' + name
        super().__init__(*args, **kwargs)

    @classmethod
    def from_section(cls, section):
        category, name = section.name.split('.', 1)
        if category != cls.section:
            raise ValueError()
        if set(section.keys()) != set(cls.ContentTuple._fields):
            raise ValueError()
        data = {arg: cls.convert._asdict()[arg](section[arg]) for arg in cls.convert._fields}
        return cls(name, **data)


@register
class TimeGridConf(ConfigComponent):
    section = "Time grid"
    ContentTuple = namedtuple("TimeGridTuple", ('total_time', 'time_save_step', 'time_step_size'))
    convert = ContentTuple(float, float, float)

    def make(self):
        return TimeGrid(*self.content)


@register
class SpatialMeshConf(ConfigComponent):
    section = "Spatial mesh"
    ContentTuple = namedtuple("SpatialMeshTuple", ('grid_x_size', 'grid_x_step', 'grid_y_size',
                                                   'grid_y_step', 'grid_z_size', 'grid_z_step'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        return SpatialMesh(self.content[::2], self.content[1::2])


@register
class BoundaryConditionsConf(ConfigComponent):
    section = "Boundary conditions"
    ContentTuple = namedtuple("BoundaryConditionsTuple",
                              ('boundary_phi_right', 'boundary_phi_left', 'boundary_phi_bottom',
                               'boundary_phi_top', 'boundary_phi_near', 'boundary_phi_far'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        return BoundaryConditionsConf(*self.content)


@register
class ParticleSourceBoxConf(NamedConfigComponent):
    section = "Particle_source_box"
    ContentTuple = namedtuple("ParticleSourceBoxTuple", ('box_x_left', 'box_x_right', 'box_y_bottom',
                                                         'box_y_top', 'box_z_near', 'box_z_far',
                                                         'initial_number_fo_particles',
                                                         'particles_to_generate_each_step',
                                                         'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                         'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 6 + [int] * 2 + [float] * 6))

    def make(self):
        box = Box.init_rlbtnf(*self.content[:6])
        return ParticleSource(box, self.name, *self.content[6:])


@register
class ParticleSourceCylinderConf(NamedConfigComponent):
    section = "Particle_source_cylinder"
    ContentTuple = namedtuple("ParticleSourceCylinderTuple", ('cylinder_axis_start_x', 'cylinder_axis_start_y',
                                                              'cylinder_axis_start_z', 'cylinder_axis_end_x',
                                                              'cylinder_axis_end_y', 'cylinder_axis_end_z',
                                                              'cylinder_radius',
                                                              'initial_number_fo_particles',
                                                              'particles_to_generate_each_step',
                                                              'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                              'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 7 + [int] * 2 + [float] * 6))

    def make(self):
        cylinder = Cylinder(self.content[:3], self.content[3:6], self.content.cylinder_radius)
        return ParticleSource(cylinder, self.name, *self.content[7:])


@register
class ParticleSourceTubeConf(NamedConfigComponent):
    section = "Particle_source_tube"
    ContentTuple = namedtuple("ParticleSourceTubeTuple", ('tube_axis_start_x', 'tube_axis_start_y',
                                                          'tube_axis_start_z', 'tube_axis_end_x',
                                                          'tube_axis_end_y', 'tube_axis_end_z',
                                                          'tube_inner_radius', 'tube_outer_radius',
                                                          'initial_number_fo_particles',
                                                          'particles_to_generate_each_step',
                                                          'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                          'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 8 + [int] * 2 + [float] * 6))

    def make(self):
        tube = Tube(self.content[:3], self.content[3:6], self.content.tube_inner_radius, self.content.tube_outer_radius)
        return ParticleSource(tube, self.name, *self.content[8:])


@register
class InnerRegionBoxConf(NamedConfigComponent):
    section = "Inner_region_box"
    ContentTuple = namedtuple("InnerRegionBoxTuple", ('box_x_left', 'box_x_right', 'box_y_bottom',
                                                      'box_y_top', 'box_z_near', 'box_z_far',
                                                      'potential'))
    convert = ContentTuple(*[float] * 7)

    def make(self):
        box = Box.init_rlbtnf(*self.content[:6])
        return InnerRegion(box, self.name, self.content.potential)


@register
class InnerRegionCylinderConf(NamedConfigComponent):
    section = "Inner_region_cylinder"
    ContentTuple = namedtuple("InnerRegionCylinderTuple", ('cylinder_axis_start_x', 'cylinder_axis_start_y',
                                                           'cylinder_axis_start_z', 'cylinder_axis_end_x',
                                                           'cylinder_axis_end_y', 'cylinder_axis_end_z',
                                                           'cylinder_radius', 'potential'))
    convert = ContentTuple(*[float] * 8)

    def make(self):
        cylinder = Cylinder(self.content[:3], self.content[3:6], self.content.cylinder_radius)
        return ParticleSource(cylinder, self.name, self.content.potential)


@register
class InnerRegionTubeConf(NamedConfigComponent):
    section = "Inner_region_tube"
    ContentTuple = namedtuple("InnerRegionTubeTuple", ('tube_axis_start_x', 'tube_axis_start_y',
                                                       'tube_axis_start_z', 'tube_axis_end_x',
                                                       'tube_axis_end_y', 'tube_axis_end_z',
                                                       'tube_inner_radius', 'tube_outer_radius',
                                                       'potential'))
    convert = ContentTuple(*[float] * 9)

    def make(self):
        tube = Tube(self.content[:3], self.content[3:6], self.content.tube_inner_radius, self.content.tube_outer_radius)
        return InnerRegion(tube, self.name, self.content.potential)


@register
class ParticleInteractionModel(ConfigComponent):
    section = "Particle interaction model"
    ContentTuple = namedtuple("ParticleInteractionModelTuple", ('particle_interaction_model'))
    convert = ContentTuple(str)

    def make(self):
        pass


@register
class ExternalFieldMagneticUniformConf(NamedConfigComponent):
    section = "ExternalFieldMagneticUniform"
    ContentTuple = namedtuple("ExternalFieldMagneticUniform",
                              ('magnetic_field_x', 'magnetic_field_y', 'magnetic_field_z'))
    convert = ContentTuple(float, float, float)

    def make(self):
        pass


@register
class ExternalFieldElectricUniformConf(NamedConfigComponent):
    section = "ExternalFieldElectricUniform"
    ContentTuple = namedtuple("ExternalFieldElectricUniform",
                              ('electric_field_x', 'electric_field_y', 'electric_field_z'))
    convert = ContentTuple(float, float, float)

    def make(self):
        pass


@register
class OutputFilenameConf(ConfigComponent):
    section = "Output filename"
    ContentTuple = namedtuple("OutputFileNameTuple", ('output_filename_prefix', 'output_filename_suffix'))
    convert = ContentTuple(str, str)

    def make(self):
        pass


class TimeGrid:
    def __init__(self, total_time=100.0, time_save_step=10.0, time_step_size=1.0):
        self.total_time = total_time
        self.time_save_step = time_save_step
        self.time_step_size = time_step_size

    def visualize(self, visualizer):
        pass


class SpatialMesh:
    def __init__(self, grid_size=(10.0, 10.0, 10.0), grid_step=(1, 1, 1)):
        self.grid_size = np.array(grid_size)
        self.grid_step = np.array(grid_step)
        self.plotting_args = {'wireframe': True, 'label': 'volume', 'colors': 'k', 'linewidths': 1}

    def visualize(self, visualizer):
        visualizer.draw_box(self.grid_size, **self.plotting_args)


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


class Box:
    def __init__(self, origin=(0, 0, 0), size=(1, 1, 1)):
        self.origin = np.array(origin)
        self.size = np.array(size)

    @classmethod
    def init_rlbtnf(cls, r=5, l=6, b=2, t=5, n=1, f=3):
        return cls((r, b, n), (l - r, t - b, f - n))

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_box(self.size, self.origin, **kwargs)


class Cylinder:
    def __init__(self, a=(0, 0, 0), b=(0, 0, 1), radius=1):
        self.a = np.array(a)
        self.b = np.array(b)
        self.r = radius

    @classmethod
    def init_aligned_z(cls, x=6, y=5, z1=2, z2=5, r=2):
        return cls((x, y, z1), (x, y, z2), r)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cylinder(self.a, self.b, self.r, **kwargs)


class Tube:
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


class ParticleSource:
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


class InnerRegion:
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


class ExternalFieldElectricOnRegularGridFromH5File:

    def __init__(self, name="elec_file", filename="field.h5"):
        self.name = name
        self.filename = filename

    def visualize(self, ax):
        pass


def main():
    conf = EfConf()
    box = ParticleSource(Box.init_rlbtnf())
    tube = ParticleSource(Tube((5, 5, 5), (7, 5, 7), 1, 2))
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
