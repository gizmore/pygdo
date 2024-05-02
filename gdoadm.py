import argparse
import os
import sys

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOError
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Files
from gdo.install.Config import Config
from gdo.install.Installer import Installer


class App:

    def argparser(self):
        parser = argparse.ArgumentParser(
            description='PyGdo admin utility.',
            usage='''gdo_adm.sh <command> [<args>]
        The Commands are:
           configure   Re-/Create the protected/config.toml.
           webconfig   Show apache or nginx config.
           install     Install modules.
           wipe        Remove modules from the database.
           migrate     Auto-Migrate the database for modules.
           skeleton    Create a module skeleton inside an empty module folder
        ''')
        parser.add_argument('command', help='subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def configure(self):
        Files.create_dir(Application.file_path('files/'))
        Files.create_dir(Application.file_path('protected/'))
        loader = ModuleLoader.instance()
        loader.load_modules_fs()
        loader.init_modules(False)
        parser = argparse.ArgumentParser(description='Configure modules. Example: ./gdo_adm.sh configure --interactive --unittests')
        parser.add_argument('--interactive', '-i', action='store_true')
        parser.add_argument('--unittests', '-u', action='store_true')
        parser.add_argument('--path', default='protected/config.toml')
        args = parser.parse_args(sys.argv[2:])
        path = args.path
        data = Config.data(Application.CONFIG)
        if args.unittests:
            import unittest
            Application.init(os.path.dirname(__file__))
        if args.interactive:
            self.configure_interactive(path, data)
        else:
            Config.rewrite(path, data)
        print("All Done!")

    def webconfig(self):

        parser = argparse.ArgumentParser(description='Print webserver config. Example: ./gdo_adm.sh webconfig --apache')
        parser.add_argument('--apache', '-a', action='store_true')
        parser.add_argument('--nginx', '-n', action='store_true')
        args = parser.parse_args(sys.argv[2:])
        if args.apache:
            print("""
            <VirtualHost *:80>
            WSGIScriptReloading On
            WSGIProcessGroup test
            WSGIDaemonProcess test user=gizmore group=gizmore threads=5 python-home=/usr/ home=/home/gizmore/PycharmProjects/pygdo/
            WSGIScriptAlias / /home/gizmore/PycharmProjects/pygdo/test.py  process-group=test application-group=%{GLOBAL}
            ServerName py.giz.org
            AllowEncodedSlashes NoDecode
            DocumentRoot /home/gizmore/PycharmProjects/pygdo/
            <Directory "/home/gizmore/PycharmProjects/pygdo/">
                    Options +FollowSymLinks +Indexes +ExecCGI
                    AllowOverride All
                    Require all granted
            </Directory>
            ErrorLog /home/gizmore/www/pygdo.error.log
            CustomLog /home/gizmore/www/pygdo.access.log combined
            </VirtualHost>
            """)
        elif args.nginx:
            print("""TODO!""")
        else:
            print("Error: Use webconfig --apache or --nginx")

    def configure_interactive(self, path: str, data: dict[str, GDT]):
        pass

    def install(self):
        loader = ModuleLoader.instance()
        parser = argparse.ArgumentParser(description='Install modules. Example: ./gdo_adm.sh install --all or ./gdo_adm.sh install Core|Dog*')
        parser.add_argument('--reinstall', action='store_true')
        parser.add_argument('-a', '--all', action='store_true')
        parser.add_argument('--unittests', '-u', action='store_true')
        parser.add_argument('module', nargs='?')
        args = parser.parse_args(sys.argv[2:])
        reinstall = args.reinstall

        if args.unittests:
            import unittest  # Required for unittest detection later
            Application.init(os.path.dirname(__file__))

        if args.all:
            modules = list(loader.load_modules_fs('*', reinstall).values())
        elif args.module:
            modules = ModuleLoader.instance().load_modules_fs(args.module, reinstall)
            modules = list(modules.values())
        else:
            modules = []
        loader.init_modules()
        Installer.install_modules(modules, True)
        print("All Done!")

    def wipe(self):
        parser = argparse.ArgumentParser(description='Remove modules. Example: ./gdo_adm.sh wipe --all OR ./gdo_adm.sh wipe ma*,irc ')
        parser.add_argument('--all', '-a', action='store_true')
        parser.add_argument('--unittests', '-u', action='store_true')
        parser.add_argument('module', nargs='?')
        args = parser.parse_args(sys.argv[2:])

        if args.unittests:
            import unittest  # Required when init shall detect unit tests
            Application.init(os.path.dirname(__file__))

        if args.all:
            Application.DB.query(f"DROP DATABASE IF EXISTS {Application.DB.db_name}")
            Application.DB.query(f"CREATE DATABASE {Application.DB.db_name}")
            print("All Done!")
            exit(0)
        elif args.module:
            modules = ModuleLoader.instance().load_modules_fs(args.module, True)
            modules = list(modules.values())
        else:
            parser.print_help()
            exit(0)

        for module in modules:
            print(f"Wiping module {module.get_name()}")
            Installer.wipe(module)

        print("All Done!")

    def migrate(self):
        parser = argparse.ArgumentParser(
            description='Migrate the database for a single module or all of them.')
        parser.add_argument('--all', '-a')
        parser.add_argument('--unittests', '-u', action='store_true')
        parser.add_argument('module', nargs='?')
        args = parser.parse_args(sys.argv[2:])

        if args.unittests:
            import unittest  # Required for init with unit tests
            Application.init(os.path.dirname(__file__))

        if args['all']:
            modules = ModuleLoader.instance().load_modules_fs('*', True)
        elif args.module:
            modules = ModuleLoader.instance().load_modules_fs(args.module, True)
        else:
            parser.print_help()
            exit(0)
        modules = list(modules.values())
        Installer.migrate_modules(modules)
        print("All done!")

    def skeleton(self):
        parser = argparse.ArgumentParser(
            description='Create a module skeleton because we are lazy. Example: ./gdo_adm.sh skeleton foo_module')
        parser.add_argument('modulename')
        args = parser.parse_args(sys.argv[2:])
        name = args.modulename
        base = Application.file_path(f'gdo/{name}/')
        Files.append_content(f"{base}__init__.py", f'from gdo.{name}.module_{name} import module_{name}\n')
        Files.append_content(f"{base}module_{name}.py", f'from gdo.base.GDO_Module import GDO_Module\n\n\nclass module_{name}(GDO_Module):\n    pass\n')
        Files.copy(Application.file_path('LICENSE'), f"{base}LICENSE")
        Files.create_dir(f"{base}lang/")
        Files.append_content(f"{base}lang/{name}_en.toml", f'module_{name} = "{name.title()}"\n')
        Files.create_dir(f"{base}method/")
        Files.append_content(f"{base}method/__init__.py", '\n')
        Files.append_content(f"{base}.gitignore", '__pycache__/\n*.pclprof\n')
        print("All done!")


def run_pygdo_admin():
    try:
        path = os.path.dirname(__file__) + "/"
        Application.init(path)
        Logger.init()
        Application.init_cli()
        App().argparser()
    except Exception as ex:
        Logger.exception(ex)
        raise ex


if __name__ == "__main__":
    run_pygdo_admin()
