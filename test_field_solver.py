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


def test_global_index():
    double_index = list(FieldSolver.double_index(np.array((9, 10, 6))))
    for i in range(7):
        for j in range(8):
            for k in range(4):
                n = i + j * 7 + k * 7 * 8
                assert FieldSolver.global_index_in_matrix_to_node_ijk(n, 9, 10, 6) == (i + 1, j + 1, k + 1)
                assert FieldSolver.node_ijk_to_global_index_in_matrix(i + 1, j + 1, k + 1, 9, 10, 6) == n
                assert double_index[n] == (n, i + 1, j + 1, k + 1)
    assert list(FieldSolver.double_index(np.array((4, 5, 3)))) == [(0, 1, 1, 1),
                                                                   (1, 2, 1, 1),
                                                                   (2, 1, 2, 1),
                                                                   (3, 2, 2, 1),
                                                                   (4, 1, 3, 1),
                                                                   (5, 2, 3, 1)]
