from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text


class GDT_RestOfText(GDT_Repeat):

    def __init__(self, name: str):
        super().__init__(GDT_Text(name))

    def get_val(self):
        return super().get_val()

    def val(self, val: str | list[str] | None):
        """Store CLI tokens as one text value for the text-field proxy."""
        if isinstance(val, list):
            val = " ".join(val)
        return super().val(val)

    def get_value(self):
        if not self._converted:
            self._value = self.get_val()
            self._converted = True
        return self._value

    def is_multiple(self) -> bool:
        return True

    def render_form(self) -> str:
        """A web request is one text value, unlike the CLI token remainder."""
        return GDT_Text.render_form(self)
