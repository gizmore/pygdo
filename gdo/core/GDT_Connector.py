from gdo.core.Connector import Connector
from gdo.core.GDT_Select import GDT_Select


class GDT_Connector(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return Connector.AVAILABLE
    