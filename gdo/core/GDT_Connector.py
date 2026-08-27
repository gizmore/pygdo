from gdo.core.Connector import Connector
from gdo.core.GDT_Select import GDT_Select


class GDT_Connector(GDT_Select):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return Connector.AVAILABLE

    def to_value(self, val: str):
        if val is None:
            return None
        return Connector.get_by_name(val)

    def display_var(self, val: str) -> str:
        """Connector choices are classes, while the persisted value is its key."""
        return str(val) if val is not None else super().display_var(val)
