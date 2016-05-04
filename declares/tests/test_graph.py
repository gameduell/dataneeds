import pytest

import declares as dc
from declares.tests import graph


def test_entities():
    n = graph.Node()
    e = graph.Edge()

    with pytest.raises(AttributeError):
        n.foobar

    assert isinstance(n.id, dc.Number)
    assert isinstance(n.label, dc.String)
    assert isinstance(n.edges, dc.Set)
    assert isinstance(n.edges.inner, graph.Edge)

    assert isinstance(e.id, dc.Number)
    assert isinstance(e.weight, dc.Number)
    assert isinstance(e.source, graph.Node)
    assert isinstance(e.target, graph.Node)


def test_resolve():
    dc.resolve(graph.Node)
    dc.resolve(graph.Edge)
