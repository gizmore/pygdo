from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDT_UInt import GDT_UInt


class module_table(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 10

    ##########
    # Config #
    ##########

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_UInt('table_ipp').min(1).max(1000).initial('25').not_null(),
            GDT_UInt('page_menu_ipp').min(1).max(100).initial('4').not_null(),
        ]

    def cfg_ipp(self) -> int:
        return self.get_config_value('table_ipp')

    def cfg_page_menu_ipp(self) -> int:
        return self.get_config_value('page_menu_ipp')
