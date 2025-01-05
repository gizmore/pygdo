from gdo.base.Util import html
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.WithObject import WithObject


class GDT_Object(WithObject, GDT_UInt):

    def html_value(self):
        if gdo := self.get_gdo():
            return html(gdo.render_name())
        return ''

    def render_cli(self) -> str:
        return self.render_txt()

    def render_irc(self) -> str:
        return self.render_txt()

    def render_txt(self) -> str:
        return f"{self._gdo.get_name()}"
