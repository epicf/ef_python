import numpy as np

from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


class ParticleToMeshMap(SerializableH5):

    @classmethod
    def weight_particles_charge_to_mesh(cls, spat_mesh, particle_sources):
        volume_around_node = spat_mesh.cell.prod()
        for part_src in particle_sources.sources:
            for p in part_src.particles:
                charge = p.charge / volume_around_node
                node, remainder = np.divmod(p._position, spat_mesh.cell)
                nx, ny, nz = np.array(node, np.int)
                cell_slice = spat_mesh.charge_density[nx:nx + 2, ny:ny + 2, nz:nz + 2]
                weight = remainder / spat_mesh.cell
                weights = np.array([1. - weight, weight])
                dn = np.moveaxis(np.mgrid[0:2, 0:2, 0:2], 0, -1)
                cell_slice += weights[dn, [0, 1, 2]].prod(-1) * charge

    @classmethod
    def field_at_position(cls, spat_mesh, position):
        node, remainder = np.divmod(position, spat_mesh.cell)
        nx, ny, nz = np.array(node, np.int)
        cell_slice = spat_mesh.electric_field[nx:nx + 2, ny:ny + 2, nz:nz + 2]
        weight = remainder / spat_mesh.cell
        weights = np.array([1. - weight, weight])
        dn = np.moveaxis(np.mgrid[0:2, 0:2, 0:2], 0, -1)
        return Vec3d(*(weights[dn, [0, 1, 2]].prod(-1)[:, :, :, np.newaxis] * cell_slice).sum((0, 1, 2)))
