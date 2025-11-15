import socket

from gdo.base.Util import html
from gdo.core.GDT_String import GDT_String


class GDT_Host(GDT_String):

    _resolvable: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.ascii()
        self.maxlen(96)
        self._resolvable = False

    def resolvable(self, resolvable: bool = True) -> 'GDT_Host':
        self._resolvable = resolvable
        return self

    def validate(self, val: str|None) -> bool:
        if self._resolvable and val:
            if not socket.gethostbyname(val):
                return self.error('err_host_resolve', (html(val),))
        return super().validate(val)
