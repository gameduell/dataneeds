from .binds import Binds
from .types import Type, InstanceAttribute

import weakref

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
        return cls.__module__ + "." + cls.__name__


class Entity(Binds, metaclass=EntityMeta):
    """Base class for entity definitions."""

    def __init__(self):
        super().__init__()
        self.inputs = []
        self.__rels__ = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return Relation(lambda: owner, card={'lower': 1, 'upper': 1})
        else:
            try:
                return self.__rels__[instance]
            except KeyError:
                rel = InstanceRelation(instance, self.entity, **self.card)
                self.__rels__[instance] = rel
                return rel

    def __bind__(self, input):
        if isinstance(input, InstanceAttribute):
            self.inputs.append(input)
        elif isinstance(input, RelationKey):
            self.inputs.append(input)
        else:
            return NotImplemented

        if self not in self.__bindings__:
            self.__bindings__.append(self)

    def declare(self):
        pass

    def __str__(self):
        return str(type(self))

    def __repr__(self):
        return repr(type(self))


class Relation:
    """
    Relations through annotations for cross-references in entities.

    >>> class AEntity(Entity):
    ...     @relate
    ...     def bs(lower=0, upper=...):
    ...         return BEntity()
    """

    def __init__(self, definition):
        self.card = {}  # XXX get card from definition
        self.definition = definition
        self._entity = None
        self.__rels__ = weakref.WeakKeyDictionary()

    @property
    def entity(self):
        if self._entity is None:
            self._entity = self.definition()
        return self._entity

    def __get__(self, instance, owner):
        if instance is None:
            self
        else:
            try:
                return self.__rels__[instance]
            except KeyError:
                rel = InstanceRelation(instance, self.entity, **self.card)
                self.__rels__[instance] = rel
                return rel

relate = Relation


class RelationKey(Type):
    """Reference to a key of a related entity."""

    def __init__(self, rel, name, attr):
        self.rel = rel
        self.name = name
        self.attr = attr

    def __bind__(self, input):
        self.input = input
        self >> self.rel.instance

    def __str__(self):
        return "{rel!s}.{name}".format(rel=self.rel, name=self.name)

    def __repr__(self):
        return "{rel!r}.{name}".format(rel=self.rel, name=self.name)


class InstanceRelation(Binds):
    """Relation information to a specific entity instance."""

    def __init__(self, instance, entity, **card):
        self.instance = instance
        self.entity = entity
        self.card = card

    def __getattr__(self, name):
        rel = RelationKey(self, name, getattr(self.entity, name))
        setattr(self, name, rel)
        return rel

    def __str__(self):
        return "{src!s}->{tgt!s}".format(src=self.instance,
                                         tgt=self.entity)

    def __repr__(self):
        return "{src!r}->{tgt!r}".format(src=self.instance,
                                         tgt=self.entity)
