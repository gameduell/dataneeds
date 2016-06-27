from collections import defaultdict

import toolz

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
        try:
            return self.impls[typ]
        except KeyError as e:
            raise NotImplementedError("%s" % typ) from e


class Context:

    def __init__(self, impls):
        self.impls = impls
        self.bags = {}

    def __getitem__(self, node):
        if node not in self.bags:
            self.bags[node] = self.mk_bag(node)

        return self.bags[node]

    def mk_bag(self, node):
        bag = self.impls[type(node)](self, node)
        return bag


class InnerBag:

    def __init__(self, outer, ancher=None):
        self.outer = outer
        self.ancher = ancher or outer

    def map(self, f, **kws):
        f = toolz.curry(f, **kws)
        return InnerBag(self.outer.map(lambda inner: map(f, inner)),
                        self.ancher)


class DaskBagEngine:

    @classmethod
    def resolve(cls, items, primary, joins={}):
        ctx = Context(cls.impls)
        returns = []
        rix = {}

        for i, p in enumerate(primary):
            bag = ctx[p.binds]

            returns.append(bag)
            rix[p.binds.general] = 0, i

        exps = defaultdict(set)

        for r in returns:
            if isinstance(r, InnerBag):
                exps[r.ancher].add(r)

        for a, bs in exps.items():
            exp = a.map(len)

            returns = [(db.zip(exp, r).map(lambda n, c: [c] * n)
                        if r not in bs else r.outer).concat()
                       for r in returns]

        base = db.zip(*returns)

        if joins:
            base = base.map(lambda x: (x,))
        else:
            return base

        for n, (p, (ks, js)) in enumerate(joins.items()):
            for m, k in enumerate(ks):
                rix[k.item.general] = n + 1, m + 1

            add = cls.resolve(None, js)

            def fltr(i):
                return lambda ii: ii[0][0][i] == ii[1][0]

            def fltn():
                return lambda ii: ii[0] + (ii[1],)

            i = primary.index(p)
            base = (base
                    .product(add)
                    .filter(fltr(i))
                    .map(fltn()))

        ri = [rix[i.item.general] for i in items]

        return base.map(lambda ii: tuple(ii[n][m] for n, m in ri))

    impls = Impls()

    @impls
    def each(ctx, each: need.Each):
        bag = ctx[each.inner]
        if isinstance(bag, InnerBag):
            return bag.outer
        else:
            return bag

    @impls
    def each_part(ctx, part: need.Part[need.Each]):
        each = part.input
        return InnerBag(ctx[each.input])

    @impls
    def files(ctx, files: need.Files):
        return (db
                .from_filenames(files.pattern, **files.opts)
                .map(str.strip))

    @impls
    def here(ctx, here: need.Here):
        return db.from_sequence(here.content)

    @impls
    def json(ctx, json: need.Json):
        try:
            import ujson as js
        except ImportError:
            import js

        return ctx[json.input].map(js.loads)

    @impls
    def sep(ctx, sep: need.Sep):
        return (ctx[sep.input]
                .map(str.split, sep=sep.sep, maxsplit=sep.limit)
                .map(lambda x: [] if x == [''] else x))

    @impls
    def cons(ctx, part: need.Part[need.Cons]):
        cons = part.input
        return ctx[cons.input].pluck(part.id)

    @impls
    def named(ctx, part: need.Part[need.Named]):
        named = part.input
        return ctx[named.input].pluck(part.id)

    @impls
    def both(ctx, both: need.Same):
        return ctx[both.input]

    @impls
    def attr(ctx, attr: Attribute):
        return ctx[attr.input].map(attr.typ.__of__)

    @impls
    def reference(ctx, ref: Reference):
        return ctx[ref.input].map(ref.attr.typ.__of__)

    @impls
    def highest(ctx, high: need.infer.Highest):
        pass

resolve = DaskBagEngine.resolve
