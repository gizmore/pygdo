from gdo.base.Util import Arrays
from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_String import GDT_String


class GDT_RestOfText(GDT_Repeat):

    def __init__(self, name: str):
        super().__init__(GDT_String(name))

    def get_val(self):
        val = super().get_val()
        return val if val is None else " ".join(val)

    def get_value(self):
        if not self._converted:
            self._value = self.get_val()
            self._converted = True
        return self._value

    def is_multiple(self) -> bool:
        return True

    def render_form(self) -> str:
        return self._proxy.render_form()
