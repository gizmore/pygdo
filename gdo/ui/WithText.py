from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.base.Util import Strings
from gdo.ui.GDT_Paragraph import GDT_Paragraph


class WithText:
    _text_key: str
    _text_args: list
    _text_escaped: bool

    def text(self, key, args: list = None, escaped: bool = False):
        self._text_key = key
        self._text_args = args
        return self.text_escaped(escaped)

    def text_raw(self, text: str, escaped=True):
        return self.text('%s', [text]).text_escaped(escaped)

    def text_escaped(self, escaped=True):
        self._text_escaped = escaped
        return self

    def has_text(self) -> bool:
        return hasattr(self, '_text_key')

    def render_text(self, mode: Mode = Mode.HTML) -> str:
        out = ''
        if self.has_text():
            out = t(self._text_key, self._text_args)
            if self._text_escaped:
                return Strings.html(out, mode)
        return out
