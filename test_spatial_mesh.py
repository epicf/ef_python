import logging
import numpy as np
import pytest
from configparser import ConfigParser
from numpy.testing import assert_array_equal

from SpatialMesh import SpatialMesh
from Vec3d import Vec3d
from ef.config.components import spatial_mesh, boundary_conditions


class TestDefaultSpatialMesh:
    def test_print(self, capsys):
        mesh = SpatialMesh.do_init((10, 20, 30), (2, 1, 3), boundary_conditions.BoundaryConditions(3.14))
        mesh.print()
        assert capsys.readouterr().out == ("Grid:\n"
                                           "Length: x = 10.000, y = 20.000, z = 30.000\n"
                                           "Cell size: x = 2.000, y = 1.000, z = 3.000\n"
                                           "Total nodes: x = 6, y = 21, z = 11\n"
                                           "x_node   y_node   z_node | charge_density | potential | electric_field(x,y,z)\n")
        assert capsys.readouterr().err == ""

    def test_init(self, capsys):
        parser = ConfigParser()
        spatial_mesh.SpatialMesh((4, 2, 3), (2, 1, 3)).to_conf().add_section_to_parser(parser)
        boundary_conditions.BoundaryConditions(3.14).to_conf().add_section_to_parser(parser)
        mesh = SpatialMesh.init_from_config(parser)
        assert mesh.x_volume_size == 4.
        assert mesh.y_volume_size == 2.
        assert mesh.z_volume_size == 3.
        assert mesh.x_n_nodes == 3
        assert mesh.y_n_nodes == 3
        assert mesh.z_n_nodes == 2
        assert mesh.x_cell_size == 2.
        assert mesh.y_cell_size == 1.
        assert mesh.z_cell_size == 3.
        assert mesh.node_coordinates.shape == (3, 3, 2)
        assert mesh.charge_density.shape == (3, 3, 2)
        assert mesh.potential.shape == (3, 3, 2)
        assert mesh.electric_field.shape == (3, 3, 2)
        coords = np.array([[[Vec3d(0., 0., 0.), Vec3d(0., 0., 3.)], [Vec3d(0., 1., 0.), Vec3d(0., 1., 3.)],
                            [Vec3d(0., 2., 0.), Vec3d(0., 2., 3.)]],
                           [[Vec3d(2., 0., 0.), Vec3d(2., 0., 3.)], [Vec3d(2., 1., 0.), Vec3d(2., 1., 3.)],
                            [Vec3d(2., 2., 0.), Vec3d(2., 2., 3.)]],
                           [[Vec3d(4., 0., 0.), Vec3d(4., 0., 3.)], [Vec3d(4., 1., 0.), Vec3d(4., 1., 3.)],
                            [Vec3d(4., 2., 0.), Vec3d(4., 2., 3.)]]])
        assert_array_equal(mesh.node_coordinates, coords)
        assert_array_equal(mesh.charge_density, np.zeros((3, 3, 2)))
        potential = np.full((3, 3, 2), 3.14)
        assert_array_equal(mesh.potential, potential)
        assert_array_equal(mesh.electric_field, np.full((3, 3, 2), Vec3d.zero()))
        assert capsys.readouterr().out == ""
        assert capsys.readouterr().err == ""

    def test_do_init_warnings(self, capsys, caplog):
        mesh = SpatialMesh.do_init((12, 12, 12), (5, 5, 7), boundary_conditions.BoundaryConditions(0))
        assert capsys.readouterr().out == ""
        assert capsys.readouterr().err == ""
        assert caplog.record_tuples == [
            ('root', logging.WARNING,
             "X step on spatial grid was reduced to 4.000 from 5.000 to fit in a round number of cells."),
            ('root', logging.WARNING,
             "Y step on spatial grid was reduced to 4.000 from 5.000 to fit in a round number of cells."),
            ('root', logging.WARNING,
             "Z step on spatial grid was reduced to 6.000 from 7.000 to fit in a round number of cells."),
        ]

    def test_do_init(self):
        mesh = SpatialMesh.do_init((4, 2, 3), (2, 1, 3), boundary_conditions.BoundaryConditions(3.14))
        assert mesh.x_volume_size == 4.
        assert mesh.y_volume_size == 2.
        assert mesh.z_volume_size == 3.
        assert mesh.x_n_nodes == 3
        assert mesh.y_n_nodes == 3
        assert mesh.z_n_nodes == 2
        assert mesh.x_cell_size == 2.
        assert mesh.y_cell_size == 1.
        assert mesh.z_cell_size == 3.
        assert mesh.node_coordinates.shape == (3, 3, 2)
        assert mesh.charge_density.shape == (3, 3, 2)
        assert mesh.potential.shape == (3, 3, 2)
        assert mesh.electric_field.shape == (3, 3, 2)
        coords = np.array([[[Vec3d(0., 0., 0.), Vec3d(0., 0., 3.)], [Vec3d(0., 1., 0.), Vec3d(0., 1., 3.)],
                            [Vec3d(0., 2., 0.), Vec3d(0., 2., 3.)]],
                           [[Vec3d(2., 0., 0.), Vec3d(2., 0., 3.)], [Vec3d(2., 1., 0.), Vec3d(2., 1., 3.)],
                            [Vec3d(2., 2., 0.), Vec3d(2., 2., 3.)]],
                           [[Vec3d(4., 0., 0.), Vec3d(4., 0., 3.)], [Vec3d(4., 1., 0.), Vec3d(4., 1., 3.)],
                            [Vec3d(4., 2., 0.), Vec3d(4., 2., 3.)]]])
        assert_array_equal(mesh.node_coordinates, coords)
        assert_array_equal(mesh.charge_density, np.zeros((3, 3, 2)))
        potential = np.full((3, 3, 2), 3.14)
        assert_array_equal(mesh.potential, potential)
        assert_array_equal(mesh.electric_field, np.full((3, 3, 2), Vec3d.zero()))

    def test_do_init_potential(self):
        mesh = SpatialMesh.do_init((12, 12, 12), (4, 4, 6),
                                   boundary_conditions.BoundaryConditions(1, 2, 3, 4, 5, 6))
        potential = np.array([[[5., 1., 6.], [5., 1., 6.], [5., 1., 6.], [5., 1., 6.]],
                              [[5., 3., 6.], [5., 0., 6.], [5., 0., 6.], [5., 4., 6.]],
                              [[5., 3., 6.], [5., 0., 6.], [5., 0., 6.], [5., 4., 6.]],
                              [[5., 2., 6.], [5., 2., 6.], [5., 2., 6.], [5., 2., 6.]]])
        assert_array_equal(mesh.potential, potential)

    def test_do_init_ranges(self):
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 20), (2, 1, 3), boundary_conditions.BoundaryConditions(3.14))
        assert excinfo.value.args == ('grid_size must be a flat triple', (10, 20))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init(((1, 2), 3), (1, 1, 1), boundary_conditions.BoundaryConditions(3.14))
        assert excinfo.value.args == ('grid_size must be a flat triple', ((1, 2), 3))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, 10), [[2, 1, 3], [4, 5, 6], [7, 8, 9]],
                                boundary_conditions.BoundaryConditions(3.14))
        assert excinfo.value.args == ('step_size must be a flat triple', [[2, 1, 3], [4, 5, 6], [7, 8, 9]],)

        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, -30), (2, 1, 3), boundary_conditions.BoundaryConditions(3.14))
        assert excinfo.value.args == ('grid_size must be positive', (10, 10, -30))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, 10), (2, -2, 3), boundary_conditions.BoundaryConditions(3.14))
        assert excinfo.value.args == ('step_size must be positive', (2, -2, 3))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, 10), (17, 2, 3), boundary_conditions.BoundaryConditions(3.14))
        assert excinfo.value.args == ('step_size cannot be bigger than grid_size',)
