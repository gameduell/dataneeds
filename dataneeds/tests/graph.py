import dataneeds as need


class Node(need.Entity):
    id = need.Integer()
    label = need.String()

    @need.relate
    def edges(lower=0, upper=...):
        return Edge()


class Edge(need.Entity):
    id = need.Integer()
    weight = need.Floating()

    @need.relate
    def source():
        return Node()

    @need.relate
    def target():
        return Node()


# Node List Format
# id,label,edge-ids...
# 0,A,0,1
# 1,B,2,3,4
# 2,C,

class NodeListFormat(need.Source):
    N = Node()

    (need.Files("dataneeds/tests/*.nlf") >>
     need.Sep(',', 2) >>
     need.Cons(N.id,
               N.label,
               need.Sep(',') >> need.Each(N.edges.id)))


# Edge List Format
# id,weight,source,target
# 0,.3,0,1
# 1,.2,0,2
# 2,.2,1,0
# 3,1.,1,1
# 4,.4,1,2

class EdgeListFormat(need.Source):
    E = Edge()

    (need.Files("dataneeds/tests/*.elf") >>
     need.Sep(',') >>
     need.Cons(E.id,
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

    (need.Files("dataneeds/tests/*.nef") >>
     need.Sep(',', 2) >>
     need.Cons(N.id / E.source.id,
               N.label,
               need.Sep(',') >> need.Each(
                   need.Sep(':') >> need.Cons(
                       E.id / N.edges.id,
                       E.weight,
                       E.target.id))))
