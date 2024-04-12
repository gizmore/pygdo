from gdo.user import module_user
from gdo.user.GDO_User import GDO_User
from gdo.user.GDT_UserType import GDT_UserType


class InstallUser:

    @classmethod
    def now(cls, module: module_user):
        if not GDO_User.system():
            GDO_User.blank({
                'user_type': GDT_UserType.SYSTEM,
                'user_name': 'System',
            }).insert()
