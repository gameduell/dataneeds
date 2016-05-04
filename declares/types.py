from .formats import Format


class Type(Format):
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


class Any(Type):
    pass


class Unknown(Type):
    pass


class Optional(Type):
    def __init__(self, inner):
        self.inner = inner


class Cons(Type):
    def __init__(self, *types):
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


class Union(Type):
    def __init__(self, *types):
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
        import re
        self.regexp = re.compile(regexp)


class Timestamp(Type):
    # TODO formats
    pass


class List(Type):
    def __init__(self, inner: Type):
        self.inner = inner
    # TODO Bounds


class Set(Type):
    def __init__(self, inner: Type):
        self.inner = inner
    # TODO Bounds


class Dict(Type):
    def __init__(self, keys: Type, values: Type):
        self.keys = keys
        self.values = values
    # TODO key/value specs ...


class Categorical(Type):
    def __init__(self, name):
        self.name = name
    # TODO fixed vs open ...
