import weakref

from .binds import BindingsDescriptor, Binds
from .utils import Owned, OwningDescriptor


class Type(OwningDescriptor, Binds):

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
        pass

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__

    def __owned__(self, name, instance, owner):
        return Attribute(name, instance, owner, self)


class Attribute(Owned, Type):
    bindings = BindingsDescriptor()

    def __init__(self, name, instance, owner, typ):
        super().__init__(name, instance, owner)
        self.typ = typ

    def __str__(self):
        return "{owned}.{name}:{typ}".format(
            typ=self.typ, name=self.name, owned=self.owned)

    def __repr__(self):
        return "{owned!r}.{name}: {typ!r}".format(
            typ=self.typ, name=self.name, owned=self.owned)

    def __bind__(self, input):
        self.bindings.add(self)


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
