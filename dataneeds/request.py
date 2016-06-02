import contextlib
import itertools
from collections import defaultdict

from .entity import Reference, Relation
from .types import Attribute


@contextlib.contextmanager
def request(entity, **options):
    yield Request(entity, **options)


class Request:

    def __init__(self, entity, **options):
        self.entity = entity
        self.options = options

        self.items = []

    def resolve(self):
        bindings = resolve_primary(self.items)
        return list(resolve_joins(self.items, bindings))

    def __getattr__(self, name):
        field = getattr(self.entity, name)

        if isinstance(field, Attribute):
            item = AttrItem(self, field)
        elif isinstance(field, Relation):
            item = RelationItem(self, field)
        else:
            raise ValueError("Don't know how to request a %r" % type(field))

        self.items.append(item)
        setattr(self, name, item)
        return item


class Item:
    needs_join = False

    def __init__(self, request, item, *args, **kws):
        super().__init__(*args, **kws)
        self.request = request
        self.item = item

    @property
    def bindings(self):
        return self.item.bindings

    def __iter__(self):
        return iter((IterItem(self),))

    def __str__(self):
        return str(self.item)

    def __repr__(self):
        return repr(self.item)


class AttrItem(Item):

    def __init__(self, request, attr):
        super().__init__(request, attr)


class RelationItem(Item):

    def __init__(self, request, rel):
        super().__init__(request, rel)
        self.items = []

    def __getattr__(self, name):
        ref = getattr(self.item, name)
        if isinstance(ref, Reference):
            item = ReferenceItem(self.request, ref)
        elif isinstance(ref, Relation):
            item = RelationItem(self.request, ref)
        else:
            raise AttributeError('No request to {} ({}) through relations'
                                 .format(name, type(ref)))

        self.items.append(item)
        setattr(self, name, item)
        return item

    @property
    def needs_join(self):
        it, *its = self.items
        return its or not it.bindings

    @property
    def bindings(self):
        it, *its = self.items
        if not self.needs_join:
            return it.bindings
        else:
            return super().bindings

    def __repr__(self):
        return super().__repr__() + str(self.items)


class ReferenceItem(Item):

    def __init__(self, request, ref):
        super().__init__(request, ref)


class IterItem(Item):

    def __init__(self, item):
        self.item = item
        self.op = None

    @property
    def bindingds(self):
        raise NotImplementedError

    def __radd__(self, other):
        if other != 0:
            raise ValueError("Expected add of zero for IterItem, "
                             "use simple things like `sum(Entity.attr)` only")
        self.op = 'sum'
        return self


def resolve_primary(items):
    """
    Reslove primary bindings for items, without joins.

    :return: list of binding
    """
    ss = []
    bs = defaultdict(list)

    for it in items:
        for b in it.bindings:
            if b.source not in ss:
                ss.append(b.source)
            bs[b.source].append(b)

    return [bs[s] for s in ss if len(bs[s]) == len(items)]


def resolve_joins(items, bindings):
    """
    Reslove bindings for joins aligned to bindings.

    :return: list of list of joins
    """
    for bs in bindings:
        joins = []
        for it, b in zip(items, bs):
            if it.needs_join:
                join = [b.binds.attr] + [i.item.attr for i in it.items]
                joins.append(resolve_primary(join))
            else:
                joins.append([None])

        for js in itertools.product(*joins):
            yield bs, js
