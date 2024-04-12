from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name
from gdo.date.GDT_Created import GDT_Created
from gdo.user.GDT_UserType import GDT_UserType


class GDO_User(GDO):
    SYSTEM: GDO

    def gdo_columns(self) -> list:
        return [
            GDT_AutoInc('user_id'),
            GDT_Name('user_name').not_null().unique(),
            GDT_UserType('user_type').not_null().initial(GDT_UserType.MEMBER),
            GDT_Created('user_created'),
        ]

    @classmethod
    def system(cls):
        if not hasattr(cls, 'SYSTEM'):
            cls.SYSTEM = GDO_User.table().get_by_vars({
                'user_id': '1',
                'user_type': GDT_UserType.SYSTEM,
            })
            if cls.SYSTEM is None:
                delattr(cls, 'SYSTEM')
                return None
        return cls.SYSTEM
