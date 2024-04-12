from gdo.base.Exceptions import GDOError
from gdo.base.GDT import GDT
from gdo.base.Trans import t


class Method(GDT):
    CACHE = {}

    _params = []

    def __init__(self):
        Method.CACHE[self.__class__.__name__] = self

    def gdo_parameters(self) -> [GDT]:
        return []

    def gdo_parameter_value(self, key):
        for gdt in self.gdo_parameters():
            if gdt.get_name() == key:
                return gdt.gdo_value()
        return None

    def message_raw(self, message):
        return self.message('%s', [message])

    def message(self, key, args):
        from gdo.core.GDT_String import GDT_String
        return GDT_String("result").initial(t(key, args))

    def execute(self):
        raise GDOError('err_stub')
