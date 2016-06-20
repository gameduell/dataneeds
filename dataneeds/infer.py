from dataneeds.binds import Binds


class Rule(Binds):

    def __bind__(self, input):
        pass


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
