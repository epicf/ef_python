from collections import namedtuple

import abc

from ef.config.components import Box, Cylinder, Tube, TimeGrid, SpatialMesh, ParticleSource, InnerRegion


class ConfigComponent(abc.ABC):
    section_map = {}

    @classmethod
    def config_to_components(cls, conf):
        return [cls.section_map[section.split('.')[0]].from_section(conf[section]) for section in
                conf.sections()]

    @classmethod
    def register(cls):
        cls.section_map[cls.section] = cls

    def __init__(self, *args, **kwargs):
        self.content = self.ContentTuple(*args, **kwargs)

    @classmethod
    def from_section(cls, section):
        if section.name != cls.section:
            raise ValueError("Unexpected config section name: {}".format(section.name))
        if set(section.keys()) != set(cls.ContentTuple._fields):
            unexpected = set(section.keys()) - set(cls.ContentTuple._fields)
            if unexpected:
                raise ValueError("Unexpected config variables {} in section {}".
                                 format(tuple(unexpected), section.name))
            missing = set(cls.ContentTuple._fields) - set(section.keys())
            if missing:
                raise ValueError("Missing config variables {} in section {}".
                                 format(tuple(missing), section.name))

        data = {arg: cls.convert._asdict()[arg](section[arg]) for arg in cls.convert._fields}
        return cls(**data)

    def to_section(self, conf):
        conf.add_section(self.section)
        for k, v in self.content._asdict().items():
            conf.set(self.section, k, str(v))

    def make(self):
        raise NotImplementedError()

    def __repr__(self):
        return "{}(section={}, data={})".format(self.__class__.__name__, self.section, repr(self.content))

    def __str__(self):
        return "{}: {}".format(self.section, dict(self.content._asdict()))


def register(cls):
    ConfigComponent.section_map[cls.section] = cls
    return cls


class NamedConfigComponent(ConfigComponent):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.section = self.section + '.' + name
        super().__init__(*args, **kwargs)

    @classmethod
    def from_section(cls, section):
        category, name = section.name.split('.', 1)
        if category != cls.section:
            raise ValueError("Unexpected config section name: {}".format(section.name))
        if set(section.keys()) != set(cls.ContentTuple._fields):
            unexpected = set(section.keys()) - set(cls.ContentTuple._fields)
            if unexpected:
                raise ValueError("Unexpected config variables {} in section {}".
                                 format(tuple(unexpected), section.name))
            missing = set(cls.ContentTuple._fields) - set(section.keys())
            if missing:
                raise ValueError("Missing config variables {} in section {}".
                                 format(tuple(missing), section.name))

        data = {arg: cls.convert._asdict()[arg](section[arg]) for arg in cls.convert._fields}
        return cls(name, **data)


@register
class TimeGridConf(ConfigComponent):
    section = "Time grid"
    ContentTuple = namedtuple("TimeGridTuple", ('total_time', 'time_save_step', 'time_step_size'))
    convert = ContentTuple(float, float, float)

    def make(self):
        return TimeGrid(*self.content)


