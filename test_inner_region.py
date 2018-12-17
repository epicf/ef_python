from InnerRegion import InnerRegion
from Node import Node
from SpatialMesh import SpatialMesh
from ef.config.components import BoundaryConditionsConf


class TestInnerRegion:
    def test_init(self):
        ir = InnerRegion()
        assert ir.total_absorbed_particles == 0
        assert ir.total_absorbed_charge == 0
        assert ir.inner_nodes == []
        assert ir.inner_nodes_not_at_domain_edge == []

    def test_mark_inner_nodes(self):
        mesh = SpatialMesh.do_init((8, 8, 8), (2, 2, 2), BoundaryConditionsConf(0))
        ir = InnerRegion()
        ir.check_if_point_inside = lambda x, y, z: x > 5 and y == z + 2
        ir.mark_inner_nodes(mesh)
        assert set(ir.inner_nodes) == set([Node(3, 1, 0), Node(4, 1, 0), Node(3, 2, 1), Node(4, 2, 1), Node(3, 3, 2),
                                           Node(4, 3, 2), Node(3, 4, 3), Node(4, 4, 3)])
