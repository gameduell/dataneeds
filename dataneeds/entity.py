from .binds import BindingsDescriptor, Binds
from .types import Attribute, Type
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

    def __owned__(self, name, instance, owner):
        """An Entity is a Relation when being part of another Entity."""
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
        item = None
        obj = getattr(self.towards, name)
        if isinstance(obj, Owned):
            # so we have
            # >>> class ThisEntity:
            # ...     @relate
            # ...     def rel():
            # ...         return OtherEntity()
            # >>> ThisEntity().rel.name
            instance = self                         # Relation with instance
            owner = self.general                    # Relation with owner only

        if isinstance(obj, (Attribute, Reference)):
            item = Reference(name, instance, owner)
        elif isinstance(obj, Relation):
            # XXX do we have to allow this?
            item = Relation(name, instance, owner, obj)
        else:
            raise AttributeError("No access to {!r} ({}) through relations."
                                 .format(name, type(obj).__name__))

        setattr(self, name, item)
        return item

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


class Reference(Owned, Type, Binds):
    """Reference to an attribte of a related entity."""

    bindings = BindingsDescriptor()

    @property
    def attr(self):
        return getattr(self.instance.towards, self.name)

    def __bind__(self, input):
        self.bindings.add(self)
        self.instance.bindings.add(self)

    def __str__(self):
        return "{rel!s}.{name}".format(rel=self.instance, name=self.name)

    def __repr__(self):
        return "{rel!r}.{name}".format(rel=self.instance, name=self.name)
