from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.core.GDT_Select import GDT_Select


class GDT_Bool(GDT_Select):

    def gdo_column_define(self) -> str:
        return f"{self._name} TINYINT(1) {self.gdo_column_define_null()} {self.gdo_column_define_default()}"

    def gdo_choices(self) -> dict:
        return {
            '0': False,
            '1': True,
        }

    def display_val(self, val: str) -> str:
        if val is None:
            return Render.italic(t('none'))
        return t('yes') if val == '1' else t('no')
