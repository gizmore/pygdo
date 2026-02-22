from functools import lru_cache

from gdo.base.Exceptions import GDOException
from gdo.base.GDT import GDT
from gdo.base.WithName import WithName
from gdo.core.GDT_Field import GDT_Field
from gdo.core.WithGDO import WithGDO
from gdo.core.WithNullable import WithNullable
from gdo.ui.WithIcon import WithIcon


class GDT_Composite(WithName, WithIcon, WithGDO, WithNullable, GDT):
    """
    A composite GDT for multiple database columns.
    """

    def __init__(self, name: str):
        super().__init__()
        self.name(name)
        self.label(name)

    def gdo_components(self) -> list['GDT_Field']:
        raise GDOException(f'Composite {self.__class__.__name__} has to override gdo_components')

    def dirty_vals(self) -> dict[str,str]:
        vals = {}
        vals.update(super().dirty_vals())
        for gdt in self.components():
            if gdt is not self:
                vals.update(gdt.dirty_vals())
        return vals

    # def gdo_column_define(self) -> str:
    #     back = [super().gdo_column_define()]
    #     for gdt in self.gdo_components():
    #         back.append(gdt.gdo_column_define())
    #     return ",\n".join(back)

    def component(self, name: str) -> GDT:
        for gdt in self.components()[1:]:
            if gdt.get_name() == name:
                return gdt

    # def not_null(self, not_null: bool = True):
    #     for gdt in self.gdo_components():
    #         gdt.not_null(not_null)
    #     return super(WithGDO, self).not_null(not_null)

    def validate(self, val: str|None) -> bool:
        for gdt in self.gdo_components()[1:]:
            if not gdt.validate(gdt.get_val()):
                return self.error(gdt._errkey, gdt._errargs)
        return True

