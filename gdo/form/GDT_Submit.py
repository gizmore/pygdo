from gdo.base.Render import Mode
from gdo.ui.GDT_Button import GDT_Button


class GDT_Submit(GDT_Button):
    _default_button: bool

    def __init__(self, name: str = 'submit'):
        super().__init__(name)
        self.name(name)
        self.text('submit')
        self._default_button = False

    def default_button(self, default_button: bool = True):
        self._default_button = default_button
        return self

    def render_form(self):
        return f'<span class="gdt-submit"><input type="submit" name="{self.get_name()}" value="{self.render_text(Mode.HTML)}"></span>'



