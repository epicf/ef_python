import h5py

from ParticleSourceBox import ParticleSourceBox
from TimeGrid import TimeGrid
from SpatialMesh import SpatialMesh
from InnerRegionsManager import InnerRegionsManager
from ParticleToMeshMap import ParticleToMeshMap
from FieldSolver import FieldSolver
from ExternalFieldsManager import ExternalFieldsManager
from ParticleInteractionModel import ParticleInteractionModel
from ParticleSourcesManager import ParticleSourcesManager
from Vec3d import Vec3d
import physical_constants
#from Solid_boundary import Solid_boundary

class Domain():

    def __init__(self):
        self.time_grid = None
        self.spat_mesh = None
        self.inner_regions = None
        self.particle_to_mesh_map = None
        self.field_solver = None
        self.particle_sources = None
        self.external_fields = None
        self.particle_interaction_model = None
        self.output_filename_prefix = None
        self.output_filename_suffix = None


    @classmethod
    def init_from_config(cls, conf):
        new_obj = cls()
        new_obj.time_grid = TimeGrid.init_from_config(conf)
        new_obj.spat_mesh = SpatialMesh.init_from_config(conf)
        new_obj.inner_regions = InnerRegionsManager.init_from_config(
            conf, new_obj.spat_mesh)
        new_obj.particle_to_mesh_map = ParticleToMeshMap()
        new_obj.field_solver = FieldSolver(new_obj.spat_mesh, new_obj.inner_regions)
        new_obj.particle_sources = ParticleSourcesManager.init_from_config(conf)
        new_obj.external_fields = ExternalFieldsManager.init_from_config(conf)
        new_obj.particle_interaction_model = ParticleInteractionModel.init_from_config(
            conf)
        new_obj.output_filename_prefix = conf["Output filename"]["output_filename_prefix"]
        new_obj.output_filename_suffix = conf["Output filename"]["output_filename_suffix"]
        return new_obj


    @classmethod
    def init_from_h5(cls, h5file, filename_prefix, filename_suffix):
        new_obj = cls()
        new_obj.time_grid = TimeGrid.init_from_h5(h5file["/Time_grid"])
        new_obj.spat_mesh = SpatialMesh.init_from_h5(h5file["/Spatial_mesh"])
        new_obj.inner_regions = InnerRegionsManager.init_from_h5(
            h5file["/Inner_regions"], new_obj.spat_mesh)
        new_obj.particle_to_mesh_map = ParticleToMeshMap()
        new_obj.field_solver = FieldSolver(new_obj.spat_mesh, new_obj.inner_regions)
        new_obj.particle_sources = ParticleSourcesManager.init_from_h5(
            h5file["/Particle_sources"])
        new_obj.external_fields = ExternalFieldsManager.init_from_h5(
            h5file["/External_fields"])
        new_obj.particle_interaction_model = ParticleInteractionModel.init_from_h5(
            h5file["/Particle_interaction_model"])
        new_obj.output_filename_prefix = filename_prefix
        new_obj.output_filename_suffix = filename_suffix
        return new_obj


    def start_pic_simulation(self):
        self.eval_and_write_fields_without_particles()
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
                i, i+1, total_time_iterations))
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
        self.particle_to_mesh_map.weight_particles_charge_to_mesh(
            self.spat_mesh, self.particle_sources)


    def eval_potential_and_fields(self):
        self.field_solver.eval_potential(self.spat_mesh, self.inner_regions)
        self.field_solver.eval_fields_from_potential(self.spat_mesh)


    def push_particles(self):
        dt = self.time_grid.time_step_size
        current_time = self.time_grid.current_time
        self.particle_sources.boris_integration(
            dt, current_time,
            self.spat_mesh, self.external_fields, self.inner_regions,
            self.particle_to_mesh_map, self.particle_interaction_model)


    def apply_domain_constrains(self):
        # First generate then remove.
        # This allows for overlap of source and inner region.
        self.generate_new_particles()
#        self.apply_domain_boundary_conditions()
        if self.particle_interaction_model.binary:
           self.check_position_of_the_particle_outside()
#        self.remove_particles_inside_inner_regions()


    def check_position_of_the_particle_outside(self):
        for src in self.particle_sources.sources:
            for p in src.particles:
                iter = p.id
                dt = self.time_grid.time_step_size
                pos = p.position                                                # Extraction of each particle Cartesian coordinate vector
                mom = p.momentum                                                # Extraction of each particle momentum vector
                m = p.mass
                pos_est = self.future_step_particle_evolution(dt, pos, mom, m)
                pos_new, mom_new = self.gradient_reflection(pos_est, mom)
                p.position = pos_new
                p.momentum = mom_new

    def future_step_particle_evolution(self, dt, pos, mom, mass):
        pos_step_change = mom.times_scalar(dt / mass)                  # Change of the particle position for a dt time interval
        pos_step_evol = pos.add(pos_step_change)                            # The coordinate vector of the particle for a dt time step
        return pos_step_evol

    def gradient_reflection(self, pos_step_evol, mom):
