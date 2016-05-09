import pytest

import declare as dc


class Node(dc.Entity):
    id = dc.Number()
    label = dc.String()

    @dc.relate(0, ...)
    def edges():
        return Edge()


class Edge(dc.Entity):
    id = dc.Number()
    weight = dc.Number()

    @dc.relate(1)
    def source():
        return Node()

    @dc.relate(1)
    def target():
        return Node()


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

    assert "Number" in repr(n.id)
    assert "Node" in repr(n.id)


# Node List Format
# id,label,edge-ids...
# 0,A,0,1
# 1,B,2,3,4
# 2,C,

class NodeListFormat(dc.Source):
    N = Node()

    (dc.Files("*.nlf") >>
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

    (dc.Files("*.elf") >>
     dc.Sep(',') >>
     dc.Cons(E.id,
             E.weight,
             E.source.id,
             E.target.id))


def test_binds():

    assert Node.__bindings__ is not Edge.__bindings__
    assert Node().__bindings__ is Node().__bindings__

    assert len(Node.__bindings__) == 2
    assert len(Edge.__bindings__) == 2


def test_resolve():
    dc.resolve(Node)
    dc.resolve(Edge)


# Node Edge Format
# node-id,laebl,edge-id:weight:target-id,...
# 0,A,0:.3:1,1:.2:2
# 1,B,2:.2:0,3:1.:1,4:.4:2
# 2,C,

class NodeEdgeFormat:
    N = Node()
    E = Edge()
    (dc.Files("*.nef") >>
     dc.Sep(',', 3) >>
     dc.Cons(dc.Both(N.id, E.source),
             N.label,
             dc.Sep(',') >> dc.Each(
                  dc.Sep('.') >> dc.Cons(dc.Both(E.id, N.edges.id),
                                         E.weight,
                                         E.target))))
