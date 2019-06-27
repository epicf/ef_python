import logging
from itertools import product

import numpy as np

from ef.util.serializable_h5 import SerializableH5


class MeshGrid(SerializableH5):
    def __init__(self, size, n_nodes, origin=(0, 0, 0)):
        self.size = size
        self.n_nodes = n_nodes
        self.origin = np.asarray(origin)

    @classmethod
    def from_step(cls, size, step, origin=(0, 0, 0)):
        n_nodes = np.ceil(size / step).astype(int) + 1
        return cls(size, n_nodes, origin)

    @property
    def cell(self):
        return self.size / (self.n_nodes - 1)

    @property
    def node_coordinates(self):
        return self.origin + \
               np.moveaxis(np.mgrid[0:self.n_nodes[0], 0:self.n_nodes[1], 0:self.n_nodes[2]], 0, -1) * self.cell

    def distribute_scalar_at_positions(self, value, positions):
        """
        Given a set of points, distribute the scalar value's density onto the grid nodes.

        :param value: scalar
        :param positions: array of shape (np, 3)
        :return: array of shape (nx, ny, nz)
        """
        volume_around_node = self.cell.prod()
        density = value / volume_around_node  # scalar
        result = np.zeros(self.n_nodes)
        pos = positions - self.origin
        nodes, remainders = np.divmod(pos, self.cell)  # (np, 3)
        nodes = nodes.astype(int)  # (np, 3)
        weights = remainders / self.cell  # (np, 3)
        w = np.stack([1. - weights, weights], axis=-2)  # (np, 2, 3)
        dn = np.array(list(product((0, 1), repeat=3)))  # (8, 3)
        weight_on_nodes = w[:, dn[:, (0, 1, 2)], (0, 1, 2)].prod(-1)  # (np, 8)
        nodes_to_update = nodes[:, np.newaxis] + dn[np.newaxis, :]  # (np, 8, 3)
        wf = weight_on_nodes.flatten()  # (np*8)
        nf = nodes_to_update.reshape((-1, 3))  # (np*8, 3)
        wz = wf[wf > 0]
        nz = nf[wf > 0]
        # df = pd.DataFrame.from_dict({'coords': nodes_to_update, 'weight': weight_on_nodes})
        if np.any(np.logical_or(nz >= self.n_nodes, nz < 0)):
            raise ValueError("Position is out of meshgrid bounds")
        for i in range(len(wz)):
            result[tuple(nz[i])] += wz[i] * density
        return result

    def interpolate_field_at_positions(self, field, positions):
        """
        Given a field on this grid, interpolate it at n positions.

        :param field: array of shape (nx, ny, nz, {F})
        :param positions: array of shape (np, 3)
        :return: array of shape (np, {F})
        """
        node, remainder = np.divmod(positions - self.origin, self.cell)
        node = node.astype(int)  # shape is (p, 3)
        weight = remainder / self.cell  # shape is (np, 3)
        w = np.stack([1. - weight, weight], axis=-2)  # shape is (np, 2, 3)
        dn = np.array(list(product((0, 1), repeat=3)))  # shape is (8, 3)
        nodes_to_use = node[..., np.newaxis, :] + dn  # shape is (np, 8, 3)
        field_indexes = np.moveaxis(nodes_to_use, -1, 0)  # shape is (3, np, 8)
        out_of_bounds = np.logical_or(nodes_to_use >= self.n_nodes, nodes_to_use < 0).any(axis=-1)  # (np, 8)
        field_on_nodes = np.empty((*field.shape[3:], len(positions), 8))  # (F, np, 8)
        field_on_nodes[..., out_of_bounds] = 0  # (F, np, 8) interpolate out-of-bounds field as 0
        field_on_nodes[..., ~out_of_bounds] = field[tuple(field_indexes[:, ~out_of_bounds])].transpose()  # sorry...
        weight_on_nodes = w[..., dn[:, (0, 1, 2)], (0, 1, 2)].prod(-1)  # shape is (np, 8)
        return np.moveaxis((field_on_nodes * weight_on_nodes).sum(axis=-1), -1, 0)  # shape is (np, F)


class SpatialMesh(SerializableH5):
    def __init__(self, mesh, charge_density, potential, electric_field):
        self.mesh = mesh
        self.charge_density = charge_density
        self.potential = potential
        self.electric_field = electric_field

    @property
    def size(self):
        return self.mesh.size

    @property
    def cell(self):
        return self.mesh.cell

    @property
    def n_nodes(self):
        return self.mesh.n_nodes

    @property
    def node_coordinates(self):
        return self.mesh.node_coordinates

    @classmethod
    def do_init(cls, grid_size, step_size, boundary_conditions):
        try:
            size = np.array(grid_size, np.float)
        except ValueError as exception:
            raise ValueError("grid_size must be a flat triple", grid_size) from exception
        try:
            step = np.array(step_size, np.float)
        except ValueError as exception:
            raise ValueError("step_size must be a flat triple", step_size) from exception
        # Check argument ranges
        if size.shape != (3,):
            raise ValueError("grid_size must be a flat triple", grid_size)
        if step.shape != (3,):
            raise ValueError("step_size must be a flat triple", step_size)
        if np.any(size <= 0):
            raise ValueError("grid_size must be positive", grid_size)
        if np.any(step <= 0):
            raise ValueError("step_size must be positive", step_size)
        if np.any(step > size):
            raise ValueError("step_size cannot be bigger than grid_size")

        grid = MeshGrid.from_step(size, step)
        for i in np.nonzero(grid.cell != step_size)[0]:
            logging.warning(f"{('X', 'Y', 'Z')[i]} step on spatial grid was reduced to "
                            f"{grid.cell[i]:.3f} from {step_size[i]:.3f} "
                            f"to fit in a round number of cells.")
        charge_density = np.zeros(grid.n_nodes, dtype='f8')
        potential = np.zeros(grid.n_nodes, dtype='f8')
        potential[:, 0, :] = boundary_conditions.bottom
        potential[:, -1, :] = boundary_conditions.top
        potential[0, :, :] = boundary_conditions.right
        potential[-1, :, :] = boundary_conditions.left
        potential[:, :, 0] = boundary_conditions.near
        potential[:, :, -1] = boundary_conditions.far
        electric_field = np.zeros(list(grid.n_nodes) + [3], dtype='f8')
        return cls(grid, charge_density, potential, electric_field)

    def weight_particles_charge_to_mesh(self, particle_arrays):
        for p in particle_arrays:
            self.charge_density += self.mesh.distribute_scalar_at_positions(p.charge, p.positions)

    def field_at_position(self, positions):
        return self.mesh.interpolate_field_at_positions(self.electric_field, positions)

    def clear_old_density_values(self):
        self.charge_density.fill(0)

    def is_potential_equal_on_boundaries(self):
        p = self.potential[0, 0, 0]
        return np.all(self.potential[0] == p) and np.all(self.potential[-1] == p) and \
               np.all(self.potential[:, 0] == p) and np.all(self.potential[:, -1] == p) and \
               np.all(self.potential[:, :, 0] == p) and np.all(self.potential[:, :, -1] == p)
