import dataneeds as need
import dataneeds.engine.dask_bag


class Foo(need.Entity):
    id = need.Integer()

    begin = need.Timestamp()
    end = need.Timestamp()

    @need.relate
    def bars(self, lower=0, upper=None):
        return Bar()


class Bar(need.Entity):
    time = need.Timestamp()
    label = need.String()

    foo = Foo()


class Grouping:
    F = Foo()
    B = Bar()

    (need.Here("0,7:14,getting up",
               "0,7:30,breakfast",
               "1,9:50,getting up",
               "0,8:00,bike",
               "1,10:00,station",
               "0,10:02,station",
               "1,10:05,train",
               "0,10:05,train") >>
     need.Sep(',') >>
     need.Cons(B.foo.id / need.infer.By() >> F.id,
               B.time /
               need.infer.Lowest() >> F.begin,
               need.infer.Highest() >> F.end,
               B.label))


def test_group():
    with need.request(Foo) as F:
        F.id, F.begin, F.end

    rqs = F.resolve_primary()
    assert len(rqs) == 1

    rq, *_ = rqs.values()
    assert len(rq) == 3

    e = dataneeds.engine.dask_bag.DaskBagEngine()
    bag = e.resolve(F.items, rq, {})

    assert bag.compute() == [(0, "7:14", "10:05")
                             (1, "9:50", "10:05")]
