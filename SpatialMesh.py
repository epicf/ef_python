import logging

import numpy as np

from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


class SpatialMesh(SerializableH5):
    def __init__(self, size, n_nodes, charge_density, potential, electric_field):
        self.size = size
        self.n_nodes = n_nodes
        self.cell = size / (self.n_nodes - 1)
        self._node_coordinates = np.moveaxis(np.mgrid[0:self.n_nodes[0], 0:self.n_nodes[1], 0:self.n_nodes[2]], 0, -1) \
                                 * self.cell
        self.charge_density = charge_density
        self.potential = potential
        self.electric_field = electric_field

    @property
    def node_coordinates(self):
        return self._node_coordinates

    @property
    def dict(self):
        d = super().dict
        del d["cell"]
        return d

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

        n_nodes = np.ceil(size / step).astype(int) + 1
        charge_density = np.zeros(n_nodes, dtype='f8')
        potential = np.zeros(n_nodes, dtype='f8')
        potential[:, 0, :] = boundary_conditions.bottom
        potential[:, -1, :] = boundary_conditions.top
        potential[0, :, :] = boundary_conditions.right
        potential[-1, :, :] = boundary_conditions.left
        potential[:, :, 0] = boundary_conditions.near
        potential[:, :, -1] = boundary_conditions.far
        electric_field = np.zeros(list(n_nodes) + [3], dtype='f8')

        self = cls(size, n_nodes, charge_density, potential, electric_field)

        for i in np.nonzero(self.cell != step_size)[0]:
            logging.warning(f"{('X', 'Y', 'Z')[i]} step on spatial grid was reduced to "
                            f"{self.cell[i]:.3f} from {step_size[i]:.3f} "
                            f"to fit in a round number of cells.")
        return self

    def weight_particles_charge_to_mesh(self, particle_sources):
        volume_around_node = self.cell.prod()
        for part_src in particle_sources:
            for p in part_src.particles:
                charge = p.charge / volume_around_node
                node, remainder = np.divmod(p._position, self.cell)
                nx, ny, nz = np.array(node, np.int)
                cell_slice = self.charge_density[nx:nx + 2, ny:ny + 2, nz:nz + 2]
                weight = remainder / self.cell
                weights = np.array([1. - weight, weight])
                dn = np.moveaxis(np.mgrid[0:2, 0:2, 0:2], 0, -1)
                cell_slice += weights[dn, [0, 1, 2]].prod(-1) * charge

    def field_at_position(self, position):
        node, remainder = np.divmod(position, self.cell)
        nx, ny, nz = np.array(node, np.int)
        cell_slice = self.electric_field[nx:nx + 2, ny:ny + 2, nz:nz + 2]
        weight = remainder / self.cell
        weights = np.array([1. - weight, weight])
        dn = np.moveaxis(np.mgrid[0:2, 0:2, 0:2], 0, -1)
        return Vec3d(*(weights[dn, [0, 1, 2]].prod(-1)[:, :, :, np.newaxis] * cell_slice).sum((0, 1, 2)))

    def clear_old_density_values(self):
        self.charge_density.fill(0)

    def is_potential_equal_on_boundaries(self):
        p = self.potential[0, 0, 0]
        return np.all(self.potential[0] == p) and np.all(self.potential[-1] == p) and \
               np.all(self.potential[:, 0] == p) and np.all(self.potential[:, -1] == p) and \
               np.all(self.potential[:, :, 0] == p) and np.all(self.potential[:, :, -1] == p)
