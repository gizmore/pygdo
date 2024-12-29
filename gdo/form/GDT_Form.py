from enum import Enum

from gdo.base.GDT import GDT
from gdo.base.WithError import WithError
from gdo.base.WithName import WithName
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class Encoding(Enum):
    URLENCODED = 'application/x-www-form-urlencoded'
    MULTIPART = 'multipart/form-data'


class GDT_Form(WithError, WithHREF, WithTitle, WithText, WithName, GDT_Container):
    _actions: GDT_Menu
    _slim: bool
    _encoding: Encoding

    def __init__(self):
        super().__init__()
        self._href = '?'
        self._actions = GDT_Menu()
        self._slim = False
        self._encoding = Encoding.URLENCODED

    def slim(self, slim: bool = True):
        self._slim = slim
        return self

    def actions(self):
        return self._actions

    def validate(self, val: str | None, value: any) -> bool:
        for gdt in self.fields():
            self.validate_gdt(gdt)
        if not self.has_error():
            for gdt in self.fields():
                gdt.gdo_form_validated()
            return True
        return False

    def multipart(self):
        self._encoding = Encoding.MULTIPART
        return self

    def add_field(self, *fields):
        super().add_field(*fields)
        for gdt in fields:
            gdt.gdo_added_to_form(self)

    ##########
    # Render #
    ##########

    def render_enctype(self) -> str:
        return self._encoding.value

    def render_html(self):
        return GDT_Template.python('form', 'form.html', {'field': self})

    def render_cli(self):
        return ''

    def render_irc(self):
        return ''

    def validate_gdt(self, gdt: GDT):
        if not gdt.validated():
            self.error('err_form')
        if gdt.has_fields():
            for gdt2 in gdt.all_fields():
                self.validate_gdt(gdt2)
