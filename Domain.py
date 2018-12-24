import h5py
import numpy as np

from FieldSolver import FieldSolver
from ef.util.serializable_h5 import SerializableH5


class Domain(SerializableH5):

    def __init__(self, time_grid, spat_mesh, inner_regions,
                 particle_sources,
                 external_fields, particle_interaction_model,
                 output_filename_prefix, outut_filename_suffix):
        self.time_grid = time_grid
        self.spat_mesh = spat_mesh
        self.inner_regions = inner_regions
        self._field_solver = FieldSolver(spat_mesh, inner_regions)
        self.particle_sources = particle_sources
        self.external_fields = external_fields
        self.particle_interaction_model = particle_interaction_model
        self._output_filename_prefix = output_filename_prefix
        self._output_filename_suffix = outut_filename_suffix

    @classmethod
    def init_from_h5(cls, h5file, filename_prefix, filename_suffix):
        domain = cls.load_h5(h5file)
        domain._output_filename_prefix = filename_prefix
        domain._output_filename_suffix = filename_suffix
        return domain

    def start_pic_simulation(self):
        self.eval_and_write_fields_without_particles()
        self.particle_sources.generate_initial_particles()
        self.prepare_recently_generated_particles_for_boris_integration()
        self.write_step_to_save()
        self.run_pic()

    def continue_pic_simulation(self):
        self.run_pic()

    def run_pic(self):
        total_time_iterations = self.time_grid.total_nodes - 1
        current_node = self.time_grid.current_node
        for i in range(current_node, total_time_iterations):
            print("Time step from {:d} to {:d} of {:d}".format(
                i, i + 1, total_time_iterations))
            self.advance_one_time_step()
            self.write_step_to_save()

    def prepare_recently_generated_particles_for_boris_integration(self):
        if self.particle_interaction_model.pic:
            self.eval_charge_density()
            self.eval_potential_and_fields()
        self.shift_new_particles_velocities_half_time_step_back()

    def advance_one_time_step(self):
        self.push_particles()
        self.apply_domain_constrains()
        if self.particle_interaction_model.pic:
            self.eval_charge_density()
            self.eval_potential_and_fields()
        self.update_time_grid()

    def eval_charge_density(self):
        self.spat_mesh.clear_old_density_values()
        self.spat_mesh.weight_particles_charge_to_mesh(self.particle_sources)

    def eval_potential_and_fields(self):
        self._field_solver.eval_potential(self.spat_mesh, self.inner_regions)
        self._field_solver.eval_fields_from_potential(self.spat_mesh)

    def push_particles(self):
        dt = self.time_grid.time_step_size
        current_time = self.time_grid.current_time
        self.particle_sources.boris_integration(
            dt, current_time,
            self.spat_mesh, self.external_fields, self.inner_regions,
            self.particle_interaction_model)

    def apply_domain_constrains(self):
        # First generate then remove.
        # This allows for overlap of source and inner region.
        self.generate_new_particles()
        self.apply_domain_boundary_conditions()
        self.remove_particles_inside_inner_regions()

    #
    # Push particles
    #

    def shift_new_particles_velocities_half_time_step_back(self):
        minus_half_dt = -1.0 * self.time_grid.time_step_size / 2.0
        #
        self.particle_sources.prepare_boris_integration(
            minus_half_dt, self.time_grid.current_time,
            self.spat_mesh, self.external_fields, self.inner_regions,
            self.particle_interaction_model)

    #
    # Apply domain constrains
    #

    def apply_domain_boundary_conditions(self):
        for src in self.particle_sources.sources:
            src.particles[:] = [p for p in src.particles if not self.out_of_bound(p)]

    def remove_particles_inside_inner_regions(self):
        for region in self.inner_regions:
            for src in self.particle_sources.sources:
                src.particles[:] = \
                    [p for p in src.particles \
                     if not region.check_if_particle_inside_and_count_charge(p)]

    def out_of_bound(self, particle):
        return np.any(particle._position < 0) or np.any(particle._position > self.spat_mesh.size)

    def generate_new_particles(self):
        self.particle_sources.generate_each_step()
        self.shift_new_particles_velocities_half_time_step_back()

    #
    # Update time grid
    #

    def update_time_grid(self):
        self.time_grid.update_to_next_step()

    #
    # Write domain to file
    #

    def write_step_to_save(self):
        current_step = self.time_grid.current_node
        step_to_save = self.time_grid.node_to_save
        if (current_step % step_to_save) == 0:
            self.write()

    def write(self):
        file_name_to_write = self.construct_output_filename(
            self._output_filename_prefix, self.time_grid.current_node,
            self._output_filename_suffix)
        h5file = h5py.File(file_name_to_write, mode="w")
        if not h5file:
            print("Error: can't open file " + file_name_to_write + \
                  "to save results of initial field calculation!")
            print("Recheck \'output_filename_prefix\' key in config file.")
            print("Make sure the directory you want to save to exists.")
            print("Writing initial fields to file " + file_name_to_write)
        print("Writing step {} to file {}".format(self.time_grid.current_node, file_name_to_write))
        self.save_h5(h5file)
        h5file.close()

    @staticmethod
    def construct_output_filename(output_filename_prefix,
                                  current_time_step,
                                  output_filename_suffix):
        filename = output_filename_prefix + \
                   "{:07d}".format(current_time_step) + \
                   output_filename_suffix
        return filename

    #
    # Free domain
    #

    def free(self):
        print("TODO: free domain.\n")

    #
    # Various functions
    #

    def print_particles(self):
        self.particle_sources.print_particles()

    def eval_and_write_fields_without_particles(self):
        self.spat_mesh.clear_old_density_values()
        self.eval_potential_and_fields()
        file_name_to_write = self._output_filename_prefix + "fieldsWithoutParticles" + self._output_filename_suffix
        h5file = h5py.File(file_name_to_write, mode="w")
        if not h5file:
            print("Error: can't open file " + file_name_to_write + \
                  "to save results of initial field calculation!")
            print("Recheck \'output_filename_prefix\' key in config file.")
            print("Make sure the directory you want to save to exists.")
            print("Writing initial fields to file " + file_name_to_write)
        h5file.attrs['class'] = self.__class__.__name__
        self._save_value(h5file, "spat_mesh", self.spat_mesh)
        self._save_value(h5file, "external_fields", self.external_fields)
        self._save_value(h5file, "inner_regions", self.inner_regions)
        h5file.close()
