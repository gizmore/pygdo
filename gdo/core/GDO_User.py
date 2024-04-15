from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created
from gdo.core.GDT_UserType import GDT_UserType


class GDO_User(GDO):
    SYSTEM: GDO

    def gdo_columns(self) -> list:
        return [
            GDT_AutoInc('user_id'),
            GDT_UserType('user_type').not_null().initial(GDT_UserType.MEMBER),
            GDT_Name('user_name').not_null(),
            GDT_String('user_displayname').not_null(),
            GDT_Server('user_server').not_null(),
            GDT_Created('user_created'),
        ]

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
