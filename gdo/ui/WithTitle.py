from gdo.base.Trans import t
from gdo.base.Util import Strings


class WithTitle:

    _title_key: str
    _title_args: list
    _title_escaped: bool

    def render_title(self) -> str:
        out = t(self._title_key, self._title_args)
        if self._title_escaped:
            return Strings.html(out)
        return out

    def title(self, key, args: list = None, title_escaped=False):
        self._title_key = key
        self._title_args = args
        return self.title_escaped(title_escaped)

    def title_raw(self, title: str, escaped=True):
        return self.title('%s', [title]).title_escaped(escaped)

    def title_escaped(self, escaped=True):
        self._title_escaped = escaped
        return self