#        self.particle_sources.sources[0].()
        outside_xleft = pos_step_evol.x <= self.particle_sources.sources[0].xleft
        outside_xright = pos_step_evol.x >= self.particle_sources.sources[0].xright
        if outside_xleft == 1:
            x_grad = self.particle_sources.sources[0].xleft - pos_step_evol.x
            mom_ch_x = -1
        elif outside_xright == 1:
            x_grad = self.particle_sources.sources[0].xright - pos_step_evol.x
            mom_ch_x = -1
        else:
            x_grad = 0
            mom_ch_x = 0

        outside_ybottom = pos_step_evol.y <= self.particle_sources.sources[0].ybottom
        outside_ytop = pos_step_evol.y >= self.particle_sources.sources[0].ytop
        if outside_ybottom == 1:
            y_grad = self.particle_sources.sources[0].ybottom - pos_step_evol.y
            mom_ch_y = -1
        elif outside_ytop == 1:
            y_grad = self.particle_sources.sources[0].ytop - pos_step_evol.y
            mom_ch_y = -1
        else:
            y_grad = 0
            mom_ch_y = 0

        outside_zfar = pos_step_evol.z <= self.particle_sources.sources[0].znear
        outside_znear = pos_step_evol.z >= self.particle_sources.sources[0].zfar
        if outside_zfar == 1:
            z_grad = self.particle_sources.sources[0].zfar - pos_step_evol.z
            mom_ch_z = -1
        elif outside_znear == 1:
            z_grad = self.particle_sources.sources[0].znear - pos_step_evol.z
            mom_ch_z = -1
        else:
            z_grad = 0
            mom_ch_z = 0

        pos_new = Vec3d(pos_step_evol.x + 2*x_grad, pos_step_evol.y + 2*y_grad, pos_step_evol.z + 2*z_grad)
        mom_new = Vec3d(mom.x + 2*mom_ch_x*mom.x, mom.y + 2*mom_ch_y*mom.y, mom.z + 2*mom_ch_z)
        return pos_new, mom_new

#
# Push particles
#


    def shift_new_particles_velocities_half_time_step_back(self):
        minus_half_dt = -self.time_grid.time_step_size / 2.0
        #
        for src in self.particle_sources.sources:
            for p in src.particles:
                if not p.momentum_is_half_time_step_shifted:
                    total_el_field = \
                    self.external_fields.total_electric_field_at_particle_position(
                        p, self.time_grid.current_time)
                    pic_el_field = self.particle_to_mesh_map.field_at_particle_position(
                        self.spat_mesh, p)
                    total_el_field = total_el_field.add(pic_el_field)
                    #
                    total_mgn_field = \
                    self.external_fields.total_magnetic_field_at_particle_position(
                        p, self.time_grid.current_time)
                    #
                    if not self.external_fields.magnetic:
                        dp = total_el_field.times_scalar(p.charge * minus_half_dt)
                        p.momentum = p.momentum.add(dp)
                    else:
                        q_quote = minus_half_dt * p.charge / p.mass / 2.0
                        half_el_force = total_el_field.times_scalar(q_quote)
                        v_current = p.momentum.times_scalar(1.0 / p.mass)
                        u = v_current.add(half_el_force)
                        h = total_mgn_field.times_scalar(
                            q_quote / physical_constants.speed_of_light)
                        s = h.times_scalar(
                            2.0 / (1.0 + h.dot_product(h)))
                        tmp = u.add(u.cross_product(h))
                        u_quote = u.add(tmp.cross_product(s))
                        p.momentum = u_quote.add(half_el_force).times_scalar(p.mass)
                    p.momentum_is_half_time_step_shifted = True



#
# Apply domain constrains
#

    def apply_domain_boundary_conditions(self):
        for src in self.particle_sources.sources:
            src.particles[:] = [p for p in src.particles if not self.out_of_bound(p)]


    def remove_particles_inside_inner_regions(self):
        for src in self.particle_sources.sources:
            src.particles[:] = \
              [p for p in src.particles \
               if not self.inner_regions.check_if_particle_inside_and_count_charge(p)]




    def out_of_bound(self, particle):
        x = particle.position.x
        y = particle.position.y
        z = particle.position.z
        out = (x >= self.spat_mesh.x_volume_size) or (x <= 0) \
              or \
              (y >= self.spat_mesh.y_volume_size) or (y <= 0) \
              or \
              (z >= self.spat_mesh.z_volume_size) or (z <= 0)
        return out


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
            self.output_filename_prefix, self.time_grid.current_node,
            self.output_filename_suffix)
        h5file = h5py.File(file_name_to_write, mode="w")
        if not h5file:
            print("Error: can't open file " + file_name_to_write + \
                   "to save results of initial field calculation!")
            print("Recheck \'output_filename_prefix\' key in config file.")
            print("Make sure the directory you want to save to exists.")
            print("Writing initial fields to file " + file_name_to_write)
        print("Writing step {} to file {}".format(
            self.time_grid.current_node, file_name_to_write))
        self.time_grid.write_to_file(h5file)
        self.spat_mesh.write_to_file(h5file)
        self.particle_sources.write_to_file(h5file)
        self.inner_regions.write_to_file(h5file)
        self.external_fields.write_to_file(h5file)
        self.particle_interaction_model.write_to_file(h5file)
        h5file.close()


    def construct_output_filename(self, output_filename_prefix,
                                  current_time_step, output_filename_suffix):
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
        file_name_to_write = self.output_filename_prefix + \
                             "fieldsWithoutParticles" + \
                             self.output_filename_suffix
        h5file = h5py.File(file_name_to_write, mode="w")
        if not h5file:
            print("Error: can't open file " + file_name_to_write + \
                   "to save results of initial field calculation!")
            print("Recheck \'output_filename_prefix\' key in config file.")
            print("Make sure the directory you want to save to exists.")
            print("Writing initial fields to file " + file_name_to_write)
        self.spat_mesh.write_to_file(h5file)
        self.external_fields.write_to_file(h5file)
        self.inner_regions.write_to_file(h5file)
        h5file.close()
