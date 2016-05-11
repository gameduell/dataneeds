import pytest

import declare as dc


class Node(dc.Entity):
    id = dc.Number()
    label = dc.String()

    @dc.relate
    def edges(lower=0, upper=...):
        return Edge()


class Edge(dc.Entity):
    id = dc.Number()
    weight = dc.Number()

    @dc.relate
    def source():
        return Node()

    @dc.relate
    def target():
        return Node()


# Node List Format
# id,label,edge-ids...
# 0,A,0,1
# 1,B,2,3,4
# 2,C,

class NodeListFormat(dc.Source):
    N = Node()

    (dc.Files("tests/*.nlf") >>
     dc.Sep(',', 3) >>
     dc.Cons(N.id,
             N.label,
             dc.Sep(',') >> dc.Each(N.edges.id)))


# Edge List Format
# id,weight,source,target
# 0,.3,0,1
# 1,.2,0,2
# 2,.2,1,0
# 3,1.,1,1
# 4,.4,1,2

class EdgeListFormat(dc.Source):
    E = Edge()

    (dc.Files("tests/*.elf") >>
     dc.Sep(',') >>
     dc.Cons(E.id,
             E.weight,
             E.source.id,
             E.target.id))


# Node Edge Format
# node-id,laebl,edge-id:weight:target-id,...
# 0,A,0:.3:1,1:.2:2
# 1,B,2:.2:0,3:1.:1,4:.4:2
# 2,C,

class NodeEdgeFormat:
    N = Node()
    E = Edge()

    (dc.Files("tests/*.nef") >>
     dc.Sep(',', 3) >>
     ((N.id & E.source.id) + N.label + dc.Sep(',') >> dc.Each(
         dc.Sep('.') >> ((E.id & N.edges.id) + E.weight + E.target.id))))


def test_entities():
    n = Node()
    e = Edge()

    with pytest.raises(AttributeError):
        n.foobar

    assert isinstance(n.id.typ, dc.Number)
    assert isinstance(n.label.typ, dc.String)

    assert isinstance(n.edges.entity, Edge)  # XXX Relation

    assert isinstance(e.id.typ, dc.Number)
    assert isinstance(e.weight.typ, dc.Number)

    assert isinstance(e.source.entity, Node)  # XXX Relation
    assert isinstance(e.target.entity, Node)  # XXX Relation

    assert "test_graph" in repr(n.id)
    assert "Number" in repr(n.id)
    assert "Node" in repr(n.id)

    assert "test_graph.Node" in repr(n.edges.id)
    assert "test_graph.Edge.id" in repr(n.edges.id)


def test_binds():
    assert Node.__bindings__ is not Edge.__bindings__
    assert Node().__bindings__ is Node().__bindings__

    assert len(Node.__bindings__) == 2
    assert len(Edge.__bindings__) == 2

    nra, nrb = Node.__bindings__

    assert isinstance(nra, Node)
    assert isinstance(nrb, Node)
    assert nra != nrb
    assert len(nrb.inputs) == 3
    assert len(nra.inputs) == 3

    assert nra.id in nra.inputs
    assert nra.label in nra.inputs
    assert nra.edges.id in nra.inputs
    assert isinstance(nra.id.input, dc.Cons)
    assert nra.id.input == nra.label.input

    assert isinstance(nra.edges.id.input, dc.Each)
    assert isinstance(nra.edges.id.input.input, dc.Sep)
    assert nra.id.input == nra.edges.id.input.input.input

    assert isinstance(nra.id.input.input, dc.Sep)

    era, erb = Edge.__bindings__

    assert isinstance(era, Edge)
    assert isinstance(erb, Edge)
    assert era != erb
    assert len(era.inputs) == 4
    assert len(erb.inputs) == 4

    assert nrb.id.input == erb.source.id.input
    assert nrb.edges.id.input == erb.id.input


def test_resolve():
    resolve("Node[id, label, edges.id]")

    resolve("Edge[weight, source.label, target.label]")

    resolve("Node[label, sum(edges.weight)]")


    with resolving(Node) as N:
        (N.id, N.label, N.edges.id)

    with resloving(Edge) as E:
        (E.id, E.source.label, E.target.label)

    with resloving(Node) as N:
        (N.label, sum(N.edges.weight))
