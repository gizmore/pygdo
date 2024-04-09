from gdo.core.GDT import GDT


class GDT_Container(GDT):

    _fields: list

    def __init__(self):
        super().__init__()
        self._fields = []

    def add(self, gdt: GDT):
        self._fields.append(gdt)
        return self

