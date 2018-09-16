import io
from configparser import ConfigParser

from ef.config.components import *
from ef.config.data_class import DataClass
from ef.config.section import ConfigSection


class EfConf(DataClass):
    # repr_arg_separator = ',\n'

    def __init__(self, time_grid=TimeGrid(), spatial_mesh=SpatialMesh(), sources=(), inner_regions=(),
                 output_file=OutputFile(), boundary_conditions=BoundaryConditions(),
                 particle_interaction_model=ParticleInteractionModel(), external_fields=()):
        self.time_grid = time_grid
        self.spatial_mesh = spatial_mesh
        self.sources = list(sources)
        self.inner_regions = list(inner_regions)
        self.output_file = output_file
        self.boundary_conditions = boundary_conditions
        self.particle_interaction_model = particle_interaction_model
        self.external_fields = list(external_fields)

    @classmethod
    def from_components(cls, components):
        parents = {'time_grid': TimeGrid, 'spatial_mesh': SpatialMesh,
                   'sources': ParticleSource, 'inner_regions': InnerRegion,
                   'output_file': OutputFile, 'boundary_conditions': BoundaryConditions,
                   'particle_interaction_model': ParticleInteractionModel,
                   'external_fields': Field}
        singletons = TimeGrid, SpatialMesh, OutputFile, BoundaryConditions, ParticleInteractionModel
        kwargs = {}
        for arg, parent in parents.items():
            children = [c for c in components if isinstance(c, parent)]
            if parent in singletons:
                if len(children) > 1:
                    raise Exception("Several {} configured, cannot init EfConf".format(parent))
                if len(children) < 1:
                    raise Exception("No {} configuration found, cannot init EfConf".format(parent))
                kwargs[arg] = children[0]
            else:
                kwargs[arg] = children
        return cls(**kwargs)

    @classmethod
    def from_configparser(cls, parser):
        return cls.from_components([section.make() for section in ConfigSection.parser_to_confs(parser)])

    @classmethod
    def from_fname(cls, fname):
        parser = ConfigParser()
        parser.read(fname)
        return cls.from_configparser(parser)

    @classmethod
    def from_file(cls, file):
        parser = ConfigParser()
        parser.read_file(file)
        return cls.from_configparser(parser)

    @classmethod
    def from_string(cls, s):
        parser = ConfigParser()
        parser.read_string(s)
        return cls.from_configparser(parser)

    @property
    def components(self):
        return [self.time_grid, self.spatial_mesh] + self.sources + self.inner_regions + \
               [self.output_file, self.boundary_conditions, self.particle_interaction_model] + self.external_fields

    def get_potentials(self):
        return [self.boundary_conditions.potential] + [region.potential for region in self.inner_regions]

    def to_sections(self):
        return [c.to_conf() for c in self.components]

    def visualize_all(self, visualizer):
        p = self.get_potentials()
        visualizer.set_potential_lim(min(p), max(p))
        self.boundary_conditions.visualize(visualizer, self.spatial_mesh.size)
        visualizer.visualize(self.sources)
        visualizer.visualize(self.inner_regions)
        visualizer.visualize(self.external_fields)
        visualizer.show()

    def export_to_fname(self, fname):
        with open(fname, 'w') as f:
            self.export_to_file(f)

    def export_to_file(self, file):
        parser = ConfigParser()
        for section in self.to_sections():
            section.add_section_to_parser(parser)
        parser.write(file)

    def export_to_string(self):
        iostr = io.StringIO()
        self.export_to_file(iostr)
        return iostr.getvalue()


def main():
    ef = EfConf()
    print(ef)


if __name__ == "__main__":
    main()
