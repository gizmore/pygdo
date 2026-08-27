from abc import ABC, abstractmethod

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_List import GDT_List
from gdo.table.GDT_Search import GDT_Search


class MethodCompletion(Method, ABC):
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

    def get_query(self) -> str | None:
        return self.param_val('q')

    @abstractmethod
    def gdo_completion_items(self) -> list[dict[str, str]]:
        """Return completion items with ``id``, submitted ``var`` and visible ``display_var``."""
        raise NotImplementedError

    def gdo_execute(self) -> GDT:
        return GDT_List(*self.gdo_completion_items())
