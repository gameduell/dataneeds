from dataneeds.binds import Binds


class Rule(Binds):

    def __bind__(self, input):
        pass


class Any(Rule):
    pass


class Lowest(Rule):
    pass


class Highest(Rule):
    pass


class AtMost(Rule):
    pass


class AtLeast(Rule):
    pass
