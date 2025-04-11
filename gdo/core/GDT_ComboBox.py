from gdo.core.GDT_String import GDT_String
from gdo.core.WithCompletion import WithCompletion


class GDT_ComboBox(WithCompletion, GDT_String):
    _choices: dict[str, any]

    def __init__(self, name):
        super().__init__(name)

    def choices(self, choices: dict[str, any]):
        self._choices = choices
        return self
