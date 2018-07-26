import os

class ExternalField:

    def __init__( self ):
        pass

    @classmethod
    def init_from_config( cls, field_conf, field_conf_name ):
        new_obj = cls()        
        new_obj.name = field_conf_name[ field_conf_name.rfind(".") + 1 : ]
        return new_obj

    @classmethod
    def init_from_h5( cls, h5group ):
        new_obj = cls() 
        new_obj.name = os.path.basename( h5group.name )
        return new_obj


    def write_to_file( self, h5_fields_group ):
        current_field_group = h5_fields_group.create_group( "./" + self.name )
        self.write_hdf5_field_parameters( current_field_group )


    def field_at_particle_position(self, particle, current_time):
        # virtual method
        raise NotImplementedError()
