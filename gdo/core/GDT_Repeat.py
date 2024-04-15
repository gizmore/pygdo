from gdo.base.GDT import GDT
from gdo.core.WithProxy import WithProxy


class GDT_Repeat(WithProxy, GDT):

    def __init__(self):
        super().__init__()

    def is_positional(self) -> bool:
        return True
        