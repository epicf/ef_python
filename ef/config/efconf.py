import io
from configparser import ConfigParser

import Domain
from ExternalFieldsManager import ExternalFieldsManager
from FieldSolver import FieldSolver
from InnerRegionsManager import InnerRegionsManager
from ParticleSourcesManager import ParticleSourcesManager
from ParticleToMeshMap import ParticleToMeshMap
from ef.config.components import *
from ef.config.section import ConfigSection
from ef.util.data_class import DataClass


class EfConf(DataClass):
    def __init__(self, time_grid=TimeGridConf(), spatial_mesh=SpatialMeshConf(), sources=(), inner_regions=(),
                 output_file=OutputFileConf(), boundary_conditions=BoundaryConditionsConf(),
                 particle_interaction_model=ParticleInteractionModelConf(), external_fields=()):
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
        parents = {'time_grid': TimeGridConf, 'spatial_mesh': SpatialMeshConf,
                   'sources': ParticleSourceConf, 'inner_regions': InnerRegionConf,
                   'output_file': OutputFileConf, 'boundary_conditions': BoundaryConditionsConf,
                   'particle_interaction_model': ParticleInteractionModelConf,
                   'external_fields': FieldConf}
        singletons = TimeGridConf, SpatialMeshConf, OutputFileConf, BoundaryConditionsConf, ParticleInteractionModelConf
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
        bc = self.boundary_conditions
        return [bc.left, bc.right, bc.top, bc.bottom, bc.near, bc.far] + [region.potential for region in
                                                                          self.inner_regions]

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

    def make(self):
        mesh = self.spatial_mesh.make(self.boundary_conditions)
        regions = InnerRegionsManager([ir.make() for ir in self.inner_regions])
        return Domain.Domain(self.time_grid.make(), mesh, regions, ParticleToMeshMap(), FieldSolver(mesh, regions),
                             ParticleSourcesManager([s.make() for s in self.sources]),
                             ExternalFieldsManager(
                                 [s.make() for s in self.external_fields if s.electic_or_magnetic == 'electric'],
                                 [s.make() for s in self.external_fields if s.electic_or_magnetic == 'magnetic']),
                             self.particle_interaction_model.make(), self.output_file.prefix, self.output_file.suffix)


def main():
    ef = EfConf()
    print(ef)


if __name__ == "__main__":
    main()
