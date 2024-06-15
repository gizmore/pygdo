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
