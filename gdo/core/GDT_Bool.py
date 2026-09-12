from typing import Self

from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.core.GDT_Select import GDT_Select


class GDT_Bool(GDT_Select):

    _undetermined: bool = False

    def undetermined(self, undetermined: bool = True) -> Self:
        """Allow the explicit third value 2, separate from nullable/unset."""
        self._undetermined = undetermined
        if hasattr(self, '_choices'):
            del self._choices
        return self

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('thumbs_up')

    def gdo_column_define(self) -> str:
        return f"{self._name} TINYINT(1) {self.gdo_column_define_null()} {self.gdo_column_define_default()}"

    def gdo_choices(self) -> dict:
        choices = {
            '0': False,
            '1': True,
        }
        if self._undetermined:
            choices['2'] = 2
        return choices

    def display_var(self, val: str) -> str:
        if val is None:
            return Render.italic(t('none'))
        if val == '2' and self._undetermined:
            return t('undetermined')
        return t('yes') if val == '1' else t('no')

    def render_txt(self) -> str:
        return self.render_val()
