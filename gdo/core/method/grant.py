from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_User import GDT_User


class grant(Method):
    """Grant or revoke one explicit permission for a user."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'grant'

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Bool('remove').initial('0'),
            GDT_User('user').not_null().positional(),
            GDT_String('permission').maxlen(32).positional(),
        ]

    async def gdo_execute(self) -> GDT:
        user = self.param_value('user')
        permission_name = self.param_val('permission')
        if not permission_name:
            permissions = ', '.join(user.permissions()) or self.t('none', ())
            return self.reply('msg_user_permissions', (user.render_name(), permissions))
        permission = GDO_Permission.get_by_name(permission_name)
        if permission is None:
            return self.err('err_permission_not_found')
        if not self._env_user.has_permission(permission.get_name()):
            return self.err('err_permission_grant_denied')
        if self.param_value('remove'):
            await GDO_UserPermission.revoke_permission(user, permission)
            return self.reply('msg_permission_revoked', (permission.get_name(), user.render_name()))
        await GDO_UserPermission.grant_permission(user, permission)
        return self.reply('msg_permission_granted', (permission.get_name(), user.render_name()))
