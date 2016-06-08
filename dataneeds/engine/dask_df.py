import dask.dataframe as df
import dataneeds as dc
import dataneeds.formats as fmt


class CsvFiles:
    pass


class DataFrame:

    def confirm(self, columns=None, dtypes=None):
        pass


class FilesImpl:
    __out__ = CsvFiles

    def __init__(self, files: fmt.Files):
        self.files = files


class SepImpl:
    __in__ = CsvFiles
    __out__ = DataFrame

    def __init__(self, sep: fmt.Sep):
        self.sep = sep
        self.names = None

    def __update__(self, in_fs, out_df):
        if out_df is not None:
            self.names = out_df.columns
            self.dtypes = out_df.dtypes

    @property
    def __bag__(self):
        return df.read_csv(self.in_fs,
                           sep=self.sep,
                           names=self.names,
                           dtypes=self.dtypes)


class RecordImpl:
    __in__ = DataFrame
    __out__ = DataFrame

    def __init__(self, rec: dc.Record):
        self.rec = rec

    def __bind__(self, in_df, out_df):
        self.in_df.confirm(columns=...,
                           dtypes=...)
        self.out_df.confirm(columns=...,
                            dtypes=...)


# TODO json impl

# TODO Projections pulled down, or does dusk handle this
# TODO Joines ...
