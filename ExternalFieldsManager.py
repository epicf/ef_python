from ExternalFields import ExternalField
from ExternalFields import ExternalFieldMagneticUniform, ExternalFieldElectricUniform

class ExternalFieldsManager():

    def __init__( self ):
        electric = []
        magnetic = []
        pass

    @classmethod 
    def init_from_config( cls, conf ):
        new_obj = cls()
        new_obj.electric = []
        new_obj.magnetic = []
        for field_conf in conf["External fields"]:
            if type( field_conf ) == "magnetic_uniform":
                new_obj.magnetic.append(
                    ExternalFieldMagneticUniform.init_from_config( field_conf ) )
            elif type( field_conf ) == "electric_uniform":
                new_obj.electric.append(
                    ExternalFieldElectricUniform.init_from_config( field_conf ) )
            else:
                print( "In fields_manager constructor: " )
                print( "Unknown config type. Aborting" )
                sys.exit( -1 )
        return new_obj

    @classmethod
    def init_from_h5( cls, h5_external_fields_group ):
        new_obj = cls()
        new_obj.electric = []
        new_obj.magnetic = []
        pass
    #     err = H5Gget_num_objs(h5_external_fields_group, &nobj);
    #     for( hsize_t i = 0; i < nobj; i++ ){
    #         len = H5Gget_objname_by_idx( h5_external_fields_group, i, 
    #                                      memb_name_cstr, MAX_NAME );
    #         otype = H5Gget_objtype_by_idx( h5_external_fields_group, i );
    #         if ( otype == H5G_GROUP ) {
    #             current_field_grpid = H5Gopen( h5_external_fields_group,
    #                                            memb_name_cstr, H5P_DEFAULT );
    #             parse_hdf5_external_field( current_field_grpid );
    #             err = H5Gclose( current_field_grpid ); hdf5_status_check( err );
    #   return new_obj

    def parse_hdf5_external_field( self, current_field_grpid ):
        # status = H5LTget_attribute_string( current_field_grpid, "./",
        #                                    "field_type", field_type_cstr );
        if field_type == "magnetic_uniform":
            self.magnetic.append(
                ExternalFieldMagneticUniform.init_from_h5( current_field_grpid ) )
        elif field_type == "electric_uniform":
            self.electric.append(
                ExternalFieldElectricUniform.init_from_h5( current_field_grpid ) )
        else:
            print( "In External_field_manager constructor-from-h5: " )
            print( "Unknown external_field type. Aborting" )
            sys.exit( -1 )

    
    def write_to_file( self, hdf5_file_id ):
        hdf5_groupname = "/External_fields";
        n_of_electric_fields = len( self.electric )
        n_of_magnetic_fields = len( self.magnetic )
        fields_group = hdf5_file_id.create_group( hdf5_groupname )
        fields_group.attrs.create( "number_of_electric_fields", n_of_electric_fields )
        fields_group.attrs.create( "number_of_magnetic_fields", n_of_magnetic_fields )
        for el_field in self.electric:
            el_field.write_to_file( fields_group )
        for mgn_field in self.magnetic:
            mgn_field.write_to_file( fields_group )


    def print_fields( self ):
        for el_field in self.electric:
            el_field.print()
        for mgn_field in self.magnetic:
            mgn_field.print()
