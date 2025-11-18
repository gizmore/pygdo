from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.base.Util import Strings

class WithText:
    _text_key: str
    _text_args: tuple|None
    _text_escaped: bool

    def text(self, key: str, args: tuple = None, escaped: bool = False):
        self._text_key = key
        self._text_args = args
        return self.text_escaped(escaped)

    def text_raw(self, text: str, escaped=True):
        return self.text('%s', (text,)).text_escaped(escaped)

    def text_escaped(self, escaped=True):
        self._text_escaped = escaped
        return self

    def has_text(self) -> bool:
        return hasattr(self, '_text_key')

    def render_text(self, mode: Mode = Mode.render_html) -> str:
        out = t(self._text_key, self._text_args)
        return Strings.html(out, mode) if self._text_escaped else out