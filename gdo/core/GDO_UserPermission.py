from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Permission import GDT_Permission
from gdo.core.GDT_User import GDT_User


class GDO_UserPermission(GDO):

    @classmethod
    def grant(cls, user: GDO_User, perm_name: str):
        cls.grant_permission(user, GDO_Permission.get_by_name(perm_name))

    @classmethod
    def grant_permission(cls, user: GDO_User, permission: GDO_Permission):
        cls.blank({
            'pu_user': user.get_id(),
            'pu_perm': permission.get_id(),
        }).replace()

    @classmethod
    def users_with_perm_id(cls, perm_id: str):
        return cls.table().select('pu_user_t.*').fetch_as(GDO_User.table()).join_object('pu_user').where(f'pu_perm={GDT.quote(perm_id)}').exec().fetch_all()

    @classmethod
    def has_permission(cls, user: GDO_User, permission: GDO_Permission) -> bool:
        return cls.table().count_where(f"pu_user={user.get_id()} AND pu_perm={permission.get_id()}") == 1

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_User('pu_user').primary(),
            GDT_Permission('pu_perm').primary(),
        ]


