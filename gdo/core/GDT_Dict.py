from gdo.base.GDT import GDT


class GDT_Dict(GDT):

    _dict: dict[str, any]

    def __init__(self, **kwargs):
        super().__init__()
        self._dict = {}
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = GDT_Dict(**value)
            self._dict[key] = value

    def gdo_redis_fields(self) -> list[str]:
        return [
            '_dict',
        ]

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __contains__(self, key):
        return key in self._dict

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()
