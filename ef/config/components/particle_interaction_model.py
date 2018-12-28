__all__ = ["ParticleInteractionModelConf", "ParticleInteractionModelSection"]

from collections import namedtuple

import particle_interaction_model
from ef.config.component import ConfigComponent
from ef.config.section import ConfigSection


class ParticleInteractionModelConf(ConfigComponent):
    def __init__(self, model="PIC"):
        if model not in ("PIC", 'noninteracting', 'binary'):
            raise ValueError("Unexpected particle interaction model: {}".format(model))
        self.model = model

    def to_conf(self):
        return ParticleInteractionModelSection(self.model)

    def make(self):
        return particle_interaction_model.ParticleInteractionModel(self.model)


class ParticleInteractionModelSection(ConfigSection):
    section = "ParticleInteractionModel"
    ContentTuple = namedtuple("ParticleInteractionModelTuple", ('particle_interaction_model',))
    convert = ContentTuple(str)

    def make(self):
        return ParticleInteractionModelConf(self.content.particle_interaction_model)
