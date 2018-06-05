import sys


class ParticleInteractionModel:
    @property
    def noninteracting(self):
        return self.particle_interaction_model == "noninteracting"

    @property
    def binary(self):
        return self.particle_interaction_model == "binary"

    @property
    def pic(self):
        return self.particle_interaction_model == "PIC"

    def __init__(self, model=None):
        self.particle_interaction_model = model

    @classmethod
    def init_from_config(cls, conf):
        new_obj = cls()
        new_obj.check_correctness_of_related_config_fields(conf)
        new_obj.get_values_from_config(conf)
        ParticleInteractionModel.mark_partintmodel_sec_as_used(conf)
        return new_obj

    @staticmethod
    def mark_partintmodel_sec_as_used(conf):
        # For now simply mark sections as 'used' instead of removing them.
        conf["ParticleInteractionModel"]["used"] = "True"

    def check_correctness_of_related_config_fields(self, conf):
        conf_part = conf["ParticleInteractionModel"]
        model = conf_part["particle_interaction_model"]
        # 'PIC' or 'noninteracting' or 'binary'
        if model != "noninteracting" and model != "binary" and model != "PIC":
            print("Error: wrong value of 'particle_interaction_model': {}".format(model))
            print("Allowed values : 'noninteracting', 'binary', 'PIC'")
            print("Aborting")
            sys.exit(-1)

    def get_values_from_config(self, conf):
        conf_part = conf["ParticleInteractionModel"]
        self.particle_interaction_model = conf_part["particle_interaction_model"]

    @classmethod
    def init_from_h5(cls, h5group):
        new_obj = cls()
        new_obj.particle_interaction_model = h5group.attrs["particle_interaction_model"]
        return new_obj

    def __str__(self):
        return "particle_interaction_model = {}".format(self.particle_interaction_model)

    def print(self):
        print("### ParticleInteractionModel:")
        print(self)
        print("self.noninteracting = {}".format(self.noninteracting))
        print("self.binary = {}".format(self.binary))
        print("self.pic = {}".format(self.pic))

    def write_to_file(self, h5file):
        groupname = "/ParticleInteractionModel"
        h5group = h5file.create_group(groupname)
        h5group.attrs["particle_interaction_model"] = self.particle_interaction_model
