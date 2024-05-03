from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Name import GDT_Name


class GDO_Permission(GDO):
    ADMIN = 'admin'
    STAFF = 'staff'
    CRONJOB = 'cronjob'

    @classmethod
    def get_by_name(cls, name: str):
        return GDO_Permission.table().get_by_vals({
            'perm_name': name,
        })

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
