__all__ = [
        'Particle',
        'particles',
        ]
"""
Style: name: [mass(string),isQCD(bool)]
"""

particle_table = {
        'u'    : ['0' , True],
        'ubar' : ['0' , True],
        't'    : ['mt', True],
        'tbar' : ['mt', True],
        'e'    : ['0' , False],
        'ebar' : ['0' , False],
        'g'    : ['0' , True]
        }

par_id = 1


class Particle(object):
    def __init__(self,name):
        self.name = name
        try:
            self.mass = particle_table[name][0]
            self.isQCD = particle_table[name][1]
            self.isMassive = False if self.mass == '0' else True
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

    def __setattr__(self,name,value):
        super(Particle,self).__setattr__(name,value)

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
