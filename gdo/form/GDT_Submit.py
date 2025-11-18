from gdo.base.Render import Mode
from gdo.core.GDT_Template import GDT_Template
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

    def render(self, mode: Mode = Mode.render_html):
        if mode.is_html():
            return GDT_Template.python('form', 'submit.html', {'field': self})
        return ''
