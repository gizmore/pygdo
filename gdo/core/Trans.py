import json

from gdo.core.Util import Files


def t(key: str, args=None):
    if args is None:
        args = []
    return Trans.t(key, args)


class Trans:
    CACHE = {
        'en': {}
    }

    ISO = 'en'
    BASES = []
    LOADED = False

    def __init__(self):
        pass

    @classmethod
    def add_language(cls, base_path):
        cls.BASES.append(base_path)

    @classmethod
    def _load(cls):
        if not cls.LOADED:
            for path in cls.BASES:
                file_path = f"{path}_en.json"  # Construct the file path
                if Files.exists(file_path):
                    with open(file_path, 'r') as file:
                        more = json.load(file)  # Load JSON data from the file
                        cls.CACHE['en'].update(more)  # Update the CACHE dictionary with the loaded data
            cls.LOADED = True

    @classmethod
    def t(cls, key, args):
        try:
            cls._load()
            return cls.CACHE['en'][key] % args
        except KeyError as ex:
            return (cls.CACHE.en[key]) + ",".join(args)
