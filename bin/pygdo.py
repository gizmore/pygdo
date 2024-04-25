import os
import readline
import sys


def run():
    from gdo.base.Application import Application
    from gdo.base.ModuleLoader import ModuleLoader
    Application.init(__file__ + "/../../")
    Application.init_cli()
    ModuleLoader.instance().load_modules_cached()
    ModuleLoader.instance().init_modules()
    ModuleLoader.instance().init_cli()

    if len(sys.argv) > 1:
        process_line(" ".join(sys.argv[1:]))
    else:
        repl()


def process_line(line: str) -> None:
    from gdo.base.Application import Application
    from gdo.base.Util import CLI
    from gdo.base.Trans import t
    method = CLI.parse(line)
    if method:
        Application.fresh_page()
        gdt = method.execute()
        txt = gdt.render_cli()
        txt = Application.get_page()._top_bar.render_cli() + txt
        print(txt)
    else:
        print(t('err_method', sys.argv[1] or t('none')))


def repl():
    from gdo.base.Exceptions import GDOModuleException
    while True:
        try:
            input_line = input(">>> ")
            if input_line == "":
                input_line = readline.get_history_item(readline.get_current_history_length())
            if input_line.lower() == "exit":
                break
            process_line(input_line)
        except GDOModuleException as ex:
            print(str(ex))
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as ex:
            print(str(ex))


if __name__ == '__main__':
    parent_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))
    sys.path.append(parent_dir)
    run()
