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

    def draw_box_rlbtnf(self, r, l, b, t, n, f, **kwargs):
        # left > right: x, bottom < top: y, near < far: z
        origin = np.array((r, b, n))
        far = np.array((l, t, f))
        self.draw_box_size_origin(far - origin, origin, **kwargs)

    def draw_box_size_origin(self, size, position=np.zeros(3), wireframe=False, **kwargs):
        cube = np.mgrid[0:2, 0:2, 0:2].reshape(3, 8).T
        vertices = size * cube + position
        self.ax.scatter(*[vertices[:, i] for i in (0, 1, 2)], alpha=0.0)
        if wireframe:
            edge_masks = [np.logical_and(cube[:, i] == v, cube[:, j] == w)
                          for w in (0, 1) for v in (0, 1) for i in (0, 1) for j in range(i + 1, 3)]
            edges = [vertices[edge, :] for edge in edge_masks]
            self.ax.add_collection(
                Line3DCollection(edges, **kwargs))
        else:
            face_masks = [cube[:, i] == v for v in (0, 1) for i in (0, 1, 2)]
            polygons = [vertices[face, :][(0, 1, 3, 2), :] for face in face_masks]
            self.ax.add_collection(
                Poly3DCollection(polygons, **kwargs))

    def draw_cylinder(self, a, b, r, wireframe=False, **kwargs):
        phi = np.radians(np.linspace(0, 360, 32, endpoint=wireframe))
        circle = np.stack((np.cos(phi), np.sin(phi), np.zeros_like(phi))).T
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


    def draw_cylinder_xyz(self, x, y, z, X, Y, Z, r, **kwargs):
        self.draw_cylinder(np.array((x, y, z)), np.array((X, Y, Z)), r, **kwargs)

    def draw_tube(self, a, b, r, R, wireframe=False, **kwargs):
        phi = np.radians(np.linspace(0, 360, 32, endpoint=wireframe))
        circle = np.stack((np.cos(phi), np.sin(phi), np.zeros_like(phi))).T
        if wireframe:
            lines = (a + circle * r, a + circle * R, b + circle * r, b + circle * R)
            self.ax.add_collection(Line3DCollection(lines, **kwargs))
        else:
            ring = np.stack((r * circle, r * np.roll(circle, 1, axis=0), R * np.roll(circle, 1, axis=0), R * circle),
                            axis=1)
            rings = np.concatenate((a + ring, b + ring))
            self.ax.add_collection(Poly3DCollection(rings, **kwargs))

    def draw_tube_xyz(self, x, y, z, X, Y, Z, r, R, **kwargs):
        self.draw_tube(np.array((x, y, z)), np.array((X, Y, Z)), r, R, **kwargs)


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
        visualizer.draw_box_size_origin(self.grid_size, wireframe=True, label='volume', colors='k', linewidths=1)


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


class ParticleSourceBox():
    def __init__(self, name='box_source',
                 initial_number_of_particles=500,
                 particles_to_generate_each_step=500,
                 box_x_left=6, box_x_right=5,
                 box_y_bottom=2, box_y_top=5,
                 box_z_near=1, box_z_far=3,
                 mean_momentum_x=0,
                 mean_momentum_y=0,
                 mean_momentum_z=6.641e-15,
                 temperature=0.0,
                 charge=-1.799e-6,
                 mass=3.672e-24):
        self.name = name
        self.box_x_left = box_x_left
        self.box_x_right = box_x_right
        self.box_y_bottom = box_y_bottom
        self.box_y_top = box_y_top
        self.box_z_near = box_z_near
        self.box_z_far = box_z_far
        self.initial_number_of_particles = initial_number_of_particles
        self.particles_to_generate_each_step = particles_to_generate_each_step
        self.mean_momentum_x = mean_momentum_x
        self.mean_momentum_y = mean_momentum_y
        self.mean_momentum_z = mean_momentum_z
        self.temperature = temperature
        self.charge = charge
        self.mass = mass

    def visualize(self, visualizer):
        visualizer.draw_box_rlbtnf(self.box_x_left, self.box_x_right,
                                   self.box_y_bottom, self.box_y_top,
                                   self.box_z_near, self.box_z_far,
                                   wireframe=True, label=self.name, colors='c', linewidths=1)


