from gdo.base.GDT import GDT
from gdo.core.GDT_Enum import GDT_Enum


class GDT_UserSetting(GDT_Enum):
    KNOWN: dict[str, GDT] = {}

    @classmethod
    def register(cls, gdt: GDT):
        cls.KNOWN[gdt.get_name()] = gdt

    def gdo_choices(self) -> dict:
        return self.KNOWN


