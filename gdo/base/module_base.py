from packaging.version import Version

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDO_ModuleVal import GDO_ModuleVal
from gdo.base.GDT import GDT
from gdo.base.Util import Files
from gdo.core.GDT_Bool import GDT_Bool


class module_base(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 0

    def gdo_classes(self):
        return [
            GDO_Module,
            GDO_ModuleVal,
        ]

    def gdo_install(self):
        Files.create_dir(Application.file_path('assets'))
        Files.create_dir(Application.file_path('cache'))
        Files.create_dir(Application.file_path('files'))
        Files.create_dir(Application.file_path('files_test'))

    ##########
    # Config #
    ##########

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('500_mails').initial('1'),
            GDT_Bool('serve_dotfiles').initial('0'),
            GDT_Bool('serve_gdo_assets').initial('0')
        ]

    def cfg_serve_dot_files(self) -> bool:
        return self.get_config_value('serve_dotfiles')

    def cfg_serve_gdo_assets(self) -> bool:
        return self.get_config_value('serve_dotfiles')

