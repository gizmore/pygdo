from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.Util import html
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.WithObject import WithObject


class GDT_Object(WithObject, GDT_UInt):

    def html_value(self):
        if gdo := self.get_value():
            return html(gdo.render_name())
        return ''

    def get_test_vals(self) -> list[str | None]:
        return [self._table.select().first().exec().fetch_object().get_id()]

    def render_cli(self) -> str:
        return self.render_txt()

    def render_irc(self) -> str:
        return self.render_txt()

    def render_suggestion(self) -> str:
        return t('suggest_object')

    def render_txt(self) -> str:
        if obj := self.get_value():
            return f"{obj.render_name()}"
        return Render.italic(t('none'))
