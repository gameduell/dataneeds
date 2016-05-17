import contextlib
from collections import defaultdict

from .entity import Relation
from .types import Attribute


@contextlib.contextmanager
def request(entity, **options):
    yield Request(entity, **options)


class Request:

    def __init__(self, entity, **options):
        self.entity = entity
        self.options = options

        self.items = []

    def reslove(self):
        sets = defaultdict(set)

        for item in self.items:
            for b in item.resolving.bindings:
                sets[b.source].add(b)

        complete = set(tuple(s)
                       for s in sets.values() if len(s) == len(self.items))
        if complete:
            return complete

        else:
            raise NotImplementedError("Resolve with %s" % sets)

    def __getattr__(self, name):
        field = getattr(self.entity, name)

        if isinstance(field, Attribute):
            item = AttrItem(self, field)
        elif isinstance(field, Relation):
            item = RelationItem(self, field)
        else:
            raise ValueError("Don't know how to request a %r" % type(field))

        self.items.append(item)
        return item


class Item:

    def __iter__(self):
        return iter((IterItem(self),))


class AttrItem(Item):

    def __init__(self, request, attr):
        self.request = request
        self.attr = attr

    @property
    def resolving(self):
        return self.attr


class RelationItem(Item):

    def __init__(self, request, rel):
        self.request = request
        self.rel = rel
        self.item = None

    @property
    def resolving(self):
        return self.item.resolving

    def __getattr__(self, name):
        field = getattr(self.rel.towards, name)

        if isinstance(field, Attribute):
            item = AttrItem(self, field)
        elif isinstance(field, Relation):
            item = RelationItem(self, field)
        else:
            raise ValueError("Don't know how to request a %r" % type(field))

        self.item = item
        return item


class IterItem(Item):

    def __init__(self, item):
        self.item = item
        self.op = None

    @property
    def resolving(self):
        return self.item.resolving

    def __radd__(self, other):
        if other != 0:
            raise ValueError("Expected add of zero for IterItem, "
                             "use simple things like `sum(Entity.attr)` only")
        self.op = 'sum'
        return self
