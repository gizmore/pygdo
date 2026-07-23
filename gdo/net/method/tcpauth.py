from gdo.base.GDT import GDT
from gdo.core.GDT_Secret import GDT_Secret
from gdo.login.GDT_Login import GDT_Login
from gdo.login.method.form import form


class tcpauth(form):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'tcpauth'

    def gdo_connectors(self) -> str:
        return 'tcp'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_user_type(self) -> str | None:
        return None

    def gdo_create_form(self, form_) -> None:
        """TCP authentication is positional and has no HTML form fields."""

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Login('login').not_null(),
            GDT_Secret('password').not_null(),
        ]

    def max_attempts(self) -> int:
        from gdo.login.module_login import module_login
        return module_login.instance().cfg_failure_attempts()

    async def gdo_execute(self) -> GDT:
        if not self.ban_check():
            return self.empty()

        login = self.param_val('login')
        user = self.get_user(login)
        password = self.param_val('password')
        registered = user is None
        if registered:
            user = await self._env_server.get_or_create_user(login)
            from gdo.login.module_login import module_login
            module_login.instance().set_password_for(user, password)
        elif not self.check_password(user, password):
            self.login_failed(user)
            return self.empty()

        connector = self._env_server.get_connector()
        if not await connector.authenticate_user(self._env_user, user):
            return self.err('err_tcpauth_in_use')
        self._message.env_user(user)
        key = 'msg_tcpauth_registered' if registered else 'msg_tcpauth_success'
        return self.reply(key, (user.render_name(),))

    @staticmethod
    def check_password(user, password: str) -> bool:
        from gdo.core.GDT_Password import GDT_Password
        hash_ = user.get_setting_val('password')
        return bool(hash_ and GDT_Password.check(hash_, password))
