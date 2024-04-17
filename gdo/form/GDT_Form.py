from gdo.base.GDT import GDT
from gdo.base.WithError import WithError
from gdo.base.WithName import WithName
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.GDT_Paragraph import GDT_Paragraph
from gdo.ui.GDT_Title import GDT_Title
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Form(WithError, WithHREF, WithTitle, WithText, WithName, GDT_Container):
    _actions: GDT_Menu

    def __init__(self):
        super().__init__()
        self._href = '?'

    def actions(self):
        if not hasattr(self, '_actions'):
            self._actions = GDT_Menu()
        return self._actions

    def validate(self, value) -> bool:
        for gdt in self.fields():
            self.validate_gdt(gdt)
        return not self.has_error()



    ##########
    # Render #
    ##########

    def render_html(self):
        return GDT_Template.python('form', 'form.html', {'field': self})

    def validate_gdt(self, gdt: GDT):
        if not gdt.validated():
            self.error('err_form')
        for gdt2 in gdt.fields():
            self.validate_gdt(gdt2)
