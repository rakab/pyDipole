__all__ = [
        'Process',
        ]

class Process(object):
    def __init__(self, proc):
        self.initial = proc[0];
        self.final = proc[1];

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
