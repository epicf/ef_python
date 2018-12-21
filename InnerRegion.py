import os

import numpy as np

from Node import Node
from ef.util.serializable_h5 import SerializableH5


class InnerRegion(SerializableH5):

    def __init__(self, name, shape, potential=0, total_absorbed_particles=0, total_absorbed_charge=0):
        self.name = name
        self.shape = shape
        self.potential = potential
        self.total_absorbed_particles = total_absorbed_particles
        self.total_absorbed_charge = total_absorbed_charge

    def check_if_particle_inside(self, p):
        return self.check_if_point_inside(*p._position)

    def check_if_particle_inside_and_count_charge(self, p):
        in_or_out = self.check_if_particle_inside(p)
        if in_or_out:
            self.total_absorbed_particles += 1
            self.total_absorbed_charge += p.charge
        return in_or_out

    def check_if_point_inside(self, x, y, z):
        return self.shape.is_point_inside((x, y, z))

    def check_if_node_inside(self, node, dx, dy, dz):
        return self.check_if_point_inside(node.x * dx, node.y * dy, node.z * dz)
