__all__ = ["ParticleInteractionModel", "ParticleInteractionModelSection"]

from collections import namedtuple

from ef.config.section import ConfigSection
from ef.config.component import ConfigComponent
from ParticleInteractionModel import ParticleInteractionModel as _ParticleInteractionModel


class ParticleInteractionModel(ConfigComponent):
    def __init__(self, model="PIC"):
        if model not in ("PIC", 'noninteracting', 'binary'):
            raise ValueError("Unexpected particle interaction model: {}".format(model))
        self.model = model

    def to_conf(self):
        return ParticleInteractionModelSection(self.model)

    def make(self):
        return _ParticleInteractionModel.do_init()


class ParticleInteractionModelSection(ConfigSection):
    section = "ParticleInteractionModel"
    ContentTuple = namedtuple("ParticleInteractionModelTuple", ('particle_interaction_model',))
    convert = ContentTuple(str)

    def make(self):
        return ParticleInteractionModel(self.content.particle_interaction_model)
