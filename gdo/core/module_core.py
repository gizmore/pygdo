from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.Connector import Connector
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.InstallUser import InstallUser
from gdo.core.connector.Bash import Bash


class module_core(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 1

    def gdo_init(self):
        Connector.register(Bash)

    def gdo_dependencies(self) -> list:
        return [
            'base',
            'date',
            'language',
            'mail',
            'net',
        ]

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('send_403_mails').initial('1'),
            GDT_Bool('send_404_mails').initial('1'),
        ]

    def cfg_403_mails(self) -> bool:
        return self.get_config_value('send_403_mails')

    def cfg_404_mails(self) -> bool:
        return self.get_config_value('send_404_mails')

    def gdo_classes(self):
        return [
            GDO_Server,
            GDO_User,
            GDO_Permission,
            GDO_UserPermission,
            GDO_Session,
            GDO_UserSetting,
        ]

    def gdo_install(self):
        InstallUser.now()

    def gdo_load_scripts(self, page):
        self.add_css('css/pygdo.css')
        self.add_js('js/pygdo.js')
