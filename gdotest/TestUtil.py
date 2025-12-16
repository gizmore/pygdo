import asyncio
import logging

import nest_asyncio
from typing_extensions import TYPE_CHECKING

from gdo.base.Message import Message
from gdo.base.Util import gdo_print
from gdo.core.GDO_UserPermission import GDO_UserPermission

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User

import cProfile
import io
import time
import unittest
import urllib
from http.cookies import SimpleCookie
from urllib.parse import urlencode

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import Parser
from gdo.base.Render import Mode
from gdo.core.GDO_Session import GDO_Session
from gdo.core.connector.Web import Web
from gdo.core.connector.Bash import Bash
from gdo.install.Installer import Installer
from index_wsgi import application, pygdo_application


class GDOTestCase(unittest.IsolatedAsyncioTestCase):
    MESSAGES: dict[str, list[str]] = {}
    TICKS: int = 0
    _profile: cProfile

    def __init__(self, name: str):
        super().__init__(name)
        logging.getLogger("asyncio").setLevel(logging.ERROR)

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.IS_TEST = True
        Application.LOOP = loop = asyncio.get_running_loop()
        nest_asyncio.apply()
        loop.set_debug(False)
        WebPlug.COOKIES = {}
        all_private_messages()

    def _tearDownAsyncioRunner(self):
        asyncio.gather(*Application.TASKS)
        Application.LOOP.stop()
        Application.LOOP.close()

    async def ticker(self, ticks: int = 1):
        for i in range(ticks):
            Application.TIME += 1
            await Application.EVENTS.update_timers(Application.TIME)
        self.TICKS += ticks

    Shadowdogs = None
    @classmethod
    def sd(cls):
        if not cls.Shadowdogs:
            from gdo.shadowdogs.engine.Shadowdogs import Shadowdogs
            cls.Shadowdogs = Shadowdogs
        return cls.Shadowdogs

    async def ticker_for(self, user: 'GDO_User' = None):

        user = user or cli_gizmore()
        return await self.ticker(self.sd().USERMAP[user.get_id()].get_busy_seconds() + 2)

    async def party_ticker_for(self, user: 'GDO_User' = None):
        user = user or cli_gizmore()
        p = self.sd().USERMAP[user.get_id()].get_party()
        a = p.get_action()
        while a == p.get_action():
            await self.ticker(1)

    async def party_ticker_until(self, action: str, user: 'GDO_User' = None):
        user = user or cli_gizmore()
        p = self.sd().USERMAP[user.get_id()].get_party()
        start = Application.TIME
        while action != p.get_action_name():
            await self.ticker(1)
            if Application.TIME - start > 3600:
                self.assertFalse(True, 'Took too long.')
        await self.ticker(1)


def reinstall_module(name):
    drop_module(name)
    return install_module(name)

def drop_module(name: str):
    module = ModuleLoader.instance().load_module_fs(name)
    Installer.wipe(module)


def install_module(name: str):
    install_modules([name])
    return ModuleLoader.instance().get_module(name)


def install_modules(modules: list[str]):
    for name in modules:
        install_module_b(name)


def install_module_b(name: str):
    module = ModuleLoader.instance().load_module_fs(name)
    asyncio.run(Installer.install_modules([module]))


