import h5py
import numpy as np

from ef.field.solvers.field_solver import FieldSolver
from ef.util.serializable_h5 import SerializableH5


class Simulation(SerializableH5):

    def __init__(self, time_grid, spat_mesh, inner_regions,
                 particle_sources,
                 electric_fields, magnetic_fields, particle_interaction_model,
                 output_filename_prefix, outut_filename_suffix, max_id=-1, particle_arrays=()):
        self.time_grid = time_grid
        self.spat_mesh = spat_mesh
        self.inner_regions = inner_regions
        self._field_solver = FieldSolver(spat_mesh, inner_regions)
        self.particle_sources = particle_sources
        self.electric_fields = electric_fields
        self.magnetic_fields = magnetic_fields
        self.particle_interaction_model = particle_interaction_model
        self._output_filename_prefix = output_filename_prefix
        self._output_filename_suffix = outut_filename_suffix
        self.max_id = max_id
        self.particle_arrays = list(particle_arrays)

    @classmethod
    def init_from_h5(cls, h5file, filename_prefix, filename_suffix):
        domain = cls.load_h5(h5file)
        domain._output_filename_prefix = filename_prefix
        domain._output_filename_suffix = filename_suffix
        return domain

    def start_pic_simulation(self):
        self.eval_and_write_fields_without_particles()
        for src in self.particle_sources:
            particles = src.generate_initial_particles()
            if len(particles.ids):
                particles.ids = self.generate_particle_ids(len(particles.ids))
                self.particle_arrays.append(particles)
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
        self.spat_mesh.weight_particles_charge_to_mesh(self.particle_arrays)

    def eval_potential_and_fields(self):
        self._field_solver.eval_potential(self.spat_mesh, self.inner_regions)
        self._field_solver.eval_fields_from_potential(self.spat_mesh)

    def push_particles(self):
        self.boris_integration(self.time_grid.time_step_size)

    def apply_domain_constrains(self):
        # First generate then remove.
        # This allows for overlap of source and inner region.
        self.generate_new_particles()
        self.apply_domain_boundary_conditions()
        self.remove_particles_inside_inner_regions()

    def boris_integration(self, dt):
        for particles in self.particle_arrays:
            total_el_field, total_mgn_field = \
                self.compute_total_fields_at_positions(particles.positions)
            if total_mgn_field is not None and total_mgn_field.any():
                particles.boris_update_momentums(dt, total_el_field, total_mgn_field)
            else:
                particles.boris_update_momentum_no_mgn(dt, total_el_field)
            particles.update_positions(dt)

    def prepare_boris_integration(self, minus_half_dt):
        # todo: place newly generated particle_arrays into separate buffer
        for particles in self.particle_arrays:
            if not particles.momentum_is_half_time_step_shifted:
                total_el_field, total_mgn_field = \
                    self.compute_total_fields_at_positions(particles.positions)
                if total_mgn_field is not None and total_mgn_field.any():
                    particles.boris_update_momentums(minus_half_dt, total_el_field, total_mgn_field)
                else:
                    particles.boris_update_momentum_no_mgn(minus_half_dt, total_el_field)
                particles.momentum_is_half_time_step_shifted = True

    def compute_total_fields_at_positions(self, positions):
        total_el_field = np.zeros_like(positions)  # make sure shape is set, as += operators can't broadcast left side
        total_el_field += sum(f.get_at_points(positions, self.time_grid.current_time) for f in self.electric_fields)
        if self.particle_interaction_model.noninteracting:
            if self.inner_regions or not self.spat_mesh.is_potential_equal_on_boundaries():
                total_el_field += self.spat_mesh.field_at_position(positions)
        elif self.particle_interaction_model.binary:
            total_el_field += self.binary_electric_field_at_positions(positions)
            if self.inner_regions or not self.spat_mesh.is_potential_equal_on_boundaries():
                total_el_field += self.spat_mesh.field_at_position(positions)
        elif self.particle_interaction_model.pic:
            total_el_field += self.spat_mesh.field_at_position(positions)
        mgn_field = None
        if self.magnetic_fields:
            mgn_field = sum(f.get_at_points(positions, self.time_grid.current_time) for f in self.magnetic_fields)
        return total_el_field, mgn_field

    def binary_electric_field_at_positions(self, positions):
        return sum(
            np.nan_to_num(p.field_at_points(positions)) for p in self.particle_arrays)

    #
    # Push particles
    #

    def shift_new_particles_velocities_half_time_step_back(self):
        minus_half_dt = -1.0 * self.time_grid.time_step_size / 2.0
        #
        self.prepare_boris_integration(minus_half_dt)

    #
    # Apply domain constrains
    #

    def apply_domain_boundary_conditions(self):
        for arr in self.particle_arrays:
            collisions = self.out_of_bound(arr)
            arr.remove(collisions)
        self.particle_arrays = [a for a in self.particle_arrays if len(a.ids) > 0]

    def remove_particles_inside_inner_regions(self):
        for region in self.inner_regions:
            for p in self.particle_arrays:
                region.collide_with_particles(p)
            self.particle_arrays = [a for a in self.particle_arrays if len(a.ids) > 0]

    def out_of_bound(self, particle):
        return np.logical_or(np.any(particle.positions < 0, axis=-1),
                             np.any(particle.positions > self.spat_mesh.size, axis=-1))

    def generate_new_particles(self):
        for src in self.particle_sources:
            particles = src.generate_each_step()
            if len(particles.ids):
                particles.ids = self.generate_particle_ids(len(particles.ids))
                self.particle_arrays.append(particles)
        self.shift_new_particles_velocities_half_time_step_back()

    def generate_particle_ids(self, num_of_particles):
        range_of_ids = range(self.max_id + 1, self.max_id + num_of_particles + 1)
        self.max_id += num_of_particles
        return np.array(range_of_ids)

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
        self._save_value(h5file, "electric_fields", self.electric_fields)
        self._save_value(h5file, "magnetic_fields", self.magnetic_fields)
        self._save_value(h5file, "inner_regions", self.inner_regions)
        h5file.close()
