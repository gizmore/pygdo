import re

from gdo.core.GDT_Char import GDT_Char


class GDT_Color(GDT_Char):

    def __init__(self, name: str):
        super().__init__(name)
        self.label('color')
        self.icon('color')
        self.minlen(9)
        self.pattern(r'^#[0-9a-f]{8}$', re.IGNORECASE)
        self.ascii()
        self.case_i()
        self._input_type = "color"
        self._mode = 3
        self._no_hash = False

    def mode(self, mode: int):
        self._mode = mode
        return self

    def get_input(self, value: str | None = None) -> str | None:
        """Normalize browser colour input to the stored RGBA representation."""
        value = self.get_val() if value is None else value
        if isinstance(value, str) and re.fullmatch(r'#[0-9a-f]{6}', value, re.IGNORECASE):
            return value + 'ff'
        return value

    def val(self, val: str | list):
        if isinstance(val, str):
            val = self.get_input(val)
        return super().val(val)

    def render_html(self):
        return f'<span class="gdt_color" style="background: {self.get_value()}">{self.get_val()}</span>'

    # def to_val(self, value) -> str:
    #     if value is None:
    #         return None
    #     value = value.lstrip('#')
    #     if self._mode == 1:
    #         return value
    #     elif self._mode == 2:
    #         return value[2:] + value[0:2]
    #     else:
    #         return value + "ff"
    #
    # def to_value(self, val: str):
    #     if val is None:
    #         return None
    #     if self._mode == 1:
    #         return self._val
    #     elif self._mode == 2:
    #         return val[0:6] + val[6:]
    #     else:
    #         return val[0:6]

    def html_value(self):
        value = self.get_value()
        return value[:7] if value else value

    def html_pattern(self):
        return ''
