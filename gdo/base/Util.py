from __future__ import annotations

import getpass
import os.path
import secrets
from collections import OrderedDict
from typing import Sequence

from gdo.base.Render import Mode


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
        if s != '':
            return s
        return None

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

    def recursive_map(cls, seq, func):
        for item in seq:
            if isinstance(item, Sequence):
                yield type(item)
                cls.recursive_map(item, func)
            else:
                yield func(item)


class Random():

    @classmethod
    def token(cls, length: int):
        return secrets.token_hex(length)
