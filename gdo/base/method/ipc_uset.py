from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserSetting import GDT_UserSetting


class ipc_uset(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User('user').not_null(),
            GDT_UserSetting('key').not_null(),
            GDT_String('value').not_null(),
        ]

    def get_user(self) -> GDO_User:
        return self.param_value('user')

    def gdo_execute(self) -> GDT:
        key = self.param_val('key')
        if user := Cache.OCACHE['gdo_user'].get(key):
            user._settings[key] = self.param_val('value')
        return self.empty()
