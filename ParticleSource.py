import os
import sys
import h5py
import random
from math import sqrt, copysign

from common import production_assert
from Vec3d import Vec3d
from Particle import Particle

class ParticleSource():

    def __init__():
        pass

    @classmethod
    def init_from_config( cls, conf, this_source_config_part ):
        new_obj = cls()
        new_obj.check_correctness_of_related_config_fields(
            conf, this_source_config_part )
        new_obj.set_parameters_from_config( this_source_config_part )
        return new_obj


    @classmethod
    def init_from_h5( cls, h5group ):
        new_obj = cls()
        new_obj.read_hdf5_source_parameters( h5group )
        new_obj.read_hdf5_particles( h5group )
        # Random number generator
        # Instead of saving/loading it's state to file just
        # reinit with different seed.
        tmp = random.getstate()
        random.seed() # system time is used by default
        new_obj.rnd_state = random.getstate()
        random.setstate( tmp )
        return new_obj
        
        
    def check_correctness_of_related_config_fields( self, conf, this_source_config_part ):
        self.initial_number_of_particles_gt_zero(
            conf, this_source_config_part )
        self.particles_to_generate_each_step_ge_zero(
            conf, this_source_config_part )
        self.temperature_gt_zero( conf, this_source_config_part )
        self.mass_gt_zero( conf, this_source_config_part )
        

    def set_parameters_from_config( self, this_source_config_part ):
        self.name = this_source_config_part.name
        self.initial_number_of_particles = \
            this_source_config_part["initial_number_of_particles"]
        self.particles_to_generate_each_step = \
            this_source_config_part["particles_to_generate_each_step"]
        self.mean_momentum = Vec3d( this_source_config_part["mean_momentum_x"], 
                                    this_source_config_part["mean_momentum_y"],
                                    this_source_config_part["mean_momentum_z"] )
        self.temperature = this_source_config_part["temperature"]
        self.charge = this_source_config_part["charge"]
        self.mass = this_source_config_part["mass"]
        #
        tmp = random.getstate()
        random.seed() # system time is used by default
        self.rnd_state = random.getstate()
        random.setstate( tmp )
        # Initial id
        self.max_id = 0

	
    def read_hdf5_source_parameters( self, h5group ):
        self.name = os.path.basename( h5group.name )
        self.temperature = h5group.attrs["temperature"][0]
        mean_momentum_x = h5group.attrs["mean_momentum_x"][0]
        mean_momentum_y = h5group.attrs["mean_momentum_y"][0]
        mean_momentum_z = h5group.attrs["mean_momentum_z"][0]
        self.mean_momentum = Vec3d( mean_momentum_x, mean_momentum_y, mean_momentum_z )
        self.charge = h5group.attrs["charge"][0]
        self.mass = h5group.attrs["mass"][0]
        self.initial_number_of_particles = h5group.attrs["initial_number_of_particles"][0]
        self.particles_to_generate_each_step = \
            h5group.attrs["particles_to_generate_each_step"][0]
        self.max_id = h5group.attrs["max_id"][0]


    def read_hdf5_particles( self, h5group ):        
        id_buf = h5group["./particle_id"]
        x_buf = h5group["./position_x"]
        y_buf = h5group["./position_y"]
        z_buf = h5group["./position_z"]
        px_buf = h5group["./momentum_x"]
        py_buf = h5group["./momentum_y"]
        pz_buf = h5group["./momentum_z"]
        #
        for (i, x, y, z, px, py, pz) in \
            zip( id_buf, x_buf, y_buf, z_buf, px_buf, py_buf, pz_buf ):
            pos = Vec3d( x, y, z )
            mom = Vec3d( px, py, pz )
            self.particles.append( Particle( i, self.charge, self.mass, pos, mom ) )
            self.particles[-1].momentum_is_half_time_step_shifted = true
            

    def generate_initial_particles( self ):
        #particles.reserve( initial_number_of_particles )
        self.generate_num_of_particles( self.initial_number_of_particles )

        
    def generate_each_step( self ):
        #particles.reserve( particles.size() + particles_to_generate_each_step );
        self.generate_num_of_particles( self.particles_to_generate_each_step )

        
    def generate_num_of_particles( self, num_of_particles ):
        vec_of_ids = self.populate_vec_of_ids( num_of_particles )
        for i in range( num_of_particles ):
            pos = self.uniform_position_in_source( self.rnd_state )
            mom = self.maxwell_momentum_distr(
                self.mean_momentum, self.temperature, self.mass, self.rnd_state )
            self.particles.append(
                vec_of_ids, self.charge, self.mass, pos, mom )

            
    def populate_vec_of_ids( self, num_of_particles ):
        vec_of_ids = []
        for i in range( num_of_particles ):
            vec_of_ids.append( self.max_id += 1 )
        return vec_of_ids

    
    def random_in_range( self, low, up, rnd_state ):
        tmp = random.getstate()
        random.setstate( rnd_state )
        r = random.randrange( low, up )
        random.setstate( tmp )
        return r

    
    def maxwell_momentum_distr( self, mean_momentum, temperature, mass, rnd_state ):
        maxwell_gauss_std_mean_x = mean_momentum.x
        maxwell_gauss_std_mean_y = mean_momentum.y
        maxwell_gauss_std_mean_z = mean_momentum.z
        maxwell_gauss_std_dev = sqrt( mass * temperature )
        #
        tmp = random.getstate()
        random.setstate( rnd_state )
        px = random.gauss( maxwell_gauss_std_mean_x, maxwell_gauss_std_dev )
        py = random.gauss( maxwell_gauss_std_mean_y, maxwell_gauss_std_dev )
        pz = random.gauss( maxwell_gauss_std_mean_z, maxwell_gauss_std_dev )
        random.setstate( tmp )
        #
        mom = Vec3d( px, py, pz )
        mom = mom.times_scalar( 1.0 ) # recheck
        return mom

    
    def update_particles_position( self, dt ):
        for p in self.particles:
            p.update_position( dt )

            
    def print_particles( self ):
        print( "Source name: " + self.name )
        for p in self.particles:
            p.print_short()

            
    def write_to_file( self, h5group ):
        print( "Source name = {}, number of particles = {}".format(
            self.name, len( self.particles ) ) )
        this_source_h5group = h5group.create( "./" + self.name )
        self.write_hdf5_particles( this_source_h5group )
        self.write_hdf5_source_parameters( this_source_h5group )

        
    def write_hdf5_particles( self, this_source_h5group ):
        id_buf = np.empty( self.particles.size, dtype = 'i8' )
        x_buf = np.empty( self.particles.size, dtype = 'f8' )
        y_buf = np.empty_like( x_buf )
        z_buf = np.empty_like( x_buf )
        px_buf = np.empty_like( x_buf )
        py_buf = np.empty_like( x_buf )
        pz_buf = np.empty_like( x_buf )
        #
        for i, p in enumerate( self.particles ):
            id_buf[i] = p.id
            x_buf[i] = p.position.x
            y_buf[i] = p.position.y
            z_buf[i] = p.position.z
            px_buf[i] = p.momentum.x
            py_buf[i] = p.momentum.y
            pz_buf[i] = p.momentum.z
        #
        this_source_h5group.create_dataset( "./particle_id", data = id_buf )
        this_source_h5group.create_dataset( "./position_x", data = x_buf )
        this_source_h5group.create_dataset( "./position_y", data = y_buf )
        this_source_h5group.create_dataset( "./position_z", data = z_buf )
        this_source_h5group.create_dataset( "./momentum_x", data = px_buf )
        this_source_h5group.create_dataset( "./momentum_y", data = py_buf )
        this_source_h5group.create_dataset( "./momentum_z", data = pz_buf )


    def write_hdf5_source_parameters( self, this_source_h5group ):
        this_source_h5group.attrs.create( "geometry_type", self.geometry_type )
        this_source_h5group.attrs.create( "temperature", self.temperature )
        this_source_h5group.attrs.create( "mean_momentum_x", self.mean_momentum_x )
        this_source_h5group.attrs.create( "mean_momentum_y", self.mean_momentum_y )
        this_source_h5group.attrs.create( "mean_momentum_z", self.mean_momentum_z )
        this_source_h5group.attrs.create( "charge", self.charge )
        this_source_h5group.attrs.create( "mass", self.mass )
        this_source_h5group.attrs.create( "initial_number_of_particles",
                                          self.initial_number_of_particles )
        this_source_h5group.attrs.create( "particles_to_generate_each_step",
                                          self.particles_to_generate_each_step )
        this_source_h5group.attrs.create( "max_id", self.max_id )


        def initial_number_of_particles_gt_zero( self, conf, this_source_config_part ):
            production_assert(
                this_source_config_part["initial_number_of_particles"] > 0,
                "initial_number_of_particles <= 0" )


        def particles_to_generate_each_step_ge_zero( self, conf, this_source_config_part ):
            production_assert(
                this_source_config_part["particles_to_generate_each_step"] >= 0,
                "particles_to_generate_each_step < 0" )


        def temperature_gt_zero( self, conf, this_source_config_part ):
            production_assert( this_source_config_part["temperature"] >= 0,
                               "temperature < 0" )

        def mass_gt_zero( self, conf, this_source_config_part ):
            production_assert( this_source_config_part["mass"] >= 0,
                               "mass < 0" )

