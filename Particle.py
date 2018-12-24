import numpy as np

import physical_constants
from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


def boris_update_momentum(charge, mass, momentum, dt, total_el_field, total_mgn_field):
    q_quote = dt * charge / mass / 2.0  # scalar. how easy is it to move? dt * Q / m /2
    half_el_force = np.asarray(total_el_field) * q_quote  # (n, 3) half the dv caused by electric field
    v_current = momentum / mass  # (n, 3) current velocity (at -1/2 dt already)
    u = v_current + half_el_force  # (n, 3) v_minus
    h = np.array(total_mgn_field) * (q_quote / physical_constants.speed_of_light)  # (n, 3)
    # rotation vector t = qB/m * dt/2
    s = h * (2.0 / (1.0 + np.sum(h * h, -1)))[..., np.newaxis]  # (n, 3) rotation vector s = 2t / (1 + t**2)
    tmp = u + np.cross(u, h)  # (n, 3) v_prime is v_minus rotated by t
    u_quote = u + np.cross(tmp, s)  # (n, 3) v_plus = v_minus + v_prime * s
    return (u_quote + half_el_force) * mass  # (n, 3) finally add the other half-velocity


class Particle(SerializableH5):
    def __init__(self, particle_id, charge, mass, position, momentum, momentum_is_half_time_step_shifted=False):
        self.particle_id = particle_id
        self.charge = charge
        self.mass = mass
        self._position = np.array(position)
        self.momentum = np.array(momentum)
        self.momentum_is_half_time_step_shifted = momentum_is_half_time_step_shifted

    @property
    def dict(self):
        d = super().dict
        d['position'] = self._position
        return d

    def update_position(self, dt):
        self._position += dt / self.mass * self.momentum

    def field_at_point(self, point):
        diff = np.array(point) - self._position
        dist = np.linalg.norm(diff)
        return self.charge / dist ** 3 * diff

    def boris_update_momentum(self, dt, total_el_field, total_mgn_field):
        self.momentum = boris_update_momentum(self.charge, self.mass, self.momentum, dt, total_el_field,
                                              total_mgn_field)

    def boris_update_momentum_no_mgn(self, dt, total_el_field):
        self.momentum += self.charge * dt * np.array(total_el_field)
