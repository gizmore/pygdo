from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import GDT_Template


class GDT_Text(GDT_String):
    """
    A longer chunk of text, using a different mysql column define
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.maxlen(4096)

    def get_val(self):
        if self._val is None:
            return None
        return self._val.strip() or None

    def render_form(self):
        if self.is_hidden():
            return super().render_form()
        return GDT_Template.python('core', 'form_text.html', {'field': self})

    def gdo_column_define(self) -> str:
        return (f"{self._name} TEXT({self._max_len}) "
                f"CHARSET {self.gdo_column_define_charset()}{self.gdo_column_define_collate()} "
                f"{self.gdo_column_define_default()} "
                f"{self.gdo_column_define_null()} ")
