from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User


from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name


class GDO_Permission(GDO):
    OWNER: str = 'owner'  # gizzle
    ADMIN: str = 'admin'  # OP
    STAFF: str = 'staff'  # HalfOP
    VOICE: str = 'voice'  # Voice
    CRONJOB: str = 'cronjob'

    @classmethod
    def get_by_name(cls, name: str) -> 'GDO_Permission':
        return GDO_Permission.table().get_by_vals({
            'perm_name': name,
        })

    @classmethod
    def get_or_create(cls, name: str) -> 'GDO_Permission':
        if perm := cls.get_by_name(name):
            return perm
        return cls.blank({
            'perm_name': name,
        }).insert()

    @classmethod
    def has_permission(cls, user: 'GDO_User', permission: str):
        from gdo.core.GDO_UserPermission import GDO_UserPermission
        for perm_name in permission.split(','):
            if perm := cls.get_by_name(perm_name):
                if GDO_UserPermission.has_permission(user, perm):
                    return True
        return False

    def __init__(self):
        super().__init__()

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('perm_id'),
            GDT_Name('perm_name').unique(),
        ]

    def count(self) -> int:
        from gdo.core.GDO_UserPermission import GDO_UserPermission
        return GDO_UserPermission.table().count_where(f'pu_perm={self.get_id()}')

    def users(self) -> list:
        from gdo.core.GDO_UserPermission import GDO_UserPermission
        return GDO_UserPermission.users_with_perm_id(self.get_id())
