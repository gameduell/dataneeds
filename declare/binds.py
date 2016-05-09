class Binds:
    def __bind__(self, input):
        return NotImplemented

    def __rrshift__(self, other):
        # other >> self
        print('{} >> {} (rr)'.format(other, self))
        res = self.__bind__(other)
        return self if res is None else res
