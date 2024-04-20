from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
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
    def setting_column(cls, key: str, user: GDO_User):
        gdt = GDT_UserSetting.KNOWN[key]
        gdo = cls.get_setting(user, key)
        if gdo:
            gdt.val(gdo.get_val())
        return gdt

    @classmethod
    def get_users_with_setting(cls, server_id: str, key: str, val: str, op: str = '=') -> Query:
        setting = GDT_UserSetting.KNOWN[key]
        settings_table = cls.table()
        query = (GDO_User.table().select().
                 join(f"LEFT JOIN {settings_table.gdo_table_name()} settings ON settings.uset_user = gdo_user.user_id").
                 where(f'gdo_user.user_server={cls.quote(server_id)}').
                 where(f"settings.uset_val{op}{cls.quote(val)}"))
        if setting.get_initial() == val:
            query.or_where("settings.uset_val IS NULL")
        return query
