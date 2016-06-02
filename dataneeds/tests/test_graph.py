import pytest

import dataneeds as need
import graph
from dask.async import get_sync
from dataneeds.engine.dask_bag import DaskBagEngine


def test_entities():
    n = graph.Node()
    e = graph.Edge()

    with pytest.raises(AttributeError):
        n.foobar

    with pytest.raises(AttributeError):
        n.edges.baz

    assert isinstance(n.id.typ, need.Integer)
    assert isinstance(n.label.typ, need.String)

    assert isinstance(n.edges.towards, graph.Edge)  # XXX Relation

    assert isinstance(e.id.typ, need.Integer)
    assert isinstance(e.weight.typ, need.Floating)

    assert isinstance(e.source.towards, graph.Node)  # XXX Relation
    assert isinstance(e.target.towards, graph.Node)  # XXX Relation

    assert "graph" in repr(n.id)
    assert "Integer" in repr(n.id)
    assert "Node" in repr(n.id)
    assert "id" in repr(n.id)

    assert "graph.Node" in repr(n.edges.id)
    assert "graph.Edge" in repr(n.edges.id)
    assert "id" in repr(n.edges.id)


def test_binds():
    assert graph.Node().id.bindings == graph.Node.id.bindings
    assert graph.Edge.id.bindings != graph.Node.id.bindings
    assert graph.Node.label.bindings != graph.Node.id.bindings
    assert graph.Node.edges.id.bindings != graph.Node.id.bindings

    assert len(graph.Node.id.bindings) == 2
    assert len(graph.Node.edges.id.bindings) == 2
    assert len(graph.Edge.weight.bindings) == 2

    a, b = graph.Node.id.bindings

    assert "Node" in str(a)
    assert "Node" in str(b)
    assert "id" in str(a)
    assert "id" in str(b)
    assert a != b

    assert isinstance(a.input, need.Part)
    assert isinstance(a.input.input, need.Cons)
    assert a.input.input == graph.Node.label.bindings[0].input.input

    e = graph.Node.edges.id.bindings[0]
    assert isinstance(e.input, need.Each)
    assert isinstance(e.input.input, need.Sep)
    assert a.input.input == e.input.input.input.input

    assert isinstance(a.input.input.input, need.Sep)

    c = graph.Edge.source.id.bindings[1]

    assert c.input == b.input

    from dataneeds.entity import Relation, Reference
    assert isinstance(graph.Node.edges.target, Relation)
    assert isinstance(graph.Node.edges.target.label, Reference)


def test_request():
    with need.request(graph.Node()) as N:
        N.id, N.label, N.edges.id

    assert len(N.items) == 3

    with need.request(graph.Edge()) as E:
        E.id, E.weight, E.source.label, E.target.label

    assert len(E.items) == 4

    with need.request(graph.Node()) as N:
        N.label, sum(N.edges.weight)

    assert len(N.items) == 2


def test_resolve():
    with need.request(graph.Node()) as N:
        N.id, N.label
    rs = N.resolve()

    assert(len(rs) == 2)

    (a, c), (b, d) = rs

    assert isinstance(a[0].source, need.Files)
    assert isinstance(b[0].source, need.Files)

    assert all(ai.source == a[0].source for ai in a)
    assert all(bi.source == b[0].source for bi in b)
    assert a[0].source != b[0].source

    assert c == (None, None)
    assert d == (None, None)

    with need.request(graph.Edge()) as E:
        E.id, E.weight, E.source.id, E.target.id

    rs = E.resolve()
    assert rs
    assert(len(rs) == 2)


def test_execute():
    with need.request(graph.Node()) as N:
        N.id, N.label

    (r1, j1), (r2, j1) = N.resolve()

    e = DaskBagEngine()
    bag = e.resolve(r1)

    assert bag.compute(get=get_sync) == [(0, 'A'), (1, 'B'), (2, 'C')]

    bag = e.resolve(r2)

    assert bag.compute(get=get_sync) == [(0, 'A'), (1, 'B'), (2, 'C')]

    with need.request(graph.Edge()) as E:
        E.source.id, E.target.id, E.weight

    (r1, j1), (r2, j2) = E.resolve()

    bag = e.resolve(r1)
    expect = [(0, 1, 0.3), (0, 2, 0.2),
              (1, 0, 0.2), (1, 1, 1.0), (1, 2, 0.4)]
    assert bag.compute(get=get_sync) == expect

    bag = e.resolve(r2)
    assert bag.compute(get=get_sync) == expect


def test_resolve_join():
    with need.request(graph.Edge()) as E:
        E.source.label, E.target.label, E.weight

    rs = E.resolve()
    assert(len(rs) == 8)

    resolves = {}

    for rr in rs:
        rp, (js1, js2, _) = rr
        sr, s1, s2 = rp[0].source, js1[0].source, js2[0].source

        assert len(rp) == 3
        assert len(js1) == 2
        assert len(js2) == 2

        assert _ is None
        assert all(r.source == sr for r in rp)
        assert all(j.source == s1 for j in js1)
        assert all(j.source == s2 for j in js2)

        resolves[sr.pattern, s1.pattern, s2.pattern] = rr

    elf = 'dataneeds/tests/*.elf'
    nlf = 'dataneeds/tests/*.nlf'
    nef = 'dataneeds/tests/*.nef'
    assert set(resolves) == {(elf, nlf, nlf),
                             (elf, nlf, nef),
                             (elf, nef, nlf),
                             (elf, nef, nef),
                             (nef, nlf, nlf),
                             (nef, nlf, nef),
                             (nef, nef, nlf),
                             (nef, nef, nef)}

    e = DaskBagEngine()
    bag = e.resolve(*resolves[elf, nlf, nlf])
    expect = [('A', 'B', 0.3), ('A', 'C', 0.2),
              ('B', 'A', 0.2), ('B', 'B', 1.0), ('B', 'C', 0.4)]
    assert bag.compute(get=get_sync) == expect
