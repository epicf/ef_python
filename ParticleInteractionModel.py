from enum import Enum, auto

from ef.util.serializable_h5 import SerializableH5


class Model(Enum):
    noninteracting = auto()
    binary = auto()
    PIC = auto()

    def __repr__(self):
        return f"Model.{self.name}"


class ParticleInteractionModel(SerializableH5):
    @property
    def noninteracting(self):
        return self.particle_interaction_model == Model.noninteracting

    @property
    def binary(self):
        return self.particle_interaction_model == Model.binary

    @property
    def pic(self):
        return self.particle_interaction_model == Model.PIC

    def __init__(self, particle_interaction_model=Model.PIC):
        if isinstance(particle_interaction_model, Model):
            self.particle_interaction_model = particle_interaction_model
        else:
            self.particle_interaction_model = Model[particle_interaction_model]
