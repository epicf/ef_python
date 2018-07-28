from math import ceil
from Vec3d import Vec3d

class ParticleToMeshMap():  

    @classmethod
    def weight_particles_charge_to_mesh(cls, spat_mesh, particle_sources):
        # Rewrite:
        # forall particles {
        #   find nonzero weights and corresponding nodes
        #   charge[node] = weight(particle, node) * particle.charge
        # }
        dx = spat_mesh.x_cell_size
        dy = spat_mesh.y_cell_size
        dz = spat_mesh.z_cell_size
        cell_volume = dx * dy * dz
        volume_around_node = cell_volume
        # 'tlf' = 'top_left_far'
        for part_src in particle_sources.sources:
            for p in part_src.particles:
                tlf_i, tlf_x_weight = next_node_num_and_weight(p.position.x, dx)
                tlf_j, tlf_y_weight = next_node_num_and_weight(p.position.y, dy)
                tlf_k, tlf_z_weight = next_node_num_and_weight(p.position.z, dz)
                spat_mesh.charge_density[tlf_i][tlf_j][tlf_k] += \
                        tlf_x_weight * tlf_y_weight * tlf_z_weight \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i-1][tlf_j][tlf_k] += \
                        (1.0 - tlf_x_weight) * tlf_y_weight * tlf_z_weight \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i][tlf_j-1][tlf_k] += \
                        tlf_x_weight * (1.0 - tlf_y_weight) * tlf_z_weight \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i-1][tlf_j-1][tlf_k] += \
                        (1.0 - tlf_x_weight) * (1.0 - tlf_y_weight) * tlf_z_weight \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i][tlf_j][tlf_k - 1] += \
                        tlf_x_weight * tlf_y_weight * (1.0 - tlf_z_weight) \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i-1][tlf_j][tlf_k - 1] += \
                        (1.0 - tlf_x_weight) * tlf_y_weight * (1.0 - tlf_z_weight) \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i][tlf_j-1][tlf_k - 1] += \
                        tlf_x_weight * (1.0 - tlf_y_weight) * (1.0 - tlf_z_weight) \
                        * p.charge / volume_around_node
                spat_mesh.charge_density[tlf_i-1][tlf_j-1][tlf_k - 1] += \
                        (1.0 - tlf_x_weight) * (1.0 - tlf_y_weight) * \
                        (1.0 - tlf_z_weight) \
                        * p.charge / volume_around_node


    @classmethod
    def field_at_particle_position(cls, spat_mesh, p):
        dx = spat_mesh.x_cell_size
        dy = spat_mesh.y_cell_size
        dz = spat_mesh.z_cell_size
        # 'tlf' = 'top_left_far'
        tlf_i, tlf_x_weight = next_node_num_and_weight(p.position.x, dx)
        tlf_j, tlf_y_weight = next_node_num_and_weight(p.position.y, dy)
        tlf_k, tlf_z_weight = next_node_num_and_weight(p.position.z, dz)
        # tlf
        total_field = Vec3d.zero()
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j][tlf_k].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # trf
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j][tlf_k].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # blf
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j - 1][tlf_k].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # brf
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j-1][tlf_k].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # tln
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j][tlf_k-1].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # trn
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j][tlf_k-1].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # bln
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j - 1][tlf_k-1].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # brn
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j-1][tlf_k-1].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        #
        return total_field


    @classmethod
    def force_on_particle(cls, spat_mesh, p):
        dx = spat_mesh.x_cell_size
        dy = spat_mesh.y_cell_size
        dz = spat_mesh.z_cell_size
        # 'tlf' = 'top_left_far'
        tlf_i, tlf_x_weight = next_node_num_and_weight(p.position.x, dx)
        tlf_j, tlf_y_weight = next_node_num_and_weight(p.position.y, dy)
        tlf_k, tlf_z_weight = next_node_num_and_weight(p.position.z, dz)
        # tlf
        total_field = Vec3d.zero()
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j][tlf_k].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # trf
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j][tlf_k].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # blf
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j - 1][tlf_k].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # brf
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j-1][tlf_k].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # tln
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j][tlf_k-1].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # trn
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j][tlf_k-1].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # bln
        field_from_node = spat_mesh.electric_field[tlf_i][tlf_j - 1][tlf_k-1].times_scalar(
            tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        # brn
        field_from_node = spat_mesh.electric_field[tlf_i-1][tlf_j-1][tlf_k-1].times_scalar(
            1.0 - tlf_x_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_y_weight)
        field_from_node = field_from_node.times_scalar(1.0 - tlf_z_weight)
        total_field = total_field.add(field_from_node)
        #
        force = total_field.times_scalar(p.charge)
        return force


def next_node_num_and_weight(x, grid_step):
    x_in_grid_units = x / grid_step
    next_node = ceil(x_in_grid_units)
    weight = 1.0 - (next_node - x_in_grid_units)
    return (next_node, weight)
