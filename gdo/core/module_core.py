from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.Connector import Connector
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_File import GDO_File
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_User import GDT_User
from gdo.core.InstallUser import InstallUser
from gdo.core.connector.Bash import Bash
from gdo.core.connector.Web import Web
from gdo.date.GDT_DateTime import GDT_DateTime


class module_core(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 1

    def gdo_init(self):
        Connector.register(Bash)
        Connector.register(Web, False)

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
            GDT_Bool('guest_system').initial('1'),
            GDT_Bool('send_403_mails').initial('1'),
            GDT_Bool('send_404_mails').initial('1'),
            GDT_Enum('show_perf').choices({"never": "Never", "always": "Always", "staff": "Staff"}).initial('always'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_DateTime("created"),
            GDT_User("creator"),
            GDT_DateTime("deleted"),
            GDT_User("deletor"),
        ]

    def cfg_403_mails(self) -> bool:
        return self.get_config_value('send_403_mails')

    def cfg_404_mails(self) -> bool:
        return self.get_config_value('send_404_mails')

    def cfg_show_perf(self) -> str:
        return self.get_config_val('show_perf')

    def cfg_guest_system(self) -> bool:
        return self.get_config_value('guest_system')

    def gdo_classes(self):
        return [
            GDO_Server,
            GDO_Channel,
            GDO_User,
            GDO_Permission,
            GDO_UserPermission,
            GDO_Session,
            GDO_UserSetting,
            GDO_File,
        ]

    def gdo_install(self):
        InstallUser.now()

    def gdo_load_scripts(self, page):
        self.add_css('css/pygdo.css')
        self.add_js('js/pygdo.js')

    def should_show_perf(self) -> bool:
        perf = self.cfg_show_perf()
        if perf == 'always':
            return True
        elif perf == 'never':
            return False
        else:
            return GDO_User.current().is_staff()

    def gdo_init_sidebar(self, page):
        if self.should_show_perf():
            from gdo.core.GDT_Perf import GDT_Perf
            page._bottom_bar.add_field(GDT_Perf())

