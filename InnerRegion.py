import os
import sys
import h5py
import numpy as np

from common import production_assert
from Vec3d import Vec3d

class InnerRegion():

    def __init__( self ):
        self.total_absorbed_particles = 0
        self.total_absorbed_charge = 0
        self.absorbed_particles_current_timestep = 0
        self.absorbed_charge_current_timestep = 0
        self.inner_nodes = []
        self.inner_nodes_not_at_domain_edge = []


    @classmethod
    def init_from_config( cls, conf, this_reg_config_part, sec_name, spat_mesh ):
        new_obj = cls()
        new_obj.check_correctness_of_related_config_fields( 
            conf, this_reg_config_part, spat_mesh )
        new_obj.set_parameters_from_config( this_reg_config_part, sec_name )
        return new_obj


    @classmethod
    def init_from_h5( cls, h5group ):
        new_obj = cls()
        new_obj.get_values_from_h5( h5group )
        return new_obj


    def check_correctness_of_related_config_fields( self, conf,
                                                    this_reg_config_part, spat_mesh ):
        # todo
        pass

    
    def set_parameters_from_config( self, this_reg_config_part, sec_name ):        
        self.name = sec_name[ sec_name.rfind(".") + 1 : ]
        self.potential = this_reg_config_part.potential


    def get_values_from_h5( self, h5_inner_region_group ):
        self.name = os.path.basename( h5_inner_region_group.name )        
        self.potential = h5_inner_region_group.attrs["potential"][0]
        self.total_absorbed_particles = h5_inner_region_group.attrs[
            "total_absorbed_particles"][0]
        self.total_absorbed_charge = h5_inner_region_group.attrs[
            "total_absorbed_charge"][0]


    def check_if_particle_inside( self, p ):
        x = p.position.x
        y = p.position.y
        z = p.position.z
        return self.check_if_point_inside( x, y, z );

    
    def check_if_particle_inside_and_count_charge( self, p ):
        in_or_out = self.check_if_particle_inside( p )
        if in_or_out:
            self.absorbed_particles_current_timestep++
            self.absorbed_charge_current_timestep += p.charge
        return in_or_out


    def check_if_point_inside( self, x, y, z ):
        # virtual method
        raise NotImplementedError()

    
    def check_if_node_inside( self, node, dx, dy, dz ):
        return self.check_if_point_inside( node.x * dx, node.y * dy, node.z * dz )


    def mark_inner_nodes( self, spat_mesh ):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes

        for k in range( nz ):
            for j in range( ny ):
                for i in range( nx ):
                    if self.check_if_point_inside(
                            spat_mesh.node_number_to_coordinate_x(i),
                            spat_mesh.node_number_to_coordinate_y(j),
                            spat_mesh.node_number_to_coordinate_z(k) ):
                        self.inner_nodes.append( Node( i, j, k ) )


                                                                
    def select_inner_nodes_not_at_domain_edge( self, spat_mesh ):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes            
        for node in self.inner_nodes:
            if !node.at_domain_edge( nx, ny, nz ):
                inner_nodes_not_at_domain_edge.append( node )


    def write_to_file( self, regions_group_id ):
        current_region_group_id = h5group.create_group( "./" + self.name )
        self.write_hdf5_common_parameters( current_region_group_id )
        self.write_hdf5_region_specific_parameters( current_region_group_id )


    def write_hdf5_common_parameters( self, current_region_group_id ):
        current_region_group_id.attrs["object_type"] = self.object_type
        current_region_group_id.attrs.create( "potential", self.potential )
        current_region_group_id.attrs.create( "total_absorbed_particles",
                                              self.total_absorbed_particles )
        current_region_group_id.attrs.create( "total_absorbed_charge",
                                              self.total_absorbed_charge )


    def write_hdf5_region_specific_parameters( self, current_region_group_id ):
        # virtual method
        raise NotImplementedError()
