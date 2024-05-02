from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserSetting import GDT_UserSetting


class GDO_UserSetting(GDO):
    """
    Store settings for a user.
    The Settings table uses enums for keys, which makes the install a bit tricky.
    After every module install, a migration is executed. Make sure you only *add* to the list of enums.
    To add a setting, add a GDT to modules gdo_user_config() and gdo_user_settings(). Config is not user editable, settings are user editable.
    """

    @classmethod
    def setting_column(cls, key: str, user: GDO_User):
        gdt = GDT_UserSetting.KNOWN[key]
        gdo = cls.get_setting(user, key)
        if gdo:
            gdt.val(gdo.get_val())
        return gdt

    @classmethod
    def get_setting(cls, user, key: str):
        return cls.table().get_by_vals({
            'uset_user': user.get_id(),
            'uset_key': key,
        })

    #######
    # GDO #
    #######
    def gdo_cached(self) -> bool:  # Not cached
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_User('uset_user').primary(),
            GDT_UserSetting('uset_key').primary(),
            GDT_String('uset_val'),
        ]

    def get_val(self):
        return self.gdo_val('uset_val')

    #########
    # Query #
    #########
    @classmethod
    def get_user_with_setting(cls, server_id: str, key: str, val: str, op: str = '=') -> GDO_User:
        return cls.get_user_with_settings(server_id, [(key, op, val)])

    @classmethod
    def get_user_with_settings(cls, server_id, settings: list[tuple]) -> GDO_User:
        query = cls.get_users_with_settings_query(server_id, settings)
        return query.first().exec().fetch_object()

    @classmethod
    def get_users_with_settings_query(cls, server_id: str, settings: list[tuple]) -> Query:
        """
        Get multiple users with multiple conditions
        The settings conditions are a list of tuples: key, operator, value.
        """
        query = GDO_User.table().select()
        if server_id:
            query.where(f'gdo_user.user_server={cls.quote(server_id)}')
        for key, op, val in settings:
            setting = GDT_UserSetting.KNOWN[key]
            query.join(f"LEFT JOIN {cls.table().gdo_table_name()} settings_{key} ON "
                       f"settings_{key}.uset_user = gdo_user.user_id AND "
                       f"settings_{key}.uset_key = {GDT.quote(key)}")
            where = f"(settings_{key}.uset_val {op} {cls.quote(val)}"
            if setting.get_initial() == val and op == '=':
                where += " OR settings_{key}.uset_val IS NULL"
            where += ")"
            query.where(where)
        return query
