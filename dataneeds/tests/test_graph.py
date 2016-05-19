import pytest

import dataneeds as need
from dask.async import get_sync
from dataneeds.engine.dask_bag import DaskBagEngine


@pytest.fixture
def graph():
    import graph
    return graph


def test_graph():
    import graph

    assert graph.Node
    assert graph.Edge


def test_entities(graph):
    n = graph.Node()
    e = graph.Edge()

    with pytest.raises(AttributeError):
        n.foobar

    with pytest.raises(AttributeError):
        n.edges.baz

    assert isinstance(n.id.typ, need.Number)
    assert isinstance(n.label.typ, need.String)

    assert isinstance(n.edges.towards, graph.Edge)  # XXX Relation

    assert isinstance(e.id.typ, need.Number)
    assert isinstance(e.weight.typ, need.Number)

    assert isinstance(e.source.towards, graph.Node)  # XXX Relation
    assert isinstance(e.target.towards, graph.Node)  # XXX Relation

    assert "graph" in repr(n.id)
    assert "Number" in repr(n.id)
    assert "Node" in repr(n.id)
    assert "id" in repr(n.id)

    assert "graph.Node" in repr(n.edges.id)
    assert "graph.Edge().id" in repr(n.edges.id)


def test_binds(graph):
    assert graph.Node().id.bindings == graph.Node.id.bindings
    assert graph.Edge.id.bindings != graph.Node.id.bindings
    assert graph.Node.label.bindings != graph.Node.id.bindings
    assert graph.Node.edges.bindings != graph.Node.id.bindings

    assert len(graph.Node.id.bindings) == 2
    assert len(graph.Node.edges.bindings) == 2
    assert len(graph.Edge.weight.bindings) == 2

    a, b = graph.Node.id.bindings

    assert "Node" in str(a)
    assert "Node" in str(b)
    assert "id" in str(a)
    assert "id" in str(b)
    assert a != b

    assert isinstance(a.input, need.Cons)
    assert a.input == graph.Node.label.bindings[0].input

    e = graph.Node.edges.bindings[0]
    assert isinstance(e.input, need.Each)
    assert isinstance(e.input.input, need.Sep)
    assert a.input == e.input.input.input

    assert isinstance(a.input.input, need.Sep)

    c = graph.Edge.source.bindings[1]

    assert c.input == b.input


def test_request(graph):
    with need.request(graph.Node()) as N:
        N.id, N.label, N.edges.id

    assert len(N.items) == 3

    with need.request(graph.Edge()) as E:
        E.id, E.weight, E.source.label, E.target.label

    assert len(E.items) == 4

    with need.request(graph.Node()) as N:
        N.label, sum(N.edges.weight)

    assert len(N.items) == 2


def test_resolve(graph):
    with need.request(graph.Node()) as N:
        N.id, N.label
    rs = N.resolve()

    assert(len(rs) == 2)

    a, b = rs

    assert isinstance(a[0].source, need.Files)
    assert isinstance(b[0].source, need.Files)

    assert all(ai.source == a[0].source for ai in a)
    assert all(bi.source == b[0].source for bi in b)
    assert a[0].source != b[0].source

    with need.request(graph.Edge()) as E:
        E.id, E.weight, E.source.label  # , E.target.label

    rs = E.resolve()
    assert rs
    # assert(len(rs) == 1)


def test_execute(graph):
    with need.request(graph.Node()) as N:
        N.id, N.label

    r, _ = N.resolve()
    # N.execute()
    e = DaskBagEngine()
    bag = e.resolve(r)

    assert bag.compute(get=get_sync) == [(0, 'A'), (1, 'B'), (2, 'C')]
    assert bag.compute() == [(0, 'A'), (1, 'B'), (2, 'C')]


@pytest.mark.xfail
def test_resolve_join(self):
    with need.request(graph.Edge()) as E:
        E.id, E.weight, E.source.label, E.target.label

    rs = E.resolve()
    assert(len(rs) == 1)
