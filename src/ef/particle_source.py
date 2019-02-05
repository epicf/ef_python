from math import sqrt

from numpy.random import RandomState

from ef.particle_array import ParticleArray
from ef.util.serializable_h5 import SerializableH5


class ParticleSource(SerializableH5):

    def __init__(self, name, shape, initial_number_of_particles, particles_to_generate_each_step, mean_momentum,
                 temperature, charge, mass):
        if initial_number_of_particles <= 0:
            raise ValueError("initial_number_of_particles <= 0")
        if particles_to_generate_each_step < 0:
            raise ValueError("particles_to_generate_each_step < 0")
        if temperature < 0:
            raise ValueError("temperature < 0")
        if mass < 0:
            raise ValueError("mass < 0")
        self.name = name
        self.shape = shape
        self.initial_number_of_particles = initial_number_of_particles
        self.particles_to_generate_each_step = particles_to_generate_each_step
        self.mean_momentum = mean_momentum
        self.temperature = temperature
        self.charge = charge
        self.mass = mass
        self._generator = RandomState()

    def generate_initial_particles(self):
        return self.generate_num_of_particles(self.initial_number_of_particles)

    def generate_each_step(self):
        return self.generate_num_of_particles(self.particles_to_generate_each_step)

    def generate_num_of_particles(self, num_of_particles):
        pos = self.shape.generate_uniform_random_posititons(self._generator, num_of_particles)
        mom = self._generator.normal(self.mean_momentum, sqrt(self.mass * self.temperature), (num_of_particles, 3))
        return ParticleArray(range(num_of_particles), self.charge, self.mass, pos, mom)
