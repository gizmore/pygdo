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

    def gdo_filter_query(self, gdo: 'GDO', query: 'Query'):
        """Filter an object reference through its joined, human-readable name."""
        if not self.get_val():
            return
        query.join_object(self.get_name())
        if name_column := self._table.name_column():
            alias = f'{gdo.gdo_table_name()}_{self.get_name()}_t'
            name_column.copy_as(f'{alias}.{name_column.get_name()}').val(self.get_val()).gdo_filter_query(self._table, query)
        else:
            super().gdo_filter_query(gdo, query)
