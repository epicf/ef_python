from ParticleSource import *

# Box source

class ParticleSourceBox( ParticleSource ):

    def __init__( self ):
        super().__init__()

        
    @classmethod
    def init_from_config( cls, conf, this_source_config_part, sec_name ):
        new_obj = super().init_from_config( conf, this_source_config_part, sec_name )
        new_obj.geometry_type = "box"
        new_obj.check_correctness_of_box_config_fields(
            conf, this_source_config_part )
        new_obj.set_box_parameters_from_config( this_source_config_part )
        new_obj.generate_initial_particles()
        return new_obj

    
    @classmethod
    def init_from_h5_source_group( h5_source_group ):
        new_obj = super().init_from_h5_source_group( h5_source_group )
        new_obj.geometry_type = "box"
        new_obj.read_hdf5_source_parameters( h5_source_group )
        return new_obj

    
    def check_correctness_of_box_config_fields( self, conf, this_source_config_part ):
        self.x_left_ge_zero( conf, this_source_config_part )
        self.x_left_le_particle_source_x_right( conf, this_source_config_part )
        self.x_right_le_grid_x_size( conf, this_source_config_part )
        self.y_bottom_ge_zero( conf, this_source_config_part )
        self.y_bottom_le_particle_source_y_top( conf, this_source_config_part )
        self.y_top_le_grid_y_size( conf, this_source_config_part )
        self.z_near_ge_zero( conf, this_source_config_part )
        self.z_near_le_particle_source_z_far( conf, this_source_config_part )
        self.z_far_le_grid_z_size( conf, this_source_config_part )

        
    def set_box_parameters_from_config( self, this_source_config_part ):
        self.xleft = this_source_config_part.getfloat("box_x_left")
        self.xright = this_source_config_part.getfloat("box_x_right")
        self.ytop = this_source_config_part.getfloat("box_y_top")
        self.ybottom = this_source_config_part.getfloat("box_y_bottom")
        self.znear = this_source_config_part.getfloat("box_z_near")
        self.zfar = this_source_config_part.getfloat("box_z_far")


    def read_hdf5_source_parameters( self, this_source_h5_group ):
        self.xleft = this_source_h5_group.attrs["box_x_left"][0]
        self.xright = this_source_h5_group.attrs["box_x_xright"][0]
        self.ytop = this_source_h5_group.attrs["box_y_top"][0]
        self.ybottom = this_source_h5_group.attrs["box_y_bottom"][0]
        self.zfar = this_source_h5_group.attrs["box_z_far"][0]
        self.znear = this_source_h5_group.attrs["box_z_near"][0]

        
    def x_left_ge_zero( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_x_left") >= 0,
            "box_x_left < 0" )

    
    def x_left_le_particle_source_x_right( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_x_left") <= \
            this_source_config_part.getfloat("box_x_right"),
            "box_x_left > box_x_right" )


    def x_right_le_grid_x_size( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_x_right") <= \
            conf["Spatial mesh"].getfloat("grid_x_size"),
            "box_x_right > grid_x_size" )


    def y_bottom_ge_zero( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_y_bottom") >= 0,
            "box_y_bottom < 0" )


    def y_bottom_le_particle_source_y_top( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_y_bottom") <= \
            this_source_config_part.getfloat("box_y_top"),
            "box_y_bottom > box_y_top" )


    def y_top_le_grid_y_size( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_y_top") <= \
            conf["Spatial mesh"].getfloat("grid_y_size"),
            "box_y_top > grid_y_size" )


    def z_near_ge_zero( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_z_near") >= 0,
            "box_z_near < 0" )

    def z_near_le_particle_source_z_far( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_z_near") <= \
            this_source_config_part.getfloat("box_z_far"),
            "box_z_near > box_z_far" )

    def z_far_le_grid_z_size( self, conf, this_source_config_part ):
        production_assert( 
            this_source_config_part.getfloat("box_z_far") <= \
            conf["Spatial mesh"].getfloat("grid_z_size"),
            "box_z_far > grid_z_size" )


    def write_hdf5_source_parameters( self, this_source_h5_group ):
        super().write_hdf5_source_parameters( this_source_h5_group )
        this_source_h5_group.attrs.create( "box_x_left", self.xleft )
        this_source_h5_group.attrs.create( "box_x_right", self.xright )
        this_source_h5_group.attrs.create( "box_y_top", self.ytop )
        this_source_h5_group.attrs.create( "box_y_bottom", self.ybottom )
        this_source_h5_group.attrs.create( "box_z_far", self.zfar )
        this_source_h5_group.attrs.create( "box_z_near", self.znear )


    def uniform_position_in_source( self ):
        return self.uniform_position_in_cube()

    
    def uniform_position_in_cube( self ):
        p = Vec3d( self.random_in_range( self.xleft, self.xright, self.rnd_state ), 
                   self.random_in_range( self.ybottom, self.ytop, self.rnd_state ),
                   self.random_in_range( self.znear, self.zfar, self.rnd_state ) )
        return p


    @classmethod
    def is_box_source( cls, conf_sec_name ):
        return 'Particle_source_box' in conf_sec_name
