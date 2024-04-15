import contextlib
import shutil

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Arrays
from gdo.core.GDT_Template import GDT_Template


class Config:
    """
    Create and update config.toml files.
    Setup default configuration
    """

    @classmethod
    def data(cls, cfg: dict) -> dict[str, GDT]:
        from gdo.core.GDT_Select import GDT_Select
        from gdo.core.GDT_UInt import GDT_UInt
        from gdo.ui.GDT_Section import GDT_Section
        lst = [
            GDT_Section().title_raw('Database'),
            cls.data_str('db.host', 'localhost'),
            cls.data_str('db.name', 'localhost'),
            cls.data_str('db.user', 'localhost'),
            cls.data_str('db.pass', 'localhost'),
            cls.data_int('db.debug', 0),
            GDT_Section().title_raw('Locale'),
            GDT_Select('i18n.iso').choices({'en': 'English', 'de': 'Deutsch'}).initial('en'),
        ]
        dic = {}
        for gdt in lst:
            dic[gdt.get_name()] = gdt
        return dic

    @classmethod
    def data_str(cls, key_path: str, default: str):
        from gdo.core.GDT_String import GDT_String
        gdt = GDT_String(key_path).initial(default)
        with contextlib.suppress(KeyError, IndexError):
            gdt.initial(Arrays.walk(Application.CONFIG, key_path))
        return gdt

    @classmethod
    def data_int(cls, key_path: str, default: int):
        from gdo.core.GDT_Int import GDT_Int
        gdt = GDT_Int(key_path).initial(str(default))
        with contextlib.suppress(KeyError):
            gdt.initial(str(Arrays.walk(Application.CONFIG, key_path)))
        return gdt

    @classmethod
    def rewrite(cls, path: str, data: dict[str, GDT]):
        shutil.copyfile(path, path + ".OLD")
        out = GDT_Template.python('install', 'config.toml.html', {'data': data})
        if out:
            with open(path, 'w') as fo:
                fo.write(out)
