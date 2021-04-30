from .particles import Particle

__all__ = [
        'Process',
        ]

class Process(object):
    def __init__(self, initial, final, mF_list=[]):
        """
        initial and final should be a list of initial and final state particle
        names for the Born process.
        For the NLO correction all possible gluon emissions will be assumed.

        particle name should be given as a string
        """
        self.all_particles = []
        self.mF_list = []
        for par in initial:
            p = Particle(par)
            setattr(p,'initial', True)
            self.all_particles.append(p)

        for par in final:
            p = Particle(par)
            setattr(p,'initial', False)
            self.all_particles.append(p)

        for par in final:
            p = Particle(par)
            setattr(p,'initial', False)
            self.mF_list.append(p)
