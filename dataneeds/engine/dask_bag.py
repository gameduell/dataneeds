import operator

import dask.bag as db
import dataneeds as need

from ..entity import RelationKey
from ..types import Attribute

__impls__ = {}


class DaskBagEngine:
    # to unify subtrees with `Each`-nodes, we keep track of:
    # * items: the items already generated in the subtree
    # * expands: the length of the flattend each input
    # ```
    # a << ... << Each1 << ..
    #                       ` << Cons << ...
    # b << ... << Each2 << ..`
    # ```
    # So we start from node 'a', we add the item a to each node after a.
    # When we arrive 'Each1', the expansion `input1.map(len)` is also added to
    # all nodes behind Each1.
    # Then we start with the new item b, also put the item on each node
    # behind b. Again, when reaching Each2, we also add the expansion
    # `input2.map(len)` to nodes behind Each2.
    # Now when reaching 'Cons', we already have an item/expansion there,
    # so we have to unify item1/expansion1 with item2/expansion2:
    # We apply the expansion2 on the output of item1
    # and expansion1 for the input of the second path.
    # Now the expansion for the rest of the tree is expansion1 * expansion2,
    # and item is [item1, item2]
    # TB Verified

    #
    # ... <<< Each << ..
    #                   ` <<< ...
    # ... <<< Each << ..`

    def __init__(self):
        self.explodes = {}
        self.current = None
        self.items = []

    def impl(f):
        typ, = f.__annotations__.values()
        __impls__[typ] = f

    def resolve(self, items):
        return db.zip(*[self.bag_of(it.binds) for it in items])

    def bag_of(self, node):
        bag = __impls__[type(node)](self, node)

        explode = self.explodes.get(node)
        if explode:

            bag = db.zip(explode, bag).map(lambda n, i: [i] * n).concat()
            self.current = explode

        self.explodes[node] = self.current

        return bag

    @impl
    def each(self, each: need.Each):
        ins = self.bag_of(each.input)

        self.current = ins.map(len)
        for it in self.items:
            db.zip(self.current, it).map(lambda n, i: [i] * n).concat()

        return ins.concat()

    @impl
    def files(self, files: need.Files):
        return (db
                .from_filenames(files.pattern, compression=files.compression)
                .map(str.strip))

    @impl
    def sep(self, sep: need.Sep):
        ins = self.bag_of(sep.input)
        return ins.map(str.split, sep=sep.sep, maxsplit=sep.limit)

    @impl
    def cons(self, cons: need.Cons):
        return self.bag_of(cons.input)

    @impl
    def cons_item(self, cons_item: need.Part):
        ins = self.bag_of(cons_item.input)
        return ins.map(operator.itemgetter(cons_item.id))

    @impl
    def both(self, both: need.Both):
        return self.bag_of(both.input)

    @impl
    def attr(self, attr: Attribute):
        ins = self.bag_of(attr.input)
        return ins.map(attr.typ.__of__)

    @impl
    def key(self, key: RelationKey):
        ins = self.bag_of(key.input)
        i = key.input.outputs.index(key)
        return ins.pluck(i)
