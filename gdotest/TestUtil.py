import asyncio

from typing_extensions import TYPE_CHECKING

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
from index import application


class GDOTestCase(unittest.IsolatedAsyncioTestCase):
    _profile: cProfile

    # def setUp(self):
    #     if not asyncio.get_running_loop():
    #         asyncio.new_event_loop()

    # def setUp(self):
    #     self._profile = cProfile.Profile()
    #     self._profile.enable()
    #
    # def tearDown(self):
    #     p = Stats(self._profile)
    #     p.strip_dirs()
    #     p.sort_stats('cumtime')
    #     p.print_stats()
    #


def reinstall_module(name):
    drop_module(name)
    return install_module(name)


def drop_module(name):
    module = ModuleLoader.instance().load_module_fs(name)
    Installer.wipe(module)


def install_module(name):
    install_modules([name])
    return ModuleLoader.instance().get_module(name)


def install_modules(modules):
    for name in modules:
        install_module_b(name)


def install_module_b(name):
    module = ModuleLoader.instance().load_module_fs(name)
    Installer.install_modules([module])


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
        Application.mode(Mode.HTML)
        Application.reset()

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
        url = urllib.parse.quote_plus('index.py/' + parts[0])
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
            if name == 'Set-Cookie':
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
        user = Web.get_server().get_or_create_user(username)
        session = GDO_Session.for_user(user)
        self.COOKIES['GDO'] = session.cookie_value()
        return self


def web_plug(url):
    return WebPlug(url)


def text_plug(mode: Mode, line: str, user: 'GDO_User' = None) -> str:
    if user is None:
        user = cli_gizmore()
    server = user.get_server()
    channel = None
    session = GDO_Session.for_user(user)
    Application.fresh_page()
    Application.mode(mode)
    method = Parser(mode, user, server, channel, session).parse(line[1:])
    result = method.execute()
    while asyncio.iscoroutine(result):
        result = asyncio.run(result)
    out = cli_top(mode)
    out += "\n"
    out += result.render(mode)
    return out.strip()


def cli_plug(user: 'GDO_User', command: str) -> str:
    return text_plug(Mode.CLI, command, user)


def cli_top(mode: Mode = Mode.TXT):
    return Application.get_page()._top_bar.render(mode)


def cli_gizmore():
    user = Bash.get_server().get_or_create_user('gizmore')
    GDO_UserPermission.grant(user, 'admin')
    GDO_UserPermission.grant(user, 'staff')
    GDO_UserPermission.grant(user, 'voice')
    return user


def web_gizmore():
    user = Web.get_server().get_or_create_user('gizmore')
    GDO_UserPermission.grant(user, 'admin')
    GDO_UserPermission.grant(user, 'staff')
    GDO_UserPermission.grant(user, 'voice')
    return user
