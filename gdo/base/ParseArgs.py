from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Trans import Trans
from gdo.base.Util import Strings

from typing import TYPE_CHECKING, Any, Generator

from gdo.base.WithPygdo import WithPygdo

if TYPE_CHECKING:
    from gdo.base.Method import Method

class ParseArgs(WithPygdo):
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

    def get_val(self, key: str, default: str = "") -> list[str]|str:
        return self.args.get(key, default)

    def all_vals(self) -> Generator[tuple[Any, Any] | tuple[int, Any], None, None]:
        yield from self.args.items()
        yield from enumerate(self.pargs)

    def get_method(self) -> 'Method':
        try:
            method = self.loader().get_module_method(self.module, self.method)
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

    def add_arg(self, key: str, vals: list[str]|str):
        self.args[key] = vals
        return self

    def add_get_vars(self, qs: dict[str,list[str]]):
        return self.add_web_args(qs)

    def add_post_vars(self, qs: dict[str,list[str]]):
        return self.add_web_args(qs)

    def split_bracket_key(self, key: str) -> list[str]:
        # "f[name][x]" -> ["f","name","x"]
        parts = []
        buf = []
        i = 0
        n = len(key)

        while i < n:
            c = key[i]
            if c == '[':
                if buf:
                    parts.append(''.join(buf))
                    buf.clear()
                i += 1
                while i < n and key[i] != ']':
                    buf.append(key[i])
                    i += 1
                parts.append(''.join(buf))  # may be "" for []
                buf.clear()
                if i < n and key[i] == ']':
                    i += 1
            else:
                buf.append(c)
                i += 1

        if buf:
            parts.append(''.join(buf))
        return parts

    def insert_nested(self, d: dict, key: str, values: list[str]):
        parts = self.split_bracket_key(key)
        if not parts:
            return

        # key ends with [] -> list stored at the container under the previous part
        is_list = (parts[-1] == "")
        if is_list:
            parts = parts[:-1]  # drop ""

        cur = d
        for p in parts[:-1]:
            nxt = cur.get(p)
            if not isinstance(nxt, dict):
                nxt = {}
                cur[p] = nxt
            cur = nxt

        last = parts[-1]
        if is_list:
            lst = cur.get(last)
            if not isinstance(lst, list):
                lst = []
                cur[last] = lst
            lst.extend(values)
        else:
            cur[last] = values

    def add_web_args(self, qs: dict[str, list[str]]):
        for key, vals in qs.items():
            # val = vals if len(vals) > 1 else vals[0]
            self.insert_nested(self.args, key, vals)
        return self

    # def add_web_args(self, qs: dict[str,list[str]]):
    #     for key, vals in qs.items():
    #         self.args[key.rstrip('[]')] = vals
    #     return self

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
            return Mode[f"render_{self.mode}"]
        except KeyError:
            pass
        return Application.get_mode()

    def clear(self):
        self.args = {}
        self.pargs = []
        self.files = []

    def get_cache_key(self, method: 'Method') -> str:
        return f"{method.fqcn()}.{self.args}.{self.pargs}{Application.STORAGE.lang}"
