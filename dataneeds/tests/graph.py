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


class NodeListFormat(need.Source):
    N = Node()

    # id,label,edge-ids...
    (need.Here("0,A,0,1",
               "1,B,2,3,4",
               "2,C,",
               name='nlf') >>
     need.Sep(',', 2) >>
     need.Cons(N.id,
               N.label,
               need.Sep(',') >> need.Each(N.edges.id)))


class EdgeListFormat(need.Source):
    E = Edge()

    # id,weight,source,target
    (need.Here("0,.3,0,1",
               "1,.2,0,2",
               "2,.2,1,0",
               "3,1.,1,1",
               "4,.4,1,2",
               name='elf') >>
     need.Sep(',') >>
     need.Cons(E.id,
               E.weight,
               E.source.id,
               E.target.id))


class NodeEdgeFormat:
    N = Node()
    E = Edge()

    # node-id,laebl,edge-id:weight:target-id,...
    (need.Here("0,A,0:.3:1,1:.2:2",
               "1,B,2:.2:0,3:1.:1,4:.4:2",
               "2,C,",
               name='nef') >>
     need.Sep(',', 2) >>
     need.Cons(N.id / E.source.id,
               N.label,
               need.Sep(',') >> need.Each(
                   need.Sep(':') >> need.Cons(
                       E.id / N.edges.id,
                       E.weight,
                       E.target.id))))


# class EdgeNodeFormat:
#     E = Edge()
#     N = Node()
#
#     Ns = need.inferring(N)
#     Nt = need.inferring(N)
#
#     (need.Here("0,.3,0,'A',1,'B'",
#                "1,.2,0,'A',2,'C'",
#                "2,.2,1,'B',0,'A'",
#                "3,1.,1,'B',1,'B'",
#                "4,.4,1,'B',2,'C'",
#                name='enf') >>
#      need.Sep(',') >>
#      need.Cons(E.id,
#                E.weight,
#
#                E.source.id / Ns.id,
#                need.infer.Any() >> Ns.label,
#
#                E.target.id / Nt.id,
#                need.infer.Any() >> Nt.label))
