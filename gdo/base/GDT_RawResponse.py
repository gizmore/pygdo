import msgspec.json

from gdo.base.Application import Application
from gdo.base.GDT import GDT


class GDT_RawResponse(GDT):
    """A small HTTP response that must not be wrapped in a rendered page."""

    def __init__(self, body: bytes, content_type: str, status: str = '200 OK'):
        super().__init__()
        self.body = body
        self.content_type = content_type
        self.status = status

    @classmethod
    def json(cls, value, content_type='application/json; charset=UTF-8', status='200 OK'):
        return cls(msgspec.json.encode(value), content_type, status)

    def prepare(self):
        Application.status(self.status)
        Application.header('Content-Type', self.content_type)
        Application.header('Content-Length', str(len(self.body)))
        return self.body
