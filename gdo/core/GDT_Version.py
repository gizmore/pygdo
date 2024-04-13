from gdo.core.GDT_String import GDT_String
from packaging.version import Version


class GDT_Version(GDT_String):

    def __init__(self, name):
        super().__init__(name)

    def to_value(self, val: str):
        return Version(val)
