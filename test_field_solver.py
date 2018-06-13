import numpy as np
from numpy.testing import assert_array_equal, assert_allclose

from FieldSolver import FieldSolver
from InnerRegion import InnerRegion
from InnerRegionsManager import InnerRegionsManager
from ef.config.components import BoundaryConditionsConf, SpatialMeshConf
from ef.config.components import Box


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
    assert_array_equal(mesh._electric_field, expected)


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


def test_init_rhs():
    mesh = SpatialMeshConf((4, 3, 3)).make(BoundaryConditionsConf())
    solver = FieldSolver(mesh, InnerRegionsManager())
    solver.init_rhs_vector_in_full_domain(mesh)
    assert_array_equal(solver.rhs, np.zeros(3 * 2 * 2))

    mesh = SpatialMeshConf((4, 3, 3)).make(BoundaryConditionsConf(-2))
    solver = FieldSolver(mesh, InnerRegionsManager())
    solver.init_rhs_vector_in_full_domain(mesh)
    assert_array_equal(solver.rhs, [6, 4, 6, 6, 4, 6, 6, 4, 6, 6, 4, 6])  # what

    mesh = SpatialMeshConf((4, 4, 5)).make(BoundaryConditionsConf(-2))
    solver = FieldSolver(mesh, InnerRegionsManager())
    solver.init_rhs_vector_in_full_domain(mesh)
    assert_array_equal(solver.rhs, [6, 4, 6, 4, 2, 4, 6, 4, 6,
                                    4, 2, 4, 2, 0, 2, 4, 2, 4,
                                    4, 2, 4, 2, 0, 2, 4, 2, 4,
                                    6, 4, 6, 4, 2, 4, 6, 4, 6])  # what

    mesh = SpatialMeshConf((8, 12, 5), (2, 3, 1)).make(BoundaryConditionsConf(-1))
    solver = FieldSolver(mesh, InnerRegionsManager())
    solver.init_rhs_vector_in_full_domain(mesh)
    assert_array_equal(solver.rhs, [49, 40, 49, 45, 36, 45, 49, 40, 49,
                                    13, 4, 13, 9, 0, 9, 13, 4, 13,
                                    13, 4, 13, 9, 0, 9, 13, 4, 13,
                                    49, 40, 49, 45, 36, 45, 49, 40, 49])

    mesh = SpatialMeshConf((4, 6, 9), (1, 2, 3)).make(BoundaryConditionsConf())
    solver = FieldSolver(mesh, InnerRegionsManager())
    mesh.charge_density = np.array([[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                                    [[0, 0, 0, 0], [0, 1, 2, 0], [0, -1, 0, 0], [0, 0, 0, 0]],
                                    [[0, 0, 0, 0], [0, 3, 4, 0], [0, 0, -1, 0], [0, 0, 0, 0]],
                                    [[0, 0, 0, 0], [0, 5, 6, 0], [0, -1, 0, 0], [0, 0, 0, 0]],
                                    [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]])
    solver.init_rhs_vector_in_full_domain(mesh)
    assert_allclose(solver.rhs, -np.array([1, 3, 5, -1, 0, -1, 2, 4, 6, 0, -1, 0]) * np.pi * 4 * 36)

    mesh = SpatialMeshConf((4, 6, 9), (1, 2, 3)).make(BoundaryConditionsConf())
    solver = FieldSolver(mesh, InnerRegionsManager())
    region = InnerRegion('test', Box((1, 2, 3), (1, 2, 3)), 3)
    region.mark_inner_nodes(mesh)
    region.select_inner_nodes_not_at_domain_edge(mesh)
    solver.init_rhs_vector(mesh, InnerRegionsManager([region]))
    assert_array_equal(solver.rhs, [3, 3, 0, 3, 3, 0, 3, 3, 0, 3, 3, 0])
