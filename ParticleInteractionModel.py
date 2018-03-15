import sys
import h5py

class ParticleInteractionModel():

    def __init__( self ):
        self.noninteracting = self.pic = False
        
    @classmethod
    def init_from_config( cls, conf ):
        new_obj = cls()
        new_obj.check_correctness_of_related_config_fields( conf )
        new_obj.get_values_from_config( conf )
        return new_obj
        
    def check_correctness_of_related_config_fields( self, conf ):
        conf_part = conf["Particle interaction model"]        
        model = conf_part["particle_interaction_model"]        
        # 'PIC' or 'noninteracting'
        if model != "noninteracting" and model != "PIC":
            print( "Error: wrong value of 'particle_interaction_model': {}".format( model ))
            print( "Allowed values : 'noninteracting', 'PIC'" )
            print( "Aborting" )
            sys.exit( -1 ) 

    def get_values_from_config( self, conf ):
        conf_part = conf["Particle interaction model"]
        self.particle_interaction_model = conf_part["particle_interaction_model"]        
        if self.particle_interaction_model == "noninteracting":
            self.noninteracting = True
        elif self.particle_interaction_model == "PIC":
            self.pic = True

            
    @classmethod
    def init_from_h5( cls, h5group ):
        new_obj = cls()
        new_obj.particle_interaction_model = \
                h5group.attrs["particle_interaction_model"]
        if new_obj.particle_interaction_model == "noninteracting":
            new_obj.noninteracting = True
        elif new_obj.particle_interaction_model == "PIC":
            new_obj.pic = True
        return new_obj
    
    def __str__( self ):
        return "Particle interaction model = {}".format( self.particle_interaction_model )
    
    def print( self ):
        print( "### Particle_interaction_model:" )
        print( self )
        print( "self.noninteracting = {}".format( self.noninteracting ) )
        print( "self.pic = {}".format( self.pic ) )
        
    def write_to_file( self, h5file ):
        groupname = "/Particle_interaction_model"
        h5group = h5file.create_group( groupname )        
        h5group.attrs["particle_interaction_model"] = self.particle_interaction_model
