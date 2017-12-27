class ExternalField:

    def __init__( self ):
        pass

    @classmethod
    def init_from_config( cls, field_conf ):
        new_obj = cls() 
        new_obj.name = field_conf.name
        return new_obj

    @classmethod
    def init_from_h5( cls, h5group ):
        new_obj = cls() 
        new_obj.name = os.path.basename( h5group.name )


    def write_to_file( self, h5_fields_group ):
        current_field_group = h5_fields_group[ "./" + name ].create()
        self.write_hdf5_field_parameters( current_field_group )

    

# Uniform magnetic

class ExternalFieldMagneticUniform( ExternalField ):

    def __init__( self ):
        super().__init__()

    @classmethod
    def init_from_config( cls, field_conf ):
        new_obj = cls.super().init_from_config( field_conf )
        new_obj.field_type = "magnetic_uniform"
        new_obj.check_correctness_of_related_config_fields( field_conf )
        new_obj.get_values_from_config( field_conf )


    def check_correctness_of_related_config_fields( self, field_conf ):
        pass
        # nothing to check here
        

    def get_values_from_config( self, field_conf ):
        self.magnetic_field = Vec3d( field_conf["magnetic_field_x"],
                                     field_conf["magnetic_field_y"],
                                     field_conf["magnetic_field_z"] )

    @classmethod 
    def init_from_h5( cls, h5_field_group ):
        new_obj = cls.super().init_from_h5( h5_field_group )        
        new_obj.field_type = "magnetic_uniform"
        Hx = h5_field_group.attrs["magnetic_uniform_field_x"][0]
        Hy = h5_field_group.attrs["magnetic_uniform_field_y"][0]
        Hz = h5_field_group.attrs["magnetic_uniform_field_z"][0]        
        new_obj.magnetic_field = Vec3d( Hx, Hy, Hz )
        return new_obj


    def field_at_particle_position( self, particle, current_time ):
        return self.magnetic_field


    def write_hdf5_field_parameters( current_field_group_id ):
        current_field_group_id.attrs.create( "field_type", self.field_type )
        current_field_group_id.attrs.create( "magnetic_uniform_field_x",
                                             self.magnetic_field.x )
        current_field_group_id.attrs.create( "magnetic_uniform_field_y",
                                             self.magnetic_field.y )
        current_field_group_id.attrs.create( "magnetic_uniform_field_z",
                                             self.magnetic_field.z )
        current_field_group_id.attrs.create( "speed_of_light",
                                             physical_constants.speed_of_light )

        
# Uniform electric


class ExternalFieldElectricUniform( ExternalField ):

    def __init__( self ):
        pass

    @classmethod
    def init_from_config( field_conf ):
        new_obj = cls.super().init_from_config( field_conf )
        new_obj.field_type = "electric_uniform"
        new_obj.check_correctness_of_related_config_fields( field_conf )
        new_obj.get_values_from_config( field_conf )


    def check_correctness_of_related_config_fields( self, field_conf ):
        pass
        # nothing to check here

    def get_values_from_config( self, field_conf ):
        self.electric_field = Vec3d( field_conf["electric_field_x"],
                                     field_conf["electric_field_y"],
                                     field_conf["electric_field_z"] )

    @classmethod 
    def init_from_h5( cls, h5_field_group ):
        new_obj = cls.super().init_from_h5( h5_field_group )        
        new_obj.field_type = "electric_uniform"
        Ex = h5_field_group.attrs["electric_uniform_field_x"][0]
        Ey = h5_field_group.attrs["electric_uniform_field_y"][0]
        Ez = h5_field_group.attrs["electric_uniform_field_z"][0]        
        new_obj.electric_field = Vec3d( Ex, Ey, Ez )
        return new_obj
        

    def field_at_particle_position( self, particle, current_time ):
        return self.electric_field
    

    def write_hdf5_field_parameters( current_field_group_id ):
        current_field_group_id.attrs.create( "field_type", self.field_type )
        current_field_group_id.attrs.create( "electric_uniform_field_x",
                                             self.electric_field.x )
        current_field_group_id.attrs.create( "electric_uniform_field_y",
                                             self.electric_field.y )
        current_field_group_id.attrs.create( "electric_uniform_field_z",
                                             self.electric_field.z )
