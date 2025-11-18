import asyncio
import gc
import types
from datetime import datetime

import nest_asyncio

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOException
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.core import GDO_MethodValServerBlob
from gdo.core.Connector import Connector
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_Cronjob import GDO_Cronjob
from gdo.core.GDO_Event import GDO_Event
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
from gdo.core.GDT_Serialize import GDT_Serialize
from gdo.core.GDT_Template import GDT_Template, Templite
from gdo.core.GDT_TemplateHTML import GDT_TemplateHTML
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_User import GDT_User
from gdo.core.InstallCore import InstallCore
from gdo.core.connector.Bash import Bash
from gdo.core.connector.Web import Web
from gdo.date.Time import Time
from gdo.date.GDT_DateTime import GDT_DateTime
from gdo.date.GDT_Timestamp import GDT_Timestamp
import msgspec.json


class module_core(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 1

    def gdo_init(self):
        Connector.register(Bash)
        Connector.register(Web, False)
        self.subscribe('clear_cache', self.on_cc)
        if not Application.IS_TEST:
            nest_asyncio.apply(Application.LOOP)

    async def on_cc(self):
        if hasattr(GDO_User, 'SYSTEM'):
            delattr(GDO_User, 'SYSTEM')
        Templite.cache = {}
        GDT_TemplateHTML.CACHE = {}
        self.clear_all_lru_caches()

    def clear_all_lru_caches(self):
        for obj in gc.get_objects():
            try:
                if isinstance(obj, types.FunctionType):
                    if hasattr(obj, 'cache_clear') and callable(obj.cache_clear):
                        obj.cache_clear()
            except Exception as ex:
                Logger.exception(ex, f"cache_clear failed for {obj}")

    def gdo_dependencies(self) -> list:
        return [
            'base',
            'date',
            'file',
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
            GDT_Timestamp('last_cron').initial(Time.get_date()),
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

    def cfg_last_cron(self) -> datetime:
        return self.get_config_value('last_cron')

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
            GDO_Event,
        ]

    async def gdo_install(self):
        InstallCore.now()

    def gdo_load_scripts(self, page):
        self.add_js('js/pygdo.js')
        self.add_css('css/pygdo.css')
        self.add_js_inline("window.gdo.config = "+msgspec.json.encode(self.get_core_js()).decode('utf8')+";")

    def get_core_js(self):
        return {
            'user': GDO_User.current().render_json(),
            'webroot': Application.config('core.web_root'),
        }
