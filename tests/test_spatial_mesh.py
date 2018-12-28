import logging

import h5py
import numpy as np
import pytest
from numpy.testing import assert_array_equal

from ef.particle_array import ParticleArray
from ef.spatial_mesh import SpatialMesh, MeshGrid
from ef.config.components import SpatialMeshConf, BoundaryConditionsConf, ParticleSourceConf


class TestDefaultSpatialMesh:
    def test_config(self, capsys):
        mesh = SpatialMeshConf((4, 2, 3), (2, 1, 3)).make(BoundaryConditionsConf(3.14))
        assert mesh.mesh.node_coordinates.shape == (3, 3, 2, 3)
        assert mesh.charge_density.shape == (3, 3, 2)
        assert mesh.potential.shape == (3, 3, 2)
        assert mesh.electric_field.shape == (3, 3, 2, 3)
        coords = np.array([[[[0., 0., 0.], [0., 0., 3.]], [[0., 1., 0.], [0., 1., 3.]],
                            [[0., 2., 0.], [0., 2., 3.]]],
                           [[[2., 0., 0.], [2., 0., 3.]], [[2., 1., 0.], [2., 1., 3.]],
                            [[2., 2., 0.], [2., 2., 3.]]],
                           [[[4., 0., 0.], [4., 0., 3.]], [[4., 1., 0.], [4., 1., 3.]],
                            [[4., 2., 0.], [4., 2., 3.]]]])
        assert_array_equal(mesh.mesh.node_coordinates, coords)
        assert_array_equal(mesh.charge_density, np.zeros((3, 3, 2)))
        potential = np.full((3, 3, 2), 3.14)
        assert_array_equal(mesh.potential, potential)
        assert_array_equal(mesh.electric_field, np.zeros((3, 3, 2, 3)))
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

    def test_do_init_warnings(self, capsys, caplog):
        mesh = SpatialMesh.do_init((12, 12, 12), (5, 5, 7), BoundaryConditionsConf(0))
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""
        assert caplog.record_tuples == [
            ('root', logging.WARNING,
             "X step on spatial grid was reduced to 4.000 from 5.000 to fit in a round number of cells."),
            ('root', logging.WARNING,
             "Y step on spatial grid was reduced to 4.000 from 5.000 to fit in a round number of cells."),
            ('root', logging.WARNING,
             "Z step on spatial grid was reduced to 6.000 from 7.000 to fit in a round number of cells."),
        ]

    def test_do_init(self):
        mesh = SpatialMesh.do_init((4, 2, 3), (2, 1, 3), BoundaryConditionsConf(3.14))
        assert mesh.mesh.node_coordinates.shape == (3, 3, 2, 3)
        assert mesh.charge_density.shape == (3, 3, 2)
        assert mesh.potential.shape == (3, 3, 2)
        assert mesh.electric_field.shape == (3, 3, 2, 3)
        coords = np.array([[[[0., 0., 0.], [0., 0., 3.]], [[0., 1., 0.], [0., 1., 3.]],
                            [[0., 2., 0.], [0., 2., 3.]]],
                           [[[2., 0., 0.], [2., 0., 3.]], [[2., 1., 0.], [2., 1., 3.]],
                            [[2., 2., 0.], [2., 2., 3.]]],
                           [[[4., 0., 0.], [4., 0., 3.]], [[4., 1., 0.], [4., 1., 3.]],
                            [[4., 2., 0.], [4., 2., 3.]]]])
        assert_array_equal(mesh.mesh.node_coordinates, coords)
        assert_array_equal(mesh.charge_density, np.zeros((3, 3, 2)))
        potential = np.full((3, 3, 2), 3.14)
        assert_array_equal(mesh.potential, potential)
        assert_array_equal(mesh.electric_field, np.zeros((3, 3, 2, 3)))

    def test_do_init_potential(self):
        mesh = SpatialMesh.do_init((12, 12, 12), (4, 4, 6),
                                   BoundaryConditionsConf(1, 2, 3, 4, 5, 6))
        potential = np.array([[[5., 1., 6.], [5., 1., 6.], [5., 1., 6.], [5., 1., 6.]],
                              [[5., 3., 6.], [5., 0., 6.], [5., 0., 6.], [5., 4., 6.]],
                              [[5., 3., 6.], [5., 0., 6.], [5., 0., 6.], [5., 4., 6.]],
                              [[5., 2., 6.], [5., 2., 6.], [5., 2., 6.], [5., 2., 6.]]])
        assert_array_equal(mesh.potential, potential)

    def test_is_potential_equal_on_boundaries(self):
        for x, y, z in np.ndindex(4, 4, 3):
            mesh = SpatialMesh.do_init((12, 12, 12), (4, 4, 6), BoundaryConditionsConf(3.14))
            assert mesh.is_potential_equal_on_boundaries()
            mesh.potential[x, y, z] = 2.
            if np.all([x > 0, y > 0, z > 0]) and np.all([x < 3, y < 3, z < 2]):
                assert mesh.is_potential_equal_on_boundaries()
            else:
                assert not mesh.is_potential_equal_on_boundaries()

    def test_do_init_ranges(self):
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 20), (2, 1, 3), BoundaryConditionsConf(3.14))
        assert excinfo.value.args == ('grid_size must be a flat triple', (10, 20))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init(((1, 2), 3), (1, 1, 1), BoundaryConditionsConf(3.14))
        assert excinfo.value.args == ('grid_size must be a flat triple', ((1, 2), 3))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, 10), [[2, 1, 3], [4, 5, 6], [7, 8, 9]],
                                BoundaryConditionsConf(3.14))
        assert excinfo.value.args == ('step_size must be a flat triple', [[2, 1, 3], [4, 5, 6], [7, 8, 9]],)

        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, -30), (2, 1, 3), BoundaryConditionsConf(3.14))
        assert excinfo.value.args == ('grid_size must be positive', (10, 10, -30))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, 10), (2, -2, 3), BoundaryConditionsConf(3.14))
        assert excinfo.value.args == ('step_size must be positive', (2, -2, 3))
        with pytest.raises(ValueError) as excinfo:
            SpatialMesh.do_init((10, 10, 10), (17, 2, 3), BoundaryConditionsConf(3.14))
        assert excinfo.value.args == ('step_size cannot be bigger than grid_size',)

    def test_init_h5(self, tmpdir):
        fname = tmpdir.join('test_spatialmesh_init.h5')

        mesh1 = SpatialMesh.do_init((10, 20, 30), (2, 1, 3), BoundaryConditionsConf(3.14))
        with h5py.File(fname, mode="w") as h5file:
            mesh1.save_h5(h5file.create_group("/mesh"))
        with h5py.File(fname, mode="r") as h5file:
            mesh2 = SpatialMesh.load_h5(h5file["/mesh"])
        assert mesh1 == mesh2

        mesh2 = SpatialMesh.do_init((10, 20, 30), (2, 1, 3), BoundaryConditionsConf(3.14))
        assert mesh1 == mesh2
        mesh2.potential = np.random.ranf(mesh1.potential.shape)
        assert mesh1 != mesh2

        mesh2 = SpatialMesh.do_init((10, 20, 30), (2, 1, 3), BoundaryConditionsConf(3.14))
        assert mesh1 == mesh2
        mesh2.charge_density = np.random.ranf(mesh1.charge_density.shape)
        assert mesh1 != mesh2

        mesh2 = SpatialMesh.do_init((10, 20, 30), (2, 1, 3), BoundaryConditionsConf(3.14))
        assert mesh1 == mesh2
        mesh2.electric_field = np.random.ranf(mesh1.electric_field.shape)
        assert mesh1 != mesh2

        mesh2 = SpatialMesh.do_init((10, 20, 30), (2, 1, 3), BoundaryConditionsConf(3.14))
        mesh2.potential = np.random.ranf(mesh1.potential.shape)
        mesh2.charge_density = np.random.ranf(mesh1.charge_density.shape)
        mesh2.electric_field = np.random.ranf(mesh1.electric_field.shape)
        assert mesh1 != mesh2

        with h5py.File(fname, mode="w") as h5file:
            mesh2.save_h5(h5file.create_group("/SpatialMesh"))
        with h5py.File(fname, mode="r") as h5file:
            mesh1 = SpatialMesh.load_h5(h5file["/SpatialMesh"])
        assert mesh1 == mesh2

    def test_dict(self):
        mesh = SpatialMesh.do_init((4, 2, 3), (2, 1, 3), BoundaryConditionsConf())
        d = mesh.dict
        assert d.keys() == {"mesh", "electric_field", "potential", "charge_density"}
        assert d["mesh"] == MeshGrid((4, 2, 3), (3, 3, 2))
        assert_array_equal(d["electric_field"], np.zeros((3, 3, 2, 3)))
        assert_array_equal(d["potential"], np.zeros((3, 3, 2)))
        assert_array_equal(d["charge_density"], np.zeros((3, 3, 2)))

    def test_weight_particles_charge_to_mesh(self):
        mesh = SpatialMeshConf((2, 4, 8), (1, 2, 4)).make(BoundaryConditionsConf())
        sources = [ParticleSourceConf().make()]
        sources[0].particle_arrays = [ParticleArray(1, -2, 4, [(1, 1, 3)], [(0, 0, 0)])]
        mesh.weight_particles_charge_to_mesh(sources)
        assert_array_equal(mesh.charge_density,
                           np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                     [[-0.25 / 8, -0.75 / 8, 0], [-0.25 / 8, -0.75 / 8, 0], [0, 0, 0]],
                                     [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]))
        sources[0].particle_arrays = [ParticleArray([1, 2], -2, 4, [(1, 1, 3), (1, 1, 3)], np.zeros((2, 3)))]
        mesh.clear_old_density_values()
        mesh.weight_particles_charge_to_mesh(sources)
        assert_array_equal(mesh.charge_density,
                           np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                     [[-0.25 / 4, -0.75 / 4, 0], [-0.25 / 4, -0.75 / 4, 0], [0, 0, 0]],
                                     [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]))
        mesh.clear_old_density_values()
        sources[0].particle_arrays = [ParticleArray(1, -2, 4, [(2, 4, 8)], [(0, 0, 0)])]
        mesh.weight_particles_charge_to_mesh(sources)
        assert_array_equal(mesh.charge_density,
                           np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                     [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                                     [[0, 0, 0], [0, 0, 0], [0, 0, -0.25]]]))
        sources[0].particle_arrays = [ParticleArray(1, -2, 4, [(1, 2, 8.1)], [(0, 0, 0)])]
        with pytest.raises(ValueError, message="Particle out of bounds"):
            mesh.weight_particles_charge_to_mesh(sources)

    def test_field_at_position(self):
        mesh = SpatialMeshConf((2, 4, 8), (1, 2, 4)).make(BoundaryConditionsConf())
        mesh.electric_field[1:2, 0:2, 0:2] = np.array([[[2, 1, 0], [-3, 1, 0]],
                                                       [[0, -1, 0], [-1, 0, 0]]])
        assert_array_equal(mesh.field_at_position([(1, 1, 3)]), [(-1.25, 0.375, 0)])
