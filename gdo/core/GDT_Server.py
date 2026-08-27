from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.core.GDT_Object import GDT_Object


class GDT_Server(GDT_Object):

    _default_current: bool

    def __init__(self, name):
        from gdo.core.GDO_Server import GDO_Server
        super().__init__(name)
        self.table(GDO_Server.table())
        self.label('server')
        self._default_current = False

    def default_current(self, default_current: bool = True):
        self._default_current = default_current
        return self

    def to_value(self, val: str):
        if not val and self._default_current:
            return Message.CURRENT._env_server
        return super().to_value(val)

    def get_value(self):
        # GDT_Field skips to_value() for an empty input.  The current-server
        # fallback is consequently resolved here as well, so a parameter such
        # as ``--server=`` remains genuinely optional.
        if not self.get_val() and self._default_current:
            return Message.CURRENT._env_server
        return super().get_value()
