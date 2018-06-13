import numpy as np

from FieldSolver import kronecker_delta, FieldSolver
from ef.config.components import BoundaryConditionsConf, SpatialMeshConf


def test_kronecker_delta():
    assert kronecker_delta(1, 1) == 1
    assert kronecker_delta(1, 2) == 0


def test_eval_field_from_potential():
    mesh = SpatialMeshConf((1.5, 2, 1), (0.5, 1, 1)).make(BoundaryConditionsConf())
    mesh.potential = np.stack([np.array([[0., 0, 0],
                                         [1, 2, 3],
                                         [4, 3, 2],
                                         [4, 4, 4]]), np.zeros((4, 3))], -1)
    FieldSolver.eval_fields_from_potential(mesh)
    expected = np.array([[[[-2, 0, 0], [0, 0, 0]], [[-4, 0, 0], [0, 0, 0]], [[-6, 0, 0], [0, 0, 0]]],
                         [[[-4, -1, 1], [0, 0, 1]], [[-3, -1, 2], [0, 0, 2]], [[-2, -1, 3], [0, 0, 3]]],
                         [[[-3, 1, 4], [0, 0, 4]], [[-2, 1, 3], [0, 0, 3]], [[-1, 1, 2], [0, 0, 2]]],
                         [[[0, 0, 4], [0, 0, 4]], [[-2, 0, 4], [0, 0, 4]], [[-4, 0, 4], [0, 0, 4]]]])
    np.testing.assert_array_equal(mesh._electric_field, expected)
