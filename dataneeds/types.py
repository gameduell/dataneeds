import weakref

from .binds import BindingsDescriptor, Binds, Part
from .utils import Owned, OwningDescriptor


class Type(OwningDescriptor, Binds):

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.__attrs__ = weakref.WeakKeyDictionary()

    @property
    def __of__(self):
        raise NotImplementedError("__of__ on %s" % type(self).__name__)

    def __add__(self, other):
        return Cons(self, other)

    def __truediv__(self, other):
        return Same(self, other)

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

    @property
    def __of__(self):
        return self.typ.__of__

    def __str__(self):
        return "{owned}.{name}:{typ}".format(
            typ=self.typ, name=self.name, owned=self.owned)

    def __repr__(self):
        return "{owned!r}.{name}: {typ!r}".format(
            typ=self.typ, name=self.name, owned=self.owned)

    def __bind__(self, input):
        self.bindings.add(self)


class Any(Type):

    @property
    def __of__(self):
        def id(ins):
            return ins
        return id


class Unknown(Type):
    pass


class Optional(Type):

    def __init__(self, inner):
        super().__init__()
        self.inner = inner


class Same(Type):

    def __init__(self, *types):
        super().__init__()
        self.types = types

    def __truediv__(self, other):
        return Same(*(self.types + (other,)))

    def __bind__(self, input):
        for typ in self.types:
            self >> typ


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
        for i, typ in enumerate(self.types):
            Part[Cons](self, i) >> typ

    def __repr__(self):
        return 'Cons({})'.format(', '.join(map(str, self.types)))


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


class NativeType(Type):
    __native__ = None

    @property
    def __of__(self):
        return self.__native__


class Integer(NativeType):
    __native__ = int


class Floating(NativeType):
    __native__ = float


class String(NativeType):
    __native__ = str


class Regexp(Type):

    def __init__(self, regexp: String):
        super().__init__()
        import re
        self.regexp = re.compile(regexp)


class Timestamp(Type):

    def __init__(self, unit='ms'):
        super().__init__()
        self.unit = unit

    @property
    def __of__(self):
        import pandas as pd
        unit = self.unit

        def of(ts):
            try:
                return pd.Timestamp(int(ts), unit=unit)
            except ValueError:
                return pd.Timestamp(ts)
        return of


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

    @property
    def __of__(self):
        kof = self.keys.__of__
        vof = self.values.__of__

        def dct(input):
            return {kof(k): vof(v) for k, v in dict(input).items()}

        return dct

    def __init__(self, keys: Type, values: Type):
        super().__init__()
        self.keys = keys
        self.values = values


class Categorical(Type):

    def __init__(self, name):
        super().__init__()
        self.name = name

    # TODO fixed vs open ...
