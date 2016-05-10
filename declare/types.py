from .binds import Binds

import weakref


class Type(Binds):
    def __init__(self):
        super().__init__()
        self.__attrs__ = weakref.WeakKeyDictionary()

    def __add__(self, other):
        return Cons(self, other)

    def __and__(self, other):
        return Both(self, other)

    def __or__(self, other):
        return Either(self, other)

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
            return OwnedAttribute(self, owner)
        else:
            try:
                return self.__attrs__[instance]
            except KeyError:
                attr = InstanceAttribute(self, instance)
                self.__attrs__[instance] = attr
                return attr


class OwnedAttribute:
    """An attribute of an entity class defined with a Type."""

    def __init__(self, typ, owner):
        self.typ = typ
        self.owner = owner

    def __str__(self):
        return "{typ}".format(typ=self.typ)

    def __repr__(self):
        return "{typ!r} attr of {owner!r}".format(typ=self.typ,
                                                  owner=self.owner)


class InstanceAttribute(Type, Binds):
    """An attribute of an entity instance defined with a Type."""

    def __init__(self, typ, instance):
        self.typ = typ
        self.instance = instance

    def __str__(self):
        return "{typ}".format(typ=self.typ)

    def __repr__(self):
        return "{typ!r} attr of a {instance!r}".format(typ=self.typ,
                                                       instance=self.instance)

    def __bind__(self, input):
        self.input = input
        self >> self.instance


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
            input >> typ


class Cons(Type):
    def __init__(self, *types):
        super().__init__()
        self.types = types

    def __add__(self, other):
        if isinstance(other, Cons):
            return Cons(*(self.types + other.types))
        else:
            return Cons(*(self.types + (other,)))

    def __radd__(self, other):
        if isinstance(other, Cons):
            return Cons(*(other.types + self.types))
        else:
            return Cons(other, *self.types)

    def __bind__(self, input):
        self.input = input
        for typ in self.types:
            self >> typ


class Either(Type):
    def __init__(self, *types):
        super().__init__()
        self.types = types

    def __or__(self, other):
        if isinstance(other, Either):
            return Either(*(self.types + other.types))
        else:
            return Either(*(self.types + [other]))

    def __ror__(self, other):
        if isinstance(other, Either):
            return Either(*(other.types + self.types))
        else:
            return Either(other, *self.types)

    def __bind__(self, input):
        self.input = input
        for typ in self.types:
            self >> typ


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