class WebPlug:
    COOKIES = {}

    def __init__(self, url):
        self._headers = {}
        self._status = "100 CONTINUE"
        self._url = url
        self._out = b''
        self._post = {}
        self._post_raw = None
        self._boundary = None
        self.headers_in = {}
        self.args = f"_url={url}"
        self._ip = '::1'
        self._environ = {}
        Application.mode(Mode.render_html)
        Application.fresh_page()

    def ip(self, ip: str):
        self._ip = ip
        return self

    def post(self, dic: dict):
        self._post = dic
        return self

    def post_multipart(self, b: bytes, boundary: str):
        self._post_raw = b
        self._boundary = boundary
        return self

    def exec(self):
        parts = self._url.split('?')
        url = urllib.parse.quote_plus('index_wsgi.py/' + parts[0])
        query = '&' + parts[1] if len(parts) > 1 else ''
        self._environ = {
            'REMOTE_ADDR': self._ip,
            'QUERY_STRING': f"_url={url}{query}",
            'REQUEST_METHOD': 'POST' if len(self._post.items()) else 'GET',
            'mod_wsgi.request_start': str(round(time.time())),
            'REQUEST_SCHEME': 'http',
            'REQUEST_URI': url,
        }
        cookies = self.get_cookies()
        if cookies:
            self._environ['HTTP_COOKIE'] = cookies

        if self._post_raw:
            self._environ['wsgi.input'] = io.BytesIO(self._post_raw)
            self._environ['wsgi.input'].seek(0)
            self._environ['CONTENT_LENGTH'] = len(self._post_raw)
            self._environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=' + self._boundary
            self._environ['REQUEST_METHOD'] = 'POST'

        elif len(self._post.items()):
            post_bytes = urlencode(self._post).encode('UTF-8')
            self._environ['wsgi.input'] = io.BytesIO(post_bytes)
            self._environ['wsgi.input'].seek(0)
            self._environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
            self._environ['CONTENT_LENGTH'] = len(post_bytes)
        result = application(self._environ, self.start_request)
        for chunk in result:
            self._out += bytes(chunk)
        try:
            return self._out.decode('UTF-8')
        except Exception:
            return self._out

    def start_request(self, status, headers):
        self._status = status
        self._headers = headers
        for name, value in headers:
            if name.lower() == 'set-cookie':
                self.parse_cookie(value)
        return True

    @classmethod
    def parse_cookie(cls, value):
        cookie = SimpleCookie()
        cookie.load(value)
        cls.COOKIES = {key: morsel.value for key, morsel in cookie.items()}

    @classmethod
    def get_cookies(self) -> str:
        back = ''
        for key, value in self.COOKIES.items():
            back += f"{key}={value}"
        return back

    def user(self, username: str):
        user = asyncio.run(Web.get_server().get_or_create_user(username))
        session = GDO_Session.for_user(user)
        self.COOKIES['GDO'] = session.cookie_value()
        return self


def web_plug(url):
    return WebPlug(url)


def text_plug(mode: Mode, line: str, user: 'GDO_User' = None) -> str:
    user = user or cli_gizmore()
    Application.set_current_user(user)
    server = user.get_server()
    channel = server.get_or_create_channel('test_channel')
    session = GDO_Session.for_user(user)
    Application.fresh_page()
    Application.mode(mode)
    GDOTestCase.MESSAGES[user.get_id()] = []
    if not line[0].isalnum():
        method = Parser(mode, user, server, channel, session).parse(line[1:])
        result = method.execute()
    else:
        message = Message(line, Mode.render_cli).env_user(user).env_server(server).env_channel(channel).env_mode(Mode.render_cli).env_session(session).env_http(False)
        result = message.execute()
    while asyncio.iscoroutine(result):
        result = Application.LOOP.run_until_complete(result)
    asyncio.ensure_future(Application.execute_queue())
    out = cli_top(mode)
    out += "\n"
    out += all_private_messages()
    out += "\n"
    if result:
        out += result.render(mode)
    gdo_print(out)
    return out.strip()

def all_private_messages():
    out = ""
    for msgs in GDOTestCase.MESSAGES.values():
        out += "\n".join(msgs)
        out += "\n"
        msgs.clear()
    return out.strip()

def cli_plug(user: 'GDO_User', command: str) -> str:
    return text_plug(Mode.render_cli, command, user)

def cli_top(mode: Mode = Mode.render_txt):
    return Application.get_page()._top_bar.render(mode)

def cli_user(username: str) -> 'GDO_User':
    return asyncio.run(Bash.get_server().get_or_create_user(username))

def cli_gizmore():
    user = asyncio.run(Bash.get_server().get_or_create_user('gizmore'))
    asyncio.run(make_admin(user))
    return user


def web_gizmore():
    user = asyncio.run(Web.get_server().get_or_create_user('gizmore'))
    asyncio.run(make_admin(user))
    return user

async def make_admin(user: 'GDO_User'):
    await GDO_UserPermission.grant(user, 'admin')
    await GDO_UserPermission.grant(user, 'staff')
    await GDO_UserPermission.grant(user, 'voice')
