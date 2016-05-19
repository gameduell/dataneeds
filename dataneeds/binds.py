import weakref

from .utils import Owned

__all__ = ['Binds']


class Input:
    """Discreptor for inputs, can only be assigned once."""

    def __get__(self, instance, owner):
        if instance is None:
            return self

        try:
            return instance.__dict__['__input__']
        except KeyError:
            return None

    def __set__(self, instance, value):
        if instance.__dict__.get('__input__'):
            raise ValueError("Input of %r already bound (%r)." %
                             (instance, instance.__dict__['__input__']))
        instance.__dict__['__input__'] = value


class Outputs:
    """Discreptor for outputs, can only be assigned once."""

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if '__outputs__' not in instance.__dict__:
            instance.__dict__['__outputs__'] = []
        return instance.__dict__['__outputs__']


class Binds:
    """
    Implements `>>` for binding input

    >>> AFormat() >> OtherFormat() >> entity.attr
    """

    input = Input()
    outputs = Outputs()

    def __bind__(self, input):
        return NotImplemented

    def __rrshift__(self, input):
        # input >> self
        res = self.__bind__(input)

        if res is NotImplemented:
            return res

        self.input = input
        input.outputs.append(self)
        return Bundle(input, self) if res is None else res


class Bundle:
    """
    Bundling together objects after `>>`, so further binds can take place.
    """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __bind__(self, input):
        return self.a.__bind__(input)

    def __rshift__(self, other):
        # self >> other
        self.b >> other
        return Bundle(self, other)

    def __rrshift__(self, other):
        # other >> self
        other >> self.a
        return Bundle(other, self)

    def __str__(self):
        return "{}>>{}".format(self.a, self.b)

    def __repr__(self):
        return "{!r} >> {!r}".format(self.a, self.b)


class BindingsDescriptor:
    """
    Descriptor for storing bindings assosiated with owned attributes.
    """

    def __init__(self):
        self.binds = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        assert isinstance(instance, Owned)
        key = getattr(instance.owner, instance.name)
        if key not in self.binds:
            self.binds[key] = Bindings()
        return self.binds[key]


class Bindings:

    def __init__(self):
        self.bindings = []

    def __len__(self):
        return len(self.bindings)

    def __iter__(self):
        return iter(self.bindings)

    def __getitem__(self, n):
        return self.bindings[n]

    def add(self, binds):
        self.bindings.append(Binding(binds))


class Binding:

    def __init__(self, binds):
        self.binds = binds

    def __iter__(self):
        o = self.binds
        while True:
            yield o
            if o.input is None:
                return o
            else:
                o = o.input

    @property
    def source(self):
        for o in iter(self):
            pass
        return o

    @property
    def input(self):
        return self.binds.input

    def __str__(self):
        return "Binding({})".format(self.binds)

    def __repr__(self):
        return " >> ".join(map(str, reversed(list(self))))
