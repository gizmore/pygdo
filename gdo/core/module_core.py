import asyncio
import nest_asyncio

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.core import GDO_MethodValServerBlob
from gdo.core.Connector import Connector
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_Cronjob import GDO_Cronjob
from gdo.core.GDO_File import GDO_File
from gdo.core.GDO_Method import GDO_Method
from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel
from gdo.core.GDO_MethodValChannelBlob import GDO_MethodValChannelBlob
from gdo.core.GDO_MethodValServer import GDO_MethodValServer
from gdo.core.GDO_MethodValServerBlob import GDO_MethodValServerBlob
from gdo.core.GDO_MethodValUser import GDO_MethodValUser
from gdo.core.GDO_MethodValUserBlob import GDO_MethodValUserBlob
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_User import GDT_User
from gdo.core.InstallCore import InstallCore
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
        self.subscribe('clear_cache', self.on_cc)
        try:
            if Application.IS_HTTP and not Application.ASGI:
                nest_asyncio.apply(asyncio.new_event_loop())
            else:
                nest_asyncio.apply()
        except Exception as ex:
            Logger.exception(ex)

    def on_cc(self):
        if hasattr(GDO_User, 'SYSTEM'):
            delattr(GDO_User, 'SYSTEM')

    def gdo_dependencies(self) -> list:
        return [
            'base',
            'date',
            'form',
            'language',
            'mail',
            'message',
            'net',
            'table',
            'ui',
            'user',
        ]

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('guest_system').initial('1'),
            GDT_Bool('send_403_mails').initial('1'),
            GDT_Bool('send_404_mails').initial('1'),
            GDT_Bool('allow_gdo_assets').initial('0'),
            GDT_UInt('asset_version').initial('1'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_DateTime("created"),
            GDT_User("creator"),
            GDT_DateTime("deleted"),
            GDT_User("deletor"),
        ]

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Bool('notice_enabled').initial('1').not_null(),
        ]

    def cfg_guest_system(self) -> bool:
        return self.get_config_value('guest_system')

    def cfg_403_mails(self) -> bool:
        return self.get_config_value('send_403_mails')

    def cfg_404_mails(self) -> bool:
        return self.get_config_value('send_404_mails')

    def cfg_allow_gdo_assets(self) -> bool:
        return self.get_config_value('allow_gdo_assets')

    def gdo_classes(self):
        return [
            GDO_Server,
            GDO_Channel,
            GDO_User,
            GDO_Permission,
            GDO_UserPermission,
            GDO_Session,
            GDO_UserSetting,
            GDO_Cronjob,
            GDO_File,
            GDO_Method,
            GDO_MethodValChannel,
            GDO_MethodValChannelBlob,
            GDO_MethodValServer,
            GDO_MethodValServerBlob,
            GDO_MethodValUser,
            GDO_MethodValUserBlob,
        ]

    def gdo_install(self):
        InstallCore.now()

    def gdo_load_scripts(self, page):
        self.add_js('js/pygdo.js')
        self.add_css('css/pygdo.css')
