from InnerRegion import InnerRegion

class InnerRegionBox(InnerRegion):

    def __init__(self):
        super().__init__()
        self.x_left = None
        self.x_right = None
        self.y_bottom = None
        self.y_top = None
        self.z_near = None
        self.z_far = None


    @classmethod
    def init_from_config(cls, conf, inner_region_box_conf, sec_name, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_config(conf,
                                               inner_region_box_conf,
                                               sec_name,
                                               spat_mesh)
        new_obj.geometry_type = "box"
        new_obj.check_correctness_of_box_config_fields(conf, inner_region_box_conf)
        new_obj.get_box_values_from_config(inner_region_box_conf)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    @classmethod
    def init_from_h5(cls, h5_inner_region_box_group, spat_mesh):
        new_obj = cls()
        new_obj.init_common_fields_from_h5(h5_inner_region_box_group)
        new_obj.geometry_type = "box"
        new_obj.get_box_values_from_h5(h5_inner_region_box_group)
        new_obj.mark_inner_nodes(spat_mesh)
        #new_obj.select_inner_nodes_not_at_domain_edge(spat_mesh)
        return new_obj


    def check_correctness_of_box_config_fields(self, conf, inner_region_box_conf):
        # todo: check if region lies inside the domain
        pass


    def get_box_values_from_config(self, inner_region_box_conf):
        self.x_left = inner_region_box_conf.getfloat("box_x_left")
        self.x_right = inner_region_box_conf.getfloat("box_x_right")
        self.y_bottom = inner_region_box_conf.getfloat("box_y_bottom")
        self.y_top = inner_region_box_conf.getfloat("box_y_top")
        self.z_near = inner_region_box_conf.getfloat("box_z_near")
        self.z_far = inner_region_box_conf.getfloat("box_z_far")


    def get_box_values_from_h5(self, h5_inner_region_box_group):
        self.x_left = h5_inner_region_box_group.attrs["x_left"]
        self.x_right = h5_inner_region_box_group.attrs["x_right"]
        self.y_bottom = h5_inner_region_box_group.attrs["y_bottom"]
        self.y_top = h5_inner_region_box_group.attrs["y_top"]
        self.z_near = h5_inner_region_box_group.attrs["z_near"]
        self.z_far = h5_inner_region_box_group.attrs["z_far"]


    def check_if_point_inside(self, x, y, z):
        inside = (x <= self.x_left) and (x >= self.x_right)
        inside = inside and (y <= self.y_top) and (y >= self.y_bottom)
        inside = inside and (z <= self.z_far) and (z >= self.z_near)
        return inside


    def write_hdf5_region_specific_parameters(self, current_region_group):
        current_region_group.attrs.create("box_x_left", self.x_left)
        current_region_group.attrs.create("box_x_right", self.x_right)
        current_region_group.attrs.create("box_y_top", self.y_top)
        current_region_group.attrs.create("box_y_bottom", self.y_bottom)
        current_region_group.attrs.create("box_z_far", self.z_far)
        current_region_group.attrs.create("box_z_near", self.z_near)


    @classmethod
    def is_box_region(cls, conf_sec_name):
        return 'InnerRegionBox' in conf_sec_name
