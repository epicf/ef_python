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
        self._inner_nodes = []
        self._inner_nodes_not_at_domain_edge = []

    def check_if_particle_inside(self, p):
        x = p.position.x
        y = p.position.y
        z = p.position.z
        return self.check_if_point_inside(x, y, z)

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

    def mark_inner_nodes(self, spat_mesh):
        for i, j, k in np.ndindex(*spat_mesh.n_nodes):
            if self.check_if_point_inside(*spat_mesh.node_coordinates[i, j, k]):
                self._inner_nodes.append(Node(i, j, k))

    def select_inner_nodes_not_at_domain_edge(self, spat_mesh):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        for node in self._inner_nodes:
            if not node.at_domain_edge(nx, ny, nz):
                self._inner_nodes_not_at_domain_edge.append(node)

