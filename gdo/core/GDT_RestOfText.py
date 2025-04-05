from gdo.base.Util import Arrays
from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_String import GDT_String


class GDT_RestOfText(GDT_Repeat):

    def __init__(self, name):
        super().__init__(GDT_String(name))

    # def get_val(self):
    #     val = super().get_val()
    #     if val is not None:
    #         return " ".join(val)
    #     return val
    #
    def get_value(self):
        val = super().get_value()
        if val is not None:
            return " ".join(val)
        return val

    def is_multiple(self) -> bool:
        return True

    def render_form(self) -> str:
        return self._proxy.render_form()
