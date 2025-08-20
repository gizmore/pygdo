import argparse
import asyncio
import functools
import os
import sys
import signal
from asyncio.exceptions import CancelledError
from threading import Thread

from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

RUNNING = 1

class ConsoleThread(Thread):

    def __init__(self):
        super().__init__()
        self.name = "PyGDOConsoleThread"
        self.daemon = True

    def run(self):
        from gdo.base.Application import Application
        Application.init_common()
        Application.init_cli()
        Application.init_thread(self)
        asyncio.run(self.loop())

    async def loop(self):
        global RUNNING
        from gdo.base.Application import Application
        while RUNNING:
            Application.tick()
            await Application.EVENTS.update_timers(Application.TIME)
            Application.execute_queue()
            await asyncio.sleep(0.5)

async def pygdo(line: str = None):
    from gdo.base.Application import Application
    from gdo.base.ModuleLoader import ModuleLoader
    from gdo.base.Util import Files
    from gdo.base.Logger import Logger

    parser = argparse.ArgumentParser(description='Run a pygdo command or the pygdo repl interpreter.')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--dogmode', action='store_true')
    parser.add_argument('--config', nargs='?', default='protected/config.toml')
    args, rest = parser.parse_known_args(sys.argv[1:])

    if args.test:
        import unittest  # Required for unittest detection later

    Logger.init(os.path.dirname(__file__)+"/../../protected/logs/")
    Application.init(__file__ + "/../../", args.config)
    Application.init_common()
    loader = ModuleLoader.instance()
    loader.load_modules_db()
    loader.init_modules(True, True)
    Application.init_cli()
    loader.init_cli()
    Files.create_dir(Application.files_path('repl/'))
    Application.IS_DOG = True

    if args.dogmode:
        global RUNNING
        from gdo.core.method.launch import launch
        print("Dogmode!")
        Files.put_contents(launch.lock_path(), str(os.getpid()))
        RUNNING = 2

    if line:
        if line == 'repl':
            await repl()
        else:
            await process_line(line)
    elif len(rest):
        args = []
        for arg in rest:
            if len(args):
                args.append(f'"{arg}"')
            else:
                args.append(arg)
        await process_line(" ".join(args))
    else:
        await repl()


@functools.lru_cache
def get_parser():
    from gdo.base.Parser import Parser
    from gdo.base.Render import Mode
    from gdo.base.Util import CLI
    from gdo.core.GDO_Session import GDO_Session
    user = CLI.get_current_user()
    server = user.get_server()
    channel = server.get_or_create_channel(user.gdo_val('user_name'))
    session = GDO_Session.for_user(user)
    return Parser(Mode.CLI, user, server, channel, session)


async def process_line(line: str) -> None:
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
        parser = get_parser()
        message = Message(line, Mode.CLI)
        message.env_server(server).env_user(user, True)
        Application.EVENTS.publish('new_message', message)
        if line.startswith(trigger):
            method = parser.parse_line(line[1:])
            Application.fresh_page().method(method)
            gdt = method.execute()
            while asyncio.iscoroutine(gdt):
                gdt = await gdt
            Application.execute_queue()
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
            await message.deliver()
            method._env_session.save()
    except GDOParamError as ex:
        print(Render.red(str(ex), Mode.CLI))

def handle_sigusr1(self, event: str, args: any = None):
    global RUNNING
    from gdo.base.Application import Application
    from gdo.base.IPC import IPC
    asyncio.run_coroutine_threadsafe(IPC.dog_execute_events(), loop=Application.LOOP)

async def repl():
    from gdo.base.Application import Application
    from gdo.base.Exceptions import GDOModuleException, GDOError
    from gdo.base.Util import CLI
    from gdo.base.IPC import IPC
    global RUNNING
    thread = ConsoleThread()
    thread.start()
    if not sys.stdin.isatty():
        print("Terminal is no tty.")
    user = CLI.get_current_user()
    IPC.send('base.dogpid_update')
    if RUNNING == 2:
        signal.signal(signal.SIGUSR1, handler=handle_sigusr1)
    session = PromptSession(
        history=FileHistory(Application.files_path(f'repl/{user.get_name()}.txt')),
    )
    with patch_stdout():  # allows async print + input without clobbering
        while RUNNING:
            try:
                input_line = session.prompt(">>> ")
                if input_line:
                    if input_line.lower() == "exit":
                        break
                    # Application.tick()
                    await process_line(input_line)
            except (GDOModuleException, GDOError) as ex:
                print(str(ex))
            except (KeyboardInterrupt, EOFError, CancelledError):
                print("\nExiting...")
                break
            except Exception as ex:
                from gdo.base.Logger import Logger
                Logger.exception(ex)
        RUNNING = 0
        thread.join()

async def launcher(line: str = None):
    parent_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))
    sys.path.append(parent_dir)
    from gdo.base.Application import Application
    Application.LOOP = asyncio.get_running_loop()
    await pygdo(line)


if __name__ == '__main__':
    asyncio.run(launcher())
