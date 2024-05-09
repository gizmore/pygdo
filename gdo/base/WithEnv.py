from gdo.base.Render import Mode
from gdo.base.Util import dump


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

    def env_copy(self, with_env):
        self._env_http = with_env._env_http
        self._env_mode = with_env._env_mode
        self._env_server = with_env._env_server
        self._env_channel = with_env._env_channel
        self._env_user = with_env._env_user
        self._env_session = with_env._env_session
        return self

