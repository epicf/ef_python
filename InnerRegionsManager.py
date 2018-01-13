class InnerRegionsManager():

    def __init__( self ):
        pass

    @classmethod
    def init_from_config( cls, conf, spat_mesh ):
        new_obj = cls()
        new_obj.regions = []
        return new_obj

    @classmethod
    def init_from_h5( cls, h5group, spat_mesh ):
        new_obj = cls()
        new_obj.regions = []
        return new_obj        

    def write_to_file( self, h5file ):
        pass

    def check_if_particle_inside_and_count_charge( self, p ):
        pass
    
# public:
#     boost::ptr_vector<Inner_region> regions;
# public:
#     Inner_regions_manager( Config &conf, Spatial_mesh &spat_mesh )
#     {
# 	for( auto &inner_region_conf : conf.inner_regions_config_part ){
# 	    if( Inner_region_box_config_part *box_conf =
# 		dynamic_cast<Inner_region_box_config_part*>( &inner_region_conf ) ){
# 		regions.push_back( new Inner_region_box( conf,
# 							 *box_conf,
# 							 spat_mesh ) );
# 	    } else if( Inner_region_sphere_config_part *sphere_conf =
# 		dynamic_cast<Inner_region_sphere_config_part*>( &inner_region_conf ) ){
# 		regions.push_back( new Inner_region_sphere( conf,
# 							    *sphere_conf,
# 							    spat_mesh ) );
# 	    } else if( Inner_region_cylinder_config_part *cyl_conf =
# 		dynamic_cast<Inner_region_cylinder_config_part*>( &inner_region_conf ) ){
# 		regions.push_back( new Inner_region_cylinder( conf,
# 							      *cyl_conf,
# 							      spat_mesh ) );
# 	    } else if( Inner_region_tube_config_part *tube_conf =
# 		dynamic_cast<Inner_region_tube_config_part*>( &inner_region_conf ) ){
# 		regions.push_back( new Inner_region_tube( conf,
# 							  *tube_conf,
# 							  spat_mesh ) );
# 	    } else {
# 		std::cout << "In Inner_regions_manager constructor-from-conf: "
# 			  << "Unknown inner_region type. Aborting"
# 			  << std::endl;
# 		exit( EXIT_FAILURE );
# 	    }
# 	}
#     }

#     Inner_regions_manager( hid_t h5_inner_region_group, Spatial_mesh &spat_mesh )
#     {	
# 	hsize_t nobj;
# 	ssize_t len;
# 	herr_t err;
# 	int otype;
# 	size_t MAX_NAME = 1024;
# 	char memb_name_cstr[MAX_NAME];
# 	hid_t current_ir_grpid;
# 	err = H5Gget_num_objs(h5_inner_region_group, &nobj);

# 	for( hsize_t i = 0; i < nobj; i++ ){
# 	    len = H5Gget_objname_by_idx(h5_inner_region_group, i, 
# 					memb_name_cstr, MAX_NAME );
# 	    hdf5_status_check( len );
# 	    otype = H5Gget_objtype_by_idx( h5_inner_region_group, i );
# 	    if ( otype == H5G_GROUP ) {
# 		current_ir_grpid = H5Gopen( h5_inner_region_group,
# 					    memb_name_cstr, H5P_DEFAULT );
# 		parse_hdf5_inner_reg( current_ir_grpid, spat_mesh );
# 		err = H5Gclose( current_ir_grpid ); hdf5_status_check( err );
# 	    }		
# 	}
	
# 	// To iterate over subgroups, there is H5Giterate function.
# 	// However, it needs a callback function as one of it's arguments.
# 	// H5Giterate( h5_inner_region_group, "./", NULL,
# 	//               parse_hdf5_inner_reg, &spat_mesh );	
# 	// It is difficult to pass a C++ method as a callback.
# 	// See: https://isocpp.org/wiki/faq/pointers-to-members#memfnptr-vs-fnptr
# 	// Therefore, iteration is manual.
#     }
    
#     void parse_hdf5_inner_reg( hid_t current_ir_grpid, Spatial_mesh &spat_mesh )
#     {
# 	herr_t status;
# 	char object_type_cstr[50];
# 	status = H5LTget_attribute_string( current_ir_grpid, "./",
# 					   "object_type", object_type_cstr );
# 	hdf5_status_check( status );

# 	std::string obj_type( object_type_cstr );
# 	if( obj_type == "box" ){
# 	    regions.push_back( new Inner_region_box( current_ir_grpid,
# 						     spat_mesh ) );
# 	} else if ( obj_type == "sphere" ) {
# 	    regions.push_back( new Inner_region_sphere( current_ir_grpid,
# 							spat_mesh ) );
# 	} else if ( obj_type == "cylinder" ) {
# 	    regions.push_back( new Inner_region_cylinder( current_ir_grpid,
# 							  spat_mesh ) );
# 	} else if ( obj_type == "tube" ) {
# 	    regions.push_back( new Inner_region_tube( current_ir_grpid,
# 						      spat_mesh ) );
# 	} else {
# 	    std::cout << "In Inner_regions_manager constructor-from-h5: "
# 		      << "Unknown inner_region type. Aborting"
# 		      << std::endl;
# 	    exit( EXIT_FAILURE );
# 	}	
#     }

#     virtual ~Inner_regions_manager() {};    

#     bool check_if_particle_inside( Particle &p )
#     {
# 	for( auto &region : regions ){
# 	    if( region.check_if_particle_inside( p ) )
# 		return true;
# 	}
# 	return false;
#     }

#     bool check_if_particle_inside_and_count_charge( Particle &p )
#     {
# 	for( auto &region : regions ){
# 	    if( region.check_if_particle_inside_and_count_charge( p ) )
# 		return true;
# 	}
# 	return false;
#     }
   
#     void print( )
#     {
# 	for( auto &region : regions )
# 	    region.print();
#     }

#     void print_inner_nodes() {
#     	for( auto &region : regions )
# 	    region.print_inner_nodes();
#     }

#     void print_near_boundary_nodes() {
#     	for( auto &region : regions )
# 	    region.print_near_boundary_nodes();
#     }

#     void write_to_file( hid_t hdf5_file_id )
#     {
# 	hid_t group_id;
# 	herr_t status;
# 	int single_element = 1;
# 	std::string hdf5_groupname = "/Inner_regions";
# 	int n_of_regions = regions.size();
# 	group_id = H5Gcreate2(
# 	    hdf5_file_id, hdf5_groupname.c_str(),
# 	    H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT );
# 	hdf5_status_check( group_id );

# 	status = H5LTset_attribute_int(
# 	    hdf5_file_id, hdf5_groupname.c_str(),
# 	    "number_of_regions", &n_of_regions, single_element );
# 	hdf5_status_check( status );
	
# 	for( auto &reg : regions )
# 	    reg.write_to_file( group_id );

# 	status = H5Gclose(group_id);
# 	hdf5_status_check( status );
#     }; 

#     void hdf5_status_check( herr_t status )
#     {
# 	if( status < 0 ){
# 	    std::cout << "Something went wrong while "
# 		      << "writing or reading Inner_regions group. Aborting."
# 		      << std::endl;
# 	    exit( EXIT_FAILURE );
# 	}
#     };
