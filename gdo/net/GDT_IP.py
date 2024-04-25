from gdo.base.Application import Application
from gdo.core.GDT_String import GDT_String


class GDT_IP(GDT_String):
    _use_current_ip: bool

    def __init__(self, name):
        super(GDT_IP, self).__init__(name)
        self.minlen(3)
        self.maxlen(39)
        self.ascii()
        self._pattern = '/^[0-9.:]*$/'
        self._use_current_ip = False

    def use_current(self, use_current: bool = True):
        self._use_current_ip = use_current
        return self

    def to_value(self, val: str):
        if self._use_current_ip and val is None:
            return self.current()
        return val

    @classmethod
    def current(cls) -> str:
        return Application.storage('ip', '::1')

