import declares as dc


class Node(dc.Entity):
    def __init__(self):
        super().__init__()
        self.id = dc.Number()
        self.label = dc.String()

    def __connect__(self):
        self.edges = dc.Set(Edge())


class Edge(dc.Entity):
    def __init__(self):
        super().__init__()
        self.id = dc.Number()
        self.weight = dc.Number()

    def __connect__(self):
        self.source = Node()
        self.target = Node()


# Node List Format
# id,label,edge-ids...
# 0,A,0,1
# 1,B,2,3,4
# 2,C,

class NodeListFormat:
    N = Node()

    (dc.Files("*.nlf") >>
     dc.Sep(',', 3) >>
     dc.Cons(N.id,
             N.label,
             dc.Sep(',') >> dc.Each(N.edges.inner.id)))


# Edge List Format
# id,weight,source,target
# 0,.3,0,1
# 1,.2,0,2
# 2,.2,1,0
# 3,1.,1,1
# 4,.4,1,2

class EdgeListFormat:
    E = Edge()

    (dc.Files("*.elf") >>
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

    (dc.Files("*.nef") >>
     dc.Sep(',', 3) >>
     dc.Cons(N.id & E.source,
             N.label,
             dc.Sep(',') >> dc.Each(
                 dc.Sep('.') >> dc.Cons(E.id & N.edges.inner.id,
                                        E.weight,
                                        E.target))))
