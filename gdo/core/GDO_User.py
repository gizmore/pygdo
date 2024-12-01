from typing_extensions import Self

from typing import TYPE_CHECKING

from gdo.core.GDT_UserName import GDT_UserName

if TYPE_CHECKING:
    from gdo.core.GDO_Server import GDO_Server

from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserType import GDT_UserType
from gdo.date.Time import Time
from gdo.net.GDT_IP import GDT_IP


class GDO_User(GDO):
    """
    The holy user object. It should be very slim as users will be scattered around hopefully.
    Attributes are stored in GDO_UserSetting.
    """
    SYSTEM: GDO
    _authenticated: bool

    __slots__ = (
        '_authenticated',
    )

    def __init__(self):
        super().__init__()
        self._authenticated = False

    @classmethod
    def system(cls) -> Self:
        if not hasattr(cls, 'SYSTEM'):
            cls.SYSTEM = GDO_User.table().get_by_vals({
                'user_id': '1',
                'user_type': GDT_UserType.SYSTEM,
            })
            if cls.SYSTEM is None:
                delattr(cls, 'SYSTEM')
                return cls.ghost()
        return cls.SYSTEM

    @classmethod
    def ghost(cls):
        return cls.blank({
            'user_id': '0',
            'user_server': '2',
            'user_type': GDT_UserType.GHOST,
        })

    @classmethod
    def current(cls) -> Self:
        return Application.STORAGE.user or cls.system()

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

    def get_mail(self, confirmed: bool = True) -> str:
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
    def with_permission(cls, perm_name: str):
        from gdo.core.GDO_Permission import GDO_Permission
        return GDO_Permission.get_by_name(perm_name).users()

    ############
    # Settings #
    ############
    def get_setting_val(self, key: str) -> str:
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        return GDO_UserSetting.setting_column(key, self).get_val()

    def get_setting_value(self, key: str) -> any:
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        return GDO_UserSetting.setting_column(key, self).get_value()

    def save_setting(self, key: str, val: str):
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        GDO_UserSetting.blank({
            'uset_user': self.get_id(),
            'uset_key': key,
            'uset_val': val,
        }).soft_replace()
        return self

    def increase_setting(self, key: str, by: float | int):
        old = self.get_setting_value(key)
        return self.save_setting(key, str(old + by))

    def reset_setting(self, key: str):
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        GDO_UserSetting.table().delete_by_vals({
            'uset_user': self.get_id(),
            'uset_key': key,
        })
        return self

    ###############
    # Permissions #
    ###############
    def authenticate(self, session: object, bind_ip: bool = False):
        self._authenticated = True
        Application.set_current_user(self)
        self.save_setting('last_login_ip', GDT_IP.current())
        self.save_setting('last_login_datetime', Time.get_date())
        session.set_val('sess_user', self.get_id())
        if bind_ip:
            session.set_val('sess_ip', GDT_IP.current())
        session.save()
        return self

    def logout(self, session: object):
        if self.is_authenticated():
            delattr(self, '_authenticated')
            session._data = {}
            session.save_vals({
                'sess_user': None,
                'sess_ip': None,
                'sess_data': None,
            })
            Application.set_current_user(GDO_User.ghost())
        return self

    def is_authenticated(self) -> bool:
        return hasattr(self, '_authenticated')

    def is_ghost(self) -> bool:
        return self.is_type('ghost')

    def is_user(self) -> bool:
        return self.get_user_type() in ('member', 'guest', 'link')

    def is_type(self, type_: str) -> bool:
        return self.get_user_type() == type_

    def is_admin(self) -> bool:
        return self.has_permission('admin')

    def has_permission(self, permission: str) -> bool:
        from gdo.core.GDO_Permission import GDO_Permission
        return GDO_Permission.has_permission(self, permission)

    def permissions(self) -> list[str]:
        from gdo.core.GDO_UserPermission import GDO_UserPermission
        return GDO_UserPermission.table().select('perm_name').join_object('pu_perm').exec().fetch_column()

    ##########
    # Render #
    ##########

    def render_name(self) -> str:
        return self.gdo_val('user_displayname') + "{" + self.get_server().get_id() + "}"

    #########
    # Hooks #
    #########
    def gdo_after_create(self, gdo):
        self.save_setting('created', Time.get_date())
        self.save_setting('creator', self.current().get_id())

    def gdo_before_delete(self, gdo):
        self.save_setting('deleted', Time.get_date())
        self.save_setting('deletor', self.current().get_id())

    #############
    # Messaging #
    #############
    def send(self, key: str, args: list = None, reply_to: str=None):
        self.get_server().send_to_user(self, key, args, reply_to)
