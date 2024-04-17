from gdo.base.Render import Mode
from gdo.base.Util import Strings
from gdo.base.Trans import t


class WithLabel:
    _label_key: str
    _label_args: list[str]
    _label_escape: bool

    def label(self, key: str, args=[]):
        self._label_key = key
        self._label_args = args
        self._label_escape = False
        return self.label_escape(False)

    def label_raw(self, label_text: str, escape=True):
        return self.label('%s', [label_text]).label_escape(escape)

    def label_escape(self, escape=True):
        self._label_escape = escape
        return self

    def render_label(self, mode: Mode = Mode.HTML):
        trans = t(self._label_key, self._label_args)
        if self._label_escape:
            trans = Strings.html(trans, mode)
        return trans
