import re
import sys
import h5py

#include "config.h"
from Domain import Domain
#include "parse_cmd_line.h"


def main():    
    config_or_h5_file = parse_cmd_line()
    continue_from_h5 = False
    dom, continue_from_h5 = construct_domain( config_or_h5_file )
    #
    if continue_from_h5:
	dom.continue_pic_simulation()
    else:
	dom.start_pic_simulation()
    #
    return 0


def construct_domain( config_or_h5_file ):
    extension =	config_or_h5_file[ config_or_h5_file.rfind(".") + 1, : ]
    if extension == "h5":
	h5file = h5py.File( config_or_h5_file, 'r' )
	# if h5file_id < 0:
	#     print( "Can't open file: ", config_or_h5_file )
	#     sys.exit( -1 )	
	filename_prefix, filename_suffix = \
            extract_filename_prefix_and_suffix_from_h5filename( config_or_h5_file )	
	dom = Domain.init_from_h5( h5file )
	dom.set_output_filename_prefix_and_suffix( filename_prefix, filename_suffix )
	continue_from_h5 = True
    else:
	#print( config_or_h5_file )
	dom = Domain.init_from_config( conf )
        continue_from_h5 = False
    return dom, continue_from_h5


def parse_cmd_line():
    pass


def extract_filename_prefix_and_suffix_from_h5filename( h5_file ):
    rgx = "[0-9]{7}"
    match = re.search( rgx, h5_file )
    if len( match.group ) == 1:
	prefix = h5_file[ 0:match.start() ]
	suffix = h5_file.substr[ match.end(): ]
        print( prefix, suffix )
    else:
	print( "Can't identify filename prefix and suffix in ", h5_file )
	print( "Aborting." )
	sys.exit( -1 )
    #
    return prefix, suffix


if __name__ == "__main__":
    main()
