import os
import sys


def run():
    from gdo.base.Application import Application
    from gdo.base.ModuleLoader import ModuleLoader
    from gdo.base.Util import CLI

    Application.init(__file__ + "/../../")
    ModuleLoader.instance().load_modules_cached()
    ModuleLoader.instance().init_modules()
    ModuleLoader.instance().init_cli()
    method = CLI.parse(" ".join(sys.argv[1:]))
    print(method.execute().render_cli())


if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))
    sys.path.append(parent_dir)
    run()
