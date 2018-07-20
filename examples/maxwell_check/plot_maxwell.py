# -*- coding: utf-8 -*-
"""
Created on Wed July 11 13:00:00 2018
Estimation of establishing Maxwell distribution of the Hydrogen ion gas inside the box
@author: Getmanov
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import h5py

SGSE_conv_unit_current_to_A = 3e10 * 0.1;  # from current units SGSE to A
SI_conv_cm_to_m = 0.01;
SI_conv_g_to_kg = 0.001
SI_conv_Fr_to_C = 3.3356409519815207e-10


def get_source_geometry(h5file):
    start_y = h5file["/Particle_sources/cathode_emitter"].attrs["box_y_top"]
    end_y = h5file["/Particle_sources/cathode_emitter"].attrs["box_y_bottom"]
    start_x = h5file["/Particle_sources/cathode_emitter"].attrs["box_x_left"]
    end_x = h5file["/Particle_sources/cathode_emitter"].attrs["box_x_right"]
    start_z = h5file["/Particle_sources/cathode_emitter"].attrs["box_z_near"]
    end_z = h5file["/Particle_sources/cathode_emitter"].attrs["box_z_far"]
    return start_x, end_x, start_y, end_y, start_z, end_z

def draw_2dbox_boundary(start_x, end_x, start_z, end_z):
    x_box = np.arange(start_x, end_x, (end_x - start_x) / 100)
    z_box = start_z*np.ones(x_box.shape)
    np.append(x_box, x_box)
    np.append(z_box, end_z*np.ones(z_box.shape))
    z1_box = np.arange(start_z, end_z, (end_z - start_z) / 100)
    x1_box = start_x*np.ones(z1_box.shape)
    np.append(x_box, x1_box)
    np.append(z_box, z1_box)
    np.append(x_box, end_x*np.ones(z1_box.shape))
    np.append(z_box, z1_box)
    return x_box, z_box

def analyt_maxwell_distrib(num_particles, temperature, h5file):
    p_xend = h5file["/Particle_sources/cathode_emitter/momentum_x"][:]
    p_yend = h5file["/Particle_sources/cathode_emitter/momentum_y"][:]
    p_zend = h5file["/Particle_sources/cathode_emitter/momentum_z"][:]
    mass = h5file["/Particle_sources/cathode_emitter"].attrs["mass"]
    kB = 1.38e-16

    p = (p_xend ** 2 + p_yend ** 2 + p_zend ** 2) ** (1/2)

    p_grid = np.arange(0.0, p.max(), (p.max() - p.min())/150)
    p_grid_1 = p_grid[1:]
    dp = p_grid_1 - p_grid[0:len(p_grid)-1]

    distr = 4*math.pi* (1/(2*math.pi*mass*kB*temperature)) ** (3/2) * (p_grid[1:] ** 2) * np.exp(-1* (p_grid[1:] ** 2) /(2*kB*mass*temperature))*dp
    dN = num_particles * distr

    return dN, p_grid[1:]

filename = 'task_maxwell_0000001.h5'
h5 = h5py.File(filename, mode="r")

filename_1 = 'task_maxwell_0000200.h5'
h5_1 = h5py.File(filename_1, mode="r")

filename_2 = 'task_maxwell_0000400.h5'
h5_2 = h5py.File(filename_2, mode="r")

filename_3 = 'task_maxwell_0000900.h5'
h5_3 = h5py.File(filename_3, mode="r")

start_x, end_x, start_y, end_y, start_z, end_z = get_source_geometry(h5)
x_box, z_box = draw_2dbox_boundary(start_x, end_x, start_z, end_z)
dN, p_grid = analyt_maxwell_distrib(100, 7.740e+03, h5_3)

h5 = h5py.File(filename, mode="r")  # read h5 file
plt.figure(figsize=(10, 10), dpi=(100))
#plt.xlim(2*start_z , 2*end_z)
#plt.ylim(-0.0002, 0.0002)
plt.xlabel("Z position, [cm]")
plt.ylabel("X position, [cm]")
plt.plot(h5["/Particle_sources/cathode_emitter/position_z"][:],
         (h5["/Particle_sources/cathode_emitter/position_x"][:]),
         'o', label="elapsed time: 0.67e-9 s")  # plot particles
#plt.plot(h5_1["/Particle_sources/cathode_emitter/position_z"][:],
#         (h5_1["/Particle_sources/cathode_emitter/position_x"][:]),
#         'o', label="calculated_points2")
#plt.plot(h5_2["/Particle_sources/cathode_emitter/position_z"][:],
#         (h5_2["/Particle_sources/cathode_emitter/position_x"][:]),
#         'o', label="calculated_points3")
plt.plot(h5_3["/Particle_sources/cathode_emitter/position_z"][:],
         (h5_3["/Particle_sources/cathode_emitter/position_x"][:]),
         'o', label="elapsed time: 0.67e-6 s")
plt.plot(z_box,x_box,'o', label="box")
plt.legend(bbox_to_anchor=(0.32, 1), loc=1, borderaxespad=0.)
plt.savefig('plt_maxwell_distr.png')
plt.close()

p_x0 = h5["/Particle_sources/cathode_emitter/momentum_x"][:]
p_y0 = h5["/Particle_sources/cathode_emitter/momentum_y"][:]
p_z0 = h5["/Particle_sources/cathode_emitter/momentum_z"][:]

p0 = (p_x0 ** 2 + p_y0 ** 2 + p_z0 ** 2) ** (1/2)

p_xend = h5_3["/Particle_sources/cathode_emitter/momentum_x"][:]
p_yend = h5_3["/Particle_sources/cathode_emitter/momentum_y"][:]
p_zend = h5_3["/Particle_sources/cathode_emitter/momentum_z"][:]

p_end = (p_xend ** 2 + p_yend ** 2 + p_zend ** 2) ** (1/2)

plt.figure()
plt.hist(h5["/Particle_sources/cathode_emitter/momentum_z"][:],15)
plt.hist(h5_1["/Particle_sources/cathode_emitter/momentum_z"][:],15)
plt.hist(h5_2["/Particle_sources/cathode_emitter/momentum_z"][:],15)
plt.hist(h5_3["/Particle_sources/cathode_emitter/momentum_z"][:],15)

#plt.plot(position_z * 1000, -1 * contour * 1000, color='g', lw=3)
plt.legend(bbox_to_anchor=(0.32, 1), loc=1, borderaxespad=0.)
plt.savefig('plt_maxwell_hist.png')  # save png picture

plt.figure()
plt.hist(p0,20)
plt.plot(p_grid, dN)
plt.xlim(1.5e-18 , 4e-18)
plt.savefig('plt_maxwell_hist_p0.png')

plt.figure()
plt.hist(p_end,20)
plt.plot(p_grid, dN)
plt.xlim(1.5e-18 , 4e-18)
plt.savefig('plt_maxwell_hist_pend.png')

h5.close()  # close h5 file
h5_1.close()
h5_2.close()
h5_3.close()
