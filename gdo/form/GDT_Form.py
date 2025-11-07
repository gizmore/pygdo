from enum import Enum

from typing import TYPE_CHECKING

from gdo.core.GDT_TemplateHTML import tplhtml

if TYPE_CHECKING:
    from gdo.form.MethodForm import MethodForm

from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.WithError import WithError
from gdo.base.WithName import WithName
from gdo.core.GDT_Container import GDT_Container
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class Encoding(Enum):
    URLENCODED = 'application/x-www-form-urlencoded'
    MULTIPART = 'multipart/form-data'


class GDT_Form(WithError, WithHREF, WithTitle, WithText, WithName, GDT_Container):
    _slim: bool
    _actions: GDT_Menu
    _encoding: Encoding
    _method: 'MethodForm'

    def __init__(self, name: str = 'form'):
        super().__init__()
        self.name(name)
        self._href = '?'
        self._actions = GDT_Menu()
        self._slim = False
        self._encoding = Encoding.URLENCODED
        self._text_key = ''
        self._text_args = None
        self._text_escaped = False

    def method(self, method: 'MethodForm'):
        self._method = method
        return self

    def slim(self, slim: bool = True):
        self._slim = slim
        return self

    def actions(self) -> GDT_Menu:
        return self._actions

    def validate(self, val: str|None) -> bool:
        for gdt in self.all_fields():
            self.validate_gdt(gdt)
        if not self.has_error():
            for gdt in self._fields:
                gdt.gdo_form_validated(self)
            return True
        return False

    def multipart(self):
        self._encoding = Encoding.MULTIPART
        return self

    def add_field(self, field):
        super().add_field(field)
        field.gdo_added_to_form(self)

    def add_fields(self, *fields):
        super().add_fields(*fields)
        for field in fields:
            field.gdo_added_to_form(self)

    ##########
    # Render #
    ##########

    def render_enctype(self) -> str:
        return self._encoding.value

    def render(self, mode: Mode = Mode.HTML):
        if mode in (Mode.HTML, Mode.FORM):
            return self.render_html()
        return ''

    def render_html(self):
        return tplhtml('form', 'form.html', {
            'title': self.render_title(),
            'text': self.render_text(),
            'href': self.render_href(),
            'enctype': self.render_enctype(),
            'fields': self.render_fields(Mode.FORM),
            'actions': self._actions.render_fields(),
        })

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
