from gdo.base import Method
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name


class GDO_Method(GDO):

    @classmethod
    def get_by_name(cls, name: str):
        return cls.table().get_by_vals({
            'm_name': name,
        }) or cls.blank({
            'm_name': name,
        }).insert()

    @classmethod
    def for_method(cls, method: 'Method'):
        return cls.get_by_name(method.get_sqn())

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('m_id'),
            GDT_Name('m_name'),
        ]

    def gdo_persistent(self) -> bool:
        return True
