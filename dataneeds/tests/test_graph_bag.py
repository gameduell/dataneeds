import dataneeds as need
import graph
from dask.async import get_sync


def test_execute():
    with need.request(graph.Node()) as N:
        N.id, N.label

    r1, r2 = N.resolve_primary().values()

    e = need.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(N.items, r1)

    assert bag.compute(get=get_sync) == [(0, 'A'), (1, 'B'), (2, 'C')]

    bag = e.resolve(N.items, r2)

    assert bag.compute(get=get_sync) == [(0, 'A'), (1, 'B'), (2, 'C')]

    with need.request(graph.Edge()) as E:
        E.source.id, E.target.id, E.weight

    r1, r2 = E.resolve_primary().values()

    bag = e.resolve(E.items, r1)
    expect = [(0, 1, 0.3), (0, 2, 0.2),
              (1, 0, 0.2), (1, 1, 1.0), (1, 2, 0.4)]
    assert bag.compute(get=get_sync) == expect

    bag = e.resolve(E.items, r2)
    assert bag.compute(get=get_sync) == expect


def test_resolve_join():
    with need.request(graph.Edge()) as E:
        E.source.label, E.target.label, E.weight

    ps = E.resolve_primary()
    assert(len(ps) == 2)

    p1, p2 = ps.values()
    assert p1[0].binds.general == graph.Edge.source.id
    assert p1[1].binds.general == graph.Edge.target.id
    assert p1[2].binds.general == graph.Edge.weight

    joins = E.resolve_joins()

    assert len(joins) == 4

    assert all(len(js) == 2 for js in joins.values())
    assert all(len(js) == 2 for js in joins.values())

    js0, js1 = joins[p1[0]][1].values()

    assert js0[0].binds.general == graph.Node.id
    assert js0[1].binds.general == graph.Node.label

    rs = E.resolve_combined()

    assert len(rs) == 8

    lookup = {(s.pattern, ja.pattern, jb.pattern): rr
              for (s, ja, jb), rr in rs.items()}

    elf = 'dataneeds/tests/*.elf'
    nlf = 'dataneeds/tests/*.nlf'
    nef = 'dataneeds/tests/*.nef'
    assert set(lookup.keys()) == {(elf, nlf, nlf),
                                  (elf, nlf, nef),
                                  (elf, nef, nlf),
                                  (elf, nef, nef),
                                  (nef, nlf, nlf),
                                  (nef, nlf, nef),
                                  (nef, nef, nlf),
                                  (nef, nef, nef)}

    r, js = lookup[elf, nlf, nlf]

    assert len(js) == 2

    e = need.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(E.items, r, js)
    expect = [('A', 'B', 0.3), ('A', 'C', 0.2),
              ('B', 'A', 0.2), ('B', 'B', 1.0), ('B', 'C', 0.4)]
    assert bag.compute(get=get_sync) == expect

    r, js = lookup[elf, nlf, nlf]

    for fs, (r, js) in lookup.items():
        bag = e.resolve(E.items, r, js)
        assert bag.compute(get=get_sync) == expect, "Edge-join for %s" % (fs,)

    with need.request(graph.Node()) as N:
        N.label, N.edges.weight

    lookup = {(s.pattern, j.pattern): rr
              for (s, j), rr in N.resolve_combined().items()}

    assert set(lookup.keys()) == {(nlf, elf), (nlf, nef),
                                  (nef, elf), (nef, nef)}

    r, js = lookup[nef, nef]

    e = need.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(N.items, r, js)
    # expect = [('A', [.3, .2]), ('B', [.2, 1., .4]), ('C', [])]
    expect = [('A', .3), ('A', .2), ('B', .2), ('B', 1.), ('B', .4)]

    assert bag.compute(get=get_sync) == expect

    for fs, (r, js) in lookup.items():
        bag = e.resolve(N.items, r, js)
        assert bag.compute(get=get_sync) == expect, "Node-join for %s" % (fs,)


def test_resolve_join_same():
    with need.request(graph.Edge()) as E:
        E.id, E.source.id, E.source.label, E.weight

    rs = E.resolve_combined()
    assert len(rs) == 4

    (r, js), *_ = rs.values()

    e = need.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(E.items, r, js)

    expect = [(0, 0, 'A', 0.3), (1, 0, 'A', 0.2),
              (2, 1, 'B', 0.2), (3, 1, 'B', 1.0), (4, 1, 'B', 0.4)]

    assert bag.compute(get=get_sync) == expect
