from gdo.core.GDT_Char import GDT_Char


class GDT_Color(GDT_Char):

    def __init__(self, name: str):
        super().__init__(name)
        self.minlen(8)
        self.pattern(r'^[0-9a-z]{8}$')
        self.ascii()
        self.case_i()
        self._input_type = "color"

    def render_html(self):
        return f'<span class="gdt_color" style="background: #{self.get_val()}">#{self.get_val()}</span>'
