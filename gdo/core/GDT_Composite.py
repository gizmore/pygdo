import functools

from gdo.base.GDT import GDT


class GDT_Composite(GDT):
    """
    A composite GDT for multiple database columns.
    """

    def gdo_components(self) -> list['GDT']:
        return []

    def gdo_column_define(self) -> str:
        back = []
        for gdt in self.gdo_components():
            back.append(gdt.gdo_column_define())
        return ",\n".join(back)

    def component(self, name: str) -> GDT:
        for gdt in self.gdo_components():
            if gdt.get_name() == name:
                return gdt
