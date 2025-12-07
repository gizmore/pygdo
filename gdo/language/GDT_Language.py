from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.core.GDT_Select import GDT_Select


class GDT_Language(GDT_Select):
    _supported: bool

    def __init__(self, name):
        super().__init__(name)
        self._supported = False

    def supported(self, supported: bool = True):
        self._supported = supported
        return self

    def gdo_choices(self):
        return {
            'en': 'English',
            'de': 'Deutsch',
        }

    def render_val(self) -> str:
        if (val := self.get_val()) is None:
            return Render.italic(t('none'))
        return t(f'l_{val}')
