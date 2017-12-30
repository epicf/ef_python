config = {}


config["Time grid"] = {}
config["Time grid"]["total_time"] = 1.0e-7
config["Time grid"]["time_step_size"] = 1.0e-9
config["Time grid"]["time_save_step"] = 1.0e-9


config["Spatial mesh"] = {}
config["Spatial mesh"]["grid_x_size"] = 5.0
config["Spatial mesh"]["grid_x_step"] = 0.5
config["Spatial mesh"]["grid_y_size"] = 5.0
config["Spatial mesh"]["grid_y_step"] = 0.5
config["Spatial mesh"]["grid_z_size"] = 15.0
config["Spatial mesh"]["grid_z_step"] = 1.5

config["Particle sources"] = {}

config["Particle_interaction_model"] = {}
# 'noninteracting' or 'PIC'; with quotes
config["Particle_interaction_model"]["particle_interaction_model"] = "noninteracting"
#config["Particle_interaction_model"]["particle_interaction_model" = "PIC"


config["Boundary conditions"] = {}
config["Boundary conditions"]["boundary_phi_left"] = 0.0 
config["Boundary conditions"]["boundary_phi_right"] = 0.0
config["Boundary conditions"]["boundary_phi_bottom"] = 0.0
config["Boundary conditions"]["boundary_phi_top"] = 0.0
config["Boundary conditions"]["boundary_phi_near"] = 0.0
config["Boundary conditions"]["boundary_phi_far"] = 0.0	

config["External fields"] = {}

config["Output filename"] = {}
config["Output filename"]["output_filename_prefix"] = "minimal_example_"
config["Output filename"]["output_filename_suffix"] = ".h5"
