import asyncio
import functools

from typing_extensions import Self

from typing import TYPE_CHECKING

from gdo.base.Cache import gdo_cached, Cache
from gdo.base.IPC import IPC
from gdo.base.Query import Query
from gdo.base.Result import Result
from gdo.base.Util import module_enabled
from gdo.core.GDT_UserName import GDT_UserName

if TYPE_CHECKING:
    from gdo.core.GDO_Server import GDO_Server
    from gdo.core.GDO_Session import GDO_Session

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDT_UserType import GDT_UserType
from gdo.date.Time import Time
from gdo.net.GDT_IP import GDT_IP


class GDO_User(GDO):
    """
    The holy user object. It should be very slim as users will be scattered around hopefully.
    Attributes are stored in GDO_UserSetting.
    """
    _authenticated: bool
    _network_user: object  # User on a server network. Like discord's - message.author
    _session: 'GDO_Session'
    # _settings: dict[str,str]

    __slots__ = (
        '_authenticated',
        '_network_user',
        '_session',
        # '_settings',
    )

    def __init__(self):
        super().__init__()
        self._authenticated = False
        self._network_user = None
        self._session = None

    # def gdo_redis_fields(self) -> list[str]:
    #     f = super().gdo_redis_fields()
    #     # f.append('_settings')
    #     return f

    def __repr__(self):
        return f"{self.get_val('user_name')}{self.get_server_id()}"

    @classmethod
    def system(cls) -> Self:
        if not hasattr(cls, 'SYSTEM'):
            cls.SYSTEM = GDO_User.table().get_by_aid('1')
            if cls.SYSTEM is None:
                delattr(cls, 'SYSTEM')
                return cls.ghost()
        return cls.SYSTEM

    @classmethod
    @functools.lru_cache
    def ghost(cls):
        return cls.blank({
            'user_id': '0',
            'user_server': '2',
            'user_type': GDT_UserType.GHOST,
            'user_displayname': 'Guest',
            'user_name': 'Guest',
        })

    @classmethod
    def current(cls) -> Self:
        return Application.STORAGE.user or cls.ghost()

    def gdo_columns(self) -> list:
        return [
            GDT_AutoInc('user_id'),
            GDT_UserType('user_type').not_null().initial(GDT_UserType.MEMBER),
            GDT_Name('user_name').not_null(),
            GDT_UserName('user_displayname').not_null(),
            GDT_Server('user_server').not_null().cascade_delete(),
            GDT_Object('user_link').table(GDO_User.table()),
        ]

    def get_lang_iso(self):
        return self.get_setting_val('language')

    def get_mail(self, confirmed: bool = True) -> str | None:
        if confirmed and not self.get_setting_value('email_confirmed'):
            return None
        return self.get_setting_val('email')

    def get_user_type(self) -> str:
        return self.gdo_val('user_type')

    def get_server(self) -> 'GDO_Server':
        return self.gdo_value('user_server')

    def get_linked_user(self) -> 'GDO_User':
        return self.gdo_value('user_link')

    def get_server_id(self) -> str:
        return self.gdo_val('user_server')

    def get_name(self) -> str:
        return self.gdo_val('user_name')

    def get_displayname(self) -> str:
        return self.gdo_val('user_displayname')

    def get_name_sid(self):
        return "%s{%s}" % (self.get_name(), self.get_server_id())

    ##########
    # Groups #
    ##########
    @classmethod
    def admins(cls):
        return cls.with_permission('admin')

    @classmethod
    def staff(cls):
        return cls.with_permission('staff')

    @classmethod
    @gdo_cached(cache_key='users_with_permission')
    def with_permission(cls, perm_name: str):
        from gdo.core.GDO_Permission import GDO_Permission
        return GDO_Permission.get_by_name(perm_name).users()

    ############
    # Settings #
    ############

    GDO_UserSetting = None
    def gdo_user_settings(self):
        if self.__class__.GDO_UserSetting is None:
            from gdo.core.GDO_UserSetting import GDO_UserSetting
            self.__class__.GDO_UserSetting = GDO_UserSetting
        return self.__class__.GDO_UserSetting

    GDT_UserSetting = None
    def gdt_user_settings(self):
        if self.__class__.GDT_UserSetting is None:
            from gdo.core.GDT_UserSetting import GDT_UserSetting
            self.__class__.GDT_UserSetting = GDT_UserSetting
        return self.__class__.GDT_UserSetting

    def with_settings_query(self, settings: list[tuple[str, str, str]]) -> Query:
        return self.gdo_user_settings().get_users_with_settings_query(None, settings)

    def with_settings_result(self, settings: list[tuple[str, str, str]]) -> Result:
        return self.with_settings_query(settings).exec()

    def with_settings(self, settings: list[tuple[str, str, str]]) -> list['GDO_User']:
        return self.with_settings_result(settings).fetch_all()._items

    def get_setting_val(self, key: str) -> str:
        if key in self._vals:
            Cache.VHITS += 1 #PYPP#DELETE#
            return self._vals[key]
        self._vals[key] = set = self.gdo_user_settings().setting_column(key, self).get_val()
        Cache.update_for(self)
        return set

    def get_setting_value(self, key: str) -> any:
        var = self.get_setting_val(key)
        gdt = self.gdo_user_settings().setting_column(key, self)
        return gdt.get_value()

    def save_setting(self, key: str, val: str):
        if val != self.get_setting_val(key):
            self._vals[key] = val
            self.gdo_user_settings().blank({
                'uset_user': self.get_id(),
                'uset_key': key,
                'uset_val': val,
            }).soft_replace()
            IPC.send('base.ipc_uset', (self.get_id(), key, val))
            coro = Application.EVENTS.publish(f'user_setting_{key}_changed', self, val)
            if Application.LOOP.is_running():
                asyncio.create_task(coro)
            else:
                asyncio.run(coro)
            return Cache.update_for(self)
        return self

    def increase_setting(self, key: str, by: float | int):
        old = self.get_setting_value(key)
        return self.save_setting(key, str(old + by))

    def reset_setting(self, key: str):
        if key in self._vals:
            del self._vals[key]
        self.gdo_user_settings().table().delete_by_id(self.get_id(), key)
        return self

    ###############
    # Permissions #
    ###############
    async def authenticate(self, session: object, bind_ip: bool = False):
        self._authenticated = True
        Application.set_current_user(self)
        if module_enabled('login'):
            self.save_setting('last_login_ip', GDT_IP.current())
            self.save_setting('last_login_datetime', Time.get_date())
        session.set_val('sess_user', self.get_id())
        if bind_ip:
            session.set_val('sess_ip', GDT_IP.current())
        session.save()
        await Application.EVENTS.publish('user_login', self)
        return self

    async def logout(self, session: object):
        if self.is_authenticated():
            delattr(self, '_authenticated')
            session._data = {}
            session.save_vals({
                'sess_user': None,
                'sess_ip': None,
                'sess_data': None,
            })
            Application.set_current_user(GDO_User.ghost())
            await Application.EVENTS.publish('user_logout', self)
        return self

    def is_authenticated(self) -> bool:
        return self._authenticated

    def is_online(self) -> bool:
        return self.get_server().is_user_online(self)

    def is_ghost(self) -> bool:
        return self.is_type('ghost')

    def is_user(self) -> bool:
        return self.get_user_type() in ('member', 'guest', 'link')

    def is_type(self, type_: str) -> bool:
        return self.get_user_type() == type_

    def is_admin(self) -> bool:
        return self.has_permission('admin')

    def is_staff(self) -> bool:
        return self.has_permission('staff')

    def is_human(self) -> bool:
        return self.is_type(GDT_UserType.MEMBER)

    def has_permission(self, permission: str) -> bool:
        from gdo.core.GDO_Permission import GDO_Permission
        return GDO_Permission.has_permission(self, permission)

    def permissions(self) -> list[str]:
        if self.is_persisted():
            from gdo.core.GDO_UserPermission import GDO_UserPermission
            return GDO_UserPermission.table().select('perm_name').where(f'pu_user={self.get_id()}').join_object('pu_perm').exec().fetch_column()
        return self.EMPTY_LIST

    def persisted(self):
        return self.save()

    ##########
    # Render #
    ##########

    @functools.cache
    def render_name(self) -> str:
        return f'{self.gdo_val('user_displayname')}{{{self.gdo_val('user_server')}}}'

    #########
    # Hooks #
    #########
    def gdo_after_create(self, gdo):
        current = self.current()
        current = current if current.is_persisted() else self.system()
        self.save_setting('created', Time.get_date())
        self.save_setting('creator', current.get_id())

    def gdo_before_delete(self, gdo):
        current = self.current()
        current = current if current.is_persisted() else self.system()
        self.save_setting('deleted', Time.get_date())
        self.save_setting('deletor', current.get_id())

    #############
    # Messaging #
    #############
    async def send(self, key: str, args: tuple = None, notice: bool=False):
        notice = self.get_setting_value('notice_enabled') and notice
        await self.get_server().send_to_user(self, key, args, notice)

    def is_dog(self) -> bool:
        return self == self.get_server().get_connector().gdo_get_dog_user()
