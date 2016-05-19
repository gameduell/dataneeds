import dask.bag as db
import dataneeds as need

from ..entity import RelationKey
from ..types import Attribute


class FilesImpl:

    def __init__(self, files: need.Files):
        self.files = files

    @property
    def bag(self):
        return db.from_textfiles(self.files.pattern,
                                 compression=self.files.compression)


class SepImpl:

    def __init__(self, sep: need.Sep):
        self.sep = sep

    @property
    def bag(self):
        ins = self.sep.input
        return ins.bag.map(str.split, sep=self.sep.sep, limit=self.sep.limit)


__impls__ = {}


class DaskBagEngine:

    def impl(f):
        typ, = f.__annotations__.values()
        __impls__[typ] = f

    @impl
    def files(self, files: need.Files):
        return (db
                .from_filenames(files.pattern, compression=files.compression)
                .map(str.strip))

    @impl
    def sep(self, sep: need.Sep):
        ins = self.bag(sep.input)
        return ins.map(str.split, sep=sep.sep, maxsplit=sep.limit)

    @impl
    def each(self, each: need.Each):
        ins = self.bag(each.input)
        return ins.concat()

    @impl
    def cons(self, cons: need.Cons):
        return self.bag(cons.input)

    @impl
    def both(self, both: need.Both):
        return self.bag(both.input)

    @impl
    def attr(self, attr: Attribute):
        ins = self.bag(attr.input)
        if isinstance(ins, need.Both):
            ins = ins.input
        i = attr.input.outputs.index(attr)
        return ins.pluck(i).map(attr.typ.__of__)

    @impl
    def key(self, key: RelationKey):
        ins = self.bag(key.input)
        i = key.input.outputs.index(key)
        return ins.pluck(i)

    def bag(self, what):
        return __impls__[type(what)](self, what)

    def resolve(self, items):
        return db.zip(*[self.bag(it.binds) for it in items])
