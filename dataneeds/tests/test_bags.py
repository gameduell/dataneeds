import dataneeds as need
from dask.async import get_sync


def test_dict():

    class Bar(need.Entity):
        baz = need.Dict(keys=need.String(), values=need.Integer())

    class BarSource:
        B = Bar()

        (need.Here("a: 42, b: 6, c: 23", "a: 12") >>
         need.Sep(', ') >> need.Each(need.Sep(': ')) >>
         B.baz)

    with need.request(Bar()) as B:
        B.baz

    (r, js), *_ = B.resolve_combined().values()

    e = need.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(B.items, r, js)
    expect = [({'a': 42, 'b': 6, 'c': 23},), ({'a': 12},)]

    assert bag.compute(get=get_sync) == expect

    class Foo:
        foo = need.String()
        bar = need.Integer()
        baz = need.Floating()
