from InnerRegion import InnerRegion

class InnerRegionConeAlongZ(InnerRegion):

    def __init__(self):
        super().__init__()
        self.axis_x = None
        self.axis_y = None
        self.axis_start_z = None
        self.axis_end_z = None
        self.start_inner_radius = None
        self.start_outer_radius = None
        self.end_inner_radius = None
        self.end_outer_radius = None


    @classmethod
    def init_from_config(cls, conf, inner_region_cone_conf, sec_name, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_config(conf,
                                               inner_region_cone_conf,
                                               sec_name,
                                               spat_mesh)
        new_obj.geometry_type = "cone"
        new_obj.check_correctness_of_cone_config_fields(conf, inner_region_cone_conf)
        new_obj.get_cone_values_from_config(inner_region_cone_conf)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    @classmethod
    def init_from_h5(cls, h5_inner_region_cone_group, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_h5(h5_inner_region_cone_group)
        new_obj.geometry_type = "cone"
        new_obj.get_cone_values_from_h5(h5_inner_region_cone_group)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    def check_correctness_of_cone_config_fields(self, conf, inner_region_cone_conf):
        # todo: check if region lies inside the domain
        if inner_region_cone_conf.getfloat("cone_axis_start_z") > \
           inner_region_cone_conf.getfloat("cone_axis_end_z"):
            raise ValueError("Expect axis_start_z < axis_end_z")
        if inner_region_cone_conf.getfloat("cone_start_inner_radius") > \
           inner_region_cone_conf.getfloat("cone_start_outer_radius"):
            raise ValueError("Expect start_inner_radius < start_outer_radius")
        if inner_region_cone_conf.getfloat("cone_end_inner_radius") > \
           inner_region_cone_conf.getfloat("cone_end_outer_radius"):
            raise ValueError("Expect end_inner_radius < end_outer_radius")


    def get_cone_values_from_config(self, inner_region_cone_conf):
        self.axis_x = inner_region_cone_conf.getfloat("cone_axis_x")
        self.axis_y = inner_region_cone_conf.getfloat("cone_axis_y")
        self.axis_start_z = inner_region_cone_conf.getfloat("cone_axis_start_z")
        self.axis_end_z = inner_region_cone_conf.getfloat("cone_axis_end_z")
        self.start_inner_radius = \
            inner_region_cone_conf.getfloat("cone_start_inner_radius")
        self.start_outer_radius = \
            inner_region_cone_conf.getfloat("cone_start_outer_radius")
        self.end_inner_radius = inner_region_cone_conf.getfloat("cone_end_inner_radius")
        self.end_outer_radius = inner_region_cone_conf.getfloat("cone_end_outer_radius")


    def get_cone_values_from_h5(self, h5_inner_region_cone_group):
        self.axis_x = h5_inner_region_cone_group.attrs["cone_axis_x"]
        self.axis_y = h5_inner_region_cone_group.attrs["cone_axis_y"]
        self.axis_start_z = h5_inner_region_cone_group.attrs["cone_axis_start_z"]
        self.axis_end_z = h5_inner_region_cone_group.attrs["cone_axis_end_z"]
        self.start_inner_radius = \
            h5_inner_region_cone_group.attrs["cone_start_inner_radius"]
        self.start_outer_radius = \
            h5_inner_region_cone_group.attrs["cone_start_outer_radius"]
        self.end_inner_radius = h5_inner_region_cone_group.attrs["cone_end_inner_radius"]
        self.end_outer_radius = h5_inner_region_cone_group.attrs["cone_end_outer_radius"]


    @staticmethod
    def point_inside_cone(axis_x, axis_y, axis_start_z, axis_end_z,
                          r_start, r_end, x, y, z):
        z_len = abs(axis_end_z - axis_start_z)
        x_dist = x - axis_x
        y_dist = y - axis_y
        if z < axis_start_z:
            return False
        if z > axis_end_z:
            return False
        if r_start < r_end:
            tg_a = (r_end - r_start) / z_len
            z_dist = abs(z - axis_start_z)
            r = z_dist * tg_a + r_start
        else:
            tg_a = (r_start - r_end) / z_len
            z_dist = abs(z - axis_end_z)
            r = z_dist * tg_a + r_end
        if r * r < x_dist * x_dist + y_dist * y_dist:
            return False
        return True


    def check_if_point_inside(self, x, y, z):
        in_outer = self.point_inside_cone(self.axis_x, self.axis_y,
                                          self.axis_start_z, self.axis_end_z,
                                          self.start_outer_radius, self.end_outer_radius,
                                          x, y, z)
        if not in_outer: return False
        in_inner = self.point_inside_cone(self.axis_x, self.axis_y,
                                          self.axis_start_z, self.axis_end_z,
                                          self.start_inner_radius, self.end_inner_radius,
                                          x, y, z)
        if in_inner: return False
        return True


    def write_hdf5_region_specific_parameters(self, current_region_group):
        current_region_group.attrs.create("cone_axis_x", self.axis_x)
        current_region_group.attrs.create("cone_axis_y", self.axis_y)
        current_region_group.attrs.create("cone_axis_start_z", self.axis_start_z)
        current_region_group.attrs.create("cone_axis_end_z",   self.axis_end_z)
        current_region_group.attrs.create("cone_start_inner_radius",
                                          self.start_inner_radius)
        current_region_group.attrs.create("cone_start_outer_radius",
                                          self.start_outer_radius)
        current_region_group.attrs.create("cone_end_inner_radius", self.end_inner_radius)
        current_region_group.attrs.create("cone_end_outer_radius", self.end_outer_radius)


    @classmethod
    def is_cone_region(cls, conf_sec_name):
        return 'InnerRegionConeAlongZ' in conf_sec_name
