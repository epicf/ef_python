from InnerRegion import InnerRegion
from Vec3d import Vec3d

class InnerRegionTubeAlongZSegment( InnerRegion ):

    def __init__( self ):
        super().__init__()        
        

    @classmethod
    def init_from_config( cls, conf, inner_region_tube_segment_conf, sec_name, spat_mesh ):
        new_obj = super().init_from_config( conf,
                                            inner_region_tube_segment_conf,
                                            sec_name,
                                            spat_mesh )
        new_obj.object_type = "tube_along_z_segment"
        new_obj.check_correctness_tube_segment_config_fields(
            conf,
            inner_region_tube_segment_conf )
        new_obj.get_tube_segment_values_from_config( inner_region_tube_segment_conf )
        new_obj.mark_inner_nodes( spat_mesh )
        #new_obj.select_inner_nodes_not_at_domain_edge( spat_mesh )
        return new_obj

    
    @classmethod
    def init_from_h5( cls, h5_inner_region_tube_segment_group, spat_mesh ):
        new_obj = super().init_from_h5( h5_inner_region_tube_segment_group )
        new_obj.geometry_type = "tube_along_z_segment"
        new_obj.get_tube_segment_values_from_h5( h5_inner_region_tube_segment_group )
        new_obj.mark_inner_nodes( spat_mesh )
        #new_obj.select_inner_nodes_not_at_domain_edge( spat_mesh )
        return new_obj
    

    def check_correctness_of_tube_segment_config_fields( self,
                                                         conf,
                                                         inner_region_tube_segment_conf ):
        # todo: check if region lies inside the domain
        pass
    

    def get_tube_segment_values_from_config( self, inner_region_tube_segment_conf ):
        self.axis_x = inner_region_tube_segment_conf.getfloat(
            "tube_segment_axis_x" )
        self.axis_y = inner_region_tube_segment_conf.getfloat(
            "tube_segment_axis_y" )
        self.axis_start_z = inner_region_tube_segment_conf.getfloat(
            "tube_segment_axis_start_z" )
        self.axis_end_z = inner_region_tube_segment_conf.getfloat(
            "tube_segment_axis_end_z" )
        self.inner_radius = inner_region_tube_segment_conf.getfloat(
            "tube_segment_inner_radius" )
        self.outer_radius = inner_region_tube_segment_conf.getfloat(
            "tube_segment_outer_radius" )
        self.start_angle_deg = inner_region_tube_segment_conf.getfloat(
            "tube_segment_start_angle_deg" )
        self.end_angle_deg = inner_region_tube_segment_conf.getfloat(
            "tube_segment_end_angle_deg" )

        

    def get_tube_segment_values_from_h5( self, h5_inner_region_tube_segment_group ):
        self.axis_x = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_axis_x"][0]
        self.axis_y = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_axis_y"][0]
        self.axis_start_z = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_axis_start_z"][0]
        self.axis_end_z = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_axis_end_z"][0]
        self.inner_radius = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_inner_radius"][0]
        self.outer_radius = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_outer_radius"][0]
        self.start_angle_deg = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_start_angle_deg" ][0]
        self.end_angle_deg = h5_inner_region_tube_segment_group.attrs[
            "tube_segment_end_angle_deg" ][0]


    def check_if_point_inside( self, x, y, z ):
        # todo: in constructor: square inner/outer_r, convert segment angle to rad
        if z < self.axis_start_z or z > self.axis_end_z:
            return False
        shift_x = x - self.axis_x
        shift_y = y - self.axis_y
        radius = np.sqrt( shift_x**2 + shift_y**2 )
        if radius < self.inner_radius or radius > self.outer_radius:
            return False 
        polar_ang = np.arctan2( shift_y, shift_x ) * 180 / np.pi
        if polar_ang < 0:
            polar_ang = 360 + polar_ang
        if polar_ang < self.start_angle_deg or polar_ang > self.end_angle_deg:
            return False
        return True

    
    def write_hdf5_region_specific_parameters( self, current_region_group ):        
        current_region_group.attrs.create( "tube_segment_axis_x", self.axis_x )
        current_region_group.attrs.create( "tube_segment_axis_y", self.axis_y )
        current_region_group.attrs.create( "tube_segment_axis_start_z", self.axis_start_z )
        current_region_group.attrs.create( "tube_segment_axis_end_z",   self.axis_end_z )
        current_region_group.attrs.create( "tube_segment_inner_radius", self.inner_radius )
        current_region_group.attrs.create( "tube_segment_outer_radius", self.outer_radius )
        current_region_group.attrs.create( "tube_segment_start_angle_deg",
                                           self.start_angle_deg )
        current_region_group.attrs.create( "tube_segment_end_angle_deg",
                                           self.end_angle_deg )
        

    @classmethod
    def is_tube_along_z_segment_region( cls, conf_sec_name ):
        return 'Inner_region_tube_along_z_segment' in conf_sec_name
