from .binds import Binds
from .types import Type
from .utils import nameof

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


class RelatesDescriptor:
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.__rels__ = weakref.WeakKeyDictionary()

    @property
    def _entity(self):
        raise NotImplementedError

    @property
    def _cardinality(self):
        raise NotImplementedError

    def __get__(self, instance, owner):
        try:
            return self.__rels__[instance or owner]
        except KeyError:
            name = nameof(self, owner)
            if instance is None:
                key = owner
                Cls = OwnedRelation
            else:
                key = instance
                Cls = InstanceRelation

            self.__rels__[key] = rel = Cls(name, key,
                                           self._entity, self._cardinality)
            return rel


class Entity(RelatesDescriptor, Binds, metaclass=EntityMeta):
    """Base class for entity definitions."""

    def __init__(self):
        super().__init__()
        self.bindings = {}

    @property
    def _entity(self):
        return self

    def binds(self, name, input):
        self.bindings[name] = input

        if self not in self.__bindings__:
            self.__bindings__.append(self)

    def declare(self):
        pass

    def __str__(self):
        return str(type(self))

    def __repr__(self):
        return repr(type(self))


class Relation(RelatesDescriptor):
    """
    Relations through annotations for cross/self-references in entities.

    >>> class AEntity(Entity):
    ...     @relate
    ...     def bs(lower=0, upper=...):
    ...         return AEntity()
    """

    def __init__(self, definition):
        super().__init__()
        self.card = {}  # XXX get card from definition
        self.definition = definition
        self.entity = None
        self.__rels__ = weakref.WeakKeyDictionary()

    @property
    def _entity(self):
        if self.entity is None:
            self.entity = self.definition()
        return self.entity

    @property
    def _cardinality(self):
        return self.card

relate = Relation


class OwnedRelation:
    def __init__(self, name, instance, entity, card):
        pass


class InstanceRelation(Binds):
    """Relation information to a specific entity instance."""

    def __init__(self, name, instance, entity, card):
        self.name = name
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


class RelationKey(Type):
    """Reference to a key of a related entity."""

    def __init__(self, rel, name, attr):
        self.rel = rel
        self.name = name
        self.attr = attr

    def __bind__(self, input):
        self.input = input
        self.rel.instance.binds(self.rel.name + "." + self.name, self)

    def __str__(self):
        return "{rel!s}.{name}".format(rel=self.rel, name=self.name)

    def __repr__(self):
        return "{rel!r}.{name}".format(rel=self.rel, name=self.name)
