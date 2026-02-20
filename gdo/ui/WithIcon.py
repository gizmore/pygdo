from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.core.WithLabel import WithLabel
from gdo.ui.IconProvider import IconProvider


class WithIcon(WithLabel):

    @classmethod
    def display_icon(cls, name: str, mode: Mode = Mode.render_html, alt_key: str = None, alt_args = None, color: str = None, size: str = None):
        return IconProvider.display_icon(name, mode, alt_key, alt_args, color, size)

    _icon_name: str
    _icon_alt_key: str
    _icon_alt_args: tuple[str|int|float,...]
    _icon_color: str
    _icon_size: str

    def icon(self, name: str, alt_key: str = None, alt_args: tuple[str|int|float,...] = None, color: str = None, size=None):
        self._icon_name = name
        self._icon_color = color
        self._icon_size = size or '16px'
        self._icon_alt_key = alt_key or 'an_icon'
        self._icon_alt_args = alt_args if alt_key else t(name)
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

    def icon_alt(self, key: str, args: tuple[str|int|float,...]=None):
        self._icon_alt_key = key
        self._icon_alt_args = args
        return self

    # def render_icon_alt(self, mode: Mode):
    #     if hasattr(self, '_icon_alt_key'):
    #         return t(self._icon_alt_key, self._icon_alt_args) if mode.is_html() else ''
    #     return ''

    def render_icon(self, mode: Mode) -> str:
        return '' if not hasattr(self, '_icon_name') else WithIcon.display_icon(self._icon_name, mode, self._icon_alt_key, self._icon_alt_args, self._icon_color, self._icon_size)
