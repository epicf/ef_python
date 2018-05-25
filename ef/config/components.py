import numpy as np


class TimeGrid:
    def __init__(self, total=100.0, save_step=10.0, step=1.0):
        self.total = total
        self.save_step = save_step
        self.step = step

    # def to_conf(self):
    #     return TimeGridConf(total_time=self.total, time_save_step=self.save_step, time_step_size=self.step)

    @classmethod
    def from_conf(cls, conf):
        cls(conf.total_time, conf.time_save_step, conf.time_step_size)


class SpatialMesh:
    def __init__(self, grid_size=(10.0, 10.0, 10.0), grid_step=(1, 1, 1)):
        self.grid_size = np.array(grid_size)
        self.grid_step = np.array(grid_step)

    def visualize(self, visualizer):
        visualizer.draw_box(self.grid_size, wireframe=True, label='volume', colors='k', linewidths=1)


class BoundaryConditions:
    pass


class Box:
    def __init__(self, origin, size):
        self.origin = np.array(origin)
        self.size = np.array(size)

    @classmethod
    def init_rlbtnf(cls, r, l, b, t, n, f):
        return cls((r, b, n), (l - r, t - b, f - n))

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_box(self.size, self.origin, **kwargs)


class Cylinder:
    def __init__(self, a, b, radius):
        self.a = np.array(a)
        self.b = np.array(b)
        self.r = radius

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cylinder(self.a, self.b, self.r, **kwargs)


class Tube:
    def __init__(self, a, b, inner_radius, outer_radius):
        self.a = np.array(a)
        self.b = np.array(b)
        self.r = inner_radius
        self.R = outer_radius

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_tube(self.a, self.b, self.r, self.R, **kwargs)


class ParticleSource:
    def __init__(self, shape, name,
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
    def __init__(self, shape, name, potential=0):
        self.shape = shape
        self.name = name
        self.potential = potential

    def visualize(self, visualizer):
        self.shape.visualize(visualizer, wireframe=False, edgecolors='r', facecolors='y', linewidths=1)


class OutputFile:
    def __init__(self, output_filename_prefix="out_", output_filename_suffix=".h5"):
        self.output_filename_prefix = output_filename_prefix
        self.output_filename_suffix = output_filename_suffix


class ParticleInteractionModel:
    def __init__(self, particle_interaction_model="PIC"):
        self.particle_interaction_model = particle_interaction_model


class ExternalFieldElectricOnRegularGridFromH5File:

    def __init__(self, name="elec_file", filename="field.h5"):
        self.name = name
        self.filename = filename

