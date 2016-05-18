import dask.bag as db
import dataneeds as need

from .engine import Engine, impl


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


class DaskBagEngine(Engine):

    @impl
    def files(self, files: need.Files):
        return db.from_textfiles(files.pattern,
                                 compression=files.compression)

    @impl
    def sep(self, sep: need.Sep):
        ins = self.resolve(sep.input)
        return ins.map(str.split, sep=sep.sep, limit=sep.limit)

    @impl
    def cons(self, cons: need.Cons):
        cons.types

    def resolve(self, items):
        inputs = {it.input for it in items}
        ins = items + inputs
        return ins.bag

        # either we lokk for common nodes and start from there

        # or we iter through items, and join common selectors
        # files >> sep >> cons >> a/0
        # \ files.map(sep)
        #                       \.pluck(0)
        # files >> sep >> cons >> b/1
        # \ files.map(sep)
        #                       \.pluck(1)
        # = files.map(sep).pluck(0,1)
