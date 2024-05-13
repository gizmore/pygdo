import io
import json
import time
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
from gdo.ui.GDT_Page import GDT_Page
from index import application


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
    Installer.install_module(module)


class WebPlug:
    COOKIES = {}

    def __init__(self, url):
        self._headers = {}
        self._status = "100 CONTINUE"
        self._url = url
        self._out = ''
        self._post = {}
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

    def exec(self):
        parts = self._url.split('?')
        url = urllib.parse.quote_plus('index.py/' + parts[0])
        self._environ = {
            'REMOTE_ADDR': self._ip,
            'QUERY_STRING': f"_url={url}",
            'REQUEST_METHOD': 'POST' if len(self._post.items()) else 'GET',
            'mod_wsgi.request_start': str(round(time.time())),
            'REQUEST_SCHEME': 'http',
            'REQUEST_URI': url,
        }
        cookies = self.get_cookies()
        if cookies:
            self._environ['HTTP_COOKIE'] = cookies

        if len(self._post.items()):
            post_bytes = urlencode(self._post).encode('UTF-8')
            self._environ['wsgi.input'] = io.BytesIO(post_bytes)
            self._environ['wsgi.input'].seek(0)
            self._environ['CONTENT_LENGTH'] = len(post_bytes)
        result = application(self._environ, self.start_request)
        for chunk in result:
            self._out += chunk.decode('UTF-8')
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



    def get_remote_host(self):
        return '::1'


def web_plug(url):
    return WebPlug(url)


def cli_plug(user, command) -> str:
    if user is None:
        user = cli_gizmore()
    server = user.get_server()
    channel = None
    session = GDO_Session.for_user(user)
    Application.mode(Mode.CLI)
    method = Parser(Mode.CLI, user, server, channel, session).parse(command)
    result = method.execute()
    out = GDT_Page.instance()._top_bar.render(Mode.CLI)
    out += result.render(Mode.CLI)
    return out


def cli_gizmore():
    return Bash.get_server().get_or_create_user('gizmore')


def get_gizmore():
    return Web.get_server().get_or_create_user('gizmore')
