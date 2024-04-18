import urllib.parse

from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import Parser
from gdo.install.Installer import Installer
from index import handler


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
        self._url = url
        self._out = ''
        self._post = {}
        self.headers_in = {}
        self.args = f"_url={url}"

    def write(self, s):
        if s is not None:
            self._out += s

    def post(self, dic: dict):
        self._post = dic
        return self

    def read(self):
        s = urllib.parse.urlencode(self._post)
        return s.encode('UTF-8')

    def exec(self):
        handler(self)
        return self._out


def web_plug(url):
    return WebPlug(url)


def cli_plug(user, command) -> str:
    return Parser(command, user).parse().execute().render_cli()
