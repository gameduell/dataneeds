from .binds import Binds


class InstanceRelation:
    def __init__(self, instance, entity, lower, upper):
        self.instance = instance
        self.entity = entity
        self.lower = lower
        self.upper = upper

    def __getattr__(self, name):
        if hasattr(type(self.entity), name):
            attr = getattr(self.entity, name)
            return attr.typ  # XXX Relation Key ...
        else:
            return getattr(super(), name)

    def __bind__(self, input):
        self.input = input
        self.instance.__bind__(self)


class RelationDefinition:
    def __init__(self, definition, lower, upper):
        self.definition = definition
        self.lower = lower
        self.upper = upper

        self._entity = None

    @property
    def entity(self):
        if self._entity is None:
            self._entity = self.definition()
        return self._entity

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return InstanceRelation(instance, self.entity,
                                    self.lower, self.upper)


def relate(lower, upper=None):
    if upper is None:
        upper = lower

    def annotate(fn):
        return RelationDefinition(fn, lower, upper)
    return annotate


class EntityMeta(type):
    def __new__(cls, name, bases, dct):
        new = super().__new__(cls, name, bases, dct)
        new.__bindings__ = set()
        return new

    def __str__(cls):
        return cls.__module__ + "." + cls.__name__


class Entity(Binds, metaclass=EntityMeta):
    def __init__(self):
        print('mk', repr(self))

    def __bind__(self, input):
        print('bnd', repr(self), input)
        self.input = input
        self.__bindings__.add(self)

    def declare(self):
        pass

    def __str__(self):
        return str(type(self))
