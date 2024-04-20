from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time


class GDT_Duration(GDT_String):

    def __init__(self, name):
        super().__init__(name)

    def to_value(self, val: str):
        if val is None:
            return None
        return Time.human_to_seconds(val)
