from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_Template import GDT_Template
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.GDT_Paragraph import GDT_Paragraph
from gdo.ui.GDT_Title import GDT_Title


class GDT_Form(GDT_Container):
    _title: GDT_Title
    _info: GDT_Paragraph
    _actions: GDT_Menu

    def __init__(self):
        super().__init__()

    def actions(self):
        if not hasattr(self, '_actions'):
            self._actions = GDT_Menu()
        return self._actions

    def render_html(self):
        return GDT_Template.python('form', 'form.html', {'field': self})
