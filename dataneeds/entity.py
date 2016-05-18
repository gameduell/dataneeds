from .binds import BindingsDescriptor, Binds
from .types import Type
from .utils import Owned, OwningDescriptor

__all__ = ['Entity']


class EntityMeta(type):
    """Meta-class for entities."""

    def __new__(cls, name, bases, dct):
        new = super().__new__(cls, name, bases, dct)
        new.__bindings__ = []
        return new

    def __str__(cls):
        return cls.__name__

    def __repr__(cls):
        if str(cls.__module__) == '__main__':
            return cls.__name__
        else:
            return cls.__module__ + "." + cls.__name__


class Entity(OwningDescriptor, metaclass=EntityMeta):
    """
    Base class for entity definitions.

    :note: when used inside another object,
           a relation towards this entity is defined.
    """

    def __init__(self):
        super().__init__()
        self.bindings = {}

    def __owned__(self, name, instance, owner):
        return Relation(name, instance, owner, self, {})

    def __str__(self):
        return "{cls}()".format(cls=type(self))

    def __repr__(self):
        return "{cls!r}()".format(cls=type(self))


class Relation(Owned):
    """Relation definition towards another object."""

    bindings = BindingsDescriptor()

    def __init__(self, name, instance, owner, towards, cardinality={}):
        super().__init__(name, instance, owner)
        self.towards = towards
        self.cardinality = cardinality

    def __getattr__(self, name):
        attr = getattr(self.towards, name)
        if not isinstance(attr, Owned):
            raise AttributeError("No access to {!r} ({}) through relations."
                                 .format(name, type(attr).__name__))
        rel = RelationKey(self, name, attr)
        setattr(self, name, rel)
        return rel

    def __str__(self):
        return "{src!s}.{name}->{tgt!s}".format(
            src=self.owner, name=self.name, tgt=self.towards)

    def __repr__(self):
        return "{src!r}.{name}->{tgt!r}".format(
            src=self.owner, name=self.name, tgt=self.towards)


class RelationAnnotation(OwningDescriptor):
    """
    Relations through annotations for cross/self-references in entities.

    >>> class AEntity(Entity):
    ...     @relate
    ...     def bs(lower=0, upper=...):
    ...         return AEntity()
    """

    def __init__(self, definition):
        super().__init__()
        self.definition = definition
        self.entity = None

    def __owned__(self, name, instance, owner):
        assert name == self.definition.__name__
        entity = self.definition()
        card = {}  # XXX get card from definition
        return Relation(name, instance, owner, entity, card)

relate = RelationAnnotation


class RelationKey(Type, Binds):
    """Reference to a key of a related entity."""

    def __init__(self, rel, name, attr):
        self.rel = rel
        self.name = name
        self.attr = attr

    def __bind__(self, input):
        self.rel.bindings.add(self)

    def __str__(self):
        return "{rel!s}.{name}".format(rel=self.rel, name=self.name)

    def __repr__(self):
        return "{rel!r}.{name}".format(rel=self.rel, name=self.name)
