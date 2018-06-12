from ef.util.serializable_h5 import SerializableH5


class ParticleInteractionModel(SerializableH5):
    @property
    def noninteracting(self):
        return self.particle_interaction_model == "noninteracting"

    @property
    def binary(self):
        return self.particle_interaction_model == "binary"

    @property
    def pic(self):
        return self.particle_interaction_model == "PIC"

    def __init__(self, particle_interaction_model=None):
        if particle_interaction_model not in ("PIC", 'noninteracting', 'binary'):
            raise ValueError(f"Unexpected particle interaction model: {particle_interaction_model}")
        self.particle_interaction_model = particle_interaction_model

    def write_to_file(self, h5file):
        groupname = "/ParticleInteractionModel"
        h5group = h5file.create_group(groupname)
        self.save_h5(h5group)