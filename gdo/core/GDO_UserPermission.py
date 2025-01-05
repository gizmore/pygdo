from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
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
            'pu_has': '1',
        }).soft_replace()

    @classmethod
    def users_with_perm_id(cls, perm_id: str) -> list[GDO_User]:
        return cls.table().select('pu_user_t.*').fetch_as(GDO_User.table()).join_object('pu_user').where(f'pu_perm={GDT.quote(perm_id)} AND pu_has').exec().fetch_all()

    @classmethod
    def has_permission(cls, user: GDO_User, permission: GDO_Permission) -> bool:
        if user.get_id() == '0':
            return False
        if entry := cls.table().get_by_id(user.get_id(), permission.get_id()):
            return entry.gdo_value('pu_has')
        cls.blank({
            'pu_user': user.get_id(),
            'pu_perm': permission.get_id(),
        }).insert()
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_User('pu_user').primary(),
            GDT_Permission('pu_perm').primary(),
            GDT_Bool('pu_has').not_null().initial('0'),
        ]
