import json
import toml

from gdo.base.Application import Application
from gdo.base.Util import Files


def t(key: str, args=None):
    if args is None:
        args = []
    return Trans.t(key, args)


def tiso(iso: str, key: str, args=None):
    if args is None:
        args = []
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
                file_path = f"{path}_{iso}.toml"  # Construct the file path
                if Files.exists(file_path):
                    with open(file_path, 'r') as f:
                        more = toml.load(f)
                        cls.CACHE[iso].update(more)
        return cls.CACHE[iso]

    @classmethod
    def t(cls, key: str, args: list):
        iso = Application.LANG_ISO
        return tiso(iso, key, args)

    @classmethod
    def tiso(cls, iso, key: str, args: list):
        try:
            data = cls._load(iso)
            fmt = data[key]
            if args:
                return fmt % tuple(args)
            return fmt
        except KeyError:
            cls.FAILURES[key] = 1
            return f"__{key}: {json.dumps(args)}"
        except TypeError:
            cls.FAILURES[key] = 2
            return f"____{key}: {json.dumps(args)}"

    @classmethod
    def has(cls, key: str) -> bool:
        data = cls._load(Application.LANG_ISO)
        return key in data.keys()
