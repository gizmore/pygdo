import asyncio

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOParamError
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.base.WithEnv import WithEnv
from gdo.base.Parser import Parser
from gdo.core.GDO_User import GDO_User


class Message(WithEnv):
    _method: Method
    _message: str
    _result: str
    _thread_user: GDO_User  # For chatgpt
    _gdt_result: GDT  # For chatgpt
    _delivered: bool

    def __init__(self, message: str, mode: Mode):
        super().__init__()
        self.env_http(False)
        self.env_mode(mode)
        self._message = message
        # self._sender = None  # GDO_User.system()
        self._env_reply_to = None
        self._thread_user = None
        self._env_channel = None
        self._env_session = None
        self._result = ''
        self._gdt_result = None
        self._delivered = False

    def message_copy(self) -> 'Message':
        return Message(self._message, self._env_mode).env_copy(self).result(self._result).comrade(self._thread_user)

    def message(self, text: str):
        self._message = text
        return self

    def result(self, result: str):
        self._result = result
        self._delivered = False
        return self

    def comrade(self, user: GDO_User):
        self._thread_user = user
        return self

    async def execute(self):
        try:
            Application.fresh_page()
            Application.EVENTS.publish('new_message', self)
            trigger = self._env_server.get_trigger()
            if self._env_channel is not None:
                trigger = self._env_channel.get_trigger()
            if self._message.startswith(trigger):
                self._message = self._message[1:]
                parser = Parser(self._env_mode, self._env_user, self._env_server, self._env_channel, self._env_session)
                self._method = parser.parse(self._message)
                return await self.run()
        except GDOParamError as ex:
            self._result = str(ex)
            self._result += " " + str(self._method.get_arg_parser(True).format_usage())
            await self.deliver()
        except Exception as ex:
            Logger.exception(ex)
            self._result = Application.get_page()._top_bar.render(self._env_mode)
            self._result += str(ex)
            await self.deliver()

    async def run(self):
        txt = ''
        result = self._method.execute()
        while asyncio.iscoroutine(result):
            result = await result
        self._gdt_result = result
        txt2 = result.render(self._env_mode)
        if txt1 := Application.get_page()._top_bar.render(self._env_mode):
            txt += txt1 + " "
        if txt2:
            txt += txt2
        self._result = txt.strip()
        await self.deliver()

    async def deliver(self, with_events: bool=True, with_prefix: bool=True):
        text = self._result
        if not text or self._delivered:
            return
        self._delivered = True
        if self._env_channel:
            # if with_prefix:
                # reply_to = self._env_reply_to or self._env_user.render_name()
                # text = f"{reply_to}: {text}"
                # self._result = text
            await self._env_server.get_connector().send_to_channel(self, with_events)
        else:
            if self._env_reply_to:
                text = f"{self._env_reply_to}: {text}"
                self._result = text
            u = self._thread_user if self._thread_user else self._env_user
            o = self._env_user
            if self._thread_user:
                self._env_user = u
            await self._env_server.get_connector().send_to_user(self, with_events)
            if self._thread_user:
                self._env_user = o
