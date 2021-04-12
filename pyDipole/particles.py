__all__ = [
        'Particle',
        'particles',
        ]
"""
Style: name: [isMassive(bool),isQCD(bool)]
"""

particle_table = {
        'u'    : [False, True],
        'ubar' : [False, True],
        't'    : [True, True],
        'tbar' : [True, True],
        'e'    : [False, False],
        'ebar' : [False, False],
        'g'    : [False, True]
        }

par_id = 1


class Particle(object):
    def __init__(self,name):
        self.name = name
        try:
            self.isMassive = particle_table[name][0]
            self.isQCD = particle_table[name][1]
        except KeyError:
            raise KeyError("particle {} is not defined".format(name))
        global par_id
        self.id = par_id
        par_id = par_id + 1

    @property
    def name(self):
        return self.__name;

    @name.setter
    def name(self, name):
        if not isinstance(name,str):
            raise TypeError("Particle name should be a string")
        else:
            self.__name = name

    def __str__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.__dict__)

def particles(name):
    if not isinstance(name, str):
        raise TypeError("Particle names should be given as a space separated string")
    else:
        particles = name.split()
        output = tuple()
        for p in particles:
            particle=Particle(p)
            output = output + (particle,)

        return output
