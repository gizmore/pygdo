from gdo.base.Render import Mode


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
    def display_icon(cls, name: str, mode: Mode, alt: str, color: str = None, size: str = None) -> str:
        from gdo.ui.IconUTF8 import IconUTF8
        if mode.value < 10:  # HTML mode?
            for provider in reversed(IconProvider.PROVIDERS):
                if provider.has_icon(name):
                    return provider.display_icon_html(name, alt, color, size)
        return IconUTF8.MAP[name]

    @classmethod
    def display_icon_html(cls, name: str, mode: Mode, alt: str, color: str = None, size: str = None) -> str:
        return name


