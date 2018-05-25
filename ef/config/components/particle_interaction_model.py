from collections import namedtuple

from ef.config.parser import register, ConfigComponent, DataClass


class ParticleInteractionModel(DataClass):
    def __init__(self, model="PIC"):
        if model not in ("PIC", 'noninteracting', 'binary'):
            raise ValueError("Unexpected particle interaction model: {}".format(model))
        self.model = model

    def to_conf(self):
        return ParticleInteractionModelConf(self.model)


@register
class ParticleInteractionModelConf(ConfigComponent):
    section = "Particle interaction model"
    ContentTuple = namedtuple("ParticleInteractionModelTuple", ('particle_interaction_model',))
    convert = ContentTuple(str)

    def make(self):
        return ParticleInteractionModel(self.content.particle_interaction_model)
