from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.core.GDT_Select import GDT_Select
from gdo.core.GDT_UInt import GDT_UInt


class GDT_Bool(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_column_define(self) -> str:
        # return f"{self._name} BIT(1) {self.gdo_column_define_null()} {self.gdo_column_define_default()}"
        return f"{self._name} TINYINT(1) {self.gdo_column_define_null()} {self.gdo_column_define_default()}"

    def gdo_choices(self) -> dict:
        return {
            '0': False,
            '1': True,
        }

    def render_val(self) -> str:
        v = self.get_value()
        if v is None:
            return Render.italic(t('none'))
        return t('yes') if v else t('no')
