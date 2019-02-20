import sys
from logging import warning

import numpy as np
import scipy.sparse
import scipy.sparse.linalg


class FieldSolver:
    def __init__(self, spat_mesh, inner_regions):
        if inner_regions:
            print("WARNING: field-solver: inner region support is untested")
            print("WARNING: proceed with caution")
        self._double_index = self.double_index(spat_mesh.n_nodes)
        nx, ny, nz = spat_mesh.n_nodes
        nrows = (nx - 2) * (ny - 2) * (nz - 2)
        ncols = nrows
        self.A = None
        self.construct_equation_matrix(spat_mesh, inner_regions)
        self.phi_vec = np.empty(nrows, dtype='f')
        self.rhs = np.empty_like(self.phi_vec)
        self.create_solver_and_preconditioner()

    def construct_equation_matrix(self, spat_mesh, inner_regions):
        nx, ny, nz = spat_mesh.n_nodes
        dx, dy, dz = spat_mesh.cell
        self.construct_equation_matrix_in_full_domain(nx, ny, nz, dx, dy, dz)
        self.zero_nondiag_for_nodes_inside_objects(spat_mesh, inner_regions)

    def construct_equation_matrix_in_full_domain(self, nx, ny, nz, dx, dy, dz):
        self.A = self.construct_d2dx2_in_3d(nx, ny, nz)
        self.A = self.A * (dy * dy * dz * dz)
        d2dy2 = self.construct_d2dy2_in_3d(nx, ny, nz)
        self.A = self.A + d2dy2 * (dx * dx * dz * dz)
        # d2dy2 = None
        d2dz2 = self.construct_d2dz2_in_3d(nx, ny, nz)
        self.A = self.A + d2dz2 * (dx * dx * dy * dy)

    @staticmethod
    def construct_d2dx2_in_3d(nx, ny, nz):
        n = (nx - 2) * (ny - 2) * (nz - 2)
        a = scipy.sparse.dok_matrix((n, n), np.float64)
        for n, i, j, k in FieldSolver.double_index(np.array((nx, ny, nz))):
            a[n, n] = -2
            if i < nx - 2:
                a[n, n + 1] = 1
            if i > 1:
                a[n, n - 1] = 1
        return a.tocsr()

    @staticmethod
    def construct_d2dy2_in_3d(nx, ny, nz):
        n = (nx - 2) * (ny - 2) * (nz - 2)
        a = scipy.sparse.dok_matrix((n, n), np.float64)
        for n, i, j, k in FieldSolver.double_index(np.array((nx, ny, nz))):
            a[n, n] = -2
            if j < ny - 2:
                a[n, n + nx - 2] = 1
            if j > 1:
                a[n, n - nx + 2] = 1
        return a.tocsr()

    @staticmethod
    def construct_d2dz2_in_3d(nx, ny, nz):
        offset = (nx - 2) * (ny - 2)
        n = offset * (nz - 2)
        return scipy.sparse.diags([1.0, -2.0, 1.0], [-offset, 0, offset], shape=(n, n)).tocsr()

    def zero_nondiag_for_nodes_inside_objects(self, mesh, inner_regions):
        for ir in inner_regions:
            for n, i, j, k in self._double_index:
                xyz = mesh.cell * (i, j, k)
                if ir.check_if_points_inside(xyz):
                    csr_row_start = self.A.indptr[n]
                    csr_row_end = self.A.indptr[n + 1]
                    for t in range(csr_row_start, csr_row_end):
                        if self.A.indices[t] != n:
                            self.A.data[t] = 0
                        else:
                            self.A.data[t] = 1

    def create_solver_and_preconditioner(self):
        self.maxiter = 1000
        self.tol = 1e-10
        # abstol = 0
        # verbose = true
        # monitor(rhs, iteration_limit, rtol, abstol, verbose)
        # precond(A.num_rows, A.num_rows)

    def eval_potential(self, spat_mesh, inner_regions):
        self.solve_poisson_eqn(spat_mesh, inner_regions)

    def solve_poisson_eqn(self, spat_mesh, inner_regions):
        self.init_rhs_vector(spat_mesh, inner_regions)
        # cusp::krylov::cg(A, phi_vec, rhs, monitor, precond)
        self.phi_vec, info = scipy.sparse.linalg.cg(self.A, self.rhs, self.phi_vec,
                                                    self.tol, self.maxiter)
        if info != 0:
            warning(f"scipy.sparse.linalg.cg info: {info}")
        self.transfer_solution_to_spat_mesh(spat_mesh)

    def init_rhs_vector(self, spat_mesh, inner_regions):
        self.init_rhs_vector_in_full_domain(spat_mesh)
        self.set_rhs_for_nodes_inside_objects(spat_mesh, inner_regions)

    def init_rhs_vector_in_full_domain(self, spat_mesh):
        m = spat_mesh
        rhs = -4 * np.pi * m.cell.prod() ** 2 * m.charge_density[1:-1, 1:-1, 1:-1]
        dx, dy, dz = m.cell
        rhs[0] -= dy * dy * dz * dz * m.potential[0, 1:-1, 1:-1]
        rhs[-1] -= dy * dy * dz * dz * m.potential[-1, 1:-1, 1:-1]
        rhs[:, 0] -= dx * dx * dz * dz * m.potential[1:-1, 0, 1:-1]
        rhs[:, -1] -= dx * dx * dz * dz * m.potential[1:-1, -1, 1:-1]
        rhs[:, :, 0] -= dx * dx * dy * dy * m.potential[1:-1, 1:-1, 0]
        rhs[:, :, -1] -= dx * dx * dy * dy * m.potential[1:-1, 1:-1, -1]
        self.rhs = rhs.ravel('F')

    def set_rhs_for_nodes_inside_objects(self, spat_mesh, inner_regions):
        for ir in inner_regions:
            for n, i, j, k in self._double_index:
                xyz = spat_mesh.cell * (i, j, k)
                if ir.check_if_points_inside(xyz):
                    self.rhs[n] = ir.potential  # where is dx**2 dy**2 etc?

    @staticmethod
    def node_ijk_to_global_index_in_matrix(i, j, k, nx, ny, nz):
        # numbering of nodes corresponds to axis direction
        # i.e. numbering starts from bottom-left-near corner
        #   then along X axis to the right
        #   then along Y axis to the top
        #   then along Z axis far
        if ((i <= 0) or (i >= nx - 1) or \
                (j <= 0) or (j >= ny - 1) or \
                (k <= 0) or (k >= nz - 1)):
            print("incorrect index at node_ijk_to_global_index_in_matrix: " + \
                  "i  = {:d}, j  = {:d},  k  = {:d} \n".format(i, j, k) + \
                  "nx = {:d}, ny = {:d},  nz = {:d} \n".format(nx, ny, nz))
            print("this is not supposed to happen; aborting \n")
            sys.exit(-1)
        else:
            return (i - 1) + (j - 1) * (nx - 2) + (k - 1) * (nx - 2) * (ny - 2)

    @staticmethod
    def global_index_in_matrix_to_node_ijk(global_index, nx, ny, nz):
        # global_index = (i - 1) +
        #                (j - 1) * (nx - 2) +
        #                (k - 1) * (nx - 2) * (ny - 2)
        k = global_index // ((nx - 2) * (ny - 2)) + 1
        i_and_j_part = global_index % ((nx - 2) * (ny - 2))
        j = i_and_j_part // (nx - 2) + 1
        i = i_and_j_part % (nx - 2) + 1
        # todo: remove test
        # if(node_ijk_to_global_index_in_matrix(i, j, k, nx, ny, nz) != global_index){
        # 	printf("mistake in global_index_in_matrix_to_node_ijk; aborting");
        # 	exit(EXIT_FAILURE);
        # }
        return (i, j, k)

    def transfer_solution_to_spat_mesh(self, spat_mesh):
        nx, ny, nz = spat_mesh.n_nodes
        nrow = (nx - 2) * (ny - 2) * (nz - 2)
        ncol = nrow
        for global_index in range(nrow):
            i, j, k = self.global_index_in_matrix_to_node_ijk(global_index, nx, ny, nz)
            spat_mesh.potential[i][j][k] = self.phi_vec[global_index]

    @staticmethod
    def eval_fields_from_potential(spat_mesh):
        e = -np.stack(np.gradient(spat_mesh.potential, *spat_mesh.cell), -1)
        spat_mesh.electric_field = e

    @staticmethod
    def double_index(n_nodes):
        nx, ny, nz = n_nodes - 2
        return [(i + j * nx + k * nx * ny, i + 1, j + 1, k + 1)
                for k in range(nz) for j in range(ny) for i in range(nx)]

    def clear(self):
        pass
        # todo: deallocate
        # phi_vec;
        # rhs;
        # A;
        # precond;
        # monitor;
