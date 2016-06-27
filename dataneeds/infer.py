from .binds import Binds
from .entity import Attribute
from .utils import Wraps


class Inferring(Binds, Wraps):

    def __init__(self, target):
        super().__init__(target)

    def __bind__(self, input):
        self >> self.wrapped

    def __wrap__(self, field):
        if isinstance(field, Attribute):
            return Inferring(field)
        else:
            super().__wrap__(field)


class Rule(Binds):

    def __bind__(self, input):
        pass

    def __str__(self):
        return type(self).__name__

    __repr__ = __str__


class By(Rule):
    pass


class Any(Rule):
    pass


class Lowest(Rule):

    def __init__(self, range=None):
        self.range = None


class Highest(Rule):

    def __init__(self, range=None):
        self.range = None


class AtMost(Rule):
    pass


class AtLeast(Rule):
    pass
