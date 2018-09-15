from InnerRegion import InnerRegion
from Vec3d import Vec3d

class InnerRegionTube(InnerRegion):

    def __init__(self):
        super().__init__()
        self.axis_start_x = None
        self.axis_start_y = None
        self.axis_start_z = None
        self.axis_end_x = None
        self.axis_end_y = None
        self.axis_end_z = None
        self.inner_radius = None
        self.outer_radius = None


    @classmethod
    def init_from_config(cls, conf, inner_region_tube_conf, sec_name, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_config(conf,
                                               inner_region_tube_conf,
                                               sec_name,
                                               spat_mesh)
        new_obj.geometry_type = "tube"
        new_obj.check_correctness_of_tube_config_fields(conf, inner_region_tube_conf)
        new_obj.get_tube_values_from_config(inner_region_tube_conf)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    @classmethod
    def init_from_h5(cls, h5_inner_region_tube_group, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_h5(h5_inner_region_tube_group)
        new_obj.geometry_type = "tube"
        new_obj.get_tube_values_from_h5(h5_inner_region_tube_group)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    def check_correctness_of_tube_config_fields(self, conf, inner_region_tube_conf):
        # todo: check if region lies inside the domain
        pass


    def get_tube_values_from_config(self, inner_region_tube_conf):
        self.axis_start_x = inner_region_tube_conf.getfloat("tube_axis_start_x")
        self.axis_start_y = inner_region_tube_conf.getfloat("tube_axis_start_y")
        self.axis_start_z = inner_region_tube_conf.getfloat("tube_axis_start_z")
        self.axis_end_x = inner_region_tube_conf.getfloat("tube_axis_end_x")
        self.axis_end_y = inner_region_tube_conf.getfloat("tube_axis_end_y")
        self.axis_end_z = inner_region_tube_conf.getfloat("tube_axis_end_z")
        self.inner_radius = inner_region_tube_conf.getfloat("tube_inner_radius")
        self.outer_radius = inner_region_tube_conf.getfloat("tube_outer_radius")


    def get_tube_values_from_h5(self, h5_inner_region_tube_group):
        self.axis_start_x = h5_inner_region_tube_group.attrs["tube_axis_start_x"]
        self.axis_start_y = h5_inner_region_tube_group.attrs["tube_axis_start_y"]
        self.axis_start_z = h5_inner_region_tube_group.attrs["tube_axis_start_z"]
        self.axis_end_x = h5_inner_region_tube_group.attrs["tube_axis_end_x"]
        self.axis_end_y = h5_inner_region_tube_group.attrs["tube_axis_end_y"]
        self.axis_end_z = h5_inner_region_tube_group.attrs["tube_axis_end_z"]
        self.inner_radius = h5_inner_region_tube_group.attrs["tube_inner_radius"]
        self.outer_radius = h5_inner_region_tube_group.attrs["tube_outer_radius"]


    def check_if_point_inside(self, x, y, z):
        pointvec = Vec3d((x - self.axis_start_x),
                         (y - self.axis_start_y),
                         (z - self.axis_start_z))
        axisvec = Vec3d((self.axis_end_x - self.axis_start_x),
                        (self.axis_end_y - self.axis_start_y),
                        (self.axis_end_z - self.axis_start_z))
        unit_axisvec = axisvec.normalized()
        #
        projection = pointvec.dot_product(unit_axisvec)
        perp_to_axis = pointvec.sub(unit_axisvec.times_scalar(projection))
        inside = (projection >= 0 and \
                  projection <= axisvec.length() and \
                  perp_to_axis.length() >= self.inner_radius and \
                  perp_to_axis.length() <= self.outer_radius)
        return inside


    def write_hdf5_region_specific_parameters(self, current_region_group):        
        current_region_group.attrs.create("tube_axis_start_x", self.axis_start_x)
        current_region_group.attrs.create("tube_axis_start_y", self.axis_start_y)
        current_region_group.attrs.create("tube_axis_start_z", self.axis_start_z)
        current_region_group.attrs.create("tube_axis_end_x",   self.axis_end_x)
        current_region_group.attrs.create("tube_axis_end_y",   self.axis_end_y)
        current_region_group.attrs.create("tube_axis_end_z",   self.axis_end_z)
        current_region_group.attrs.create("tube_inner_radius", self.inner_radius)
        current_region_group.attrs.create("tube_outer_radius", self.outer_radius)


    @classmethod
    def is_tube_region(cls, conf_sec_name):
        return 'InnerRegionTube' in conf_sec_name
