from __future__ import annotations

import string
import functools

import asyncio

import magic

import getpass
import hashlib
import os.path
import random
import re
import secrets
import shutil
import sys
import urllib.parse
from collections import OrderedDict
from html import unescape
from itertools import product
from typing import Sequence

import msgspec.json

from gdo.base.Render import Mode

from prompt_toolkit.shortcuts import print_formatted_text as pt_print
from prompt_toolkit.formatted_text import ANSI

def gdo_print(s: str, end="\n"):
    pt_print(ANSI(s), end=end)



def hdr(name: str, value: str):
    from gdo.base.Application import Application
    Application.header(name, value)


def html(s: str, mode: Mode = Mode.HTML):
    return Strings.html(s, mode)


def urlencode(s: str):
    return urllib.parse.quote_plus(s)


def jsn(obj: any):
    return msgspec.json.encode(obj)

def bytelen(s: str, encoding: str = 'utf-8') -> int:
    """
    Get size of a string in bytes without codecs
    By ChatGPT and gizmore :)
    """
    if isinstance(s, bytes):
        return len(s)

    return len(s.encode(encoding))


def err(key: str, args: tuple = None, title: str = 'PyGDO'):
    from gdo.base.Application import Application
    from gdo.ui.GDT_Error import GDT_Error
    error = GDT_Error().text(key, args).title_raw(title)
    Application.get_page()._top_bar.add_field(error)


def err_raw(message: str, title: str = 'PyGDO'):
    err('%s', (message,))


def msg(key: str, args: tuple = None, title: str = 'PyGDO', no_log: bool = False):
    from gdo.base.Application import Application
    from gdo.ui.GDT_Success import GDT_Success
    message = GDT_Success().text(key, args).title_raw(title).no_log(no_log)
    Application.get_page()._top_bar.add_field(message)


def dump(*obj: any):
    from gdo.base.Logger import Logger
    for o in obj:
        msg = jsn(o)
        Logger.debug(msg)
        err_raw(msg)


@functools.cache
def module_enabled(module_name: str) -> bool:
    from gdo.base.ModuleLoader import ModuleLoader
    if module := ModuleLoader.instance().get_module(module_name):
        return module.is_enabled()
    return False


class CLI:

    @classmethod
    def get_current_user(cls):
        from gdo.core.connector.Bash import Bash
        name = getpass.getuser()
        return Bash.get_server().get_or_create_user(name)

class Strings:

    @staticmethod
    def substr_from(s: str, frm: str, default='') -> str:
        """Return substring from the first occurrence of `frm` in `s`, or `default` if `frm` is not found."""
        index = s.find(frm)
        return s[index + len(frm):] if index >= 0 else default

    @staticmethod
    def substr_to(s: str, to: str, default='') -> str:
        """Return substring up to (excluding) the first occurrence of `to` in `s`, or `default` if `to` is not found."""
        index = s.find(to)
        return s[:index] if index >= 0 else default

    @staticmethod
    def rsubstr_from(s: str, frm: str, default='') -> str:
        """Return substring from the last occurrence of `frm` in `s`, or `default` if `frm` is not found."""
        index = s.rfind(frm)
        return s[index + len(frm):] if index >= 0 else default

    @staticmethod
    def rsubstr_to(s: str, to: str, default='') -> str:
        """Return substring up to (excluding) the last occurrence of `to` in `s`, or `default` if `to` is not found."""
        index = s.rfind(to)
        return s[:index] if index >= 0 else default

    HTML_ESCAPE_TABLE = str.maketrans({
        '&': '&amp;',
        '"': '&quot;',
        "'": '&#039;',
        '<': '&lt;',
        '>': '&gt;',
    })

    @staticmethod
    def html(s: str, mode: Mode = Mode.HTML) -> str:
        if mode.is_html() and s is not None:
            return s.translate(Strings.HTML_ESCAPE_TABLE)
        return s or ''

    @classmethod
    def html_to_text(cls, html: str):
        html = re.sub(r'<a\s*href="([^"]+)">([^"]+)</a>', r'\1 (\2)', html)
        html = cls.br2nl(html)
        html = re.sub(r'<[^>]*>', '', html)
        return unescape(html)

    @classmethod
    def br2nl(cls, s):
        return re.sub(r'<\s*br\s*/?\s*>', '\n', s)

    @classmethod
    def split_boundary(cls, text: str, chunk_size: int):
        """
        (c) ChatGPT
        """
        # Check if the text is shorter than the chunk size
        if len(text) <= chunk_size:
            return [text]

        # Find the nearest word boundary to the chunk size
        boundary_index = chunk_size
        while boundary_index > 0 and not text[boundary_index].isspace():
            boundary_index -= 1

        # If no word boundary was found, split at the chunk size
        if boundary_index == 0:
            return [text[:chunk_size]] + cls.split_boundary(text[chunk_size:], chunk_size)

        # Otherwise, split at the word boundary
        return [text[:boundary_index]] + cls.split_boundary(text[boundary_index:], chunk_size)

    @classmethod
    def regex_first(cls, pattern: str, string: str):
        """
        Get the first matching group value of a string match
        """
        match = re.search(pattern, string)
        return match.group(1) if match else None

    @staticmethod
    def replace_all(s: str, replace: dict):
        for search, r in replace.items():
            s = s.replace(search, r)
        return s


