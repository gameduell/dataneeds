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


class Binds:
    """
    Implements `>>` for binding input

    >>> AFormat() >> OtherFormat() >> entity.attr
    """

    input = Input()

    def __bind__(self, input):
        return NotImplemented

    def __rrshift__(self, other):
        # other >> self
        res = self.__bind__(other)
        return Bundle(other, self) if res is None else res


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
            self.binds[key] = []
        return self.binds[key]
