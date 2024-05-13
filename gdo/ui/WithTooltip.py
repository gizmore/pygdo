from gdo.base.Trans import t


class WithTooltip:
    _tt_key: str
    _tt_args: list
    _tt_escaped: bool

    def tooltip(self, key: str, args: list = None):
        self._tt_key = key
        self._tt_args = args
        return self.tt_escaped(False)

    def tooltip_raw(self, tooltip: str, escaped: bool = True):
        self._tt_key = '%s'
        self._tt_args = [tooltip]
        return self.tt_escaped(escaped)

    def tt_escaped(self, escaped: bool):
        self._tt_escaped = escaped
        return self

    def has_tooltip(self) -> bool:
        return hasattr(self, '_tt_key')

    def get_tooltip_text(self) -> str:
        return t(self._tt_key, self._tt_args)
