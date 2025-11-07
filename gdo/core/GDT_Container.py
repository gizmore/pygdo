from gdo.base.GDT import GDT
from gdo.core.WithFields import WithFields


class GDT_Container(WithFields, GDT):

    def __init__(self):
        super().__init__()
        self._fields = []
