from gdo.core.GDT_Select import GDT_Select


class GDT_Language(GDT_Select):
    _supported: bool

    def __init__(self, name):
        super().__init__(name)
        self._supported = False

    def supported(self, supported: bool = True):
        return self

    def init_choices(self):
        return self.choices({
            'en': 'English'
        })
