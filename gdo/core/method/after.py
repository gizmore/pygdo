from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.date.GDT_Duration import GDT_Duration


class after(Method):

    def gdo_trigger(self) -> str:
        return 'in'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Duration('time'),
        ]

    def gdo_execute(self) -> GDT:
        pass