class ParticleSourceTube():
    def __init__(self, name='tube_source',
                 initial_number_of_particles=500,
                 particles_to_generate_each_step=500,
                 cylinder_axis_start_x=2.5, cylinder_axis_start_y=2.5,
                 cylinder_axis_start_z=4, cylinder_axis_end_x=2.5,
                 cylinder_axis_end_y=2.5, cylinder_axis_end_z=7,
                 cylinder_out_radius=1, cylinder_in_radius=0.5,
                 mean_momentum_x=0,
                 mean_momentum_y=0,
                 mean_momentum_z=6.641e-15,
                 temperature=0.0,
                 charge=-1.799e-6,
                 mass=3.672e-24):
        self.name = name
        self.cylinder_axis_start_x = cylinder_axis_start_x
        self.cylinder_axis_start_y = cylinder_axis_start_y
        self.cylinder_axis_start_z = cylinder_axis_start_z
        self.cylinder_axis_end_x = cylinder_axis_end_x
        self.cylinder_axis_end_y = cylinder_axis_end_y
        self.cylinder_axis_end_z = cylinder_axis_end_z
        self.cylinder_out_radius = cylinder_out_radius
        self.cylinder_in_radius = cylinder_in_radius
        self.initial_number_of_particles = initial_number_of_particles
        self.particles_to_generate_each_step = particles_to_generate_each_step
        self.mean_momentum_x = mean_momentum_x
        self.mean_momentum_y = mean_momentum_y
        self.mean_momentum_z = mean_momentum_z
        self.temperature = temperature
        self.charge = charge
        self.mass = mass

    def visualize(self, visualizer):
        visualizer.draw_tube_xyz(self.cylinder_axis_start_x, self.cylinder_axis_start_y,
                                 self.cylinder_axis_start_z,
                                 self.cylinder_axis_end_x, self.cylinder_axis_end_y, self.cylinder_axis_end_z,
                                 self.cylinder_in_radius, self.cylinder_out_radius,
                                 wireframe=True, label=self.name, colors='c', linewidths=1)


class InnerRegionTubeAlongZSegment():
    def __init__(self, name='segment',
                 potential=0,
                 tube_segment_axis_x=6, tube_segment_axis_y=5,
                 tube_segment_axis_start_z=2, tube_segment_axis_end_z=5,
                 tube_segment_inner_radius=1, tube_segment_outer_radius=3,
                 tube_segment_start_angle_deg=0, tube_segment_end_angle_deg=45):
        self.name = name
        self.potential = potential
        self.tube_segment_axis_x = tube_segment_axis_x
        self.tube_segment_axis_y = tube_segment_axis_y
        self.tube_segment_axis_start_z = tube_segment_axis_start_z
        self.tube_segment_axis_end_z = tube_segment_axis_end_z
        self.tube_segment_inner_radius = tube_segment_inner_radius
        self.tube_segment_outer_radius = tube_segment_outer_radius
        self.tube_segment_start_angle_deg = tube_segment_start_angle_deg
        self.tube_segment_end_angle_deg = tube_segment_end_angle_deg

    def visualize(self, visualizer):
        visualizer.draw_tube_xyz(self.tube_segment_axis_x, self.tube_segment_axis_y,
                                 self.tube_segment_axis_start_z,
                                 self.tube_segment_axis_x, self.tube_segment_axis_y, self.tube_segment_axis_end_z,
                                 self.tube_segment_inner_radius, self.tube_segment_outer_radius,
                                 wireframe=False, edgecolors='r', facecolors='c', linewidths=1)


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
    box = ParticleSourceBox()
    tube = ParticleSourceTube()
    segment = InnerRegionTubeAlongZSegment()
    conf.add_source(box)
    conf.add_source(tube)
    conf.add_inner_region(segment)
    vis = Visualizer3d()
    conf.visualize_all(vis)


if __name__ == "__main__":
    main()
