from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.table.GDT_Search import GDT_Search


class MethodCompletion(Method):
    """
    Abstract combobox completion ajax interface
    """
    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Search('q').not_null(),
        ]

