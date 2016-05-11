from .formats import Format


class Entity(Format):
    def __bind__(self, input):
        self.input = input
