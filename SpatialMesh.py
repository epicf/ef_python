import sys
import h5py
import numpy as np
from math import ceil
from Vec3d import Vec3d
from common import production_assert

class SpatialMesh():

    def __init__( self ):
        pass

    @classmethod
    def init_from_config( cls, conf ):
        new_obj = cls()
        new_obj.check_correctness_of_related_config_fields( conf )
        new_obj.init_x_grid( conf )
        new_obj.init_y_grid( conf )
        new_obj.init_z_grid( conf )
        new_obj.allocate_ongrid_values()
        new_obj.fill_node_coordinates()
        new_obj.set_boundary_conditions( conf )
        return new_obj


    @classmethod
    def init_from_h5( cls, h5group ):
        new_obj = cls()
        new_obj.x_volume_size = h5group.attrs["x_volume_size"][0]
        new_obj.y_volume_size = h5group.attrs["y_volume_size"][0]
        new_obj.z_volume_size = h5group.attrs["z_volume_size"][0]
        new_obj.x_cell_size = h5group.attrs["x_cell_size"][0]
        new_obj.y_cell_size = h5group.attrs["y_cell_size"][0]
        new_obj.z_cell_size = h5group.attrs["z_cell_size"][0]
        new_obj.x_n_nodes = h5group.attrs["x_n_nodes"][0]
        new_obj.y_n_nodes = h5group.attrs["y_n_nodes"][0]
        new_obj.z_n_nodes = h5group.attrs["z_n_nodes"][0]    
        new_obj.allocate_ongrid_values()
        #
        dim = new_obj.node_coordinates.size
        tmp_x = np.empty( dim, dtype = 'f8' )
        tmp_y = np.empty_like( tmp_x )
        tmp_z = np.empty_like( tmp_x )
        #
        tmp_x = h5group["./node_coordinates_x"]
        tmp_y = h5group["./node_coordinates_y"]
        tmp_z = h5group["./node_coordinates_z"]
        for i, (vx, vy, vz) in enumerate( zip( tmp_x, tmp_y, tmp_y ) ):
            new_obj.node_coordinates[i] = Vec3d( vx, vy, vz )
        #
        new_obj.charge_density = h5group["./charge_density"]
        new_obj.potential = h5group["./potential"]
        #
        tmp_x = h5group["./electric_field_x"]
        tmp_y = h5group["./electric_field_y"]
        tmp_z = h5group["./electric_field_z"]
        for i, (vx, vy, vz) in enumerate( zip( tmp_x, tmp_y, tmp_y ) ):
            new_obj.electric_field[i] = Vec3d( vx, vy, vz )
        #
        return new_obj

    
    def allocate_ongrid_values( self ):
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        self.node_coordinates = np.empty( (nx, ny, nz), dtype=object )
        self.charge_density = np.zeros( (nx, ny, nz), dtype='f8' )
        self.potential = np.zeros( (nx, ny, nz), dtype='f8' )
        self.electric_field = np.full( (nx, ny, nz), Vec3d.zero(), dtype=object )
    

    def check_correctness_of_related_config_fields( self, conf ):
        self.grid_x_size_gt_zero( conf )
        self.grid_x_step_gt_zero_le_grid_x_size( conf )
        self.grid_y_size_gt_zero( conf )
        self.grid_y_step_gt_zero_le_grid_y_size( conf )
        self.grid_z_size_gt_zero( conf )
        self.grid_z_step_gt_zero_le_grid_z_size( conf )


    def init_x_grid( self, conf ):
        spat_mesh_conf = conf["Spatial mesh"]
        self.x_volume_size = spat_mesh_conf.getfloat("grid_x_size")
        self.x_n_nodes = ceil( spat_mesh_conf.getfloat("grid_x_size") /
                               spat_mesh_conf.getfloat("grid_x_step") ) + 1
        self.x_cell_size = self.x_volume_size / ( self.x_n_nodes - 1 )
        if ( self.x_cell_size != spat_mesh_conf.getfloat("grid_x_step") ):
            print( "X_step was shrinked to {:.3f} from {:.3f} "
                   "to fit round number of cells".format(
                       self.x_cell_size, spat_mesh_conf.getfloat("grid_x_step") ) )


    def init_y_grid( self, conf ):
        spat_mesh_conf = conf["Spatial mesh"]
        self.y_volume_size = spat_mesh_conf.getfloat("grid_y_size")
        self.y_n_nodes = ceil( spat_mesh_conf.getfloat("grid_y_size") /
                               spat_mesh_conf.getfloat("grid_y_step") ) + 1
        self.y_cell_size = self.y_volume_size / ( self.y_n_nodes - 1 )
        if ( self.y_cell_size != spat_mesh_conf.getfloat("grid_y_step") ):        
            print( "Y_step was shrinked to {:.3f} from {:.3f} "
                   "to fit round number of cells".format(
                       self.y_cell_size, spat_mesh_conf.getfloat("grid_y_step") ) )

            
    def init_z_grid( self, conf ):
        spat_mesh_conf = conf["Spatial mesh"]
        self.z_volume_size = spat_mesh_conf.getfloat("grid_z_size")
        self.z_n_nodes = ceil( spat_mesh_conf.getfloat("grid_z_size") /
                               spat_mesh_conf.getfloat("grid_z_step") ) + 1
        self.z_cell_size = self.z_volume_size / ( self.z_n_nodes - 1 )
        if ( self.z_cell_size != spat_mesh_conf.getfloat("grid_z_step") ):        
            print( "Z_step was shrinked to {:.3f} from {:.3f} "
                   "to fit round number of cells".format(
                       self.z_cell_size, spat_mesh_conf.getfloat("grid_z_step") ) )

        
    def fill_node_coordinates( self ):
        for i in range( self.x_n_nodes ):
            for j in range( self.y_n_nodes ):
                for k in range( self.z_n_nodes ):
                    self.node_coordinates[i][j][k] = Vec3d(
                        i * self.x_cell_size, j * self.y_cell_size, k * self.z_cell_size )


    def clear_old_density_values( self ):
        self.charge_density.fill( 0 )


    def set_boundary_conditions( self, conf ):
        phi_left = conf["Boundary conditions"].getfloat("boundary_phi_left")
        phi_right = conf["Boundary conditions"].getfloat("boundary_phi_right")
        phi_top = conf["Boundary conditions"].getfloat("boundary_phi_top")
        phi_bottom = conf["Boundary conditions"].getfloat("boundary_phi_bottom")
        phi_near = conf["Boundary conditions"].getfloat("boundary_phi_near")
        phi_far = conf["Boundary conditions"].getfloat("boundary_phi_far")
        #
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        for i in range( nx ):
            for k in range( nz ):
                self.potential[i][0][k] = phi_bottom
                self.potential[i][ny-1][k] = phi_top
        for j in range( ny ):
            for k in range( nz ):
                self.potential[0][j][k] = phi_right
                self.potential[nx-1][j][k] = phi_left
        for i in range( nx ):
            for j in range( ny ):
                self.potential[i][j][0] = phi_near
                self.potential[i][j][nz-1] = phi_far

                
    def print( self ):
        self.print_grid()
        self.print_ongrid_values()

            
    def print_grid( self ):
        print( "Grid:" )
        print( "Length: x = {:.3f}, y = {:.3f}, z = {:.3f}".format(
            self.x_volume_size, self.y_volume_size, self.z_volume_size ) )
        print( "Cell size: x = {:.3f}, y = {:.3f}, z = {:.3f}".format(
            self.x_cell_size, self.y_cell_size, self.z_cell_size ) )
        print( "Total nodes: x = {:d}, y = {:d}, z = {:d}".format(
            self.x_n_nodes, self.y_n_nodes, self.z_n_nodes ) )
        
                   
    def print_ongrid_values( self ):
        nx = self.x_n_nodes
        ny = self.y_n_nodes
        nz = self.z_n_nodes
        print( "x_node   y_node   z_node | "
               "charge_density | potential | electric_field(x,y,z)" )
        for i in range( nx ):
            for j in range( ny ):
                for k in range( nz ):
                    "{:8d} {:8d} {:8d} | "
                    "{:14.3f} | {:14.3f} | "
                    "{:14.3f} {:14.3f} {:14.3f}".format(
                        i, j, k,
                        self.charge_density[i][j][k],
                        self.potential[i][j][k],
                        self.electric_field[i][j][k].x,
                        self.electric_field[i][j][k].y,
                        self.electric_field[i][j][k].z )


    def write_to_file( self, h5file ):
        groupname = "/Spatial_mesh";
        h5group = h5file.create_group( groupname )
        self.write_hdf5_attributes( h5group )
        self.write_hdf5_ongrid_values( h5group )

        
    def write_hdf5_attributes( self, h5group ):
        h5group.attrs.create( "x_volume_size", self.x_volume_size )
        h5group.attrs.create( "y_volume_size", self.y_volume_size )
        h5group.attrs.create( "z_volume_size", self.z_volume_size )
        h5group.attrs.create( "x_cell_size", self.x_cell_size )
        h5group.attrs.create( "y_cell_size", self.y_cell_size )
        h5group.attrs.create( "z_cell_size", self.z_cell_size )
        h5group.attrs.create( "x_n_nodes", self.x_n_nodes )
        h5group.attrs.create( "y_n_nodes", self.y_n_nodes )
        h5group.attrs.create( "z_n_nodes", self.z_n_nodes )

        
    def write_hdf5_ongrid_values( self, h5group ):    
        # todo: without compound datasets
        # there is this copying problem.
        dim = self.node_coordinates.size
        tmp_x = np.empty( dim, dtype = 'f8' )
        tmp_y = np.empty_like( tmp_x )
        tmp_z = np.empty_like( tmp_x )
        # todo: make view instead of copy
        for i, v in enumerate( self.node_coordinates.flat ):
            tmp_x[i] = v.x
            tmp_y[i] = v.y
            tmp_z[i] = v.z
        h5group.create_dataset( "./node_coordinates_x", data = tmp_x )
        h5group.create_dataset( "./node_coordinates_y", data = tmp_y )
        h5group.create_dataset( "./node_coordinates_z", data = tmp_z )
        # C (C-order): index along the first axis varies slowest
        # in self.node_coordinates.flat above default order is C
        flat_phi = self.potential.ravel( order = 'C' )
        h5group.create_dataset( "./potential", data = flat_phi )
        flat_rho = self.charge_density.ravel( order = 'C' )
        h5group.create_dataset( "./charge_density", data = flat_rho )
        #
        for i, v in enumerate( self.electric_field.flat ):
            tmp_x[i] = v.x
            tmp_y[i] = v.y
            tmp_z[i] = v.z
        h5group.create_dataset( "./electric_field_x", data = tmp_x )
        h5group.create_dataset( "./electric_field_y", data = tmp_y )
        h5group.create_dataset( "./electric_field_z", data = tmp_z )

        
    def grid_x_size_gt_zero( self, conf ):
        production_assert( conf["Spatial mesh"].getfloat("grid_x_size") > 0,
                           "grid_x_size < 0" )
        

    def grid_x_step_gt_zero_le_grid_x_size( self, conf ):
        production_assert( 
            ( conf["Spatial mesh"].getfloat("grid_x_step") > 0 ) and
            ( conf["Spatial mesh"].getfloat("grid_x_step") <=
              conf["Spatial mesh"].getfloat("grid_x_size") ),
            "grid_x_step < 0 or grid_x_step >= grid_x_size" )

        
    def grid_y_size_gt_zero( self, conf ):
        production_assert(
            conf["Spatial mesh"].getfloat("grid_y_size") > 0,
            "grid_y_size < 0" )

        
    def grid_y_step_gt_zero_le_grid_y_size( self, conf ):
        production_assert(
            ( conf["Spatial mesh"].getfloat("grid_y_step") > 0 ) and 
            ( conf["Spatial mesh"].getfloat("grid_y_step") <=
              conf["Spatial mesh"].getfloat("grid_y_size") ),
            "grid_y_step < 0 or grid_y_step >= grid_y_size" )


    def grid_z_size_gt_zero( self, conf ):
        production_assert( conf["Spatial mesh"].getfloat("grid_z_size") > 0,
			   "grid_z_size < 0" )

        
    def grid_z_step_gt_zero_le_grid_z_size( self, conf ):
        production_assert(
            ( conf["Spatial mesh"].getfloat("grid_z_step") > 0 ) and 
            ( conf["Spatial mesh"].getfloat("grid_z_step") <=
              conf["Spatial mesh"].getfloat("grid_z_size") ),
            "grid_z_step < 0 or grid_z_step >= grid_z_size" )


    def node_number_to_coordinate_x( self, i ):
        if i >= 0 and i < self.x_n_nodes:
            return i * self.x_cell_size
        else:
            print( "invalid node number i={:d} "
                   "at node_number_to_coordinate_x".format( i ) )
            sys.exit( -1 )

            
    def node_number_to_coordinate_y( self, j ):
        if j >= 0 and j < self.y_n_nodes:
            return j * self.y_cell_size
        else:
            print( "invalid node number j={:d} "
                   "at node_number_to_coordinate_y".format( j ) )
            sys.exit( -1 )

            
    def node_number_to_coordinate_z( self, k ):
        if k >= 0 and k < self.z_n_nodes:
            return k * self.z_cell_size
        else:
            print( "invalid node number k={:d} "
                   "at node_number_to_coordinate_z".format( k ) )
            sys.exit( -1 )
