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
