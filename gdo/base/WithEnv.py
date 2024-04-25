

class WithEnv:
    _env_user: object
    _session: object

    def user(self, user):
        self._env_user = user
        return self

    def cli_session(self):
        from gdo.core.GDO_Session import GDO_Session
        GDO_Session.init_cli(self._env_user)
        return self

    def gdo_permission(self):
        pass
