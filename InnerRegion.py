from ef.util.serializable_h5 import SerializableH5


class InnerRegion(SerializableH5):

    def __init__(self, name, shape, potential=0.0, total_absorbed_particles=0, total_absorbed_charge=0.0):
        self.name = name
        self.shape = shape
        self.potential = potential
        self.total_absorbed_particles = total_absorbed_particles
        self.total_absorbed_charge = total_absorbed_charge

    def check_if_particle_inside(self, p):
        return self.check_if_points_inside(p.positions)

    def check_if_particle_inside_and_count_charge(self, p):
        in_or_out = self.check_if_particle_inside(p)  # todo: fix for particle arrays
        if in_or_out:
            self.total_absorbed_particles += 1
            self.total_absorbed_charge += p.charge
        return in_or_out

    def check_if_points_inside(self, positions):
        return self.shape.are_points_inside(positions)
