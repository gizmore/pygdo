from uuid import uuid4

from redis.exceptions import RedisError

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_Text import GDT_Text
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Duration import GDT_Duration
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.date.Time import Time
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page
from gdo.user.GDT_Gender import GDT_Gender
from gdo.user.GDT_Level import GDT_Level
from gdo.user.GDT_ProfileLink import GDT_ProfileLink


class module_user(GDO_Module):

    ONLINE_SECONDS = 360
    UNLOCK_SCRIPT = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) end return 0"

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('activity_accuracy').not_null().units(2, False).initial('5m'),
            GDT_Secret('user_link_pepper').not_null().initial(GDT_Token.random(32)),
        ]

    async def gdo_install(self):
        # A fresh installation needs one stable secret shared by web and Dog.
        from gdo.base.GDO_ModuleVal import GDO_ModuleVal
        if GDO_ModuleVal.table().get_by_id(self.get_id(), 'user_link_pepper') is None:
            await self.save_config_val('user_link_pepper', self.get_config_val('user_link_pepper'), force=True)

    def cfg_activity_accuracy(self) -> int:
        return self.get_config_value('activity_accuracy')

    def cfg_user_link_pepper(self) -> str:
        return self.get_config_val('user_link_pepper')

    def gdo_init(self):
        Application.EVENTS.subscribe('permission_changed', self.on_permission_changed)

    async def on_permission_changed(self, user: GDO_User, perm_name: str):
        Cache.remove('users_with_permission')

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Gender('gender'),
            GDT_Text('about_me').icon('quote'),
            GDT_Link('connect_account').href(self.href('connect')).text('link_connect_account'),
        ]

    def gdo_user_config(self) -> list[GDT]:
        return [
            # Connector/service accounts can remain known for presence while
            # their automated chatter is excluded from message consumers.
            GDT_Bool('is_ignored').not_null().initial('0'),
            GDT_Timestamp('last_activity'),
            GDT_Level('level').initial('0'),
            GDT_UInt('profile_views').initial('0'),
        ]

    def get_activity_cut_date(self) -> str:
        return Time.get_date(Application.TIME - self.ONLINE_SECONDS)

    def set_last_activity(self, user: GDO_User):
        # TCP uses Ghost until tcpauth completes. A Ghost may carry the
        # synthetic id 0, but it must never create a user-setting row.
        if not self.cfg_activity_accuracy() or user.is_ghost() or not user.is_persisted():
            return
        redis = Cache.RCACHE
        if redis is None:
            user.save_setting('last_activity', Time.get_date(Application.TIME))
            return
        prefix = self.presence_prefix(user)
        token = uuid4().hex
        lock = prefix + ':lock'
        acquired = False
        try:
            redis.set(prefix + ':seen', str(Application.TIME), ex=self.ONLINE_SECONDS)
            Application.publish_event('user_presence_seen', user, Application.TIME)
            last_write = redis.get(prefix + ':written')
            if last_write is not None and Application.TIME - float(last_write) < int(self.cfg_activity_accuracy()):
                return
            acquired = bool(redis.set(lock, token, nx=True, ex=60))
            if not acquired:
                return
            last_write = redis.get(prefix + ':written')
            if last_write is not None and Application.TIME - float(last_write) < int(self.cfg_activity_accuracy()):
                return
            user.save_setting('last_activity', Time.get_date(Application.TIME))
            redis.set(prefix + ':written', str(Application.TIME))
        except RedisError as error:
            Logger.exception(error, 'Redis user activity unavailable')
            user.save_setting('last_activity', Time.get_date(Application.TIME))
        finally:
            if acquired:
                try:
                    redis.eval(self.UNLOCK_SCRIPT, 1, lock, token)
                except RedisError as error:
                    Logger.exception(error, 'Redis user activity lock release failed')

    @staticmethod
    def presence_prefix(user: GDO_User) -> str:
        return f'gdo:{Application.config("core.env", "default")}:user:presence:{user.get_id()}'

    def is_recently_active(self, user: GDO_User) -> bool:
        if Cache.RCACHE is None or user.is_ghost() or not user.is_persisted():
            return False
        try:
            return bool(Cache.RCACHE.exists(self.presence_prefix(user) + ':seen'))
        except RedisError as error:
            Logger.exception(error, 'Redis user presence unavailable')
            return False

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        user = GDO_User.current()
        if user.is_user():
            page._right_bar.add_field(GDT_ProfileLink().user(user).icon('face'))
