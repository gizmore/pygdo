import argparse
import os
import sys

from gdo.core.Application import Application
from gdo.core.ModuleLoader import ModuleLoader
from gdo.install.Installer import Installer


class App:

    def argparser(self):
        parser = argparse.ArgumentParser(
            description='PyGdo admin utility.',
            usage='''gdo_adm.sh <command> [<args>]
        The Commands are:
           install -a or -m   Install modules. Example: gdoadm.sh install -m Dog,*Comment*,DogIRC*
           wipe -a or -m      Remove modules from the database
           migrate -a or -m   Migrate the database for a single module or all of them.
           confgrade          Re-create the protected config.toml
        ''')
        parser.add_argument('command', help='subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def install(self):
        parser = argparse.ArgumentParser(description='Install modules. Example: ./gdo_adm.sh install --all')
        parser.add_argument('--reinstall', action='store_true')
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--module')
        parser.add_argument('--modules')
        args = parser.parse_args(sys.argv[2:])
        reinstall = not not args.reinstall
        if args.all:
            modules = ModuleLoader.instance().load_modules_fs('*', reinstall)
        elif args.module:
            module = ModuleLoader.instance().load_module_fs(args.module, reinstall)
            modules = [module]
        elif args.modules:
            modules = ModuleLoader.instance().load_modules_fs(args.modules, reinstall)
        else:
            modules = []

        Installer.install_modules(modules)
        print("All Done!")

    def wipe(self):
        parser = argparse.ArgumentParser(description='Remove modules. Example: ./gdo_adm.sh wipe --all')
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--module')
        parser.add_argument('--modules')
        args = parser.parse_args(sys.argv[2:])

        if args.all:
            Application.DB.query(f"DROP DATABASE IF EXISTS {Application.DB.db_name}")
            Application.DB.query(f"CREATE DATABASE {Application.DB.db_name}")
            print("All Done!")
            exit(0)
        elif args.module:
            module = ModuleLoader.instance().load_module_fs(args['module'], True)
            modules = [module]
        elif args.modules:
            modules = ModuleLoader.instance().load_modules_fs(args['modules'], True)
        else:
            modules = []

        for module in modules:
            Installer.wipe(module)

    def migrate(self):
        parser = argparse.ArgumentParser(
            description='Migrate the database for a single module or all of them.')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--all', action='all modules')
        parser.add_argument('--module', action='modulename')
        parser.add_argument('--modules', action='modulename pattern or list')
        args = parser.parse_args(sys.argv[2:])
        if args['all']:
            modules = ModuleLoader.instance().load_modules_fs('*', True)
            Installer.migrate_modules(modules)
        else:
            if args['module']:
                module = ModuleLoader.instance().load_module_fs(args['module'])
                Installer.migrate_module(module)
            if args['modules']:
                modules = ModuleLoader.instance().load_modules_fs(args['modules'], True)
                Installer.migrate_modules(modules)
        print("All done!")


def launch():
    path = os.path.dirname(__file__)
    Application.init(path)
    App().argparser()


if __name__ == "__main__":
    launch()
