import sys
from InnerRegionBox import InnerRegionBox
from InnerRegionSphere import InnerRegionSphere
from InnerRegionCylinder import InnerRegionCylinder
from InnerRegionTube import InnerRegionTube
from InnerRegionConeAlongZ import InnerRegionConeAlongZ

class InnerRegionsManager():

    def __init__(self):
        self.regions = []


    @classmethod
    def init_from_config(cls, conf, spat_mesh):
        new_obj = cls()
        for sec_name in conf.sections():
            if InnerRegionBox.is_box_region(sec_name):
                new_obj.regions.append(
                    InnerRegionBox.init_from_config(conf,
                                                    conf[sec_name],
                                                    sec_name,
                                                    spat_mesh))
                InnerRegionsManager.mark_innerreg_sec_as_used(sec_name, conf)
            elif InnerRegionSphere.is_sphere_region(sec_name):
                new_obj.regions.append(
                    InnerRegionSphere.init_from_config(conf,
                                                       conf[sec_name],
                                                       sec_name,
                                                       spat_mesh))
                InnerRegionsManager.mark_innerreg_sec_as_used(sec_name, conf)
            elif InnerRegionCylinder.is_cylinder_region(sec_name):
                new_obj.regions.append(
                    InnerRegionCylinder.init_from_config(conf,
                                                         conf[sec_name],
                                                         sec_name,
                                                         spat_mesh))
                InnerRegionsManager.mark_innerreg_sec_as_used(sec_name, conf)
            elif InnerRegionTube.is_tube_region(sec_name):
                new_obj.regions.append(
                    InnerRegionTube.init_from_config(conf,
                                                     conf[sec_name],
                                                     sec_name,
                                                     spat_mesh))
                InnerRegionsManager.mark_innerreg_sec_as_used(sec_name, conf)
            elif InnerRegionConeAlongZ.is_cone_region(sec_name):
                new_obj.regions.append(
                    InnerRegionConeAlongZ.init_from_config(conf,
                                                           conf[sec_name],
                                                           sec_name,
                                                           spat_mesh))
                InnerRegionsManager.mark_innerreg_sec_as_used(sec_name, conf)
        return new_obj


    @staticmethod
    def mark_innerreg_sec_as_used(sec_name, conf):
        # For now simply mark sections as 'used' instead of removing them.
        conf[sec_name]["used"] = "True"


    @classmethod
    def init_from_h5(cls, h5_reg_group, spat_mesh):
        new_obj = cls()
        for reg_group_name in h5_reg_group.keys():
            new_obj.parse_hdf5_inner_region(h5_reg_group[reg_group_name], spat_mesh)
        return new_obj


    def parse_hdf5_inner_region(self, this_reg_h5_group, spat_mesh):
        geometry_type = this_reg_h5_group.attrs["geometry_type"]
        if geometry_type == "box":
            self.regions.append(
                InnerRegionBox.init_from_h5(this_reg_h5_group, spat_mesh))
        elif geometry_type == "sphere":
            self.regions.append(
                InnerRegionSphere.init_from_h5(this_reg_h5_group, spat_mesh))
        elif geometry_type == "cylinder":
            self.regions.append(
                InnerRegionCylinder.init_from_h5(this_reg_h5_group, spat_mesh))
        elif geometry_type == "tube":
            self.regions.append(
                InnerRegionTube.init_from_h5(this_reg_h5_group, spat_mesh))
        elif geometry_type == "cone":
            self.regions.append(
                InnerRegionConeAlongZ.init_from_h5(this_reg_h5_group, spat_mesh))
        else:
            print("In InnerRegionsManager constructor-from-h5: "
                  "Unknown inner-region type. Aborting")
            sys.exit(-1)


    def write_to_file(self, h5file):
        h5group = h5file.create_group("/InnerRegions")
        h5group.attrs.create("number_of_regions", len(self.regions))
        for reg in self.regions:
            reg.write_to_file(h5group)


    def check_if_particle_inside(self, p):
        for region in self.regions:
            if region.check_if_particle_inside(p):
                return True
        return False


    def check_if_particle_inside_and_count_charge(self, p):
        for region in self.regions:
            if region.check_if_particle_inside_and_count_charge(p):
                return True
        return False


    def print(self):
        for region in self.regions:
            region.print()


    def print_inner_nodes(self):
        for region in self.regions:
            region.print_inner_nodes()


    def print_near_boundary_nodes(self):
        for region in self.regions:
            region.print_near_boundary_nodes()
