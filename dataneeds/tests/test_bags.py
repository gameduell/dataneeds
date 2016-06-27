import dataneeds as need
import dataneeds.engine.dask_bag
from dask.async import get_sync


def test_dict():

    class Bar(need.Entity):
        baz = need.Dict(keys=need.String(), values=need.Integer())

    class BarSource:
        B = Bar()

        (need.Here("a: 42, b: 6, c: 23",
                   "a: 12") >>
         need.Sep(', ') >> need.Each(need.Sep(': ')) >>
         B.baz)

    with need.request(Bar()) as B:
        B.baz

    (r, js), *_ = B.resolve_combined().values()

    e = dataneeds.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(B.items, r, js)
    expect = [({'a': 42, 'b': 6, 'c': 23},), ({'a': 12},)]

    assert bag.compute(get=get_sync) == expect

    class Foo:
        foo = need.String()
        bar = need.Integer()
        baz = need.Floating()


def test_simple_json():
    class Foo(need.Entity):
        id = need.Integer()
        bar = need.Boolean()
        baz = need.String()

    class FooFormat:
        (need.Here('{"id": 0, "bar": true, "baz": "abc"}',
                   '{"id": 1, "bar": true, "baz": "def"}',
                   '{"id": 2, "bar": false, "baz": ""}',
                   name="FooJson") >>
         need.Json() >> Foo())

    with need.request(Foo()) as F:
        F.id, F.bar, F.baz

    rs = F.resolve_primary()

    assert len(rs) == 1

    r, = rs.values()

    import dataneeds.engine.dask_bag as eng

    bag = eng.resolve(F.items, r)
    assert bag

    assert bag.compute(get=get_sync) == [(0, True, "abc"),
                                         (1, True, "def"),
                                         (2, False, "")]
