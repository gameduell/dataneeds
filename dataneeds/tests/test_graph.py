import pytest

import dataneeds as need


@pytest.fixture
def graph():
    import graph
    return graph


def test_entities(graph):
    n = graph.Node()
    e = graph.Edge()

    with pytest.raises(AttributeError):
        n.foobar

    assert isinstance(n.id.typ, need.Number)
    assert isinstance(n.label.typ, need.String)

    assert isinstance(n.edges.entity, graph.Edge)  # XXX Relation

    assert isinstance(e.id.typ, need.Number)
    assert isinstance(e.weight.typ, need.Number)

    assert isinstance(e.source.entity, graph.Node)  # XXX Relation
    assert isinstance(e.target.entity, graph.Node)  # XXX Relation

    assert "graph" in repr(n.id)
    assert "Number" in repr(n.id)
    assert "Node" in repr(n.id)

    assert "graph.Node" in repr(n.edges.id)
    assert "graph.Edge.id" in repr(n.edges.id)


def test_binds(graph):
    assert graph.Node.__bindings__ is not graph.Edge.__bindings__
    assert graph.Node().__bindings__ is graph.Node().__bindings__

    assert len(graph.Node.__bindings__) == 2
    assert len(graph.Edge.__bindings__) == 2

    nra, nrb = graph.Node.__bindings__

    assert isinstance(nra, graph.Node)
    assert isinstance(nrb, graph.Node)
    assert nra != nrb
    assert len(nrb.inputs) == 3
    assert len(nra.inputs) == 3

    assert nra.id in nra.inputs
    assert nra.label in nra.inputs
    assert nra.edges.id in nra.inputs
    assert isinstance(nra.id.input, need.Cons)
    assert nra.id.input == nra.label.input

    assert isinstance(nra.edges.id.input, need.Each)
    assert isinstance(nra.edges.id.input.input, need.Sep)
    assert nra.id.input == nra.edges.id.input.input.input

    assert isinstance(nra.id.input.input, need.Sep)

    era, erb = graph.Edge.__bindings__

    assert isinstance(era, graph.Edge)
    assert isinstance(erb, graph.Edge)
    assert era != erb
    assert len(era.inputs) == 4
    assert len(erb.inputs) == 4

    assert nrb.id.input == erb.source.id.input
    assert nrb.edges.id.input == erb.id.input


def test_request(graph):
    with need.request(graph.Node()) as N:
        N.id
        N.label
        N.edges.id
    assert len(N.items) == 3

    with need.request(graph.Edge()) as E:
        E.id
        E.weight
        E.source.label
        E.target.label
    assert len(E.items) == 4

    with need.request(graph.Node()) as N:
        N.label
        sum(N.edges.weight)
    assert len(N.items) == 2


def test_reslove(graph):
    with need.request(graph.Node()) as N:
        N.id, N.label
    N.reslove()
