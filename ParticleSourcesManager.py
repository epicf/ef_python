import sys
import h5py

from ParticleSource import *
from ParticleSourceBox import *
from ParticleSourceCylinder import *

class ParticleSourcesManager:

    def __init__( self ):
        pass

    
    @classmethod
    def init_from_config( cls, conf ):
        new_obj = cls()
        new_obj.sources = []
        for sec_name in conf.sections():
            if 'ParticleSourceBox' in sec_name:
                new_obj.sources.append( ParticleSourceBox( conf, conf[sec_name] ) )
            elif 'ParticleSourceCylinder' in sec_name:
                new_obj.sources.append( ParticleSourceCylinder( conf, conf[sec_name] ) )
        return new_obj
        
    @classmethod
    def init_from_h5( cls, h5_sources_group ):
        new_obj = cls()
        new_obj.sources = []
        for src_group_name in h5_sources_group.keys():
            self.parse_hdf5_particle_source( h5_sources_group["src_group_name"] )
        return new_obj

    
    def parse_hdf5_particle_source( self, this_source_h5_group ):
        geometry_type = this_source_h5_group.attr["geometry_type"][0]
        if geometry_type == "box":
            self.sources.push_back( ParticleSourceBox( this_source_h5_group ) )
        elif geometry_type == "cylinder":
            self.sources.push_back( ParticleSourceCylinder( this_source_h5_group ) )
        else:
            print( "In Particle_source_manager constructor-from-h5: "
                   "Unknown particle_source type. Aborting" )            
            sys.exit( -1 )
    
 
    def write_to_file( self, h5file ):
        h5group = h5file.create_group( "/Particle_sources" )
        for src in self.sources:
            src.write_to_file( h5group )

            
    def generate_each_step( self ):
        for src in self.sources:
            src.generate_each_step()

            
    def print_particles( self ):
        for src in self.sources:
            src.print_particles()

            
    def update_particles_position( self, dt ):
        for src in self.sources:
            src.update_particles_position( dt )
