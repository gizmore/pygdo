import glob
import os

import tomlkit

from gdo.base.Application import Application
from gdo.base.Util import Strings, dump

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User


def t(key: str, args: tuple=None):
    return Trans.t(key, args)


def tusr(user: 'GDO_User', key: str, args: tuple = None):
    return Trans.tiso(user.get_lang_iso(), key, args)


def tiso(iso: str, key: str, args: tuple = None):
    return Trans.tiso(iso, key, args)


def thas(key: str) -> bool:
    return Trans.has(key)


def sitename() -> str:
    return Application.config('core.sitename', 'PyGDO')


class Trans:
    """
    Speed optimized i18n.
    """
    EN = {}
    CACHE = {}

    old_iso: str
    new_iso: str

    def __init__(self, iso: str):
        self.new_iso = iso
        self.old_iso = Application.STORAGE.lang

    def __enter__(self):
        Application.STORAGE.lang = self.new_iso

    def __exit__(self, *args):
        Application.STORAGE.lang = self.old_iso

    @classmethod
    def init(cls):
        cls._load()

    @classmethod
    def _load(cls):
        pattern = os.path.join(Application.file_path('gdo/'), "*", "lang", "*.toml")
        for lang_file in glob.glob(pattern, recursive=True):
            cls._load_file(lang_file)
        cls.EN = cls.CACHE.get('en', {})

    @classmethod
    def _load_file(cls, lang_file: str):
        iso = Strings.rsubstr_from(lang_file, 'lang/')
        iso = iso[-7:-5]
        if iso not in cls.CACHE:
            cls.CACHE[iso] = {}
        with open(lang_file, 'r', encoding='UTF-8') as fd:
            more = tomlkit.load(fd)
            cls.CACHE[iso].update(more)

    @classmethod
    def t(cls, key: str, args: tuple=None):
        return tiso(Application.STORAGE.lang, key, args)

    @classmethod
    def tiso(cls, iso: str, key: str, args: tuple = None):
        try:
            key = cls.CACHE.get(iso, cls.EN).get(key, cls.EN.get(key, key))
            return key % args if args else key
        except:
            if args:
                return key + "(" + str(args) + ")"
            return key

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls.CACHE[Application.STORAGE.lang]
