from collections import OrderedDict

from .binds import Binds


class RecordMeta(type):

    def __prepare__(name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, dict):
        new = super().__new__(cls, name, bases, dict)
        new.__order__ = tuple(n for n in dict if not n.startswith('_'))
        return new


class Record(Binds, metaclass=RecordMeta):

    def __bind__(self, input):
        pass

    @property
    def __out__(self):
        return ...

    def __str__(self):
        return '<{}>'.format(','.join(self.__order__))

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self)
