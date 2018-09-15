from math import sqrt, copysign
import numpy as np

from Vec3d import Vec3d
from ParticleSource import ParticleSource

# Cylinder source

class ParticleSourceCylinder(ParticleSource):

    def __init__(self):
        super().__init__()
        self.axis_start_x = None
        self.axis_start_y = None
        self.axis_start_z = None
        self.axis_end_x = None
        self.axis_end_y = None
        self.axis_end_z = None
        self.radius = None


    @classmethod
    def init_from_config(cls, conf, this_source_config_part, sec_name):
        new_obj = cls()
        new_obj.read_particles_and_source_pars_from_config(
            conf, this_source_config_part, sec_name)
        new_obj.geometry_type = "cylinder"
        new_obj.check_correctness_of_cylinder_config_fields(
            conf, this_source_config_part)
        new_obj.set_cylinder_parameters_from_config(this_source_config_part)
        new_obj.generate_initial_particles()
        return new_obj


    @classmethod
    def init_from_h5(cls, h5group):
        new_obj = cls()
        new_obj.read_particles_and_source_pars_from_h5(h5group)
        new_obj.geometry_type = "cylinder"
        new_obj.read_hdf5_cylinder_parameters(h5group)
        return new_obj


    def check_correctness_of_cylinder_config_fields(self, conf, this_source_config_part):
        # todo:
        self.radius_gt_zero(conf, this_source_config_part)
        self.axis_start_x_min_rad_ge_zero(conf, this_source_config_part)
        self.axis_start_x_plus_rad_le_grid_x_size(conf, this_source_config_part)
        self.axis_start_y_min_rad_ge_zero(conf, this_source_config_part)
        self.axis_start_y_plus_rad_le_grid_y_size(conf, this_source_config_part)
        self.axis_start_z_min_rad_ge_zero(conf, this_source_config_part)
        self.axis_start_z_plus_rad_le_grid_z_size(conf, this_source_config_part)
        self.axis_end_x_min_rad_ge_zero(conf, this_source_config_part)
        self.axis_end_x_plus_rad_le_grid_x_size(conf, this_source_config_part)
        self.axis_end_y_min_rad_ge_zero(conf, this_source_config_part)
        self.axis_end_y_plus_rad_le_grid_y_size(conf, this_source_config_part)
        self.axis_end_z_min_rad_ge_zero(conf, this_source_config_part)
        self.axis_end_z_plus_rad_le_grid_z_size(conf, this_source_config_part)


    def set_cylinder_parameters_from_config(self, this_source_config_part):
        self.axis_start_x = this_source_config_part.getfloat("cylinder_axis_start_x")
        self.axis_start_y = this_source_config_part.getfloat("cylinder_axis_start_y")
        self.axis_start_z = this_source_config_part.getfloat("cylinder_axis_start_z")
        self.axis_end_x = this_source_config_part.getfloat("cylinder_axis_end_x")
        self.axis_end_y = this_source_config_part.getfloat("cylinder_axis_end_y")
        self.axis_end_z = this_source_config_part.getfloat("cylinder_axis_end_z")
        self.radius = this_source_config_part.getfloat("cylinder_radius")


    def read_hdf5_cylinder_parameters(self, this_source_h5_group):        
        self.axis_start_x = this_source_h5_group.attrs["cylinder_axis_start_x"]
        self.axis_start_y = this_source_h5_group.attrs["cylinder_axis_start_y"]
        self.axis_start_z = this_source_h5_group.attrs["cylinder_axis_start_z"]
        self.axis_end_x = this_source_h5_group.attrs["cylinder_axis_end_x"]
        self.axis_end_y = this_source_h5_group.attrs["cylinder_axis_end_y"]
        self.axis_end_z = this_source_h5_group.attrs["cylinder_axis_end_z"]
        self.radius = this_source_h5_group.attrs["cylinder_radius"]


    def radius_gt_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("radius < 0")


    def axis_start_x_min_rad_ge_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_start_x") - \
           this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("cylinder_axis_start_x - cylinder_radius < 0")


    def axis_start_x_plus_rad_le_grid_x_size(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_start_x") + \
           this_source_config_part.getfloat("cylinder_radius") > \
           conf["SpatialMesh"].getfloat("grid_x_size"):
            raise ValueError("cylinder_axis_start_x + cylinder_radius > grid_x_size")


    def axis_start_y_min_rad_ge_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_start_y") - \
           this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("cylinder_axis_start_y - cylinder_radius < 0")


    def axis_start_y_plus_rad_le_grid_y_size(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_start_y") + \
           this_source_config_part.getfloat("cylinder_radius") > \
           conf["SpatialMesh"].getfloat("grid_y_size"):
            raise ValueError("cylinder_axis_start_y + cylinder_radius > grid_y_size")


    def axis_start_z_min_rad_ge_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_start_z") - \
           this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("cylinder_axis_start_z - cylinder_radius < 0")


    def axis_start_z_plus_rad_le_grid_z_size(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_start_z") + \
           this_source_config_part.getfloat("cylinder_radius") > \
           conf["SpatialMesh"].getfloat("grid_z_size"):
            raise ValueError("cylinder_axis_start_z + cylinder_radius > grid_z_size")


    def axis_end_x_min_rad_ge_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_end_x") - \
           this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("cylinder_axis_end_x - cylinder_radius < 0")


    def axis_end_x_plus_rad_le_grid_x_size(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_end_x") + \
           this_source_config_part.getfloat("cylinder_radius") >\
           conf["SpatialMesh"].getfloat("grid_x_size"):
            raise ValueError("cylinder_axis_end_x + cylinder_radius > grid_x_size")


    def axis_end_y_min_rad_ge_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_end_y") - \
           this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("cylinder_axis_end_y - cylinder_radius < 0")


    def axis_end_y_plus_rad_le_grid_y_size(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_end_y") + \
           this_source_config_part.getfloat("cylinder_radius") > \
           conf["SpatialMesh"].getfloat("grid_y_size"):
            raise ValueError("cylinder_axis_end_y + cylinder_radius > grid_y_size")


    def axis_end_z_min_rad_ge_zero(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_end_z") - \
           this_source_config_part.getfloat("cylinder_radius") < 0:
            raise ValueError("cylinder_axis_end_z - cylinder_radius < 0")


    def axis_end_z_plus_rad_le_grid_z_size(self, conf, this_source_config_part):
        if this_source_config_part.getfloat("cylinder_axis_end_z") + \
           this_source_config_part.getfloat("cylinder_radius") > \
           conf["SpatialMesh"].getfloat("grid_z_size"):
            raise ValueError("cylinder_axis_end_z + cylinder_radius > grid_z_size")


    def write_hdf5_source_parameters(self, this_source_h5_group):
        super().write_hdf5_source_parameters(this_source_h5_group)
        this_source_h5_group.attrs.create("cylinder_axis_start_x", self.axis_start_x)
        this_source_h5_group.attrs.create("cylinder_axis_start_y", self.axis_start_y)
        this_source_h5_group.attrs.create("cylinder_axis_start_z", self.axis_start_z)
        this_source_h5_group.attrs.create("cylinder_axis_end_x", self.axis_end_x)
        this_source_h5_group.attrs.create("cylinder_axis_end_y", self.axis_end_y)
        this_source_h5_group.attrs.create("cylinder_axis_end_z", self.axis_end_z)
        this_source_h5_group.attrs.create("cylinder_radius", self.radius)


    def uniform_position_in_source(self):
        return self.uniform_position_in_cylinder()


    def uniform_position_in_cylinder(self):
        # random point in cylinder along z
        cyl_axis = Vec3d((self.axis_end_x - self.axis_start_x),
                         (self.axis_end_y - self.axis_start_y),
                         (self.axis_end_z - self.axis_start_z))
        cyl_axis_length = cyl_axis.length()
        r = sqrt(self.random_in_range(0.0, 1.0)) * self.radius
        phi = self.random_in_range(0.0, 2.0 * np.pi)
        z = self.random_in_range(0.0, cyl_axis_length)
        #
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        z = z
        random_pnt_in_cyl_along_z = Vec3d(x, y, z)
        # rotate:
        # see "https://en.wikipedia.org/wiki/Rodrigues'_rotation_formula"
        # todo: Too complicated. Try rejection sampling.
        unit_cyl_axis = cyl_axis.normalized()
        unit_along_z = Vec3d(0, 0, 1.0)
        rotation_axis = unit_along_z.cross_product(unit_cyl_axis)
        rotation_axis_length = rotation_axis.length()
        if rotation_axis_length == 0:
            if copysign(1.0, unit_cyl_axis.z) >= 0:
                random_pnt_in_rotated_cyl = random_pnt_in_cyl_along_z
            else:
                random_pnt_in_rotated_cyl = random_pnt_in_cyl_along_z.negate()
        else:
            unit_rotation_axis = rotation_axis.normalized()
            rot_cos = unit_cyl_axis.dot_product(unit_along_z)
            rot_sin = rotation_axis_length
            random_pnt_in_rotated_cyl = \
                random_pnt_in_cyl_along_z.times_scalar(rot_cos) + \
                unit_rotation_axis.cross_product(random_pnt_in_cyl_along_z) * rot_sin + \
                unit_rotation_axis.times_scalar(\
                    (1 - rot_cos) * \
                    unit_rotation_axis.dot_product(random_pnt_in_cyl_along_z))
        # shift:
        shifted = random_pnt_in_rotated_cyl.add(
            Vec3d(self.axis_start_x,
                  self.axis_start_y,
                  self.axis_start_z))
        return shifted


    @classmethod
    def is_cylinder_source(cls, conf_sec_name):
        return 'ParticleSourceCylinder' in conf_sec_name
