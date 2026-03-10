from typing import Any

from gdo.core.GDT_String import GDT_String


class GDT_ComboBox(GDT_String):

    _choices: dict[str, Any]

    def choices(self, choices: dict[str, Any]):
        self._choices = choices
        return self
