from typing import Any

from gdo.core.GDT_String import GDT_String


class GDT_ComboBox(GDT_String):

    _choices: dict[str, Any]
    _errorhint_all: bool = False

    def errorhint_all(self, enabled: bool = True):
        self._errorhint_all = enabled
        return self

    def choices(self, choices: dict[str, Any]):
        self._choices = choices
        return self
