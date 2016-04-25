from collections import OrderedDict

from .entity import Entity


class RecordMeta(type):
    def __prepare__(name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, dict):
        new = super().__new__(cls, name, bases, dict)
        new.__order__ = tuple(n for n in dict if not n.startswith('_'))
        return new


class Record(metaclass=RecordMeta):
    def __str__(self):
        return '<{}>'.format(','.join(self.__order__))

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self)


class Event(Record, Entity):
    pass
