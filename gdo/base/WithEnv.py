from gdo.base.Render import Mode


class WithEnv:
    """
    Add environment variables to a GDT
    """
    _env_http: bool
    _env_mode: Mode
    _env_user: object
    _env_server: object
    _env_channel: object
    _env_session: object

    def env_http(self, http: bool):
        self._env_http = http
        return self

    def env_mode(self, mode: Mode):
        self._env_mode = mode
        return self

    def env_user(self, user):
        self._env_user = user
        return self

    def env_server(self, server):
        self._env_server = server
        return self

    def env_channel(self, channel):
        self._env_channel = channel
        return self

    def env_session(self, session):
        self._env_session = session
        return self

    def cli_session(self):
        from gdo.core.GDO_Session import GDO_Session
        return self.env_session(GDO_Session.init_cli(self._env_user))
