import functools
import os
import readline
import sys
import traceback


def pygdo():
    from gdo.base.Application import Application
    from gdo.base.ModuleLoader import ModuleLoader
    Application.init(__file__ + "/../../")
    Application.init_cli()
    ModuleLoader.instance().load_modules_cached()
    ModuleLoader.instance().init_modules()
    ModuleLoader.instance().init_cli()

    if len(sys.argv) > 1:
        sys.argv = [f'"{arg}"' for arg in sys.argv]
        process_line(" ".join(sys.argv[1:]))
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
    from gdo.base.Application import Application
    append_to_history(line)
    parser = get_parser()
    method = parser.parse_line(line)
    Application.fresh_page()
    gdt = method.execute()
    txt = gdt.render_cli()
    txt = Application.get_page()._top_bar.render_cli() + txt
    print(txt)


def append_to_history(line: str):
    from gdo.base.Util import CLI
    from gdo.base.Application import Application
    from gdo.base.Util import Files
    user = CLI.get_current_user()
    path = Application.file_path(f'cache/{user.get_id()}.repl.log')
    Files.append_content(path, f"{line}\n", create=True)


def reload_history():
    from gdo.base.Util import CLI
    from gdo.base.Application import Application
    from gdo.base.Util import Files
    user = CLI.get_current_user()
    path = Application.file_path(f'cache/{user.get_id()}.repl.log')
    try:
        with open(path, "r") as file:
            for line in file:
                readline.add_history(line.strip())
    except FileNotFoundError:
        print(f"First Run? - Creating repl history at {path}")
        Files.touch(path, True)


def repl():
    from gdo.base.Application import Application
    from gdo.base.Exceptions import GDOModuleException
    reload_history()
    while True:
        try:
            input_line = input(">>> ")
            if input_line == "":
                input_line = readline.get_history_item(readline.get_current_history_length())
            if input_line.lower() == "exit":
                break
            Application.tick()
            process_line(input_line)
        except GDOModuleException as ex:
            print(str(ex))
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as ex:
            print(str(ex))
            traceback.print_exception(ex)


if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))
    sys.path.append(parent_dir)
    pygdo()