@register
class SpatialMeshConf(ConfigComponent):
    section = "Spatial mesh"
    ContentTuple = namedtuple("SpatialMeshTuple", ('grid_x_size', 'grid_x_step', 'grid_y_size',
                                                   'grid_y_step', 'grid_z_size', 'grid_z_step'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        return SpatialMesh(self.content[::2], self.content[1::2])


@register
class BoundaryConditionsConf(ConfigComponent):
    section = "Boundary conditions"
    ContentTuple = namedtuple("BoundaryConditionsTuple",
                              ('boundary_phi_right', 'boundary_phi_left', 'boundary_phi_bottom',
                               'boundary_phi_top', 'boundary_phi_near', 'boundary_phi_far'))
    convert = ContentTuple(*[float] * 6)

    def make(self):
        return BoundaryConditionsConf(*self.content)


@register
class ParticleSourceBoxConf(NamedConfigComponent):
    section = "Particle_source_box"
    ContentTuple = namedtuple("ParticleSourceBoxTuple", ('box_x_right', 'box_x_left', 'box_y_bottom',
                                                         'box_y_top', 'box_z_near', 'box_z_far',
                                                         'initial_number_of_particles',
                                                         'particles_to_generate_each_step',
                                                         'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                         'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 6 + [int] * 2 + [float] * 6))

    def make(self):
        box = Box.init_rlbtnf(*self.content[:6])
        return ParticleSource(box, self.name, *self.content[6:])


@register
class ParticleSourceCylinderConf(NamedConfigComponent):
    section = "Particle_source_cylinder"
    ContentTuple = namedtuple("ParticleSourceCylinderTuple", ('cylinder_axis_start_x', 'cylinder_axis_start_y',
                                                              'cylinder_axis_start_z', 'cylinder_axis_end_x',
                                                              'cylinder_axis_end_y', 'cylinder_axis_end_z',
                                                              'cylinder_radius',
                                                              'initial_number_of_particles',
                                                              'particles_to_generate_each_step',
                                                              'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                              'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 7 + [int] * 2 + [float] * 6))

    def make(self):
        cylinder = Cylinder(self.content[:3], self.content[3:6], self.content.cylinder_radius)
        return ParticleSource(cylinder, self.name, *self.content[7:])


@register
class ParticleSourceTubeConf(NamedConfigComponent):
    section = "Particle_source_tube"
    ContentTuple = namedtuple("ParticleSourceTubeTuple", ('tube_axis_start_x', 'tube_axis_start_y',
                                                          'tube_axis_start_z', 'tube_axis_end_x',
                                                          'tube_axis_end_y', 'tube_axis_end_z',
                                                          'tube_inner_radius', 'tube_outer_radius',
                                                          'initial_number_of_particles',
                                                          'particles_to_generate_each_step',
                                                          'mean_momentum_x', 'mean_momentum_y', 'mean_momentum_z',
                                                          'temperature', 'charge', 'mass'))
    convert = ContentTuple(*([float] * 8 + [int] * 2 + [float] * 6))

    def make(self):
        tube = Tube(self.content[:3], self.content[3:6], self.content.tube_inner_radius, self.content.tube_outer_radius)
        return ParticleSource(tube, self.name, *self.content[8:])


@register
class InnerRegionBoxConf(NamedConfigComponent):
    section = "Inner_region_box"
    ContentTuple = namedtuple("InnerRegionBoxTuple", ('box_x_right', 'box_x_left', 'box_y_bottom',
                                                      'box_y_top', 'box_z_near', 'box_z_far',
                                                      'potential'))
    convert = ContentTuple(*[float] * 7)

    def make(self):
        box = Box.init_rlbtnf(*self.content[:6])
        return InnerRegion(box, self.name, self.content.potential)


@register
class InnerRegionCylinderConf(NamedConfigComponent):
    section = "Inner_region_cylinder"
    ContentTuple = namedtuple("InnerRegionCylinderTuple", ('cylinder_axis_start_x', 'cylinder_axis_start_y',
                                                           'cylinder_axis_start_z', 'cylinder_axis_end_x',
                                                           'cylinder_axis_end_y', 'cylinder_axis_end_z',
                                                           'cylinder_radius', 'potential'))
    convert = ContentTuple(*[float] * 8)

    def make(self):
        cylinder = Cylinder(self.content[:3], self.content[3:6], self.content.cylinder_radius)
        return ParticleSource(cylinder, self.name, self.content.potential)


@register
class InnerRegionTubeConf(NamedConfigComponent):
    section = "Inner_region_tube"
    ContentTuple = namedtuple("InnerRegionTubeTuple", ('tube_axis_start_x', 'tube_axis_start_y',
                                                       'tube_axis_start_z', 'tube_axis_end_x',
                                                       'tube_axis_end_y', 'tube_axis_end_z',
                                                       'tube_inner_radius', 'tube_outer_radius',
                                                       'potential'))
    convert = ContentTuple(*[float] * 9)

    def make(self):
        tube = Tube(self.content[:3], self.content[3:6], self.content.tube_inner_radius, self.content.tube_outer_radius)
        return InnerRegion(tube, self.name, self.content.potential)


@register
class ParticleInteractionModel(ConfigComponent):
    section = "Particle interaction model"
    ContentTuple = namedtuple("ParticleInteractionModelTuple", ('particle_interaction_model',))
    convert = ContentTuple(str)

    def make(self):
        pass


@register
class ExternalMagneticFieldUniformConf(NamedConfigComponent):
    section = "External_magnetic_field_uniform"
    ContentTuple = namedtuple("ExternalMagneticFieldUniform",
                              ('magnetic_field_x', 'magnetic_field_y', 'magnetic_field_z'))
    convert = ContentTuple(float, float, float)

    def make(self):
        pass


@register
class ExternalElectricFieldUniformConf(NamedConfigComponent):
    section = "External_electric_field_uniform"
    ContentTuple = namedtuple("ExternalElectricFieldUniform",
                              ('electric_field_x', 'electric_field_y', 'electric_field_z'))
    convert = ContentTuple(float, float, float)

    def make(self):
        pass


@register
class OutputFilenameConf(ConfigComponent):
    section = "Output filename"
    ContentTuple = namedtuple("OutputFileNameTuple", ('output_filename_prefix', 'output_filename_suffix'))
    convert = ContentTuple(str, str)

    def make(self):
        pass


def main():
    from configparser import ConfigParser
    import io
    from glob import glob

    for f in glob('../../examples/*/*.conf'):
        print(f)
        conf = ConfigParser()
        conf.read(f)
        try:
            c = ConfigComponent.config_to_components(conf)
        except Exception as e:
            raise Exception("Error parsing {}".format(f)) from e

        conf = ConfigParser()
        for x in c:
            x.to_section(conf)
        str_out = io.StringIO()
        conf.write(str_out)
        print(str_out.getvalue())


if __name__ == "__main__":
    main()
