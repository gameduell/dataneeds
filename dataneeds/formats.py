from .binds import Binds, Part


class Format(Binds):

    def __bind__(self, input):
        return NotImplemented

    @property
    def __out__(self):
        return ()


class Either(Format):

    def __init__(self, *formats):
        self.formats = formats

    def __bind__(self, input):
        for fmt in self.formats:
            self >> fmt

    @property
    def __out__(self):
        return (self.inputself.__out__,)

    def __str__(self):
        return "|".join(map(str, self.formats))

    def __repr__(self):
        return "Either({})".format(", ".join(map(repr, self.formats)))


class Each(Format):
    __outputs__ = None

    def __init__(self, inner):
        self.inner = inner

    def __bind__(self, input):
        Part[Each](self, None) >> self.inner

    def __str__(self):
        return "Each"

    def __repr__(self):
        return "Each({!r})".format(self.inner)


class Re(Format):

    def __init__(self, exp):
        import re
        self.re = re.compile(exp)

    def __bind__(self, input):
        # assert input.__out__ == str
        pass

    @property
    def __out__(self):
        if self.re.groupindex:
            names = {i: n for n, i in self.re.groupindex}
            return [(names.get(i + 1, None), str) for i in range(self.groups)]
        else:
            return [str] * self.re.groups


class Sep(Format):

    def __init__(self, sep=',', limit=-1):
        self.sep = sep
        self.limit = limit

    def __bind__(self, input):
        # assert isinstance(self.sep, input.__out__)
        pass

    def __str__(self):
        return 'Sep({sep!r}, {limit})'.format(sep=self.sep, limit=self.limit)

    @property
    def __out__(self):
        if self.limit:
            return [type(self.sep)] * self.limit
        else:
            return [type(self.sep), ...]


class Json(Format):

    def __bind__(self, input):
        # assert issubclass(input.__out__, str)
        pass

    @property
    def __out__(self):
        return ...


class Files(Format):

    def __init__(self, pattern, **opts):
        self.pattern = pattern
        self.opts = opts

    def __str__(self):
        return self.pattern

    def __repr__(self):
        return "Files({})".format(self.pattern)

    @property
    def __out__(self):
        return str


class Here(Format):

    def __init__(self, *content):
        self.content = content
