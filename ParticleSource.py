import random
from math import sqrt

from Particle import Particle
from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


class ParticleSource(SerializableH5):

    def __init__(self, name, shape, initial_particles, particles_to_generate_each_step, mean_momentum, temperature,
                 charge, mass, particles=[], max_id=0):
        if initial_particles <= 0:
            raise ValueError("initial_particles <= 0")
        if particles_to_generate_each_step < 0:
            raise ValueError("particles_to_generate_each_step < 0")
        if temperature < 0:
            raise ValueError("temperature < 0")
        if mass < 0:
            raise ValueError("mass < 0")
        self.name = name
        self.shape = shape
        self.initial_number_of_particles = initial_particles
        self.particles_to_generate_each_step = particles_to_generate_each_step
        self.mean_momentum = mean_momentum
        self.temperature = temperature
        self.charge = charge
        self.mass = mass
        self.particles = []
        self.max_id = 0
        # Random number generator
        # Instead of saving/loading it's state to file just
        # reinit with different seed.
        tmp = random.getstate()
        random.seed()  # system time is used by default
        self._rnd_state = random.getstate()
        random.setstate(tmp)
        self.generate_num_of_particles(self.initial_number_of_particles)

    def generate_each_step(self):
        # particles.reserve(particles.size() + particles_to_generate_each_step);
        self.generate_num_of_particles(self.particles_to_generate_each_step)

    def generate_num_of_particles(self, num_of_particles):
        vec_of_ids = self.populate_vec_of_ids(num_of_particles)
        for i in range(num_of_particles):
            pos = self.shape.generate_uniform_random_point(self.random_in_range)
            mom = self.maxwell_momentum_distr(
                Vec3d(*self.mean_momentum), self.temperature, self.mass)
            self.particles.append(
                Particle(vec_of_ids[i], self.charge, self.mass, pos, mom))

    def populate_vec_of_ids(self, num_of_particles):
        vec_of_ids = []
        for i in range(num_of_particles):
            self.max_id += 1
            vec_of_ids.append(self.max_id)
        return vec_of_ids

    def random_in_range(self, low, up):
        tmp = random.getstate()
        random.setstate(self._rnd_state)
        r = random.uniform(low, up)
        self._rnd_state = random.getstate()
        random.setstate(tmp)
        return r

    def maxwell_momentum_distr(self, mean_momentum, temperature, mass):
        maxwell_gauss_std_mean_x = mean_momentum.x
        maxwell_gauss_std_mean_y = mean_momentum.y
        maxwell_gauss_std_mean_z = mean_momentum.z
        maxwell_gauss_std_dev = sqrt(mass * temperature)
        #
        tmp = random.getstate()
        random.setstate(self._rnd_state)
        px = random.gauss(maxwell_gauss_std_mean_x, maxwell_gauss_std_dev)
        py = random.gauss(maxwell_gauss_std_mean_y, maxwell_gauss_std_dev)
        pz = random.gauss(maxwell_gauss_std_mean_z, maxwell_gauss_std_dev)
        self._rnd_state = random.getstate()
        random.setstate(tmp)
        #
        mom = Vec3d(px, py, pz)
        mom = mom.times_scalar(1.0)  # recheck
        return mom

    def update_particles_position(self, dt):
        for p in self.particles:
            p.update_position(dt)
