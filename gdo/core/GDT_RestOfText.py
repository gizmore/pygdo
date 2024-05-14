from gdo.base.Util import Arrays
from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_String import GDT_String


class GDT_RestOfText(GDT_Repeat):

    def __init__(self, name):
        super().__init__(GDT_String(name))

    def to_value(self, vals: list[str]):
        if Arrays.empty(vals):
            return None
        return " ".join(vals)
