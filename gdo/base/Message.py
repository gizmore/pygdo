import threading

from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.base.WithEnv import WithEnv
from gdo.base.Parser import Parser


class Message(WithEnv, threading.Thread):
    _method: Method
    _message: str
    _result: str

    def __init__(self, message: str, mode: Mode):
        super().__init__()
        self.env_http(False)
        self.env_mode(mode)
        self._message = message
        self.daemon = True

    def result(self, result: str):
        self._result = result
        return self

    async def execute(self):
        # Application.fresh_page()
        parser = Parser(self._env_mode, self._env_user, self._env_server, self._env_channel, self._env_session)
        self._method = parser.parse(self._message)
        await self.run()

    async def run(self):
        self._result = self._method.execute().render(self._env_mode)
        await self.deliver()

    async def deliver(self):
        if self._env_channel:
            self._result = f"{self._env_user.render_name()}: {self._result}"
            await self._env_server.get_connector().send_to_channel(self)
        else:
            await self._env_server.get_connector().send_to_user(self)

