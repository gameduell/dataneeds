from collections import defaultdict

import declares as dc


class Engine:
    def __init__(self):
        self.outs = defaultdict(list)
        self.ins = defaultdict(list)

    def register(self, impl):
        self.ins[impl.__in__].append(impl)
        self.outs[impl.__out__].append(impl)

    def resolve(self, what, path=()):
        # XXX avoid circles
        if what.__in__ is None:
            yield path + (what,)
        for Impl in self.outs[what.__in__]:
            yield from self.resolve(Impl, path+(what,))

    def reslove_rec(self, rec: dc.Record, **options):
        raise NotImplementedError

    def resolve_entity(self, entity: dc.Entity, **options):
        raise NotImplementedError
