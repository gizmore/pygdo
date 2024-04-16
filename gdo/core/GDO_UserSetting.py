from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserSetting import GDT_UserSetting


class GDO_UserSetting(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_User('uset_user').primary(),
            GDT_UserSetting('uset_key').primary(),
            GDT_String('uset_val'),
        ]

    @classmethod
    def get_setting(cls, user, key: str):
        return cls.table().get_by_vals({
            'uset_user': user.get_id(),
            'uset_key': key,
        })

    def get_val(self):
        return self.gdo_val('uset_val')

    @classmethod
    def setting_column(cls, key: str, user: 'GDO_User'):
        gdt = GDT_UserSetting.KNOWN[key]
        gdo = cls.get_setting(user, key)
        if gdo:
            gdt.val(gdo.get_val())
        return gdt
