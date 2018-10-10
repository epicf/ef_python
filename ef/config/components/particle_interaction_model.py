__all__ = ["ParticleInteractionModel", "ParticleInteractionModelConf"]

from collections import namedtuple

from ef.config.section import register, ConfigSection
from ef.config.component import ConfigComponent


class ParticleInteractionModel(ConfigComponent):
    def __init__(self, model="PIC"):
        if model not in ("PIC", 'noninteracting', 'binary'):
            raise ValueError("Unexpected particle interaction model: {}".format(model))
        self.model = model

    def to_conf(self):
        return ParticleInteractionModelConf(self.model)


@register
class ParticleInteractionModelConf(ConfigSection):
    section = "ParticleInteractionModel"
    ContentTuple = namedtuple("ParticleInteractionModelTuple", ('particle_interaction_model',))
    convert = ContentTuple(str)

    def make(self):
        return ParticleInteractionModel(self.content.particle_interaction_model)
