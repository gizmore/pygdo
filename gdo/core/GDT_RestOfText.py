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
        # A web form submits one string. Rendering the generic repeat widget
        # creates a ``name[]`` input and an extra empty field, although this
        # type is only repeated to consume all remaining *CLI* tokens.
        # ParseArgs still supplies the web value as a one-item list, so the
        # regular rest-of-text conversion remains intact after submission.
        proxy = self._proxy
        name = proxy.get_name()
        value = proxy.get_val()
        try:
            return proxy.name(self._name).val(self.get_val() or '').render_form()
        finally:
            proxy.name(name).val(value)
    #     return self._proxy.render_form()