class Files:

    @classmethod
    def exists(cls, path: str) -> bool:
        return os.path.exists(path)

    @classmethod
    def human_file_size(cls, num: int, div: int = 1000, suffix: str = "B") -> str:
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if num < div:
                return f"{num:3.1f}{unit}{suffix}"
            num /= div
        return f"{num:.1f}Yi{suffix}"

    @classmethod
    def is_file(cls, path: str) -> bool:
        return os.path.isfile(path)

    @classmethod
    def is_dir(cls, path: str) -> bool:
        return os.path.isdir(path)

    @classmethod
    def empty_dir(cls, path: str) -> bool:
        cls.delete_dir(path)
        return cls.create_dir(path)

    @classmethod
    def delete_dir(cls, path: str) -> bool:
        shutil.rmtree(path)
        return True

    @classmethod
    def create_dir(cls, path: str) -> bool:
        os.makedirs(path, mode=0o700, exist_ok=True)
        return True

    @classmethod
    async def acreate_dir(cls, dir_name: str):
        await asyncio.to_thread(os.makedirs, dir_name, exist_ok=exist_ok, mode=0o700)
        # await aiofiles.os.makedirs(dir_name, mode=0o700, exist_ok=True)
        return True

    @classmethod
    def remove(cls, path: str) -> bool:
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False

    @classmethod
    def touch(cls, path: str, create: bool = False) -> bool:
        if create and not os.path.isfile(path):
            with open(path, "w"):
                return True
        from gdo.base.Application import Application
        time = Application.TIME
        os.utime(path, (time, time))
        return True

    @classmethod
    def append_content(cls, path: str, content: str, create: bool = False) -> bool:
        with open(path, "a") as f:
            f.write(content)
        return True

    @classmethod
    def copy(cls, src: str, dst: str) -> bool:
        shutil.copy(src, dst)
        return True

    @classmethod
    def put_contents(cls, path: str, contents) -> bool:
        with open(path, 'wb') as f:
            f.write(contents.encode() if isinstance(contents, str) else contents)
        return True

    @classmethod
    def get_contents(cls, path: str):
        try:
            with open(path, 'r', encoding='UTF-8') as f:
                return f.read()
        except FileNotFoundError as ex:
            from gdo.base.Logger import Logger
            Logger.exception(ex)

    @staticmethod
    @functools.lru_cache()
    def mime(path: str):
        if path[-4:] == '.css':
            return 'text/css'
        return magic.from_file(path, mime=True)

    @staticmethod
    def size(path: str) -> int:
        return os.path.getsize(path)

    @classmethod
    def dir_size_recursive(cls, dir_name: str) -> int:
        total_size = 0
        try:
            with os.scandir(dir_name) as entries:
                for entry in entries:
                    if entry.is_file(follow_symlinks=False):
                        total_size += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total_size += cls.dir_size_recursive(entry.path)
        except PermissionError as ex:
            pass
        return total_size

    @classmethod
    def md5(cls, path: str) -> str:
        from gdo.base.Application import Application
        hash_md5 = hashlib.md5()
        block_size = int(Application.config('file.block_size', "4096"))
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @classmethod
    def dirname(cls, path: str) -> str:
        return os.path.dirname(path)

    @classmethod
    def move(cls, src: str, dest: str) -> bool:
        os.rename(src, dest)
        return True


