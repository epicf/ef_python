import sys

import numpy as np
import scipy.sparse
import scipy.sparse.linalg

from Vec3d import Vec3d

class FieldSolver:

    def __init__(self, spat_mesh, inner_regions):
        if inner_regions.regions:
            print("WARNING: field-solver: inner region support is untested")
            print("WARNING: proceed with caution")
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        nrows = (nx-2) * (ny-2) * (nz-2)
        ncols = nrows
        self.A = None
        self.construct_equation_matrix(spat_mesh, inner_regions)
        self.phi_vec = np.empty(nrows, dtype='f')
        self.rhs = np.empty_like(self.phi_vec)
        self.create_solver_and_preconditioner()


    def construct_equation_matrix(self, spat_mesh, inner_regions):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        dx = spat_mesh.x_cell_size
        dy = spat_mesh.y_cell_size
        dz = spat_mesh.z_cell_size
        self.construct_equation_matrix_in_full_domain(nx, ny, nz, dx, dy, dz)
        self.zero_nondiag_for_nodes_inside_objects(nx, ny, nz, inner_regions)


    def construct_equation_matrix_in_full_domain(self, nx, ny, nz, dx, dy, dz):
        self.A = self.construct_d2dx2_in_3d(nx, ny, nz)
        self.A = self.A * (dy * dy * dz * dz)
        d2dy2 = self.construct_d2dy2_in_3d(nx, ny, nz)
        self.A = self.A + d2dy2 * (dx * dx * dz * dz)
        #d2dy2 = None
        d2dz2 = self.construct_d2dz2_in_3d(nx, ny, nz)
        self.A = self.A + d2dz2 * (dx * dx * dy * dy)
        #d2dz2 = None
        self.A = self.A.tocsr()


    def construct_d2dx2_in_3d(self, nx, ny, nz):
        nrow = (nx - 2) * (ny - 2) * (nz - 2)
        ncol = nrow
        cols = []
        rows = []
        vals = []
        #
        for row_idx in range(nrow):
            i, j, k = self.global_index_in_matrix_to_node_ijk(row_idx, nx, ny, nz)
            if i == 1:
                # left boundary
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
                rows.append(row_idx)
                cols.append(row_idx + 1)
                vals.append(1.0)
            elif i == nx - 2:
                # right boundary
                rows.append(row_idx)
                cols.append(row_idx - 1)
                vals.append(1.0)
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
            else:
                # center
                rows.append(row_idx)
                cols.append(row_idx - 1)
                vals.append(1.0)
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
                rows.append(row_idx)
                cols.append(row_idx + 1)
                vals.append(1.0)
            #printf("d2dx2 loop: i = %d \n", i);
        d2dx2 = scipy.sparse.coo_matrix((vals, (rows, cols)))
        return d2dx2


    def construct_d2dy2_in_3d(self, nx, ny, nz):
        nrow = (nx - 2) * (ny - 2) * (nz - 2)
        ncol = nrow
        cols = []
        rows = []
        vals = []
        #
        for row_idx in range(nrow):
            i, j, k = self.global_index_in_matrix_to_node_ijk(row_idx, nx, ny, nz)
            if j == 1:
                # bottom boundary
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
                rows.append(row_idx)
                cols.append(row_idx + (nx - 2))
                vals.append(1.0)
            elif j == ny - 2:
                # top boundary
                rows.append(row_idx)
                cols.append(row_idx - (nx - 2))
                vals.append(1.0)
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
            else:
                # center
                rows.append(row_idx)
                cols.append(row_idx - (nx - 2))
                vals.append(1.0)
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
                rows.append(row_idx)
                cols.append(row_idx + (nx - 2))
                vals.append(1.0)
            #printf("d2dy2 loop: i = %d \n", i);
        d2dy2 = scipy.sparse.coo_matrix((vals, (rows, cols)))
        return d2dy2


    def construct_d2dz2_in_3d(self, nx, ny, nz):
        nrow = (nx - 2) * (ny - 2) * (nz - 2)
        ncol = nrow
        cols = []
        rows = []
        vals = []
        #
        for row_idx in range(nrow):
            #i, j, k = global_index_in_matrix_to_node_ijk(row_idx, nx, ny, nz)
            if row_idx < (nx - 2) * (ny - 2):
                # near boundary
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
                rows.append(row_idx)
                cols.append(row_idx + (nx - 2) * (ny - 2))
                vals.append(1.0)
            elif row_idx >= (nx - 2) * (ny - 2) * (nz - 3):
                # far boundary
                rows.append(row_idx)
                cols.append(row_idx - (nx - 2) * (ny - 2))
                vals.append(1.0)
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
            else:
                # center
                rows.append(row_idx)
                cols.append(row_idx - (nx - 2) * (ny - 2))
                vals.append(1.0)
                rows.append(row_idx)
                cols.append(row_idx)
                vals.append(-2.0)
                rows.append(row_idx)
                cols.append(row_idx + (nx - 2) * (ny - 2))
                vals.append(1.0)
            #printf("d2dz2 loop: i = %d \n", i);
        d2dz2 = scipy.sparse.coo_matrix((vals, (rows, cols)))
        return d2dz2


    def zero_nondiag_for_nodes_inside_objects(self, nx, ny, nz, inner_regions):
        for ir in inner_regions.regions:
            for node in ir.inner_nodes_not_at_domain_edge:
                row_idx = self.node_ijk_to_global_index_in_matrix(
                    node.x, node.y, node.z, nx, ny, nz)
                csr_row_start = self.A.indptr[row_idx]
                csr_row_end = self.A.indptr[row_idx + 1]
                for j in range(csr_row_start, csr_row_end):
                    if self.A.indices[j] != row_idx:
                        self.A.data[j] = 0
                    else:
                        self.A.data[j] = 1


    def create_solver_and_preconditioner(self):
        self.maxiter = 1000
        self.tol = 1e-10
        #abstol = 0
        #verbose = true
        #monitor(rhs, iteration_limit, rtol, abstol, verbose)
        #precond(A.num_rows, A.num_rows)


    def eval_potential(self, spat_mesh, inner_regions):
        self.solve_poisson_eqn(spat_mesh, inner_regions)


    def solve_poisson_eqn(self, spat_mesh, inner_regions):
        self.init_rhs_vector(spat_mesh, inner_regions)
        #cusp::krylov::cg(A, phi_vec, rhs, monitor, precond)
        self.phi_vec, info = scipy.sparse.linalg.cg(self.A, self.rhs, self.phi_vec,
                                                    self.tol, self.maxiter)
        if info != 0:
            print("warning: scipy.sparse.linalg.cg info: ", info)
        self.transfer_solution_to_spat_mesh(spat_mesh)


    def init_rhs_vector(self, spat_mesh, inner_regions):
        self.init_rhs_vector_in_full_domain(spat_mesh)
        self.set_rhs_for_nodes_inside_objects(spat_mesh, inner_regions)


    def init_rhs_vector_in_full_domain(self, spat_mesh):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        dx = spat_mesh.x_cell_size
        dy = spat_mesh.y_cell_size
        dz = spat_mesh.z_cell_size
        # todo: split into separate functions
        for k in range(1, nz-1):
            for j in range(1, ny-1):
                for i in range(1, nx-1):
                    # - 4 * pi * rho * dx^2 * dy^2
                    rhs_at_node = -4.0 * np.pi * spat_mesh.charge_density[i][j][k]
                    rhs_at_node = rhs_at_node * dx * dx * dy * dy * dz * dz
                    # left and right boundary
                    rhs_at_node = rhs_at_node - \
                    dy * dy * dz * dz * \
                    (kronecker_delta(i, 1) * spat_mesh.potential[0][j][k] + \
                     kronecker_delta(i, nx-2) * spat_mesh.potential[nx-1][j][k])
                    # top and bottom boundary
                    rhs_at_node = rhs_at_node - \
                    dx * dx * dz * dz * \
		    (kronecker_delta(j, 1) * spat_mesh.potential[i][0][k] + \
                     kronecker_delta(j, ny-2) * spat_mesh.potential[i][ny-1][k])
                    # near and far boundary
                    rhs_at_node = rhs_at_node - \
                    dx * dx * dy * dy * \
		    (kronecker_delta(k, 1) * spat_mesh.potential[i][j][0] + \
                     kronecker_delta(k, nz-2) * spat_mesh.potential[i][j][nz-1])
                    # set rhs vector values
                    global_idx = self.node_ijk_to_global_index_in_matrix(i, j, k,
                                                                         nx, ny, nz)
                    self.rhs[global_idx] = rhs_at_node


    def set_rhs_for_nodes_inside_objects(self, spat_mesh, inner_regions):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        for ir in inner_regions.regions:
            for node in ir.inner_nodes_not_at_domain_edge:
                global_idx = self.node_ijk_to_global_index_in_matrix(
                    node.x, node.y, node.z, nx, ny, nz)
                self.rhs[global_idx] = ir.potential


    def node_ijk_to_global_index_in_matrix(self, i, j, k, nx, ny, nz):
        # numbering of nodes corresponds to axis direction
        # i.e. numbering starts from bottom-left-near corner
        #   then along X axis to the right
        #   then along Y axis to the top
        #   then along Z axis far
        if ((i <= 0) or (i >= nx-1) or \
            (j <= 0) or (j >= ny-1) or \
            (k <= 0) or (k >= nz-1)):
            print("incorrect index at node_ijk_to_global_index_in_matrix: " + \
                  "i  = {:d}, j  = {:d},  k  = {:d} \n".format(i, j, k) + \
                  "nx = {:d}, ny = {:d},  nz = {:d} \n".format(nx, ny, nz))
            print("this is not supposed to happen; aborting \n")
            sys.exit(-1)
        else:
            return (i - 1) + (j - 1) * (nx - 2) + (k - 1) * (nx - 2) * (ny - 2)


    def global_index_in_matrix_to_node_ijk(self, global_index, nx, ny, nz):
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
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        nrow = (nx - 2) * (ny - 2) * (nz - 2)
        ncol = nrow
        for global_index in range(nrow):
            i, j, k = self.global_index_in_matrix_to_node_ijk(global_index, nx, ny, nz)
            spat_mesh.potential[i][j][k] = self.phi_vec[global_index]


    def eval_fields_from_potential(self, spat_mesh):
        nx = spat_mesh.x_n_nodes
        ny = spat_mesh.y_n_nodes
        nz = spat_mesh.z_n_nodes
        dx = spat_mesh.x_cell_size
        dy = spat_mesh.y_cell_size
        dz = spat_mesh.z_cell_size
        phi = spat_mesh.potential
        #
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if i == 0:
                        ex = - boundary_difference(phi[i][j][k], phi[i+1][j][k], dx)
                    elif i == nx - 1:
                        ex = - boundary_difference(phi[i-1][j][k], phi[i][j][k], dx)
                    else:
                        ex = - central_difference(phi[i-1][j][k], phi[i+1][j][k], dx)
                    #
                    if j == 0:
                        ey = - boundary_difference(phi[i][j][k], phi[i][j+1][k], dy)
                    elif j == ny - 1:
                        ey = - boundary_difference(phi[i][j-1][k], phi[i][j][k], dy)
                    else:
                        ey = - central_difference(phi[i][j-1][k], phi[i][j+1][k], dy)
                    #
                    if k == 0:
                        ez = - boundary_difference(phi[i][j][k], phi[i][j][k+1], dz)
                    elif k == nz - 1:
                        ez = - boundary_difference(phi[i][j][k-1], phi[i][j][k], dz)
                    else:
                        ez = - central_difference(phi[i][j][k-1], phi[i][j][k+1], dz)
                    #
                    spat_mesh.electric_field[i][j][k] = Vec3d(ex, ey, ez)


    def clear(self):
        pass
        # todo: deallocate
        # phi_vec;
        # rhs;
        # A;
        # precond;
        # monitor;


def central_difference(phi1, phi2, dx):
    return (phi2 - phi1) / (2.0 * dx)


def boundary_difference(phi1, phi2, dx):
    return (phi2 - phi1) / dx


def kronecker_delta(i, j):
    if i == j:
        return 1
    else:
        return 0
