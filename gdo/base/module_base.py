from gdo.base.Application import Application
from gdo.base.GDO_GDOTable import GDO_GDOTable
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDO_ModuleVal import GDO_ModuleVal
from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.core.GDT_Bool import GDT_Bool
from gdo.base.GDO import GDO


class module_base(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 0

    def gdo_classes(self) -> list[type[GDO]]:
        return [
            GDO_GDOTable,
            GDO_Module,
            GDO_ModuleVal,
        ]

    async def gdo_install(self):
        for path in (Application.config('dir').values()):
            Files.create_dir(path)

    ##########
    # Config #
    ##########

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('500_mails').not_null().initial('1'),
            GDT_Bool('serve_dot_files').not_null().initial('0'),
            GDT_Bool('serve_gdo_assets').not_null().initial('1')
        ]

    def cfg_500_mails(self) -> bool:
        return self.get_config_value('500_mails')

    def cfg_serve_dot_files(self) -> bool:
        return self.get_config_value('serve_dot_files')

    def cfg_serve_gdo_assets(self) -> bool:
        return self.get_config_value('serve_gdo_assets')

