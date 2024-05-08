from gdo.base.Render import Mode


class WithIcon:

    @classmethod
    def display_icon(cls, name: str, mode: Mode, alt: str, color: str = None, size: str = None):
        from gdo.ui.IconProvider import IconProvider
        return IconProvider.display_icon(name, mode, alt, color, size)

    _icon_name: str
    _icon_alt: str
    _icon_color: str
    _icon_size: str

    def icon(self, name: str, alt: str = None, color: str = None, size='14px'):
        self._icon_name = name
        self._icon_alt = alt or f"{name} icon"
        self._icon_color = color
        self._icon_size = size
        return self

    def icon_name(self, name: str):
        self._icon_name = name
        return self

    def icon_color(self, color: str):
        self._icon_color = color
        return self

    def icon_size(self, size: str):
        self._icon_size = size
        return self

    def icon_alt(self, alt: str):
        self._icon_alt = alt
        return self

    def render_icon(self, mode: Mode) -> str:
        return WithIcon.display_icon(self._icon_name, mode, self._icon_alt, self._icon_color, self._icon_size)
