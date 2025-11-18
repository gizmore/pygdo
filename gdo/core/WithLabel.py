from gdo.base.Render import Mode
from gdo.base.Util import Strings, dump
from gdo.base.Trans import t


class WithLabel:
    _label_key: str
    _label_args: tuple
    _label_escape: bool

    def label(self, key: str, args: tuple=None):
        self._label_key = key
        self._label_args = args
        self._label_escape = False
        return self

    def label_raw(self, label_text: str, escape=True):
        return self.label('%s', (label_text,)).label_escape(escape)

    def label_escape(self, escape=True):
        self._label_escape = escape
        return self

    def has_label(self) -> bool:
        return hasattr(self, '_label_key')

    def render_label(self, mode: Mode = Mode.render_html):
        trans = t(self._label_key, self._label_args)
        if self._label_escape:
            trans = Strings.html(trans, mode)
        return trans
