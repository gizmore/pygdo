from gdo.base.GDT import GDT
from gdo.base.Method import Method


class die(Method):

    def gdo_parameters(self) -> [GDT]:
        return [

        ]

    def gdo_execute(self):
        Application.RUNNING = False
