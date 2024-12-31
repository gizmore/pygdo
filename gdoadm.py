import argparse
import getpass
import os
import subprocess
import sys

import tomlkit

from gdo.base import Util
from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render, Mode
from gdo.base.Util import Files, module_enabled, Arrays
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_UserPermission import GDO_UserPermission
from gdo.core.method.clear_cache import clear_cache
from gdo.install.Config import Config
from gdo.install.Installer import Installer
from gdo.mail import module_mail
from gdoproviders import git_remote_url


class App:

    def argparser(self):
        parser = argparse.ArgumentParser(
            description='PyGdo admin utility.',
            usage='''gdo_adm.sh <command> [<args>]
            The Commands are:
            configure   Re-/Create the protected/config.toml. Use -i for interactive prompts.
            database    Show Database setup help how to create a database and user.
            setenv      Append pygdo/bin/ to your PATH env variables. Use -x to really do it. This is optional.
            webconfig   Show apache or nginx config.
            provide     Download modules and dependencies
            install     Install modules.
            migrate     Auto-Migrate the database for modules.
            admin       Create a user that is admin
            wipe        Remove modules from the database.
            update      Triggers after update hooks.
            skel        Create a module skeleton inside an existing module folder.
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
        loader.init_modules(False, False)
        parser = argparse.ArgumentParser(description='Configure modules. Example: ./gdo_adm.sh configure --interactive --unittests')
        parser.add_argument('--interactive', '-i', action='store_true')
        parser.add_argument('--unittests', '-u', action='store_true')
        # parser.add_argument('--path', default='protected/config.toml')
        args = parser.parse_args(sys.argv[2:])
        path = Application.CONFIG_PATH
        data = Config.data(Application.CONFIG)
        if args.unittests:
            import unittest
            Application.init(os.path.dirname(__file__))
        if args.interactive:
            self.configure_interactive(path, data)
        else:
            Config.rewrite(path, data)
        print("All Done!")

    def database(self):
        parser = argparse.ArgumentParser(description='Print help for a database setup.')
        parser.add_argument('--mysql', '--mariadb', '-m', action='store_true', default=True)
        args = parser.parse_args(sys.argv[2:])

        db_name = Application.config('db.name')
        db_user = Application.config('db.user')
        db_pass = Application.config('db.pass')

        if args.mysql:
            print("Create a database with these commands:\n")
            print("sudo mysql # starts mysql client session as root user\n")
            print("Inside MariaDB:\n")
            print(f"CREATE DATABASE {db_name};")
            print(f"CREATE USER {db_user}@localhost identified by '{db_pass}';")
            print(f"GRANT ALL ON {db_name}.* to {db_user}@localhost;")
        else:
            parser.print_help()

    def setenv(self):
        parser = argparse.ArgumentParser(description='Append pygdo/bin/ to your PATH environment variables or help howto.')
        parser.add_argument('-x', '--execute', action='store_true')
        args = parser.parse_args(sys.argv[2:])

        paths = os.getenv('PATH').split(os.pathsep)
        in_path = any('pygdo/bin' in path for path in paths)

        if in_path:
            print("pygdo/bin is already in your PATH.")
            exit(0)

        pygdo_path = Application.file_path('bin/')
        if not args.execute:
            code = f'export PATH=\\"{pygdo_path}:\\$PATH\\"'
            code = f"echo {code} >> ~/.bashrc"
            print(f"To add pygdo cli, please exceute:\n\n{code}\nsource ~/.bashrc\n")
            exit(0)
        else:
            code = f'export PATH="{pygdo_path}:$PATH"'
            file = os.path.expanduser("~/.bashrc")
            Files.append_content(file, f"\n# Added by pygdo admin utility:\n{code}\n\n")
            print(f'Added {code} to your .bashrc')
            print("Now execute\n\nsource ~/.bashrc\n")

    def webconfig(self):
        parser = argparse.ArgumentParser(description='Print webserver config. Example: ./gdo_adm.sh webconfig --apache')
        parser.add_argument('--apache', '-a', action='store_true')
        parser.add_argument('--nginx', '-n', action='store_true')
        args = parser.parse_args(sys.argv[2:])
        if args.apache:
            GLOBAL = "{GLOBAL}"
            user = getpass.getuser()
            domain = Application.domain()
            pygdo_home = Application.PATH
            python_home = os.path.abspath(sys.executable + "/../../") + "/"
            print(f"""
<VirtualHost *:80>
    ServerName {domain}
    WSGIScriptReloading On
    WSGIProcessGroup pygdo
    WSGIDaemonProcess pygdo user={user} group={user} threads=5 python-home={python_home} home={pygdo_home}
    WSGIScriptAlias / {pygdo_home}index.py  process-group=pygdo application-group=%{GLOBAL}
    AllowEncodedSlashes NoDecode
    DocumentRoot "{pygdo_home}"
    <Directory "{pygdo_home}">
        Options +FollowSymLinks +Indexes +ExecCGI
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /home/{user}/pygdo.error.log
    CustomLog /home/{user}/pygdo.access.log combined
</VirtualHost>
""")
        elif args.nginx:
            print("""TODO!""")
        else:
            print("Error: Use webconfig --apache or --nginx")

    def configure_interactive(self, path: str, data: dict[str, GDT]):
        pass

    def _load_provider_toml(self) -> dict:
        return Installer.load_provider_toml()

    def provide(self):
        """
        GIT clone a module and it's dependencies.
        """
        parser = argparse.ArgumentParser(description='Download or print out modules. Example: ./gdo_adm.sh provide -y irc,blackjack')
        parser.add_argument('modules', nargs='?')
        parser.add_argument('-y', '--yes', action='store_true')
        parser.add_argument('-s', '--ssh', action='store_true')
        args = parser.parse_args(sys.argv[2:])

        loader = ModuleLoader.instance()
        on_disk = loader.load_modules_fs()
        providers = self._load_provider_toml()

        if not args.modules:
            print(f"There are {len(providers.keys())} modules known to me:")
            decorated = []
            for name in providers.keys():
                bold = not (name in on_disk and on_disk[name].is_core_module())
                green = loader.module_installed(name)
                name = Render.underline(name, Mode.CLI) if providers[name][2] else name
                name = Render.bold(name, Mode.CLI) if bold else name
                name = Render.green(name, Mode.CLI) if green else name
                decorated.append(name)
            print(', '.join(decorated))
            exit(0)

        wanted = args.modules.lower().split(',')
        unknown = []
        for name in wanted:
            if name not in providers:
                unknown.append(name)
        if unknown:
            print(f"Unknown modules: {', '.join(unknown)}")
            exit(1)
        missing = []
        for name in wanted:
            if name not in on_disk:
                missing.append(name)
        if not missing:
            print(f"All wanted modules and their dependencies are on disk. You can ./gdo_adm.sh install {args.modules} now.")
            if not args.yes:
                choice = input('Shall i do this now? (y)').lower()
                if choice != 'y' or choice != '':
                    exit(0)
            process_args = ["./gdo_adm.sh", "install"]
            if args.yes:
                process_args.append('--yes')
            process_args.append(args.modules)
            subprocess.run(process_args, check=True)
            exit(0)
        need = missing
        to_process = list(need)
        before = 0
        after = len(to_process)
        while before != after:
            before = len(to_process)
            for name in to_process:
                deps = providers[name][1]
                for dep in deps:
                    if dep not in on_disk:
                        need.append(dep)
            to_process = Arrays.unique(need)
            after = len(to_process)
        need = Arrays.unique(need)
        print(f"You need to clone {len(need)} modules: {', '.join(need)}.")
        choices = {}
        for name in need:
            multi = providers[name][0]
            if len(multi) > 1:
                while True:
                    try:
                        n = 0
                        print(f"{name} has multiple providers:")
                        for url in multi:
                            n += 1
                            print(f"{n}) {git_remote_url(url, args.ssh)}")
                        if args.yes:
                            n = 1
                        else:
                            choice = input(f"Please enter a choice from 1 to {n} (1): ")
                            if choice == '':
                                n = 1
                            else:
                                n = int(choice)
                        choices[name] = git_remote_url(multi[n - 1], args.ssh)
                        break
                    except KeyboardInterrupt:
                        exit(-1)
                    except Exception:
                        print('ERROR!')
            else:
                choices[name] = git_remote_url(multi[0], args.ssh)
        print(f"I will download {len(choices)} modules as a git repository:")
        for name, url in choices.items():
            print(f"{name}: {url}")
        if not args.yes:
            input("Is that OK? Press Enter.")
        old_dir = Application.file_path()
        gdo_dir = Application.file_path('gdo/')
        os.chdir(gdo_dir)
        for name, url in choices.items():
            print(f"{name}: {url}")
            path = os.path.join(gdo_dir, name)
            clone_cmd = ["git", "clone", url, path]
            subprocess.run(clone_cmd, check=True)
        os.chdir(old_dir)
        self.post_install()
        print("All done!")

    def post_install(self):
        print("Installing requirements.")
        subprocess.run("./gdo_requirements.sh", check=True)
        print("Running post install scripts.")
        subprocess.run("./gdo_post_install.sh", check=True)

    def install(self):
        loader = ModuleLoader.instance()
        parser = argparse.ArgumentParser(description='Install modules. Example: ./gdo_adm.sh install --all or ./gdo_adm.sh install Core|Dog*')
        parser.add_argument('--reinstall', action='store_true')
        parser.add_argument('-a', '--all', action='store_true')
        parser.add_argument('-y', '--yes', action='store_true')
        parser.add_argument('module', nargs='?')
        args = parser.parse_args(sys.argv[2:])
        reinstall = args.reinstall

        if args.all:
            modules = list(loader.load_modules_fs('*', reinstall).values())
        elif args.module:
            modules = loader.load_modules_fs(args.module.lower(), reinstall)
            modules = list(modules.values())
        else:
            modules = []
        if not modules:
            print("No modules found!", file=sys.stderr)
            exit(-1)
        Installer.install_modules(modules, True)
        self._run_yarn_script()
        print("All Done!")

    def admin(self):
        parser = argparse.ArgumentParser(description='Create / assign an admin user for a connector (web by default).'
                                                     'Example: ./gdo_adm.sh admin gizmore 11111111 gizmore@gizmore.org')
        parser.add_argument('--connector', default='bash')
        parser.add_argument('username')
        parser.add_argument('password')
        parser.add_argument('email', nargs='?')
        args = parser.parse_args(sys.argv[2:])

        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)

        server = GDO_Server.get_by_connector(args.connector)
        user = server.get_or_create_user(args.username)
        GDO_UserPermission.grant(user, GDO_Permission.ADMIN)
        GDO_UserPermission.grant(user, GDO_Permission.STAFF)
        GDO_UserPermission.grant(user, GDO_Permission.VOICE)
        GDO_UserPermission.grant(user, GDO_Permission.CRONJOB)
        if module_enabled('login'):
            from gdo.login import module_login
            module_login.instance().set_password_for(user, args.password)
        email = args.email
        if email:
            if module_enabled('mail'):
                module_mail.instance().set_email_for(user, email)
        print("All Done!")

    def wipe(self):
        parser = argparse.ArgumentParser(description='Remove modules. Example: ./gdo_adm.sh wipe --all OR ./gdo_adm.sh wipe ma*,irc ')
        parser.add_argument('--all', '-a', action='store_true')
        parser.add_argument('module', nargs='?')
        args = parser.parse_args(sys.argv[2:])

        if args.all:
            Application.db().query(f"DROP DATABASE IF EXISTS {Application.db().db_name}")
            Application.db().query(f"CREATE DATABASE {Application.db().db_name}")
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
        parser.add_argument('--all', '-a', action='store_true')
        parser.add_argument('module', nargs='?')
        args = parser.parse_args(sys.argv[2:])
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        if args.all:
            modules = loader.load_modules_fs('*', True)
        elif args.module:
            modules = loader.load_modules_fs(args.module, True)
        else:
            parser.print_help()
            exit(0)
        modules = list(modules.values())
        # modules = Installer.modules_with_deps(modules)
        loader.init_modules(False, True)
        Installer.migrate_modules(modules)
        print("All done!")

    def update(self):
        parser = argparse.ArgumentParser(description='Execute functions required after an update like clear_cache')
        args = parser.parse_args(sys.argv[2:])
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)
        self._run_yarn_script()
        clear_cache().gdo_execute()
        print("All done!")

    def skel(self):
        parser = argparse.ArgumentParser(
            description='Create a module skeleton because we are lazy. Example: ./gdo_adm.sh skel module_name. The folder gdo/module_name has to exist.')
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
        ignore = [
            '__pycache__/',
            '*.pclprof',
            'node_modules/',
            'yarn.lock',
        ]
        Files.append_content(f"{base}.gitignore", "\n".join(ignore) + '\n')
        Files.touch(f"{base}requirements.txt", True)
        print("All done!")

    def _run_yarn_script(self):
        print("Running ./gdo_yarn.sh ")
        result = subprocess.run([Application.file_path('gdo_yarn.sh')], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        print("Done.")

    def _run_requirement_scripts(self):
        pass


def run_pygdo_admin():
    try:
        path = os.path.dirname(__file__) + "/"
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', '-c', nargs='?', default='protected/config.toml')
        parser.add_argument('--unittests', '-u', action='store_true')
        args, rest = parser.parse_known_args()
        sys.argv = sys.argv[0:1]
        sys.argv.extend(rest)
        config_file = args.config
        if args.unittests:
            import unittest  # Required for unittest detection later
            config_file = 'protected/config_test.toml'
        Application.init(path, config_file)
        try:
            Application.init_cli()
        except Exception as ex:
            Logger.exception(ex)
        App().argparser()
    except Exception as ex:
        Logger.exception(ex)
        raise ex


if __name__ == "__main__":
    run_pygdo_admin()
