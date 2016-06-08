import operator

import dask.bag as db
import dataneeds as need

from ..entity import Reference
from ..types import Attribute


class Impls:

    def __init__(self):
        self.impls = {}

    def __call__(self, method):
        typ, = method.__annotations__.values()
        self.impls[typ] = method

    def __getitem__(self, typ):
        return self.impls[typ]


class Context:

    def __init__(self, impls):
        self.impls = impls
        self.returns = []
        self.explode = None
        self.explodes = {}

        self.bags = {}

    def __getitem__(self, node):
        if node not in self.bags:
            self.bags[node] = self.mk_bag(node)

        return self.bags[node]

    def mk_bag(self, node):
        bag = self.impls[type(node)](self, node)

        explode = self.explodes.get(node)
        if explode:
            bag = db.zip(explode, bag).map(lambda n, i: [i] * n).concat()
            self.explode = explode

        self.explodes[node] = self.explode
        return bag

    def add_explode(self, expl):
        self.explode = expl.map(len)
        self.returns = [(db
                         .zip(self.explode, it)
                         .map(lambda n, i: [i] * n)
                         .concat()) for it in self.returns]


class DaskBagEngine:

    def resolve(self, returns, primary, joins={}):
        ctx = Context(self.impls)

        rix = {}

        for i, p in enumerate(primary):
            bag = ctx[p.binds]
            ctx.returns.append(bag)
            rix[p.binds.general] = 0, i

        base = db.zip(*ctx.returns)

        if joins:
            base = base.map(lambda x: (x,))
        else:
            return base

        for n, (p, (ks, js)) in enumerate(joins.items()):
            for m, k in enumerate(ks):
                rix[k.item.general] = n + 1, m + 1

            add = self.resolve(None, js)

            def fltr(i):
                return lambda ii: ii[0][0][i] == ii[1][0]

            def fltn():
                return lambda ii: ii[0] + (ii[1],)

            i = primary.index(p)
            base = (base
                    .product(add)
                    .filter(fltr(i))
                    .map(fltn()))

        ri = [rix[r.item.general] for r in returns]

        return base.map(lambda ii: tuple(ii[n][m] for n, m in ri))

        for p in primary:
            bag = ctx[p.binds]

        return db.zip(*ctx.returns)

    impls = Impls()

    @impls
    def each(ctx, each: need.Each):
        ctx.add_explode(ctx[each.input])
        return ctx[each.input].concat()

    @impls
    def files(ctx, files: need.Files):
        return (db
                .from_filenames(files.pattern, **files.opts)
                .map(str.strip))

    @impls
    def sep(ctx, sep: need.Sep):
        return (ctx[sep.input]
                .map(str.split, sep=sep.sep, maxsplit=sep.limit)
                .map(lambda x: [] if x == [''] else x))

    @impls
    def cons(ctx, cons: need.Cons):
        return ctx[cons.input]

    @impls
    def part(ctx, part: need.Part):
        return ctx[part.input].map(operator.itemgetter(part.id))

    @impls
    def both(ctx, both: need.All):
        return ctx[both.input]

    @impls
    def attr(ctx, attr: Attribute):
        return ctx[attr.input].map(attr.typ.__of__)

    @impls
    def reference(ctx, ref: Reference):
        return ctx[ref.input].map(ref.attr.typ.__of__)
