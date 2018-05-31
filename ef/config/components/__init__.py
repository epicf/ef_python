# import this file to make sure all config section names are registered in ef.config.section:ConfigSection to be parsed
from ef.config.components import boundary_conditions, inner_region, output_file, particle_interaction_model,\
    particle_source, shapes, spatial_mesh, time_grid
import ef.config.components.fields.magnetic.uniform
from ef.config.components.fields.electric import uniform, h5