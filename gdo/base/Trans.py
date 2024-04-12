import json

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


class Trans:
    CACHE = {
        'en': {},
        'de': {},
    }

    BASES = []
    LOADED = False

    def __init__(self):
        pass

    @classmethod
    def add_language(cls, base_path):
        cls.BASES.append(base_path)

    @classmethod
    def _load(cls, iso: str):
        if not len(cls.CACHE[iso]):
            for path in cls.BASES:
                file_path = f"{path}_{iso}.json"  # Construct the file path
                if Files.exists(file_path):
                    with open(file_path, 'r') as file:
                        more = json.load(file)  # Load JSON data from the file
                        cls.CACHE[iso].update(more)  # Update the CACHE dictionary with the loaded data
            cls.LOADED = True

    @classmethod
    def t(cls, key, args):
        iso = Application.LANG_ISO
        return tiso(iso, key, args)

    @classmethod
    def tiso(cls, iso, key, args):
        cls._load(iso)
        data = cls.CACHE[iso]
        if key not in data.keys():
            return f"__{key}: {json.dumps(args)}"
        fmt = data[key]
        if args:
            return fmt % args
        return fmt
