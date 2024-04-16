from gdo.base.ModuleLoader import ModuleLoader
from gdo.install.Installer import Installer


def install_module(name):
    install_modules([name])


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
        self.headers_in = {}
        self.args = f"_url={url}"

    def write(self, s):
        if s is not None:
            self._out += s


def web_plug(url):
    return WebPlug(url)
