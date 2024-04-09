from gdo.core.GDT import GDT


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

    @classmethod
    def make(cls):
        return cls()

    @classmethod
    def count(cls):
        return len(cls.CACHE)