class Arrays:
    """
    List and Dictionary utilities.
    """

    @classmethod
    def walk(cls, dictionary: dict, path: str):
        """
        Access a nested dictionary via a path separated by dot.
        """
        keys = path.split('.')
        value = dictionary
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        return value

    @classmethod
    def reverse_dict(cls, dic: dict) -> dict:
        """
        Reverse a dictionary.
        """
        return OrderedDict(reversed(list(dic.items())))

    @classmethod
    def unique(cls, lst: list) -> list:
        """
        Return only unique items of a list
        """
        return list(set(lst))

    @classmethod
    def chunkify(cls, lst: list, chunk_size: int) -> list:
        """
        Split a list into chunks of a specified size.

        Args:
            lst (list): The list to split.
            chunk_size (int): The size of each chunk.

        Returns:
            list: A list of lists, each containing elements of the original list in chunks.
        """
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @classmethod
    def recursive_map(cls, seq, func, out=''):
        for item in seq:
            if isinstance(item, Sequence):
                yield type(item)
                cls.recursive_map(item, func)
            else:
                yield func(item)

    @classmethod
    def map_dict_values_only(cls, f: callable, dic: dict) -> dict:
        """
        Map a dict recursively but only touch values.
        """
        for key, val in dic.items():
            if isinstance(val, dict):
                dic[key] = cls.map_dict_values_only(f, val)
            else:
                dic[key] = f(val)
        return dic

    @classmethod
    def dict_index(cls, dic: dict[str, any], value):
        index_no = list(dic.values()).index(value)
        return list(dic.keys())[index_no]

    @classmethod
    def human_join(cls, lst: list[str], conn: str = 'and') -> str:
        from gdo.base.Trans import t
        if len(lst) == 0:
            return ''
        elif len(lst) == 1:
            return lst[0]
        else:
            return f"{', '.join(lst[:-1])} {t(conn)} {lst[-1]}"

    @classmethod
    def empty(cls, vals: list[str]) -> bool:
        return not vals or len(vals) == 0 or (len(vals) == 1 and not vals[0])

    @classmethod
    def mem_size(cls, obj: any, seen: set[any] = None) -> int:
        """Recursively find size of objects in bytes."""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum(cls.mem_size(k, seen) + cls.mem_size(v, seen) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            size += sum(cls.mem_size(i, seen) for i in obj)
        return size

    @staticmethod
    def extend_unknown(target: dict, source: dict) -> dict:
        """Extend target with keys from source, but only if they are not already present."""
        for k, v in source.items():
            target.setdefault(k, v)
        return target


class Random:

    _seed: int
    _old_state: any

    def __init__(self, seed: int):
        self._seed = seed
        self._old_state = random.getstate()

    def __enter__(self):
        Random.init(self._seed)

    def __exit__(self, *a):
        random.setstate(self._old_state)

    @staticmethod
    def init(seed: int):
        random.seed(seed)

    @staticmethod
    def token(length: int):
        return secrets.token_hex(length)

    @staticmethod
    def rand(lo: int = 0, hi: int = sys.maxsize):
        return lo + secrets.randbelow(hi - lo + 1)

    @staticmethod
    def randf(lo: float = 0.0, hi: float = 1.0):
        r = secrets.randbits(53) / (1 << 53)
        return lo + (hi - lo) * r

    @staticmethod
    def mrand(lo: int = 0, hi: int = sys.maxsize):
        return random.randint(lo, hi)

    @staticmethod
    def mrandf(lo: float = None, hi: float = None):
        if lo is None:
            lo = -sys.float_info.max
        if hi is None:
            hi = sys.float_info.max
        return random.uniform(lo, hi)

    @staticmethod
    def dict_key(dic: dict):
        """
        Return a random dictionary key
        """
        keys = list(dic.keys())
        return Random.list_item(keys)

    @staticmethod
    def list_item(lst: list):
        if lst:
            index = Random.mrand(0, len(lst) - 1)
            return lst[index]
        return None


class Permutations:
    def __init__(self, values: list[list[int|str|float]]):
        self.values = values
        self.count = self.count_permutations(values)
        self.last_permutation = [0] * len(values)

    @staticmethod
    def count_permutations(values):
        return len(list(product(*values)))

    def generate(self):
        yield self.get_current_permutation()
        for _ in range(1, self.count):
            self.update_next_permutation()
            yield self.get_current_permutation()

    def get_current_permutation(self):
        return [self.values[i][self.last_permutation[i]] for i in range(len(self.values))]

    def update_next_permutation(self):
        for i in range(len(self.values)):
            self.last_permutation[i] += 1
            if self.last_permutation[i] < len(self.values[i]):
                break
            self.last_permutation[i] = 0


class NumericUtil:

    DIGITS = string.digits + string.ascii_uppercase + string.ascii_lowercase + "+/"
    DIGITS_BASE64 = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"

    @staticmethod
    def output_prefix(base: int) -> str:
        return {2: '0b', 8: '0o', 16: '0x'}.get(base, '')

    @staticmethod
    def to_base(n: int, base: int, charset: str = DIGITS) -> str:
        if n == 0:
            return charset[0]
        neg = n < 0
        n = abs(n)
        result = []
        while n > 0:
            result.append(charset[n % base])
            n //= base
        if neg:
            result.append('-')
        return ''.join(reversed(result))

    @staticmethod
    def from_base(s: str, base: int, charset: str = DIGITS) -> int:
        s = s.strip()
        neg = 1
        if s.startswith('-'):
            neg = -1
            s = s[1:]
        num = 0
        for char in s:
            if char not in charset:
                raise ValueError(f"Invalid character {char} for NumericUtil encoding")
            num = num * base + charset.index(char)
        return num * neg
