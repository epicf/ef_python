import numpy as np

from ef.util.physical_constants import speed_of_light
from ef.util.serializable_h5 import SerializableH5


def boris_update_momentums(charge, mass, momentum_arr, dt, el_field_arr, mgn_field_arr):
    momentum_arr = np.asarray(momentum_arr)
    el_field_arr = np.asarray(el_field_arr)
    mgn_field_arr = np.asarray(mgn_field_arr)
    q_quote = dt * charge / mass / 2.0  # scalar. how easy is it to move? dt * Q / m /2
    half_el_force = np.asarray(el_field_arr) * q_quote  # (n, 3) half the dv caused by electric field
    v_current = momentum_arr / mass  # (n, 3) current velocity (at -1/2 dt already)
    u = v_current + half_el_force  # (n, 3) v_minus
    h = np.array(mgn_field_arr) * (q_quote / speed_of_light)  # (n, 3)
    # rotation vector t = qB/m * dt/2
    s = h * (2.0 / (1.0 + np.sum(h * h, -1)))[..., np.newaxis]  # (n, 3) rotation vector s = 2t / (1 + t**2)
    tmp = u + np.cross(u, h)  # (n, 3) v_prime is v_minus rotated by t
    u_quote = u + np.cross(tmp, s)  # (n, 3) v_plus = v_minus + v_prime * s
    return (u_quote + half_el_force) * mass  # (n, 3) finally add the other half-velocity


class ParticleArray(SerializableH5):
    def __init__(self, ids, charge, mass, positions, momentums, momentum_is_half_time_step_shifted=False):
        self.ids = np.array(ids)
        self.charge = charge
        self.mass = mass
        self.positions = np.array(positions)
        self.momentums = np.array(momentums)
        self.momentum_is_half_time_step_shifted = momentum_is_half_time_step_shifted

    def keep(self, mask):
        self.ids = self.ids[mask]
        self.positions = self.positions[mask]
        self.momentums = self.momentums[mask]

    def remove(self, mask):
        self.keep(np.logical_not(mask))

    def update_positions(self, dt):
        self.positions += dt / self.mass * self.momentums

    def field_at_point(self, point):
        diff = np.asarray(point) - self.positions
        dist = np.linalg.norm(diff, axis=-1)
        return self.charge * np.sum(diff / (dist ** 3)[..., np.newaxis], axis=0)

    def boris_update_momentums(self, dt, total_el_field, total_mgn_field):
        self.momentums = boris_update_momentums(self.charge, self.mass, self.momentums, dt, total_el_field,
                                                total_mgn_field)

    def boris_update_momentum_no_mgn(self, dt, total_el_field):
        self.momentums += self.charge * dt * np.asarray(total_el_field)
