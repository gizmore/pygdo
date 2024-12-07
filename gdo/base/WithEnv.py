from gdo.base.Render import Mode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_Channel import GDO_Channel
    from gdo.core.GDO_Server import GDO_Server
    from gdo.core.GDO_Session import GDO_Session
    from gdo.core.GDO_User import GDO_User


class WithEnv:
    """
    Add environment variables to a GDT
    """
    _env_http: bool
    _env_mode: Mode
    _env_user: 'GDO_User'
    # _env_reply_to: str
    _env_server: 'GDO_Server'
    _env_channel: 'GDO_Channel'
    _env_session: 'GDO_Session'

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

    def env_channel(self, channel: 'GDO_Channel'):
        self._env_channel = channel
        return self

    def env_session(self, session):
        self._env_session = session
        return self

    def env_reply_to(self, reply_to: str):
        self._env_reply_to = reply_to
        return self

    def env_copy(self, with_env):
        self._env_http = with_env._env_http
        # self._env_mode = with_env._env_mode
        self._env_server = with_env._env_server
        self._env_channel = with_env._env_channel
        self._env_user = with_env._env_user
        self._env_session = with_env._env_session
        # self._env_reply_to = with_env._env_reply_to
        return self
