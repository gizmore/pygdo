from __future__ import annotations

import getpass
import mimetypes
import os.path
import secrets
from collections import OrderedDict
from typing import Sequence

from gdo.base.Render import Mode


def err(msg: str, title: str = 'PyGDO'):
    from gdo.base.Application import Application
    from gdo.ui.GDT_Error import GDT_Error
    Application.get_page()._top_bar.add_field(GDT_Error().title_raw(title).title_raw(msg))


def href(module_name: str, method_name: str, append: str = '', fmt: str = 'html'):
    return f"/{module_name}.{method_name}{append}.{fmt}"


class CLI:

    @classmethod
    def get_current_user(cls):
        from gdo.core.connector.Bash import Bash
        name = getpass.getuser()
        return Bash.get_server().get_or_create_user(name)

    @classmethod
    def parse(cls, line):
        from gdo.base.Parser import Parser
        method = Parser(line, cls.get_current_user()).parse()
        return method


class Strings:
    @classmethod
    def substr_from(cls, s: str, frm: str, default='') -> str:
        """Return substring from the first occurrence of `frm` in `s`, or `default` if `frm` is not found."""
        index = s.find(frm)
        if index != -1:
            return s[index + len(frm):]
        return default

    @classmethod
    def substr_to(cls, s: str, to: str, default='') -> str:
        """Return substring up to (excluding) the first occurrence of `to` in `s`, or `default` if `to` is not found."""
        index = s.find(to)
        if index != -1:
            return s[:index]
        return default

    @classmethod
    def rsubstr_from(cls, s: str, frm: str, default='') -> str:
        """Return substring from the last occurrence of `frm` in `s`, or `default` if `frm` is not found."""
        index = s.rfind(frm)
        if index != -1:
            return s[index + len(frm):]
        return default

    @classmethod
    def rsubstr_to(cls, s: str, to: str, default='') -> str:
        """Return substring up to (excluding) the last occurrence of `to` in `s`, or `default` if `to` is not found."""
        index = s.rfind(to)
        if index != -1:
            return s[:index]
        return default

    @classmethod
    def nullstr(cls, s: str):
        """Return None on empty strings"""
        if s is None or s == '':
            return None
        return str(s)

    @classmethod
    def html(cls, s: str, mode: Mode = Mode.HTML):
        """
        Escape output for various formats
        """
        if s is None:
            return ''
        match mode:
            case Mode.HTML:
                return (s.replace('&', '&amp;').
                        replace('"', '&quot;').
                        replace("'", '&#039;').
                        replace('<', '&lt;').
                        replace('>', '&gt;'))
            case _:
                return s


class Files:

    @classmethod
    def exists(cls, path: str) -> bool:
        return os.path.exists(path)

    @classmethod
    def serve_filename(cls, file_path: str, request) -> bool:
        from gdo.base.Application import Application
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            request.content_type = mime_type
        with open(file_path, 'rb') as file:
            chunk_size = int(Application.config('file.block_size', 4096))
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                request.write(chunk)
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


class Random:

    @classmethod
    def token(cls, length: int):
        return secrets.token_hex(length)
