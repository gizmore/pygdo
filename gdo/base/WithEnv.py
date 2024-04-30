class WithEnv:
    _env_user: object
    _env_server: object
    _env_channel: object
    _env_session: object

    def env_user(self, user):
        self._env_user = user
        return self

    def env_server(self, server):
        self._env_server = server
        return self

    def env_channel(self, channel):
        self._env_channel = channel
        return self

    def cli_session(self):
        from gdo.core.GDO_Session import GDO_Session
        GDO_Session.init_cli(self._env_user)
        return self

