from typing import Any

from gdo.core.GDT_String import GDT_String
from gdo.core.WithCompletion import WithCompletion


class GDT_ComboBox(WithCompletion, GDT_String):

    _choices: dict[str, Any]

    def choices(self, choices: dict[str, Any]):
        self._choices = choices
        return self
