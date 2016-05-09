import dask.bag as db

import declares as dc
import declares.formats as fmt


class FilesImpl(implement=dc.Files):
    def __init__(self, files: fmt.Files):
        self.files = files

    def __bind__(self, out_str):
        pass

    @property
    def __bag__(self):
        return db.from_textfiles(self.files.pattern,
                                 compression=self.files.compression)


class SepImpl(implement=dc.Sep):
    def __init__(self, sep: fmt.Sep):
        self.sep = sep
        self.nfields = None

    def __bind__(self, in_str, out_tup):
        pass

    def __update__(self, in_str, out_tup):
        if in_str is not None:
            # TODO ensure same type and encoding
            pass
        if out_tup is not None:
            self.nfields = out_tup.nfields

    @property
    def __bag__(self):
        # TODO ensure filter bla
        return self.in_str.__bag__.map(str.split, key=self.sep)


class RecordTupleImpl:
    __in__ = dc.Tuples
    __out__ = dc.Records

    def __init__(self, rec: dc.Record):
        self.rec = rec

    def __bind__(self, in_tup, out_rec):
        fs = [f.type for f in self.rec.fields()]
        in_tup.confirm(fs)
        out_rec.confirm(fs)

    def __bag__(self):
        # TODO ensure filter bla
        return self.in_str.__bag__


class JsonDictsImpl:
    __in__ = dc.Strings
    __out__ = dc.Dicts

    def __init__(self):
        self.names = set()

    def __bind__(self, in_str, out_dct):
        pass

    def __update__(self, in_str, out_dct):
        if in_str is not None:
            pass
        if out_dct is not None:
            self.names = {nt.name for nt in out_dct.keys()}

    @property
    def __bag__(self):
        import ujson
        # XXX error ensure filter bla ...
        self.in_tup.__bag__.apply(ujson.loads)


class RecordDictImpl:
    __in__ = dc.Dicts
    __out__ = dc.Records

    def __init__(self, rec: dc.Record):
        self.rec = rec

    def __bind__(self, in_tup, out_rec):
        fs = [f.type for f in self.rec.fields()]
        in_tup.confirm(fs)
        out_rec.confirm(fs)

    @property
    def __bag__(self):
        self.in_tup.__bag__


# TODO Projections pulled down
