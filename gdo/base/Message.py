import threading

from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.base.WithEnv import WithEnv
from gdo.base.Parser import Parser
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Page import GDT_Page


class Message(WithEnv, threading.Thread):
    _method: Method
    _message: str
    _result: str
    _sender: GDO_User

    def __init__(self, message: str, mode: Mode):
        super().__init__()
        self.env_http(False)
        self.env_mode(mode)
        self._message = message
        self.daemon = True
        self._sender = None  # GDO_User.system()
        self._env_reply_to = None
        self._env_channel = None
        self._env_session = None
        self._result = ''

    def message_copy(self) -> 'Message':
        copy = Message(self._message, self._env_mode).env_copy(self)
        return copy

    def result(self, result: str):
        self._result = result
        return self

    async def execute(self):
        # Application.fresh_page()
        parser = Parser(self._env_mode, self._env_user, self._env_server, self._env_channel, self._env_session)
        self._method = parser.parse(self._message)
        await self.run()

    async def run(self):
        txt = ''
        txt2 = self._method.execute().render(self._env_mode)
        txt1 = GDT_Page.instance()._top_bar.render(self._env_mode)
        if txt1:
            txt += txt1 + " "
        if txt2:
            txt += txt2
        self._result = txt.strip()
        await self.deliver()

    async def deliver(self):
        text = self._result
        if self._env_channel:
            reply_to = self._env_reply_to or self._env_user.render_name()
            text = f"{reply_to}: {text}"
            self._result = text
            await self._env_server.get_connector().send_to_channel(self)
        else:
            if self._env_reply_to:
                text = f"{self._env_reply_to}: {text}"
                self._result = text
            await self._env_server.get_connector().send_to_user(self)

