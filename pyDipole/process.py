from .particles import Particle

__all__ = [
        'Process',
        ]

class Process(object):
    def __init__(self, initial, final):
        """
        initial and final should be a list of initial and final state particle
        names for the Born process.
        For the NLO correction all possible gluon emissions will be assumed.

        particle name should be given as a string
        """
        self.initial = []
        for init_par in initial:
            self.initial.append(Particle(init_par))

        self.final = []
        for fin_par in final:
            self.final.append(Particle(fin_par))

        self.all_particles = self.initial+self.final

    @property
    def initial(self):
        return self.__initial;

    @initial.setter
    def initial(self, initial):
        self.__initial = initial

    @property
    def final(self):
        return self.__final;

    @final.setter
    def final(self, final):
        self.__final = final
