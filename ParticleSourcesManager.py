import numpy as np

from Vec3d import Vec3d
from ef.util.serializable_h5 import SerializableH5


class ParticleSourcesManager(SerializableH5):

    def __init__(self, sources=()):
        self.sources = list(sources)

    def generate_initial_particles(self):
        for src in self.sources:
            src.generate_initial_particles()

    def generate_each_step(self):
        for src in self.sources:
            src.generate_each_step()

    def print_particles(self):
        for src in self.sources:
            src.print_particles()

    def print_num_of_particles(self):
        for src in self.sources:
            src.print_num_of_particles()

    def update_particles_position(self, dt):
        for src in self.sources:
            src.update_particles_position(dt)

    def boris_integration(self, dt, current_time,
                          spat_mesh, external_fields, inner_regions,
                          particle_interaction_model):
        # todo: too many arguments
        for src in self.sources:
            for particle in src.particles:
                total_el_field, total_mgn_field = \
                    self.compute_total_fields_at_position(
                        particle._position, current_time, spat_mesh, external_fields, inner_regions,
                        particle_interaction_model)
                if total_mgn_field:
                    particle.boris_update_momentum(dt, total_el_field, total_mgn_field)
                else:
                    particle.boris_update_momentum_no_mgn(dt, total_el_field)
                particle.update_position(dt)

    def prepare_boris_integration(self, minus_half_dt, current_time,
                                  spat_mesh, external_fields, inner_regions,
                                  particle_interaction_model):
        # todo: too many arguments
        # todo: place newly generated particles into separate buffer
        for src in self.sources:
            for particle in src.particles:
                if not particle.momentum_is_half_time_step_shifted:
                    total_el_field, total_mgn_field = \
                        self.compute_total_fields_at_position(
                            particle._position, current_time, spat_mesh, external_fields, inner_regions,
                            particle_interaction_model)
                    if total_mgn_field:
                        particle.boris_update_momentum(minus_half_dt,
                                                       total_el_field, total_mgn_field)
                    else:
                        particle.boris_update_momentum_no_mgn(minus_half_dt,
                                                              total_el_field)
                    particle.momentum_is_half_time_step_shifted = True

    def compute_total_fields_at_position(
            self, position, current_time, spat_mesh, external_fields, inner_regions,
            particle_interaction_model):
        total_el_field = external_fields.total_electric_field_at_position(position, current_time)
        if particle_interaction_model.noninteracting:
            if inner_regions or not spat_mesh.is_potential_equal_on_boundaries():
                total_el_field += spat_mesh.field_at_position(position)
        elif particle_interaction_model.binary:
            total_el_field += self.binary_field_at_point(position)
            if inner_regions or not spat_mesh.is_potential_equal_on_boundaries():
                total_el_field += spat_mesh.field_at_position(position)
        elif particle_interaction_model.pic:
            total_el_field += spat_mesh.field_at_position(position)
        total_mgn_field = None
        if external_fields.magnetic:
            total_mgn_field = external_fields.total_magnetic_field_at_position(position, current_time)
        return total_el_field, total_mgn_field

    def binary_field_at_point(self, position):
        return Vec3d(
            *sum(np.nan_to_num(p.field_at_point(position)) for src in self.sources for p in src.particles))
