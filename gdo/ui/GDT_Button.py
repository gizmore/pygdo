from gdo.base.GDT import GDT
from gdo.base.WithName import WithName
from gdo.core.GDT_Field import GDT_Field
from gdo.ui.WithText import WithText


class GDT_Button(WithName, WithText, GDT_Field):
    _call: callable

    def __init__(self, name: str):
        super().__init__(name)

    def calling(self, call: callable):
        self._call = call
        return self

    def call(self) -> GDT:
        return self._call()

