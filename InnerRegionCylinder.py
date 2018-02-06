from InnerRegion import InnerRegion
from Vec3d import Vec3d

class InnerRegionCylinder( InnerRegion ):

    def __init__( self ):
        super().__init__()        
        

    @classmethod
    def init_from_config( cls, conf, inner_region_cylinder_conf, sec_name, spat_mesh ):
        new_obj = super().init_from_config( conf,
                                            inner_region_cylinder_conf,
                                            sec_name,
                                            spat_mesh )
        new_obj.object_type = "cylinder"
        new_obj.check_correctness_of_cylinder_config_fields( conf,
                                                             inner_region_cylinder_conf )
        new_obj.get_cylinder_values_from_config( inner_region_cylinder_conf )
        new_obj.mark_inner_nodes( spat_mesh )
        #new_obj.select_inner_nodes_not_at_domain_edge( spat_mesh )
        return new_obj

    
    @classmethod
    def init_from_h5( cls, h5_inner_region_cylinder_group, spat_mesh ):
        new_obj = super().init_from_h5( h5_inner_region_cylinder_group )
        new_obj.geometry_type = "cylinder"
        new_obj.get_cylinder_values_from_h5( h5_inner_region_cylinder_group )
        new_obj.mark_inner_nodes( spat_mesh )
        #new_obj.select_inner_nodes_not_at_domain_edge( spat_mesh )
        return new_obj
    

    def check_correctness_of_cylinder_config_fields( self,
                                                     conf, inner_region_cylinder_conf ):
        # todo: check if region lies inside the domain
        pass
    

    def get_cylinder_values_from_config( self, inner_region_cylinder_conf ):
        self.axis_start_x = inner_region_cylinder_conf.getfloat( "cylinder_axis_start_x" )
        self.axis_start_y = inner_region_cylinder_conf.getfloat( "cylinder_axis_start_y" )
        self.axis_start_z = inner_region_cylinder_conf.getfloat( "cylinder_axis_start_z" )
        self.axis_end_x = inner_region_cylinder_conf.getfloat( "cylinder_axis_end_x" )
        self.axis_end_y = inner_region_cylinder_conf.getfloat( "cylinder_axis_end_y" )
        self.axis_end_z = inner_region_cylinder_conf.getfloat( "cylinder_axis_end_z" )
        self.radius = inner_region_cylinder_conf.getfloat( "cylinder_radius" )


    def get_cylinder_values_from_h5( self, h5_inner_region_cylinder_group ):
        self.axis_start_x = h5_inner_region_cylinder_group.attrs[
            "cylinder_axis_start_x"][0]
        self.axis_start_y = h5_inner_region_cylinder_group.attrs[
            "cylinder_axis_start_y"][0]
        self.axis_start_z = h5_inner_region_cylinder_group.attrs[
            "cylinder_axis_start_z"][0]
        self.axis_end_x = h5_inner_region_cylinder_group.attrs["cylinder_axis_end_x"][0]
        self.axis_end_y = h5_inner_region_cylinder_group.attrs["cylinder_axis_end_y"][0]
        self.axis_end_z = h5_inner_region_cylinder_group.attrs["cylinder_axis_end_z"][0]
        self.radius = h5_inner_region_cylinder_group.attrs["cylinder_radius"][0]


    def check_if_point_inside( self, x, y, z ):
        pointvec = Vec3d( (x - self.axis_start_x),
                          (y - self.axis_start_y),
                          (z - self.axis_start_z) )
        axisvec = Vec3d( ( self.axis_end_x - self.axis_start_x ),
                         ( self.axis_end_y - self.axis_start_y ),
                         ( self.axis_end_z - self.axis_start_z ) )
        unit_axisvec = axisvec.normalized()
        
        projection = pointvec.dot_product( unit_axisvec )
        perp_to_axis = pointvec.sub( unit_axisvec.times_scalar( projection ) )
        inside = ( projection >= 0 and \
                   projection <= axisvec.length() and 
                   perp_to_axis.length() <= self.radius )
        return inside


    
    def write_hdf5_region_specific_parameters( self, current_region_group ):        
        current_region_group.attrs.create( "cylinder_axis_start_x", self.axis_start_x )
        current_region_group.attrs.create( "cylinder_axis_start_y", self.axis_start_y )
        current_region_group.attrs.create( "cylinder_axis_start_z", self.axis_start_z )
        current_region_group.attrs.create( "cylinder_axis_end_x",   self.axis_end_x )
        current_region_group.attrs.create( "cylinder_axis_end_y",   self.axis_end_y )
        current_region_group.attrs.create( "cylinder_axis_end_z",   self.axis_end_z )
        current_region_group.attrs.create( "cylinder_radius",       self.radius )


    @classmethod
    def is_cylinder_region( cls, conf_sec_name ):
        return 'Inner_region_cylinder' in conf_sec_name
