from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Util import Strings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.base.Method import Method

class ParseArgs:
    ARG_SEPARATOR = "~"
    ENTRY_SEPARATOR = ";"
    ESCAPED_SEPARATOR = ";;"
    TEMP_MARKER = "\x01"

    def __init__(self):
        self.module = None
        self.method = None
        self.mode = None
        self.clear()

    def __repr__(self):
        return f"ParserArgs(module={self.module}, method={self.method}, args={self.args})"

    def get_val(self, key: str, default: str = "") -> list[str]:
        return self.args.get(key, default)

    def all_vals(self) -> dict[str, list[str]]:
        yield from self.args.items()
        yield from enumerate(self.pargs)

    def get_method(self) -> 'Method':
        try:
            from gdo.base.ModuleLoader import ModuleLoader
            method = ModuleLoader.instance().get_module_method(self.module, self.method)
            method._raw_args = self
            return method
        except:
            raise GDOModuleException(self.module)

    #############
    # Add input #
    #############

    def add_path_vars(self, url: str):
        try:
            if url:
                url = url.lstrip('/').replace(self.ESCAPED_SEPARATOR, self.TEMP_MARKER)
                parts = url.split(self.ENTRY_SEPARATOR)
                self.mode = Strings.rsubstr_from(parts[-1], '.', 'html')
                parts[-1] = Strings.rsubstr_to(parts[-1], '.', parts[-1])
                if parts[0].index('.'):
                    self.module, self.method = parts[0].split('.', 1)
                for part in parts[1:]:
                    key, val = part.split(self.ARG_SEPARATOR, 1)
                    self.args[key] = [val.replace(self.TEMP_MARKER, self.ENTRY_SEPARATOR)]
        except Exception as ex:
            pass

    def add_get_vars(self, qs: dict[str,list[str]]):
        return self.add_web_args(qs)

    def add_post_vars(self, qs: dict[str,list[str]]):
        return self.add_web_args(qs)

    def add_web_args(self, qs: dict[str,list[str]]):
        for key, vals in qs.items():
            self.args[key.rstrip('[]')] = vals
        return self

    def add_file(self, name: str, filename: str, raw_data: bytes):
        self.files.append((name, filename, raw_data))

    def add_cli_part(self, part: str|GDT):
        if type(part) is str and part.startswith('--'):
            part = part.lstrip('-')
            kv = part.split('=', 1)
            self.args[kv[0]] = kv[1]
        else:
            self.pargs.append(part)

    def add_cli_line(self, cli_args: list[str]):
        for part in cli_args:
            self.add_cli_part(part)

    def get_mode(self):
        try:
            return Mode[self.mode.upper()]
        except KeyError:
            pass
        return Application.get_mode()

    def clear(self):
        self.args = {}
        self.pargs = []
        self.files = []
