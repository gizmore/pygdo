from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDT_Secret import GDT_Secret


class super(Method):

    def gdo_trigger(self) -> str:
        return "super"

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Secret('pass').not_null(),
        ]

    def gdo_method_config_server(self) -> [GDT]:
        return [
            GDT_Secret('superkey').initial('super'),
        ]

    def gdo_execute(self) -> GDT:
        key = self.get_config_server_val('superkey')
        if key == self.param_val('pass'):
            self.grant(self._env_user, self._env_server)
            return self.msg('msg_super_granted')
        return self.err('err_wrong_superword')

    def grant(self, user: GDO_User, server: GDO_Server):
        for perm in ('staff', 'admin'):
            GDO_UserPermission.grant(user, perm)
