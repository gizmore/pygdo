from gdo.base.Util import Strings
from gdo.core.GDT_Field import GDT_Field


class GDT_Hidden(GDT_Field):

    def __init__(self, name):
        super().__init__(name)
        self._writable = False

    def render_form(self):
        return f'<input type="hidden" name="{self._name}" value="{Strings.html(self._val)}" />\n'
