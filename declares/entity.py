class Entity:
    def __rshift__(self, other):
        if not isinstance(other, Entity):
            return NotImplemented
        return self
