from .formats import Format


class Entity(Format):
    def __bind__(self, input):
        self.input = input

    def __connect__(self):
        pass

    def __getattr__(self, name):
        self.__connect__()
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError("%r object has no attribute %r" %
                                 (type(self).__name__, name))
