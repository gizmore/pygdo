from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_Secret import GDT_Secret


class super(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "super"

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Secret('pass').not_null(),
        ]

    @classmethod
    def gdo_method_config_server(cls) -> [GDT]:
        return [
            GDT_Password('superkey').initial('super'),
        ]

    def gdo_execute(self) -> GDT:
        key = self.get_config_server_val('superkey')
        if GDT_Password.check(key, self.param_value('pass')):
            self.grant(self._env_user, self._env_server)
            return self.msg('msg_super_granted')
        return self.err('err_wrong_superword')

    def grant(self, user: GDO_User, server: GDO_Server):
        for perm in ('voice', 'staff', 'admin'):
            GDO_UserPermission.grant(user, perm)
