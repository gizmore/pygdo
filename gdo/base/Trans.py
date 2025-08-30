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
    EN: dict[str, str] = {}
    CACHE = {
        'en': EN,
    }

    old_iso: str
    new_iso: str

    def __init__(self, iso: str):
        self.new_iso = iso
        self.old_iso = Application.STORAGE.lang

    def __enter__(self):
        Application.STORAGE.lang = self.new_iso

    def __exit__(self, *args):
        Application.STORAGE.lang = self.old_iso

    @staticmethod
    def init():
        Trans._load()

    @staticmethod
    def _load():
        pattern = os.path.join(Application.file_path('gdo/'), "*", "lang", "**", "*.toml")
        for lang_file in glob.glob(pattern, recursive=True):
            Trans._load_file(lang_file)
        # Trans.EN = Trans.CACHE.get('en')

    @staticmethod
    def _load_file(lang_file: str):
        iso = Strings.rsubstr_from(lang_file, 'lang/')
        iso = iso[-7:-5]
        if iso not in Trans.CACHE:
            Trans.CACHE[iso] = {}
        with open(lang_file, 'r', encoding='UTF-8') as fd:
            more = tomlkit.load(fd)
            cache = Trans.CACHE[iso]
            for k, v in more.items():
                cache[k] = str(v)
            # Trans.CACHE[iso].update(more)

    @staticmethod
    def t(key: str, args: tuple=None):
        return Trans.tiso(Application.STORAGE.lang, key, args)

    @staticmethod
    def tiso(iso: str, key: str, args: tuple = None):
        try:
            if format := Trans.CACHE.get(iso, Trans.EN).get(key):
                return format % args if args else format
        except:
            pass
        return key + str(args) if args else key

    @staticmethod
    def has(key: str) -> bool:
        return key in Trans.CACHE[Application.STORAGE.lang]
