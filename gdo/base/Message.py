import asyncio
import threading

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.base.WithEnv import WithEnv
from gdo.base.Parser import Parser
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Page import GDT_Page


class Message(WithEnv):
    _method: Method
    _message: str
    _result: str
    _result_raw: str
    _sender: GDO_User
    _comrade: GDO_User
    _thread_user: GDO_User

    def __init__(self, message: str, mode: Mode):
        super().__init__()
        self.env_http(False)
        self.env_mode(mode)
        self._message = message
        self.daemon = True
        self._sender = None  # GDO_User.system()
        self._env_reply_to = None
        self._comrade = None
        self._env_channel = None
        self._env_session = None
        self._result = ''
        self._result_raw = ''

    def message_copy(self) -> 'Message':
        copy = Message(self._message, self._env_mode).env_copy(self)
        copy._sender = self._sender
        copy._result = self._result
        copy._result_raw = self._result_raw
        return copy

    def message(self, text: str):
        self._message = text
        return self

    def result(self, result: str):
        self._result = result
        return self

    def comrade(self, user: GDO_User):
        self._comrade = user
        self._thread_user = user
        return self

    async def execute(self):
        Application.EVENTS.publish('new_message', self)
        try:
            trigger = self._env_server.get_trigger()
            if self._env_channel is not None:
                trigger = self._env_channel.get_trigger()
            if self._message.startswith(trigger):
                self._message = self._message[1:]
                parser = Parser(self._env_mode, self._env_user, self._env_server, self._env_channel, self._env_session)
                self._method = parser.parse(self._message)
                await self.run()
        except Exception as ex:
            Logger.exception(ex)
            self._result = Application.get_page()._top_bar.render_irc()
            self._result += str(ex)
            await self.deliver()

    async def run(self):
        txt = ''
        result = self._method.execute()
        if asyncio.iscoroutine(result):
            result = await result
        txt2 = result.render(self._env_mode)
        txt1 = GDT_Page.instance()._top_bar.render(self._env_mode)
        if txt1:
            txt += txt1 + " "
        if txt2:
            txt += txt2
        self._result = txt.strip()
        await self.deliver()

    async def deliver(self, with_events: bool=True):
        text = self._result
        if not text:
            return
        self._result_raw = text  # for chatgpt :/
        if self._env_channel:
            reply_to = self._env_reply_to or self._env_user.render_name()
            text = f"{reply_to}: {text}"
            self._result = text
            await self._env_server.get_connector().send_to_channel(self, with_events)
        else:
            if self._env_reply_to:
                text = f"{self._env_reply_to}: {text}"
                self._result = text
            u = self._env_user
            if self._comrade:
                self._env_user = self._comrade
                self._comrade = u
            await self._env_server.get_connector().send_to_user(self, with_events)
            self._comrade = self._env_user
            self._env_user = u


