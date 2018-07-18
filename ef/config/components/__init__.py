"""This package contains all supported configuration components

use "from components import *" before turning a configparser object into components
to make sure all config section names are registered in ef.config.section:ConfigSection"""

from ef.config.components.fields import *
from ef.config.components.boundary_conditions import *
from ef.config.components.inner_region import *
from ef.config.components.output_file import *
from ef.config.components.particle_interaction_model import *
from ef.config.components.particle_source import *
from ef.config.components.shapes import *
from ef.config.components.spatial_mesh import *
from ef.config.components.time_grid import *
