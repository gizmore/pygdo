from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created
from gdo.core.GDT_UserType import GDT_UserType


class GDO_User(GDO):
    SYSTEM: GDO

    @classmethod
    def system(cls):
        if not hasattr(cls, 'SYSTEM'):
            cls.SYSTEM = GDO_User.table().get_by_vals({
                'user_id': '1',
                'user_type': GDT_UserType.SYSTEM,
            })
            if cls.SYSTEM is None:
                delattr(cls, 'SYSTEM')
                return None
        return cls.SYSTEM

    def gdo_columns(self) -> list:
        return [
            GDT_AutoInc('user_id'),
            GDT_UserType('user_type').not_null().initial(GDT_UserType.MEMBER),
            GDT_Name('user_name').not_null(),
            GDT_String('user_displayname').not_null(),
            GDT_Server('user_server').not_null(),
            GDT_Created('user_created'),
        ]

    def get_mail(self) -> str:
        return self.get_setting_val('email')

    ############
    # Settings #
    ############
    def get_setting_val(self, key: str) -> str:
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        return GDO_UserSetting.setting_column(key, self).get_val()

    def save_setting(self, key: str, val: str):
        from gdo.core.GDO_UserSetting import GDO_UserSetting
        GDO_UserSetting.blank({
            'uset_user': self.get_id(),
            'uset_key': key,
            'uset_val': val,
        }).soft_replace()
        return self

