from gdo.core.GDT_ComboBox import GDT_ComboBox


class GDT_Select(GDT_ComboBox):

    _choices: dict

    def __init__(self, name):
        super().__init__(name)

    def init_choices(self):
        if not hasattr(self, 'choices'):
            self._choices = {}
            self._choices.update(self.gdo_choices())
        return self._choices

    def gdo_choices(self) -> dict:
        return {}
