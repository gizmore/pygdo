from gdo.base.Logger import Logger
from gdo.base.Render import Render, Mode
from gdo.base.Trans import Trans, sitename
from gdo.base.Util import html
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Error(GDT_Panel):

    _trace: bool

    def __init__(self):
        super().__init__()
        self._trace = False

    def trace(self, trace: bool = True):
        self._trace = trace
        return self

    def html_class(self):
        if self._trace:
            return 'gdt-exception alert alert-danger'
        return 'gdt-error alert alert-warning'

    def render(self, mode: Mode = Mode.render_html):
        if not self._trace:
            with Trans('en'):
                Logger.error(self.render_text(Mode.render_txt))
        return super().render(mode)

    def render_txt(self):
        return "!!! " + self.render_text(Mode.render_txt)

    def render_cli(self):
        return Render.red(self.render_text(Mode.render_cli), Mode.render_cli)

    def render_irc(self) -> str:
        return Render.red(self.render_text(Mode.render_irc), Mode.render_irc)

    def render_telegram(self):
        return Render.red(self.render_text(Mode.render_telegram), Mode.render_telegram)

    @classmethod
    def from_exception(cls, ex: Exception, title: str = '', tb = None):
        Logger.exception(ex)
        text = html(str(ex))
        if not tb:
            tb = Logger.traceback(ex)
        return cls().trace().title_raw(sitename() + " " + title).text_raw(f"<pre>{text}\n\n{tb}</pre>\n", False)
