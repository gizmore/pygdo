import json
import tomlkit
from tomlkit.exceptions import ParseError

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Util import Files


def t(key: str, args=None):
    if args is None:
        args = []
    return Trans.t(key, args)


def tusr(user: object, key: str, args: list = None):
    return Trans.tiso(user.get_lang_iso(), key, args)


def tiso(iso: str, key: str, args=None):
    # if args is None:
    #     args = []
    return Trans.tiso(iso, key, args)


def thas(key: str) -> bool:
    return Trans.has(key)


def sitename() -> str:
    return Application.config('core.sitename', 'PyGDO')


class Trans:
    FAILURES = {}
    BASES = []
    CACHE = {
        'en': {},
        'de': {},
    }

    old_iso: str
    new_iso: str

    def __init__(self, iso: str):
        self.new_iso = iso
        self.old_iso = Application.LANG_ISO

    def __enter__(self):
        Application.LANG_ISO = self.new_iso

    def __exit__(self, *args):
        Application.LANG_ISO = self.old_iso

    @classmethod
    def reload(cls):
        cls.CACHE = {
            'en': {},
            'de': {},
        }

    @classmethod
    def add_language(cls, base_path):
        # if base_path not in cls.BASES:
        cls.BASES.append(base_path)

    @classmethod
    def _load(cls, iso: str):
        if not len(cls.CACHE[iso]):
            for path in cls.BASES:
                file_path = f"{path}_{iso}.toml"
                if Files.exists(file_path):
                    with open(file_path, 'r') as f:
                        try:
                            more = tomlkit.load(f)
                            cls.CACHE[iso].update(more)
                        except ParseError as ex:
                            Logger.exception(ex)
        return cls.CACHE[iso]

    @classmethod
    def t(cls, key: str, args: list):
        iso = Application.STORAGE.lang
        return tiso(iso, key, args)

    @classmethod
    def tiso(cls, iso, key: str, args: list):
        try:
            data = cls.CACHE[iso]
            # fmt = data[key]
            # if args:
            return data[key] % tuple(args)
            # return fmt
        except KeyError:
            cls.FAILURES[key] = 1
            return f"__{key}: {json.dumps(args)}"
        except TypeError:
            cls.FAILURES[key] = 2
            return f"_xx_{key}: {json.dumps(args)}"

    @classmethod
    def has(cls, key: str) -> bool:
        data = cls._load(Application.LANG_ISO)
        return key in data.keys()
