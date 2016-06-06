import contextlib
import itertools as it
from collections import OrderedDict, defaultdict

from .binds import Bindings
from .entity import Reference, Relation
from .types import Attribute


@contextlib.contextmanager
def request(entity, **options):
    yield Request(entity, **options)


class Request:

    def __init__(self, entity, **options):
        self.entity = entity
        self.options = options

        self.returns = []

    def returning(self, by, item):
        if self.returns[-1:] == [by]:
            self.returns.pop(-1)
        self.returns.append(item)
        return item

    def resolve_bindings(self, bindings):
        """
        Group bindings list by there source.

        :param bindings: list of Bindings for some itmes
        :returns: OrderedDcit from source to list of Binding
        """
        resolved = OrderedDict()

        for bs in bindings:
            for b in bs:
                resolved.setdefault(b.source, []).append(b)

        return OrderedDict((s, bs)
                           for s, bs in resolved.items()
                           if len(bs) == len(bindings))

    def resolve_primary(self):
        return self.resolve_bindings([it.primary for it in self.returns])

    def resolve_joins(self):
        joins = defaultdict(list)

        for ret in self.returns:
            if ret.joins:
                for p in ret.primary:
                    if p.binds.general != ret.item.general:
                        joins[p].append(ret)

        return {p: self.resolve_bindings([p.binds.attr.bindings] +
                                         [it.joins for it in its])
                for p, its in joins.items()}

    def resolve_combined(self):
        ps = self.resolve_primary()
        joins = self.resolve_joins()

        return OrderedDict(((s,) + tuple(j[0] for j in js),
                            (bs,) + tuple(j[1] for j in js))
                           for s, bs in ps.items()
                           for js in it.product(*[joins[b].items()
                                                  for b in bs if b in joins]))

    def __getattr__(self, name):
        field = getattr(self.entity, name)

        if isinstance(field, Attribute):
            item = AttrItem(self, field)
        elif isinstance(field, Relation):
            item = RelationItem(self, field)
        else:
            raise ValueError("Don't know how to request a %r" % type(field))

        return self.returning(None, item)


class Item:

    def __init__(self, request, item, *args, **kws):
        super().__init__(*args, **kws)
        self.request = request
        self.item = item

    @property
    def primary(self):
        return self.item.bindings

    @property
    def joins(self):
        return Bindings()

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
            item = ReferenceItem(self.request, ref, self)
        elif isinstance(ref, Relation):
            item = RelationItem(self.request, ref)
        else:
            raise AttributeError('No request to {} ({}) through relations'
                                 .format(name, type(ref)))

        return self.request.returning(self, item)

    def __repr__(self):
        return super().__repr__() + str(self.items)


class ReferenceItem(Item):

    def __init__(self, request, ref, parent):
        super().__init__(request, ref)
        self.parent = parent

    @property
    def primary(self):
        return self.parent.primary

    @property
    def joins(self):
        return self.item.attr.bindings


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
