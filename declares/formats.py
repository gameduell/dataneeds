class Format:
    def __bind__(self, input):
        return NotImplemented

    @property
    def __out__(self):
        return ()

    def __rrshift__(self, other):
        print('{} >> {} (rr)'.format(other, self))
        # other >> self
        res = self.__bind__(other)
        return self if res is None else res

    def __rshift__(self, other):
        # self >> other
        print('{} >> {} (rr)'.format(self, other))
        return NotImplemented


class Either(Format):
    def __init__(self, *formats):
        self.formats = formats

    def __bind__(self, input):
        self.input = input

    @property
    def __out__(self):
        return (self.input.__out__,)


class Each(Format):
    def __init__(self, inner):
        self.inner = inner

    def __bind__(self, input):
        self.input = input


class Re(Format):
    def __init__(self, exp):
        import re
        self.re = re.compile(exp)

    def __bind__(self, input):
        assert input.__out__ == str
        self.input = input

    @property
    def __out__(self):
        if self.re.groupindex:
            names = {i: n for n, i in self.re.groupindex}
            return [(names.get(i+1, None), str) for i in range(self.groups)]
        else:
            return [str] * self.re.groups


class Sep(Format):
    def __init__(self, sep=',', limit=0):
        self.sep = sep
        self.limit = limit

    def __bind__(self, input):
        assert isinstance(self.sep, input.__out__)
        self.input = input

    @property
    def __out__(self):
        return [type(self.sep), ...]


class Json(Format):
    def __bind__(self, input):
        assert issubclass(input.__out__, str)

    @property
    def __out__(self):
        return ...


class Files(Format):
    def __init__(self, pattern, compression='infer'):
        self.pattern = pattern
        self.compression = compression

    @property
    def __out__(self):
        return str
