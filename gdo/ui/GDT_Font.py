from gdo.base.GDT import GDT


class GDT_Font(GDT):
    FONTS = {}

    @classmethod
    def register(cls, key: str, path: str):
        cls.FONTS[key] = path
