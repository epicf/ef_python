import math

m = 1.67e-24                                # Ion mass
q = 4.8e-10                                 # Ion charge
kB = 1.38e-16                               # The Boltzmann constant
print( "q = {:.3e} [cgs]".format( q ) )
print( "m = {:.3e} [g]".format( m ) )
print( "k_B = {:.3e} [erg/K]".format( kB ) )

ev_to_erg = 1.60218e-12                     # Transfer from eV to erg units
E = 1 * ev_to_erg                           # The mean energy of ions
v = math.sqrt( 2 * E / m )                       # The mean velocity of ions
T = 2/3*(E / kB)                              # The temperature of the ion gas
print( "E = {:.3e} [eV] = {:.3e} [erg]".format( E / ev_to_erg, E ) )
print( "v = {:.3e} [cm/s]".format( v ) )
print( "T = {:.3e} [K]".format( T ) )

sim_time = 0.67e-6
#n_of_steps = 100
n_of_steps = 1000 # bin
dt = sim_time / n_of_steps
print( "simulation_time = {:.3e} [s]".format( sim_time ) )
print( "number_of_time_steps = {:d}".format( n_of_steps ) )
print( "time_step_size = {:.3e} [s]".format( dt ) )

#num_of_macro_particles = 5000
num_of_macro_particles = 1 # bin
macro_mean_momentum = m * v
print( "num_of_macro_particles = {:d}".format( num_of_macro_particles ) )
print( "macro_mean_momentum = {:.3e} [g * cm / s]".format( macro_mean_momentum ) )
