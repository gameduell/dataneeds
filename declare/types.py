from .binds import Binds
from .entity import Entity


class OwnedAttribute:
    """An attribute of an entity defined with a Typ."""

    def __init__(self, typ, owner):
        self.typ = typ
        self.owner = owner

    def __str__(self):
        return "{typ}".format(typ=self.typ)

    def __repr__(self):
        return "{typ!r} attr of {owner}".format(typ=self.typ,
                                                owner=self.owner)


class InstanceAttribute(Binds):
    """An attribute of an entity instance defined with a Typ."""

    def __init__(self, typ, entity):
        self.typ = typ
        self.entity = entity

    def __str__(self):
        return "{typ}".format(typ=self.typ)

    def __repr__(self):
        return "{typ!r} instance of {entity}".format(typ=self.typ,
                                                     entity=self.entity)

    def __bind__(self, input):
        print('bind', repr(self))
        self.input = input
        self.entity.__bind__(self)


class Type(Binds):
    def __init__(self):
        self.input = None
        self.entity = None

    def __add__(self, other):
        return Cons(self, other)

    def __and__(self, other):
        return self

    def __or__(self, other):
        return Union(self, other)

    def __invert__(self):
        return Optional(self)

    def __bind__(self, input):
        self.input = input

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__

    def __get__(self, instance, owner):
        if instance is None:
            if issubclass(owner, Entity):
                return OwnedAttribute(self, owner)
        else:
            if isinstance(instance, Entity):
                return InstanceAttribute(self, instance)


class Any(Type):
    pass


class Unknown(Type):
    pass


class Optional(Type):
    def __init__(self, inner):
        super().__init__()
        self.inner = inner


class Both(Type):
    def __init__(self, *types):
        super().__init__()
        self.types = types

    def __bind__(self, input):
        self.input = input
        for typ in self.types:
            typ.__bind__(input)


class Cons(Type):
    def __init__(self, *types):
        super().__init__()
        self.types = types

    def __add__(self, other):
        if isinstance(other, Cons):
            return Cons(*(self.types + other.types))
        else:
            return Cons(*(self.types + [other]))

    def __radd__(self, other):
        if isinstance(other, Cons):
            return Cons(*(other.types + self.types))
        else:
            return Cons(other, *self.types)

    def __bind__(self, input):
        for typ in self.types:
            # XXX we should bind inner types to something else ...
            typ.__bind__(input)


class Union(Type):
    def __init__(self, *types):
        super().__init__()
        self.types = types

    def __or__(self, other):
        if isinstance(other, Union):
            return Union(*(self.types + other.types))
        else:
            return Union(*(self.types + [other]))

    def __ror__(self, other):
        if isinstance(other, Union):
            return Union(*(other.types + self.types))
        else:
            return Union(other, *self.types)


class Number(Type):
    # TODO Bounds
    pass


class String(Type):
    pass


class Regexp(Type):
    def __init__(self, regexp: String):
        super().__init__()
        import re
        self.regexp = re.compile(regexp)


class Timestamp(Type):
    # TODO formats
    pass


class List(Type):
    def __init__(self, inner: Type):
        super().__init__()
        self.inner = inner
    # TODO Bounds


class Set(Type):
    def __init__(self, inner: Type):
        super().__init__()
        self.inner = inner
    # TODO Bounds


class Dict(Type):
    def __init__(self, keys: Type, values: Type):
        super().__init__()
        self.keys = keys
        self.values = values
    # TODO key/value specs ...


class Categorical(Type):
    def __init__(self, name):
        super().__init__()
        self.name = name
    # TODO fixed vs open ...
