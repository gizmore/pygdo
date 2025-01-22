from gdo.base.Trans import t
from gdo.base.Util import html


class WithTooltip:
    _tt_key: str
    _tt_args: tuple
    _tt_escaped: bool

    def tooltip(self, key: str, args: tuple = None, escaped: bool = False):
        self._tt_key = key
        self._tt_args = args
        return self.tt_escaped(escaped)

    def tooltip_raw(self, tooltip: str, escaped: bool = True):
        self._tt_key = '%s'
        self._tt_args = (tooltip,)
        return self.tt_escaped(escaped)

    def tt_escaped(self, escaped: bool):
        self._tt_escaped = escaped
        return self

    def has_tooltip(self) -> bool:
        return hasattr(self, '_tt_key')

    def render_tooltip(self) -> str:
        tt = t(self._tt_key, self._tt_args)
        return html(tt) if self._tt_escaped else tt
