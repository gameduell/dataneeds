import contextlib

from .request import Request


@contextlib.contextmanager
def request(entity, **options):
    yield Request(entity, **options)
