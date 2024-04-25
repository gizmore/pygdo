import io
import time
import urllib
from urllib.parse import urlencode

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import Parser
from gdo.core.connector.Web import Web
from gdo.install.Installer import Installer
from index import application


def reinstall_module(name):
    drop_module(name)
    return install_module(name)


def drop_module(name):
    module = ModuleLoader.instance().get_module(name)
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
    # subprocess.run(["/bin/python3", "gdoadm.py", "install", "--module", name], capture_output=True)


class WebPlug:

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
        Application.reset()

    def ip(self, ip: str):
        self._ip = ip
        return self

    # def write(self, s):
    #     if s is not None:
    #         if isinstance(s, bytes):
    #             s = s.decode('utf-8')
    #         self._out += s

    def post(self, dic: dict):
        self._post = dic
        return self

    # def read(self):
    #     s = urllib.parse.urlencode(self._post)
    #     return s.encode('UTF-8')

    def exec(self):
        parts = self._url.split('?')
        url = urllib.parse.quote_plus('index.py/' + parts[0])
        self._environ = {
            'REMOTE_ADDR': self._ip,
            'QUERY_STRING': f"_url={url}",
            'REQUEST_METHOD': 'POST' if len(self._post.items()) else 'GET',
            'mod_wsgi.request_start': str(round(time.time())),
        }
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
        return True

    def get_remote_host(self):
        return '::1'


def web_plug(url):
    return WebPlug(url)


def cli_plug(user, command) -> str:
    if user is None:
        user = Web.get_server().get_or_create_user('gizmore')
    return Parser(command, user).parse().execute().render_cli()
