from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserType import GDT_UserType


class InstallUser:

    @classmethod
    def now(cls):
        if not GDO_User.system():
            GDO_User.blank({
                'user_type': GDT_UserType.SYSTEM,
                'user_name': 'System',
            }).insert()
