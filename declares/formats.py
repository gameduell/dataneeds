class Format:
    def __rshift__(self, other):
        return self

    def __rrshift__(self, other):
        return self


class Either(Format):
    def __init__(self, *formats):
        self.formats = formats


class Re(Format):
    def __init__(self, re):
        self.re = re


class Sep(Format):
    def __init__(self, sep=','):
        self.sep = sep


class Json(Format):
    pass


class Files(Format):
    def __init__(self, pattern, compression='infer'):
        self.pattern = pattern
        self.compression = compression
