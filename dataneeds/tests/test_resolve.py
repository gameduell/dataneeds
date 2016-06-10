import pytest

import dataneeds as need
import graph


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
    assert isinstance(e.input, need.Part[need.Each])
    assert isinstance(e.input.input.input, need.Sep)
    assert a.input.input == e.input.input.input.input.input

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
    rs = N.resolve_primary()

    assert(len(rs) == 2)

    (s0, bs0), (s1, bs1) = rs.items()

    assert isinstance(s0, need.Files)
    assert isinstance(s1, need.Files)
    assert s0 != s1

    assert all(b.source == s0 for b in bs0)
    assert all(b.source == s1 for b in bs1)

    assert N.resolve_joins() == {}

    with need.request(graph.Edge()) as E:
        E.id, E.weight, E.source.id, E.target.id

    rs = E.resolve_primary()
    assert all(len(r) == 4 for r in rs.values())
    assert len(rs) == 2
    assert E.resolve_joins() == {}


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


def test_resolve_join_same():
    with need.request(graph.Edge()) as E:
        E.id, E.source.id, E.source.label, E.weight

    rs = E.resolve_combined()
    assert len(rs) == 4
