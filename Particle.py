from Vec3d import *

class Particle():
    
    def __init__( self, id, charge, mass, position, momentum ):
        self.id = id
        self.charge = charge
        self.mass = mass
        self.position = position
        self.momentum = momentum
        self.momentum_is_half_time_step_shifted = False 

    def update_position( self, dt ):
        pos_shift = self.momentum.times_scalar( dt / self.mass )
        self.position = self.position.add( pos_shift )

    def print_long( self ):
        print( "Particle: " )
        print( "id: {},".format( self.id ) )
        print( "charge = {:.3f}, mass = {:.3f}, ".format( self.charge, self.mass ) )
        print( "pos(x,y,z) = ( {:.2f}, {:.2f}, {:.2f} )".format( self.position.x,
                                                                 self.position.y,
                                                                 self.position.z ) )
        print( "momentum(px,py,pz) = ( {:.2f}, {:.2f}, {:.2f} )".format( self.momentum.x,
                                                                         self.momentum.y,
                                                                         self.momentum.z ) )


    def print_short( self ):
        print( "id: {} x = {:.2f} y = {:.2f} z = {:.2f} "
               "px = {:.2f} py = {:.2f} pz = {:.2f}".format(
                   self.id,
                   self.position.x, self.position.y, self.position.z,
                   self.momentum.x, self.momentum.y, self.momentum.z ) )
