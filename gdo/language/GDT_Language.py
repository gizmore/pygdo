from gdo.base.Query import Query
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect
from gdo.language.GDO_Language import GDO_Language


class GDT_Language(GDT_ObjectSelect):
    _supported: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('language')
        self.label('language')
        self.table(GDO_Language.table())
        self.maxlen(2)
        self.case_s()
        self.ascii()
        self._supported = False

    def supported(self, supported: bool = True):
        self._supported = supported
        return self

    def gdo_query(self) -> Query:
        query = super().gdo_query()
        if self._supported: query.where('lang_supported')
        return query

    def to_value(self, val: str):
        if val is None:
            return None
        language = self._table.get_by_id(val.lower())
        if language and (not self._supported or language.gdo_val('lang_supported') == '1'):
            return language
        return None

    def render_val(self) -> str:
        if (val := self.get_val()) is None:
            return Render.italic(t('none'))
        return t(f'l_{val}')

    def render_txt(self) -> str:
        return self.render_val()

    def render_cli(self) -> str:
        return self.render_val()

    def render_irc(self) -> str:
        return self.render_val()

    def render_cell(self) -> str:
        return self.render_val()
