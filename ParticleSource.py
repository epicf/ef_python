from math import sqrt

from numpy.random import RandomState

from ParticleArray import ParticleArray
from ef.util.serializable_h5 import SerializableH5


class ParticleSource(SerializableH5):

    def __init__(self, name, shape, initial_number_of_particles, particles_to_generate_each_step, mean_momentum,
                 temperature, charge, mass, particles=(), max_id=0):
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
        self.particles = list(particles)
        self.max_id = max_id
        self._generator = RandomState()

    def generate_initial_particles(self):
        # particles.reserve(initial_number_of_particles)
        self.generate_num_of_particles(self.initial_number_of_particles)

    def generate_each_step(self):
        # particles.reserve(particles.size() + particles_to_generate_each_step);
        self.generate_num_of_particles(self.particles_to_generate_each_step)

    def generate_num_of_particles(self, num_of_particles):
        if num_of_particles:
            vec_of_ids = self.populate_vec_of_ids(num_of_particles)
            pos = self.shape.generate_uniform_random_points(self._generator, num_of_particles)
            mom = self._generator.normal(self.mean_momentum, sqrt(self.mass * self.temperature), (num_of_particles, 3))
            self.particles.append(ParticleArray(vec_of_ids, self.charge, self.mass, pos, mom))

    def populate_vec_of_ids(self, num_of_particles):
        vec_of_ids = range(self.max_id + 1, self.max_id + num_of_particles + 1)
        self.max_id += num_of_particles
        return vec_of_ids
