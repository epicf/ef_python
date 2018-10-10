import sys

from Vec3d import Vec3d
from ParticleSourceBox import ParticleSourceBox
from ParticleSourceCylinder import ParticleSourceCylinder
from ParticleSourceTube import ParticleSourceTube

class ParticleSourcesManager:

    def __init__(self):
        self.sources = None


    @classmethod
    def init_from_config(cls, conf):
        new_obj = cls()
        new_obj.sources = []
        for sec_name in conf.sections():
            if ParticleSourceBox.is_box_source(sec_name):
                new_obj.sources.append(
                    ParticleSourceBox.init_from_config(conf,
                                                       conf[sec_name],
                                                       sec_name))
                ParticleSourcesManager.mark_particlesource_sec_as_used(sec_name, conf)
            elif ParticleSourceCylinder.is_cylinder_source(sec_name):
                new_obj.sources.append(
                    ParticleSourceCylinder.init_from_config(conf,
                                                            conf[sec_name],
                                                            sec_name))
                ParticleSourcesManager.mark_particlesource_sec_as_used(sec_name, conf)
            elif ParticleSourceTube.is_tube_source(sec_name):
                new_obj.sources.append(
                    ParticleSourceTube.init_from_config(conf,
                                                        conf[sec_name],
                                                        sec_name))
                ParticleSourcesManager.mark_particlesource_sec_as_used(sec_name, conf)
        return new_obj


    @staticmethod
    def mark_particlesource_sec_as_used(sec_name, conf):
        # For now simply mark sections as 'used' instead of removing them.
        conf[sec_name]["used"] = "True"


    @classmethod
    def init_from_h5(cls, h5_sources_group):
        new_obj = cls()
        new_obj.sources = []
        for src_group_name in h5_sources_group.keys():
            new_obj.parse_hdf5_particle_source(h5_sources_group[src_group_name])
        return new_obj


    def parse_hdf5_particle_source(self, this_source_h5_group):
        geometry_type = this_source_h5_group.attrs["geometry_type"]
        if geometry_type == "box":
            self.sources.append(
                ParticleSourceBox.init_from_h5(this_source_h5_group))
        elif geometry_type == "cylinder":
            self.sources.append(
                ParticleSourceCylinder.init_from_h5(this_source_h5_group))
        elif geometry_type == "tube":
            self.sources.append(
                ParticleSourceTube.init_from_h5(this_source_h5_group))
        else:
            print("In ParticleSourcesManager constructor-from-h5: "
                  "Unknown particle_source type. Aborting")
            sys.exit(-1)


    def write_to_file(self, h5file):
        h5group = h5file.create_group("/ParticleSources")
        for src in self.sources:
            src.write_to_file(h5group)


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
                          particle_to_mesh_map, particle_interaction_model):
        # todo: too many arguments
        for src_idx, src in enumerate(self.sources):
            for p_idx, particle in enumerate(src.particles):
                total_el_field, total_mgn_field = \
                self.compute_total_fields_at_particle_position(
                    particle, src_idx, p_idx,
                    current_time, spat_mesh, external_fields, inner_regions,
                    particle_to_mesh_map, particle_interaction_model)
                if total_mgn_field:
                    particle.boris_update_momentum(dt, total_el_field, total_mgn_field)
                else:
                    particle.boris_update_momentum_no_mgn(dt, total_el_field)
                particle.update_position(dt)


    def prepare_boris_integration(self, minus_half_dt, current_time,
                                  spat_mesh, external_fields, inner_regions,
                                  particle_to_mesh_map, particle_interaction_model):
        # todo: too many arguments
        # todo: place newly generated particles into separate buffer
        for src_idx, src in enumerate(self.sources):
            for p_idx, particle in enumerate(src.particles):
                if not particle.momentum_is_half_time_step_shifted:
                    total_el_field, total_mgn_field = \
                        self.compute_total_fields_at_particle_position(
                            particle, src_idx, p_idx,
                            current_time, spat_mesh, external_fields, inner_regions,
                            particle_to_mesh_map, particle_interaction_model)
                    if total_mgn_field:
                        particle.boris_update_momentum(minus_half_dt,
                                                       total_el_field, total_mgn_field)
                    else:
                        particle.boris_update_momentum_no_mgn(minus_half_dt,
                                                              total_el_field)
                    particle.momentum_is_half_time_step_shifted = True



    def compute_total_fields_at_particle_position(
            self, particle, src_idx, p_idx,
            current_time, spat_mesh, external_fields, inner_regions,
            particle_to_mesh_map, particle_interaction_model):
        total_el_field = external_fields.total_electric_field_at_particle_position(
            particle, current_time)
        if particle_interaction_model.noninteracting:
            if inner_regions.regions or not spat_mesh.is_potential_equal_on_boundaries():
                innerreg_el_field = particle_to_mesh_map.field_at_particle_position(
                    spat_mesh, particle)
                total_el_field = total_el_field.add(innerreg_el_field)
        elif particle_interaction_model.binary:
            bin_el_field = self.binary_field_at_particle_position(
                particle, src_idx, p_idx)
            total_el_field = total_el_field.add(bin_el_field)
            if inner_regions.regions or not spat_mesh.is_potential_equal_on_boundaries():
                innerreg_el_field = particle_to_mesh_map.field_at_particle_position(
                    spat_mesh, particle)
                total_el_field = total_el_field.add(innerreg_el_field)
        elif particle_interaction_model.pic:
            innerreg_and_pic_el_field = \
                particle_to_mesh_map.field_at_particle_position(spat_mesh, particle)
            total_el_field = total_el_field.add(innerreg_and_pic_el_field)
        #
        total_mgn_field = None
        if external_fields.magnetic:
            total_mgn_field = external_fields.total_magnetic_field_at_particle_position(
                particle, current_time)
        #
        return (total_el_field, total_mgn_field)


    def binary_field_at_particle_position(self, particle, src_idx, p_idx):
        # todo: swap src_idx and p_idx arguments order
        bin_force = Vec3d.zero()
        for iter_src_idx, src in enumerate(self.sources):
            if iter_src_idx != src_idx:
                for p in src.particles:
                    bin_force = bin_force.add(p.field_at_point(particle.position))
            else:
                for p in src.particles:
                    if p.id != particle.id:
                        bin_force = bin_force.add(p.field_at_point(particle.position))
        return bin_force
