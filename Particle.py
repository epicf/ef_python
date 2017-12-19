import vec3d

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
        print( "charge = {}, mass = {}, ".format( self.charge, self.mass ) )
        print( "pos(x,y,z) = ( {}, {}, {} )".format( self.position.x,
                                                     self.position.y,
                                                     self.position.z ) )
        print( "momentum(px,py,pz) = ( {}, {}, {} )".format( self.momentum.x,
                                                             self.momentum.y,
                                                             self.momentum.z ) )


    def print_short( self ):
        print( "id: {} x = {} y = {} z = {} px = {} py = {} pz = {}".format(
            self.id,
            self.position.x, self.position.y, self.position.z,
            self.momentum.x, self.momentum.y, self.momentum.z ) )
