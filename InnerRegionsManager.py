from ef.util.serializable_h5 import SerializableH5


class InnerRegionsManager(SerializableH5):

    def __init__(self, regions=()):
        self.regions = list(regions)

    def check_if_particle_inside(self, p):
        for region in self.regions:
            if region.check_if_particle_inside(p):
                return True
        return False

    def check_if_particle_inside_and_count_charge(self, p):
        for region in self.regions:
            if region.check_if_particle_inside_and_count_charge(p):
                return True
        return False
