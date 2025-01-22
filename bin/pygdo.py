import argparse
import asyncio
import functools
import os
import readline
import sys


def pygdo():
    from gdo.base.Application import Application
    from gdo.base.ModuleLoader import ModuleLoader
    from gdo.base.Util import Files
    from gdo.base.Logger import Logger

    parser = argparse.ArgumentParser(description='Run a pygdo command or the pygdo repl interpreter.')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--config', nargs='?', default='protected/config.toml')
    args, rest = parser.parse_known_args(sys.argv[1:])

    if args.test:
        import unittest  # Required for unittest detection later

    Logger.init(os.path.dirname(__file__)+"/../../protected/logs/")
    Application.init(__file__ + "/../../", args.config)
    loader = ModuleLoader.instance()
    loader.load_modules_db()
    loader.init_modules(True, True)
    Application.init_cli()
    loader.init_cli()
    Files.create_dir(Application.files_path('repl/'))

    if len(rest):
        args = []
        for arg in rest:
            if len(args):
                args.append(f'"{arg}"')
            else:
                args.append(arg)
        process_line(" ".join(args))
    else:
        repl()


@functools.lru_cache
def get_parser():
    from gdo.base.Parser import Parser
    from gdo.base.Render import Mode
    from gdo.base.Util import CLI
    from gdo.core.GDO_Session import GDO_Session
    user = CLI.get_current_user()
    server = user.get_server()
    channel = None
    session = GDO_Session.for_user(user)
    return Parser(Mode.CLI, user, server, channel, session)


def process_line(line: str) -> None:
    from gdo.base.Exceptions import GDOParamError
    from gdo.base.Application import Application
    from gdo.base.Render import Render, Mode
    from gdo.core.connector.Bash import Bash
    from gdo.base.Message import Message
    from gdo.base.Util import CLI
    from gdo.core.GDT_Container import GDT_Container
    try:
        server = Bash.get_server()
        user = CLI.get_current_user()
        trigger = server.get_trigger()
        append_to_history(line)
        parser = get_parser()
        message = Message(line, Mode.CLI)
        message.env_server(server).env_user(user, True)
        Application.EVENTS.publish('new_message', message)
        if line.startswith(trigger):
            method = parser.parse_line(line[1:])
            Application.fresh_page()
            gdt = method.execute()
            while asyncio.iscoroutine(gdt):
                gdt = asyncio.run(gdt)
            message._gdt_result = GDT_Container()
            message._gdt_result.add_field(Application.get_page()._top_bar)
            message._gdt_result.add_field(gdt)
            txt1 = gdt.render(Mode.CLI)
            txt2 = Application.get_page()._top_bar.render(Mode.CLI)
            if txt2:
                message._result += txt2
            if txt1:
                if txt2:
                    message._result += "\n"
                message._result += txt1
            asyncio.run(message.deliver())
            method._env_session.save()
    except GDOParamError as ex:
        print(Render.red(str(ex), Mode.CLI))


def append_to_history(line: str):
    from gdo.base.Util import CLI
    from gdo.base.Application import Application
    from gdo.base.Util import Files
    user = CLI.get_current_user()
    path = Application.files_path(f'repl/{user.get_id()}.repl.log')
    Files.append_content(path, f"{line}\n", create=True)


def reload_history():
    from gdo.base.Util import CLI
    from gdo.base.Application import Application
    from gdo.base.Util import Files
    user = CLI.get_current_user()
    path = Application.files_path(f'repl/{user.get_id()}.repl.log')
    try:
        with open(path, "r") as file:
            for line in file:
                readline.add_history(line.strip())
    except FileNotFoundError:
        print(f"First Run? - Creating repl history at {path}")
        Files.touch(path, True)


def repl():
    from gdo.base.Application import Application
    from gdo.base.Exceptions import GDOModuleException, GDOError
    reload_history()
    while True:
        try:
            input_line = input(">>> ")
            if input_line == "":
                input_line = readline.get_history_item(readline.get_current_history_length())
            if input_line:
                if input_line.lower() == "exit":
                    break
                Application.tick()
                process_line(input_line)
        except (GDOModuleException, GDOError) as ex:
            print(str(ex))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        except Exception as ex:
            from gdo.base.Logger import Logger
            Logger.exception(ex)


if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))
    sys.path.append(parent_dir)
    pygdo()
