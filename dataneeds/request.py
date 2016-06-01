import contextlib
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

    def resolve(self, items=None):
        if items is None:
            items = self.items

        sources = []
        bindings = defaultdict(list)

        for it in items:
            for b in it.bindings:
                if b.source not in sources:
                    sources.append(b.source)
                bindings[b.source].append((b, it))

        complete = []
        for src in sources:
            bs = bindings[src]
            if len(bs) == len(items):
                if bs not in complete:
                    complete.append(src)

        if not complete:
            raise NotImplementedError("Resolve with %s" % bindings)

        joins = defaultdict(list)
        for src in complete:
            for b, it in bindings[src]:
                if isinstance(it, RelationItem):
                    join = [i.item.attr for i in it.items] + [b.binds.attr]
                    joins[src] = self.resolve(join)

        return [[b for b, it in bindings[src]] for src in complete]

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

    def __repr__(self):
        return super().__repr__() + str(self.items)


class ReferenceItem(Item):

    def __init__(self, request, ref):
        super().__init__(request, ref)

    @property
    def bindingds(self):
        raise NotImplementedError


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
