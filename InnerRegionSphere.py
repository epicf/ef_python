from InnerRegion import InnerRegion

class InnerRegionSphere(InnerRegion):

    def __init__(self):
        super().__init__()
        self.origin_x = None
        self.origin_y = None
        self.origin_z = None
        self.radius = None


    @classmethod
    def init_from_config(cls, conf, inner_region_sphere_conf, sec_name, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_config(conf,
                                               inner_region_sphere_conf,
                                               sec_name,
                                               spat_mesh)
        new_obj.geometry_type = "sphere"
        new_obj.check_correctness_of_sphere_config_fields(conf,
                                                          inner_region_sphere_conf)
        new_obj.get_sphere_values_from_config(inner_region_sphere_conf)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    @classmethod
    def init_from_h5(cls, h5_inner_region_sphere_group, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_h5(h5_inner_region_sphere_group)
        new_obj.geometry_type = "sphere"
        new_obj.get_sphere_values_from_h5(h5_inner_region_sphere_group)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    def check_correctness_of_sphere_config_fields(self,
                                                  conf, inner_region_sphere_conf):
        # todo: check if region lies inside the domain
        pass


    def get_sphere_values_from_config(self, inner_region_sphere_conf):
        self.origin_x = inner_region_sphere_conf.getfloat("sphere_origin_x")
        self.origin_y = inner_region_sphere_conf.getfloat("sphere_origin_y")
        self.origin_z = inner_region_sphere_conf.getfloat("sphere_origin_z")
        self.radius = inner_region_sphere_conf.getfloat("sphere_radius")


    def get_sphere_values_from_h5(self, h5_inner_region_sphere_group):
        self.origin_x = h5_inner_region_sphere_group.attrs["sphere_origin_x"]
        self.origin_y = h5_inner_region_sphere_group.attrs["sphere_origin_y"]
        self.origin_z = h5_inner_region_sphere_group.attrs["sphere_origin_z"]
        self.radius = h5_inner_region_sphere_group.attrs["sphere_radius"]


    def check_if_point_inside(self, x, y, z):
        xdist = x - self.origin_x
        ydist = y - self.origin_y
        zdist = z - self.origin_z
        inside = (xdist * xdist + ydist * ydist + zdist * zdist <= \
                  self.radius * self.radius)
        return inside


    def write_hdf5_region_specific_parameters(self, current_region_group):
        current_region_group.attrs.create("sphere_origin_x", self.origin_x)
        current_region_group.attrs.create("sphere_origin_y", self.origin_y)
        current_region_group.attrs.create("sphere_origin_z", self.origin_z)
        current_region_group.attrs.create("sphere_radius",   self.radius)


    @classmethod
    def is_sphere_region(cls, conf_sec_name):
        return 'InnerRegionSphere' in conf_sec_name
