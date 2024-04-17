from gdo.base.GDT import GDT
from gdo.base.WithName import WithName
from gdo.ui.WithText import WithText


class GDT_Button(WithName, WithText, GDT):
    _call: callable

    def __init__(self):
        super().__init__()

    def calling(self, call: callable):
        self._call = call
        return self

    def call(self) -> GDT:
        return self._call()

