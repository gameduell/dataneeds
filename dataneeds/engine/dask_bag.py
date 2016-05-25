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

    impls = Impls()

    def resolve(self, items):
        ctx = Context(self.impls)

        for it in items:
            bag = ctx[it.binds]
            ctx.returns.append(bag)

        return db.zip(*ctx.returns)

    @impls
    def each(ctx, each: need.Each):
        ctx.add_explode(ctx[each.input])
        return ctx[each.input].concat()

    @impls
    def files(ctx, files: need.Files):
        return (db
                .from_filenames(files.pattern, compression=files.compression)
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
    def both(ctx, both: need.Both):
        return ctx[both.input]

    @impls
    def attr(ctx, attr: Attribute):
        return ctx[attr.input].map(attr.typ.__of__)

    @impls
    def reference(ctx, ref: Reference):
        return ctx[ref.input].map(ref.attr.typ.__of__)
