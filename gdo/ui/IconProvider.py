from functools import lru_cache
from gdo.base.LazyImporter import LazyImporter
from gdo.base.Render import Mode
from gdo.base.Trans import t


class IconProvider:
    PROVIDERS = []

    @classmethod
    def MAP(cls) -> dict:
        return {}

    @classmethod
    def register(cls, icon_provider):
        if icon_provider not in IconProvider.PROVIDERS:
            IconProvider.PROVIDERS.append(icon_provider)

    @classmethod
    def has_icon(cls, name: str) -> bool:
        return name in cls.MAP()

    ##########
    # Render #
    ##########
    @classmethod
    @lru_cache(maxsize=None)
    def display_icon(cls, name: str, mode: Mode, alt_key: str = None, alt_args: tuple[str|int|float,...] = None, color: str = None, size: str = None) -> str:
        if mode.is_html():  # HTML mode?
            for provider in reversed(IconProvider.PROVIDERS):
                if provider.has_icon(name):
                    return provider.display_icon_html(name, mode, alt_key, alt_args, color, size)
        IconUTF8 = LazyImporter.import_once("from gdo.ui.IconUTF8 import IconUTF8")
        if utf8_fallback := IconUTF8.MAP().get(name):
            return utf8_fallback
        return f'_-{name}-_'

    @classmethod
    def display_icon_html(cls, name: str, mode: Mode, alt_key: str=None, alt_args: tuple[str|int|float,...]=None, color: str = None, size: str = None) -> str:
        return t(alt_key, alt_args) if alt_key else name
